import os
import json
# import random
from crawler import crawler, get_article_from_query

from data_loader import load_dataset


config = {
    "recreate_index": False,
    "create_sample_queries": False,
    "add_score": False,
    "fetch_documents": True,
    "get_urls": False
}

if __name__ == '__main__':
    # init_llm(response_schema=True)
    # kg, gt = load_dataset(dataset_name="DBpedia", dataset_file="kg_modified.json")
    # data = []
    # for knowledge_graph in kg:
    #     if knowledge_graph[0].startswith('correct'):
    #         if 'death' in knowledge_graph[0].split("_"):
    #             data.append(knowledge_graph)
    # print(len(data))
    #
    # for knowledge_graph in data:
    #     identifier = knowledge_graph[0]
    #     if identifier.startswith('wrong'):
    #         search_engine(knowledge_graph, force_recreate=True)

    # get_results(data, 'results/FactBenchjson', recreate_index=True)
    #
    if config["fetch_documents"]:
        queries = []
        kg, gt = load_dataset(dataset_name="DBpedia", dataset_file="kg_modified.json")
        data = []
        for existing in os.listdir("./docs"):
            if existing.startswith("dbpedia"):
                identifier = existing.split("_")[1]
                data.append(kg[int(identifier)])
        print(len(data), len(kg), data[:1], kg[:1])

        for knowledge_graph in data:
            identifier = knowledge_graph[0]
            with open(f"./docs/dbpedia_{identifier}/questions.json", "r") as f:
                questions = json.load(f)['questions']
            # get top 3 questions based on score field
            questions = sorted(questions, key=lambda x: x['score'], reverse=True)[:3]
            questions = [{
                "id": f"dbpedia_{identifier}_{q_id + 1}", "text": q['question']} for q_id, q in enumerate(questions)
            ]
            questions.append({"id": f"dbpedia_{identifier}_0", "text": knowledge_graph[1]})
            queries.extend(questions)
            # print(queries)
        # get the documents for the queries
        crawler(queries)
    #
    # if config["get_urls"]:
    #     for knowledge_graph in kg:
    #         get_article_from_query(knowledge_graph)
    #
    # if config["create_sample_queries"]:
    #     # this code doesn't work if the directory already exists and the sample queries are already created
    #     # for recreation of sample queries, delete the directory
    #     from model import *
    #     from concurrent.futures import ThreadPoolExecutor, as_completed
    #
    #     init_llm(response_schema=True)
    #     kg, gt = load_dataset(dataset_name="DBpedia", dataset_file="kg_modified.json")
    #     print(kg[:1])
    #     steps = 5
    #     for i in range(0, len(kg), steps):
    #         inputs = kg[i:i + steps]
    #         with ThreadPoolExecutor(max_workers=steps) as executor:
    #             # Submit tasks to the executor
    #             future_to_input = {executor.submit(create_sample_queries, (f"dbpedia_{i[0]}", i[1])): i for i in inputs}
    #             # Collect results as they become available
    #             results = {}
    #             for future in as_completed(future_to_input):
    #                 input_value = future_to_input[future]
    #                 try:
    #                     result = future.result()
    #                     results[input_value[0]] = result
    #                 except Exception as e:
    #                     print(f'Generated an exception: {e}')
    #
    #             append_json("DBpedia_question_generation_time_2.json", results)

    # if config["add_score"]:
    #     kg, gt = load_dataset(dataset_name="DBpedia", dataset_file="kg_modified.json")
    #     for knowledge_graph in kg:
    #         identifier = knowledge_graph[0]
    #         try:
    #             with open(f"./docs/dbpedia_{identifier}/questions.json", "r") as f:
    #                 questions = json.loads(f.read())['questions']
    #         except FileNotFoundError:
    #             continue
    #         try:
    #             if questions[0].get('score', None) is not None:
    #                 if questions[0]['score'] < 0.5 or len(questions) < 3:
    #                     print(f"Deleting {identifier}")
    #                     shutil.rmtree(f"./docs/dbpedia_{identifier}")
    #                 continue
    #             print(f"Re-ranking questions for {identifier}")
    #             questions = re_ranker(knowledge_graph[1], [doc['question'] for doc in questions])
    #             with open(f"./docs/dbpedia_{identifier}/questions.json", "w") as f:
    #                 json.dump({"questions": questions}, f, indent=4, ensure_ascii=False)
    #         except FileExistsError | FileNotFoundError as e:
    #             print(e)
    #             continue
    #         except Exception as e:
    #             print(f"Error re-ranking questions for {identifier}")
    #             # shutil.rmtree(f"./docs/{identifier}")
    #             continue

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
