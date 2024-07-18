import json

from crawler import crawler, get_article_from_query
# from model import *
from data_loader import load_dataset
# from re_ranker import re_ranker

config = {
    "recreate_index": False,
    "create_sample_queries": False,
    "add_score": False,
    "fetch_documents": False,
    "get_urls": True
}

if __name__ == '__main__':
    # init_llm()
    kg, gt = load_dataset(dataset_name="FactBench")

    if config["fetch_documents"]:
        queries = []
        for knowledge_graph in kg:
            identifier = knowledge_graph[0]
            with open(f"./docs/{identifier}/questions.json", "r") as f:
                questions = json.load(f)['questions']
            # get top 3 questions based on score field
            questions = sorted(questions, key=lambda x: x['score'], reverse=True)[:3]
            questions = [{"id": f"{identifier}_{q_id + 1}", "text": q['question']} for q_id, q in enumerate(questions)]
            questions.append({"id": f"{identifier}_0", "text": ' '.join(knowledge_graph[1])})
            queries.extend(questions)
            # print(queries)
        # get the documents for the queries
        crawler(queries)

    if config["get_urls"]:
        for knowledge_graph in kg:
            get_article_from_query(knowledge_graph)

    if config["create_sample_queries"]:
        for knowledge_graph in kg:
            # this code doesn't work if the directory already exists and the sample queries are already created
            # for recreation of sample queries, delete the directory
            create_sample_queries(knowledge_graph)

    if config["add_score"]:
        for knowledge_graph in kg:
            identifier = knowledge_graph[0]
            try:
                with open(f"./docs/{identifier}/questions.json", "r") as f:
                    questions = json.loads(f.read())['questions']
                if questions[0].get('score', None) is not None:
                    if questions[0]['score'] < 0.5:
                        print(f"Deleting {identifier}")
                        # shutil.rmtree(f"./docs/{identifier}")
                    continue
                print(f"Re-ranking questions for {identifier}")
                questions = re_ranker(' '.join(knowledge_graph[1]), [doc['question'] for doc in questions])
                with open(f"./docs/{identifier}/questions.json", "w") as f:
                    json.dump({"questions": questions}, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"Error re-ranking questions for {identifier}")
                shutil.rmtree(f"./docs/{identifier}")
                continue

    # # Factuality check of the knowledge graph with RAG
    # responses = []
    # for knowledge_graph in kg:
    #     identifier = knowledge_graph[0]
    #     # initialize the index
    #
    #     index = get_index(Settings.embed_model, directory=f"./docs/{identifier}", force_recreate=config["recreate_index"])
    #     # initialize the query engine
    #     init_query_engine(index)
    #     # chat
    #     response = chat(" ".join(knowledge_graph[1]))
    #     responses.append((identifier, response))
    #
    # # check the responses with the ground truth
    # correct = 0
    # incorrect = 0
    # bullshit = 0
    # for response in responses:
    #     identifier = response[0]
    #     response = response[1]
    #     expected_response = gt[identifier]
    #
    #     # print(f"Identifier: {identifier}")
    #     # print(f"Expected Response: {expected_response}")
    #     # print(f"Actual Response: {response}")
    #     # print(f"Correct: {response == expected_response}")
    #     # print("\n")
    #
    #     # create some statistics report, confusion matrix, count of correct and incorrect responses and accuracy
    #     if response == expected_response:
    #         correct += 1
    #     elif response == -1:
    #         bullshit += 1
    #     else:
    #         incorrect += 1
    #
    # print(incorrect, correct, bullshit)
