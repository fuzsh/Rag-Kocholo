"""
This script is used to preprocess the dataset and generate formal sentences for the KG triples.
Here we try to generate formal sentences for the KG triples in parallel using ThreadPoolExecutor.
This way we can have human-like sentences for the KG triples for further processing and fact-checking.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed

from data_loader import load_dataset
from model import *
from utils.append_json import append_json, get_file_data

init_llm()


def remove_duplicates(kg, output_path):
    data = get_file_data(output_path)
    for key in data:
        for knowledge_graph in kg:
            if knowledge_graph[0] == key:
                kg.remove(knowledge_graph)
    return kg


dataset_name = "DBpedia"
output_path = f'{dataset_name}_modified.json'

kg, gt = load_dataset(dataset_name=dataset_name)
remove_duplicates(kg, output_path)

print("Length of remaining KG: ", len(kg))

steps = 5
for i in range(0, len(kg), steps):
    inputs = kg[i:i + steps]
    with ThreadPoolExecutor(max_workers=steps) as executor:
        # Submit tasks to the executor
        future_to_input = {executor.submit(create_formal_sentence, i): i for i in inputs}

        # Collect results as they become available
        results = {}
        for future in as_completed(future_to_input):
            input_value = future_to_input[future]
            try:
                result = future.result()
                results[input_value[0]] = result
            except Exception as e:
                print(f'Generated an exception: {e}')

    append_json(output_path, results)
