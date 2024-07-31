import json
import logging
import os
import re
import shutil
import sys
from typing import List, Optional, cast

import chromadb
import json_repair
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from llama_index.core import (Settings, VectorStoreIndex, SimpleDirectoryReader, PromptTemplate)
from llama_index.core import StorageContext
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.output_parsers import LangchainOutputParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.core.schema import NodeWithScore, QueryBundle
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.legacy.postprocessor import BaseNodePostprocessor
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore
from pydantic import Field

from re_ranker import re_rank
from templates import RAG_TEMPLATE, QUESTION_GENERATION_TEMPLATE, FORMAL_SENTENCE_TEMPLATE

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

global query_engine, llm
query_engine = None
llm = None


def init_llm(response_schema=False):
    global llm
    if response_schema:
        response_schemas = [
            ResponseSchema(
                name="output",
                description="Check the validity of the knowledge graph triple based on the provided documents, yes if the triple is correct, no if the triple is incorrect.",
                type="boolean"
            )
        ]
        # define output parser
        lc_output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        llm = Ollama(model="llama3.1", request_timeout=300.0, output_parser=LangchainOutputParser(lc_output_parser))
    else:
        llm = Ollama(model="llama3.1", request_timeout=300.0)

    # model_name = "jinaai/jina-embeddings-v2-small-en"
    model_name = "BAAI/bge-small-en-v1.5"
    embed_model = HuggingFaceEmbedding(model_name=model_name)

    Settings.llm = llm
    Settings.embed_model = embed_model

    sentence_parser = SentenceWindowNodeParser.from_defaults(
        window_size=6,  # Number of sentences in each window
        window_metadata_key="window",  # Metadata key for window information
        original_text_metadata_key="original_text"  # Metadata key for original text
    )

    Settings.node_parser = sentence_parser


class DummyNodePostprocessor(BaseNodePostprocessor):
    """Similarity-based Node processor."""

    knowledge_graph: str = Field(default="")
    similarity_cutoff: float = Field(default=None)

    @classmethod
    def class_name(cls) -> str:
        return "Change Similarity Postprocessor"

    def _postprocess_nodes(
            self,
            nodes: List[NodeWithScore],
            query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        """Postprocess nodes."""
        new_nodes = []
        sim_cutoff_exists = self.similarity_cutoff is not None

        re_rank_nodes = re_rank(self.knowledge_graph, [node.text for node in nodes])

        for node in nodes:
            score = list(filter(lambda x: x['question'] == node.text, re_rank_nodes))[0]['score']

            node.score = score
            should_use_node = True
            if sim_cutoff_exists:
                similarity = node.score
                if similarity is None:
                    should_use_node = False
                elif cast(float, similarity) < cast(float, self.similarity_cutoff):
                    should_use_node = False

            if should_use_node:
                new_nodes.append(node)

        return new_nodes


def init_index(embed_model, directory="./docs", persist=False):
    reader = SimpleDirectoryReader(input_dir=directory, recursive=True, exclude=["questions.json", "index", "all_docs"])
    documents = reader.load_data()

    sentence_parser = SentenceWindowNodeParser.from_defaults(
        window_size=6,  # Number of sentences in each window
        window_metadata_key="window",  # Metadata key for window information
        original_text_metadata_key="original_text"  # Metadata key for original text
    )

    sentence_nodes = sentence_parser.get_nodes_from_documents(documents)
    logging.info("index creating with `%d` documents", len(documents))

    if persist:
        chroma_client = chromadb.PersistentClient(path=f"{directory}/index")
    else:
        chroma_client = chromadb.EphemeralClient()
    collection_name = f"{directory.split('/')[-1]}_collection"
    chroma_collection = chroma_client.get_or_create_collection(collection_name)

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, embed_model=embed_model)
    index = VectorStoreIndex(
        sentence_nodes,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=False
    )

    if persist:
        index.storage_context.persist(persist_dir=f"{directory}/index/index")

    return index


def load_index(embed_model, directory="./docs", persist=False):
    try:
        chroma_client = chromadb.PersistentClient(path=f"{directory}/index")

        collection_name = f"{directory.split('/')[-1]}_collection"
        chroma_collection = chroma_client.get_or_create_collection(collection_name)

        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store,
                                                       persist_dir=f"{directory}/index/index")

        # Now you can load the index
        return VectorStoreIndex([], storage_context=storage_context)
    except Exception as e:
        logging.error("Error loading index - %s", e)
        return init_index(embed_model, directory, persist)


