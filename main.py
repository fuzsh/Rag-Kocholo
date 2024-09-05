import json
import os

# import random
from crawler import crawler, get_article_from_query
from data_loader import load_dataset

config = {
    "recreate_index": False,
    "create_sample_queries": False,
    "add_score": False,
    "fetch_documents": False,
    "get_urls": True
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
        dataset_name = "YAGO"
        kg, gt = load_dataset(dataset_name=dataset_name, dataset_file="kg_modified.json")
        data = []
        for existing in os.listdir("./docs"):
            if existing.startswith(dataset_name.lower()):
                for knowledge_graph in kg:
                    if knowledge_graph[0] == existing.split("_")[1]:
                        data.append(knowledge_graph)
                        break

        print(len(data), len(kg), data[:1], kg[:1])

        for knowledge_graph in data:
            identifier = knowledge_graph[0]
            with open(f"./docs/{dataset_name.lower()}_{identifier}/questions.json", "r") as f:
                questions = json.load(f)['questions']
            # get top 3 questions based on score field
            questions = sorted(questions, key=lambda x: x['score'], reverse=True)[:3]
            questions = [{
                "id": f"{dataset_name.lower()}_{identifier}_{q_id + 1}", "text": q['question']} for q_id, q in
                enumerate(questions)
            ]
            questions.append({"id": f"{dataset_name.lower()}_{identifier}_0", "text": knowledge_graph[1]})
            queries.extend(questions)
            # print(queries)
        # get the documents for the queries
        crawler(queries)

    if config["get_urls"]:
        dataset_name = "DBpedia"
        kg, gt = load_dataset(dataset_name=dataset_name, dataset_file="kg_modified.json")

        # fix identifiers
        kg = [(f"{dataset_name.lower()}_{i[0]}", i[1]) for i in kg]

        for knowledge_graph in kg:
            if knowledge_graph[0] in ['dbpedia_7961', 'wrong_mix_domainrange_subsidiary_00137', 'dbpedia_7506',
                                      'wrong_mix_property_subsidiary_00108', 'dbpedia_2625', 'dbpedia_1868',
                                      'dbpedia_3538', 'correct_foundationPlace_00005', 'dbpedia_9069', 'dbpedia_2678',
                                      'dbpedia_9264', 'dbpedia_3108', 'dbpedia_5202', 'dbpedia_2215',
                                      'wrong_mix_property_spouse_00005', 'dbpedia_1038', 'dbpedia_9067', 'dbpedia_2649',
                                      'dbpedia_2840', 'wrong_mix_random_starring_00070',
                                      'wrong_mix_range_foundationPlace_00104', 'dbpedia_7509',
                                      'wrong_mix_range_subsidiary_00055', 'wrong_mix_domain_foundationPlace_00044',
                                      'dbpedia_2623', 'dbpedia_7137', 'dbpedia_3107', 'dbpedia_4574',
                                      'wrong_mix_domainrange_foundationPlace_00130', 'wrong_mix_random_leader_00036',
                                      'dbpedia_5203', 'dbpedia_6029', 'correct_foundationPlace_00061', 'dbpedia_2679',
                                      'dbpedia_6488', 'wrong_mix_domain_publicationDate_00009', 'dbpedia_4868',
                                      'dbpedia_5982', 'correct_starring_00140', 'dbpedia_3612', 'dbpedia_589',
                                      'dbpedia_8451', 'dbpedia_3240', 'dbpedia_587', 'dbpedia_741', 'dbpedia_1346',
                                      'wrong_mix_domainrange_foundationPlace_00016', 'dbpedia_2100', 'dbpedia_5128',
                                      'dbpedia_2304', 'dbpedia_6562', 'dbpedia_172', 'dbpedia_2935', 'dbpedia_8433',
                                      'dbpedia_3487', 'wrong_mix_random_subsidiary_00053', 'dbpedia_127',
                                      'dbpedia_6395', 'dbpedia_4856', 'dbpedia_4293', 'dbpedia_6366', 'dbpedia_2759',
                                      'dbpedia_8899', 'dbpedia_4668', 'dbpedia_8297', 'dbpedia_4234', 'dbpedia_6563',
                                      'correct_subsidiary_00080', 'dbpedia_173', 'wrong_mix_range_spouse_00074',
                                      'dbpedia_2101', 'dbpedia_2902', 'dbpedia_7469',
                                      'wrong_mix_domain_foundationPlace_00115', 'dbpedia_709', 'dbpedia_6114',
                                      'dbpedia_167', 'dbpedia_7238', 'dbpedia_8080', 'wrong_mix_random_award_00053',
                                      'dbpedia_156', 'wrong_mix_range_spouse_00058', 'dbpedia_48',
                                      'wrong_mix_range_starring_00048', 'dbpedia_6921', 'dbpedia_592', 'dbpedia_6727',
                                      'dbpedia_2717', 'dbpedia_1991', 'wrong_mix_random_subsidiary_00085',
                                      'dbpedia_1739', 'dbpedia_9', 'dbpedia_533', 'dbpedia_3809', 'dbpedia_706',
                                      'wrong_mix_range_spouse_00095', 'dbpedia_166', 'dbpedia_2122',
                                      'wrong_mix_property_foundationPlace_00131', 'dbpedia_159', 'dbpedia_8276',
                                      'wrong_mix_domain_spouse_00135', 'dbpedia_708', 'dbpedia_2727', 'dbpedia_9304',
                                      'dbpedia_3606', 'dbpedia_2716', 'dbpedia_25', 'dbpedia_4872', 'dbpedia_7435',
                                      'wrong_mix_range_foundationPlace_00007', 'dbpedia_6466',
                                      'wrong_mix_domainrange_foundationPlace_00115', 'dbpedia_2652', 'dbpedia_2800',
                                      'dbpedia_423', 'wrong_mix_domain_foundationPlace_00032',
                                      'wrong_mix_range_subsidiary_00084', 'wrong_mix_domain_starring_00099',
                                      'dbpedia_7146', 'wrong_mix_random_starring_00055', 'dbpedia_1280',
                                      'wrong_mix_range_subsidiary_00046', 'dbpedia_422', 'dbpedia_5485',
                                      'wrong_mix_domainrange_foundationPlace_00114', 'dbpedia_2665', 'dbpedia_3327',
                                      'dbpedia_1642', 'dbpedia_4798', 'dbpedia_1275', 'dbpedia_6050', 'dbpedia_2299',
                                      'dbpedia_8333', 'dbpedia_2067', 'dbpedia_6433', 'wrong_mix_domain_spouse_00048',
                                      'wrong_mix_range_subsidiary_00082', 'dbpedia_8130',
                                      'wrong_mix_range_subsidiary_00049', 'wrong_mix_domain_subsidiary_00090',
                                      'dbpedia_3762', 'dbpedia_600', 'dbpedia_5230', 'dbpedia_4387', 'dbpedia_5403',
                                      'dbpedia_2626', 'dbpedia_3364', 'dbpedia_2077', 'dbpedia_6288',
                                      'wrong_mix_property_spouse_00090', 'dbpedia_3709', 'dbpedia_5051', 'dbpedia_3160',
                                      'dbpedia_2687', 'dbpedia_2680', 'dbpedia_8143', 'dbpedia_2014',
                                      'wrong_mix_domain_subsidiary_00019', 'correct_foundationPlace_00053',
                                      'dbpedia_8985', 'dbpedia_854', 'dbpedia_2013', 'dbpedia_6820',
                                      'wrong_mix_property_publicationDate_00109', 'dbpedia_1897',
                                      'wrong_mix_domainrange_subsidiary_00104', 'dbpedia_3150',
                                      'wrong_mix_domain_spouse_00066', 'dbpedia_5326', 'correct_subsidiary_00040',
                                      'wrong_mix_domainrange_foundationPlace_00012',
                                      'wrong_mix_domain_subsidiary_00109', 'dbpedia_5113', 'correct_subsidiary_00049',
                                      'wrong_mix_random_award_00018', 'dbpedia_1710', 'dbpedia_3629',
                                      'wrong_mix_random_subsidiary_00094', 'dbpedia_8031', 'dbpedia_8455',
                                      'dbpedia_4865', 'dbpedia_5988', 'dbpedia_6938', 'dbpedia_987', 'dbpedia_1577',
                                      'dbpedia_719', 'wrong_mix_range_spouse_00041', 'dbpedia_170', 'dbpedia_4459',
                                      'wrong_mix_domainrange_publicationDate_00149',
                                      'wrong_mix_domain_subsidiary_00137', 'correct_subsidiary_00041', 'dbpedia_2102',
                                      'dbpedia_4058', 'dbpedia_8453', 'dbpedia_4890', 'dbpedia_744', 'dbpedia_1343',
                                      'dbpedia_8454', 'dbpedia_3413', 'dbpedia_1386', 'dbpedia_6953', 'dbpedia_927',
                                      'dbpedia_2519', 'dbpedia_7850', 'dbpedia_3860', 'correct_subsidiary_00039',
                                      'dbpedia_4877', 'dbpedia_3856', 'dbpedia_8482', 'dbpedia_1537',
                                      'wrong_mix_domainrange_death_00043', 'wrong_mix_random_death_00061',
                                      'wrong_mix_property_subsidiary_00090', 'dbpedia_9160', 'dbpedia_6573',
                                      'dbpedia_1100', 'wrong_mix_domainrange_subsidiary_00099', 'dbpedia_6922',
                                      'dbpedia_5750', 'wrong_mix_domainrange_subsidiary_00055', 'dbpedia_7464',
                                      'dbpedia_3295', 'dbpedia_2723', 'dbpedia_3605', 'dbpedia_1152', 'dbpedia_10',
                                      'dbpedia_3053', 'dbpedia_3054', 'dbpedia_2724', 'dbpedia_8483', 'dbpedia_21',
                                      'dbpedia_2520', 'dbpedia_7851', 'dbpedia_2940', 'dbpedia_1993',
                                      'wrong_mix_random_subsidiary_00011', 'wrong_mix_domain_subsidiary_00122',
                                      'dbpedia_6923', 'dbpedia_4648', 'dbpedia_4213', 'dbpedia_9161', 'dbpedia_1101',
                                      'dbpedia_4196', 'wrong_mix_range_subsidiary_00080', 'dbpedia_2098',
                                      'dbpedia_3985', 'dbpedia_7519', 'dbpedia_1277', 'dbpedia_1419',
                                      'wrong_mix_random_spouse_00005', 'dbpedia_7588',
                                      'wrong_mix_range_subsidiary_00029', 'dbpedia_6491', 'dbpedia_9071',
                                      'wrong_mix_domain_leader_00002', 'dbpedia_3922', 'dbpedia_6498', 'dbpedia_6037',
                                      'dbpedia_2651', 'dbpedia_2256', 'wrong_mix_domain_starring_00092',
                                      'wrong_mix_domain_publicationDate_00130', 'dbpedia_8102',
                                      'wrong_mix_domain_spouse_00045', 'dbpedia_9220', 'dbpedia_1882',
                                      'wrong_mix_range_foundationPlace_00112', 'dbpedia_2099', 'dbpedia_270',
                                      'dbpedia_3923', 'dbpedia_3782', 'dbpedia_5647',
                                      'wrong_mix_range_subsidiary_00019', 'wrong_mix_domain_foundationPlace_00030',
                                      'dbpedia_3771', 'dbpedia_7587', 'dbpedia_9070', 'dbpedia_3111', 'dbpedia_8535',
                                      'dbpedia_7589', 'dbpedia_6490']:
                get_article_from_query(knowledge_graph)
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
