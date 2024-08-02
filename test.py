# from data_loader import load_dataset
# from model import *
# from concurrent.futures import ThreadPoolExecutor, as_completed
#
# init_llm()
# kg, gt = load_dataset(dataset_name="DBpedia", dataset_file="kg_modified.json")
#
# steps = 10
# for i in range(0, len(kg), steps):
#     inputs = kg[i:i + steps]
#     with ThreadPoolExecutor(max_workers=steps) as executor:
#         # Submit tasks to the executor
#         future_to_input = {executor.submit(create_sample_queries, (f"dbpedia_{i[0]}", i[1])): i for i in inputs}
import json

with open('results/FactBench.json', 'r') as f:
    data = json.load(f)

new_obj = {}
for key, value in data.items():
    if value["full_ans"] != "Empty Response":
        new_obj[key] = value


with open('results/FactBench_modified.json', 'w') as f:
    json.dump(new_obj, f, indent=4)
