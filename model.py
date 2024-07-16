import os
import sys
import json
import shutil
import logging
import chromadb
import json_repair

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import (Settings, VectorStoreIndex, SimpleDirectoryReader, PromptTemplate)
from llama_index.core import StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

global query_engine, llm
query_engine = None
llm = None


def init_llm():
    global llm

    llm = Ollama(model="llama3", request_timeout=300.0)
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    Settings.llm = llm
    Settings.embed_model = embed_model

def init_index(embed_model, directory="./docs", persist=False):
    reader = SimpleDirectoryReader(input_dir=directory, recursive=True, exclude=["questions.json", "index"])
    documents = reader.load_data()

    logging.info("index creating with `%d` documents", len(documents))

    if persist:
        chroma_client = chromadb.PersistentClient(path=f"{directory}/index")
    else:
        chroma_client = chromadb.EphemeralClient()
    collection_name = f"{directory.split('/')[-1]}_collection"
    chroma_collection = chroma_client.get_or_create_collection(collection_name)

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # use this to set custom chunk size and splitting
    # https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/

    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, embed_model=embed_model)

    if persist:
        index.storage_context.persist(persist_dir=f"{directory}/index/index")

    return index


def load_index(embed_model, directory="./docs", persist=False):
    try:
        chroma_client = chromadb.PersistentClient(path=f"{directory}/index")

        collection_name = f"{directory.split('/')[-1]}_collection"
        chroma_collection = chroma_client.get_or_create_collection(collection_name)

        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store, persist_dir=f"{directory}/index/index")

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


def create_sample_queries(knowledge_graph):
    global query_engine, llm
    identifier = knowledge_graph[0]

    # check if the directory exists, don't recreate the sample queries
    if os.path.exists(f"./docs/{identifier}/questions.json"):
        print(f"Sample queries already exist for {identifier}")
        return

    response = llm.complete("You are an intelligent system with access to a vast amount of information."
                            "I will provide you with a knowledge graph in the form of triples (subject, predicate, object)."
                            "Your task is to generate ten questions based on the knowledge graph. The questions should assess understanding and insight into the information presented in the graph. "
                            "Provide the output in JSON format, with each question having a unique identifier.\n"
                            "Instructions:\n"
                            "1. Analyze the provided knowledge graph.\n"
                            "2. Generate ten questions that are relevant to the information in the knowledge graph.\n"
                            "3. Provide the questions in JSON format, each with a unique identifier.\n\n"
                            "Input Knowledge Graph: Albert Einstein bornIn Ulm\n"
                            "Expected Response:\n"
                            """{
                            "questions": [
                            {"id": 1, "question": "Where was Albert Einstein born?"},
                            {"id": 2, "question": "What is Albert Einstein known for?"},
                            {"id": 3, "question": "In what year was the Theory of Relativity published?"},
                            {"id": 4, "question": "Where did Albert Einstein work?"},
                            {"id": 5, "question": "What prestigious award did Albert Einstein win?"},
                            {"id": 6, "question": "Which theory is associated with Albert Einstein?"},
                            {"id": 7, "question": "Which university did Albert Einstein work at?"},
                            {"id": 8, "question": "What did Albert Einstein receive the Nobel Prize in?"},
                            {"id": 9, "question": "In what field did Albert Einstein win a Nobel Prize?"},
                            {"id": 10, "question": "Name the city where Albert Einstein was born."}
                        ]}"""
                            f"Considering the above information, please respond to this Knowledge Graph: {' '.join(knowledge_graph[1])}\n"
                            f"The output should be in JSON format with each question having a unique identifier and question doesn't contain term knowledge graph, without any additional information \n"
                            )

    try:
        # parse the response to get the context and query string
        questions = json_repair.loads(response.text)

        os.makedirs(f"./docs/{identifier}", exist_ok=True)

        # create a questions.json file with the knowledge graph
        with open(f"./docs/{identifier}/questions.json", 'w') as f:
            json.dump(questions, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error("Error creating sample queries - %s", e)


def init_query_engine(index):
    global query_engine

    # custom prompt template
    template = (
        "Instructions:\n"
        "Input Documents: A collection of documents related to the subject will be provided.\n"
        "Triple Knowledge: A triple in the format ('Subject', 'Predicate', 'Object') will be given.\n"
        "Evaluation Task: Your task is to evaluate whether the information in the documents supports the triple. Your response should be \"yes\" if the triple is correct according to the documents, or \"no\" if the triple is incorrect\n\n"
        "Example:\n"
        "Documents:\n"
        "Document 1: \"Benjamin Franklin was one of the Founding Fathers of the United States. He was a renowned polymath who contributed significantly to the fields of science, politics, and diplomacy.\"\n"
        "Document 2: \"Franklin spent much of his life in Philadelphia, where he engaged in various civic projects and founded institutions such as the University of Pennsylvania.\"\n"
        "Triple: ('Benjamin Franklin', 'spouse', 'Philadelphia')\n"
        "Expected Response: \"no\"\n\n"
        "Here is some context related to the Input Documents:\n"
        "-----------------------------------------\n"
        "{context_str}\n"
        "-----------------------------------------\n"
        "Considering the above information, please respond to Input:\n"
        "Triple Knowledge question: {query_str}\n"
        "Answer succinctly, just with \"yes\" or \"no\", without any additional information.\n"
    )
    qa_template = PromptTemplate(template)

    # build query engine with custom template
    # text_qa_template specifies custom template
    # similarity_top_k configure the retriever to return the top 3 most similar documents,
    # the default value of similarity_top_k is 2
    query_engine = index.as_query_engine(text_qa_template=qa_template, similarity_top_k=3)

    return query_engine


def clear_response(response):
    # remove extra text from response and just return the yes or no
    # check which one exists in the response, if both exist, return unknown
    response = response.lower()
    if ('yes' in response and 'no' in response) or ('no' not in response and 'yes' not in response):
        return -1
    elif 'yes' in response:
        return 1
    return 0


def chat(input_question):
    global query_engine

    response = query_engine.query(input_question)
    logging.info("got response from llm - %s", response)

    return clear_response(response.response)


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