def get_index(embed_model, directory, force_recreate=False, persist=False):
    if force_recreate or not os.path.exists(f"{directory}/index"):
        if os.path.exists(f"{directory}/index"):
            # remove all the files and directories except the files with .txt, .pdf extension
            shutil.rmtree(f"{directory}/index")
        os.makedirs(f"{directory}/index", exist_ok=True)
        return init_index(embed_model, directory, persist)

    return load_index(embed_model, directory, persist)


def create_formal_sentence(knowledge_graph):
    global query_engine, llm

    response = llm.complete(FORMAL_SENTENCE_TEMPLATE(knowledge_graph))
    try:
        # parse the response to get the context and query string
        formated_text = json_repair.loads(response.text)
        if 'output' in formated_text:
            return formated_text['output']
        return None
    except Exception as e:
        logging.error("Error creating sample queries - %s", e)
        return None


def create_sample_queries(knowledge_graph):
    global query_engine, llm
    identifier = knowledge_graph[0]

    # check if the directory exists, don't recreate the sample queries
    if os.path.exists(f"./docs/{identifier}/questions.json"):
        print(f"Sample queries already exist for {identifier}")
        return

    response = llm.complete(QUESTION_GENERATION_TEMPLATE(knowledge_graph[1]))

    try:
        # parse the response to get the context and query string
        questions = json_repair.loads(response.text)

        os.makedirs(f"./docs/{identifier}", exist_ok=True)

        # create a questions.json file with the knowledge graph
        with open(f"./docs/{identifier}/questions.json", 'w') as f:
            json.dump(questions, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error("Error creating sample queries - %s", e)


def few_shot_examples_fn(**kwargs):
    queries = [
        "Pat Frank author Alas, Babylon",
        "Jonathan Swift deathPlace New York City",
        "Camilo José Cela award Nobel Prize in Literature",
    ]
    responses = [
        {"output": "yes"},
        {"output": "no"},
        {"output": "yes"},
    ]
    result_strs = []
    for query, response_dict in zip(queries, responses):
        result_str = f"""\
Query: {query}
Response: {response_dict}"""
        result_strs.append(result_str)
    return "\n\n".join(result_strs)


def init_query_engine(index, query):
    global query_engine

    qa_template = PromptTemplate(RAG_TEMPLATE, function_mappings={"few_shot_examples": few_shot_examples_fn})

    # build query engine with custom template
    # text_qa_template specifies custom template
    # similarity_top_k configure the retriever to return the top 3 most similar documents,
    query_engine = index.as_query_engine(
        similarity_top_k=3,
        text_qa_template=qa_template,
        node_postprocessors=[
            DummyNodePostprocessor(knowledge_graph=query, similarity_cutoff=0.4),
            MetadataReplacementPostProcessor(target_metadata_key="window"),
        ]
    )

    return query_engine


def clear_response(response):
    """
    Simplify the response to determine if it contains 'yes', 'no', or neither.
    Returns:
    - 1 for 'yes'
    - 0 for 'no'
    - -1 for 'unknown' (if both 'yes' and 'no' are present or neither is present)
    """

    # Convert to lower case to handle case insensitivity
    response = response.lower()

    # Use regular expressions to find 'yes' and 'no' as whole words
    has_yes = re.search(r'\byes\b', response)
    has_no = re.search(r'\bno\b', response)

    # Determine the result based on the presence of 'yes' and 'no'
    if has_yes and has_no:
        return -1  # Both 'yes' and 'no' are present
    elif has_yes:
        return 1  # Only 'yes' is present
    elif has_no:
        return 0  # Only 'no' is present

    return -1  # Neither 'yes' nor 'no' is present


def chat(input_question, n_retries=3):
    global query_engine

    if n_retries == 0:
        return -1

    try:
        response = query_engine.query(input_question)
        logging.info("got response from llm - %s", response)
        return clear_response(response.response)
    except Exception as e:
        logging.error("Error querying llm - %s", e)
        return chat(input_question, n_retries - 1)


def chat_cmd():
    global query_engine

    while True:
        input_question = input("Enter your question (or 'exit' to quit): ")
        if input_question.lower() == 'exit':
            break

        response = query_engine.query(input_question)
        logging.info("got response from llm - %s", response)


if __name__ == '__main__':
    init_llm()
    index = get_index(Settings.embed_model, directory="./docs", force_recreate=False, persist=True)
    init_query_engine(index)
    chat_cmd()
