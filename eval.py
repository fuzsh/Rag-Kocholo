import random
from collections import defaultdict

from llama_index.core.evaluation.guideline import DEFAULT_GUIDELINES

from data_loader import load_dataset
from model import *

from utils.append_json import append_json, get_file_data


def remove_duplicates(kg, output_path):
    data = get_file_data(output_path)
    for key in data:
        for knowledge_graph in kg:
            if knowledge_graph[0] == key:
                kg.remove(knowledge_graph)
    return kg


def get_results(kg, output_path, recreate_index=False):
    # remove the existing results
    remove_duplicates(kg, output_path)
    for knowledge_graph in kg:
        try:
            result = get_result(knowledge_graph, recreate_index)
            append_json(output_path, {knowledge_graph[0]: result})
        except Exception as e:
            print(f"Error in {knowledge_graph[0]}: {e}")
            continue


def get_result(knowledge_graph, recreate_index=False):
    identifier = knowledge_graph[0]
    query = re.sub(r'(?<=[a-z])([A-Z])', r' \1', " ".join(knowledge_graph[1]))

    if identifier.startswith('correct_death'):
        query = f'Did {knowledge_graph[1][0]} died in "{knowledge_graph[1][2]}"?'
    elif identifier.startswith('correct_foundationPlace'):
        query = f'Is "{knowledge_graph[1][0]}" located or founded in "{knowledge_graph[1][2]}"?'
    elif identifier.startswith('correct_nbateam'):
        query = f'Did {knowledge_graph[1][0]} play for the NBA team "{knowledge_graph[1][2]}"?'

    # initialize the index
    index = get_index(Settings.embed_model, directory=f"./docs/{identifier}", force_recreate=recreate_index)
    # initialize the query engine
    init_query_engine(index, query)

    # Add space when there is a capital letter
    return chat(query)


def analyze_results(results_path, gt, output_file='results/analysis.md'):
    with open(results_path, "r") as f:
        results = json.load(f)

    results = {k: v['short_ans'] for k, v in results.items()}

    overall_metrics = {
        'correct': 0,
        'incorrect': 0,
        'without_response': 0,
        'not_found': 0
    }

    category_metrics = defaultdict(lambda: {
        'correct': 0,
        'incorrect': 0,
        'without_response': 0,
    })

    for identifier, response in gt.items():
        expected_response = response
        response = results.get(identifier, None)

        category = identifier.split('_')
        category = '_'.join(category[1:len(category) - 1])

        if response is None:
            continue

        if response == expected_response:
            overall_metrics['correct'] += 1
            category_metrics[category]['correct'] += 1
        elif response == -1:
            overall_metrics['without_response'] += 1
            category_metrics[category]['without_response'] += 1
        else:
            overall_metrics['incorrect'] += 1
            category_metrics[category]['incorrect'] += 1

    def calculate_metrics(metrics):
        correct = metrics['correct']
        incorrect = metrics['incorrect']
        without_response = metrics['without_response']

        total_responses = correct + incorrect + without_response

        overall_accuracy = correct / total_responses if total_responses > 0 else 0
        # precision = correct / (correct + incorrect) if (correct + incorrect) > 0 else 0
        # recall = correct / (correct + not_found) if (correct + not_found) > 0 else 0
        # f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        # specificity = incorrect / (incorrect + without_response + not_found) if (
        #                                                                                     incorrect + without_response + not_found) > 0 else 0

        return {
            'overall_accuracy': overall_accuracy,
            # 'precision': precision,
            # 'recall': recall,
            # 'f1_score': f1_score,
            # 'specificity': specificity
        }

    overall_results = calculate_metrics(overall_metrics)

    with open(output_file, 'w') as file:
        file.write("# Analysis Results\n\n")
        file.write("## Metrics\n\n")
        file.write("| Category | Correct | Incorrect | Not understandable | Overall Accuracy |\n")
        file.write("| --- | --- | --- | --- | --- |\n")

        # file.write("\n## Metrics by Category\n\n")
        # file.write("| Category | Correct | Incorrect | Not understandable | Overall Accuracy |\n")
        # file.write("| --- | --- | --- | --- | --- | --- |\n")
        for category, metrics in category_metrics.items():
            category_results = calculate_metrics(metrics)
            file.write(f"| {category} | {metrics['correct']} | {metrics['incorrect']} | {metrics['without_response']} | {category_results['overall_accuracy']:.4f} |\n")

        file.write(f"| **Overall** | {overall_metrics['correct']} | {overall_metrics['incorrect']} | {overall_metrics['without_response']} | {overall_results['overall_accuracy']:.4f} |\n")


if __name__ == "__main__":
    # init_llm(response_schema=True)

    dataset = 'FactBench'
    result_file_path = 'results/FactBench_modified.json'

    # # remove the existing results
    # with open(result_file_path, "w") as f:
    #     json.dump({}, f)

    # load the dataset and shuffle it
    kg, gt = load_dataset('FactBench')
    # random.shuffle(kg)
    #
    # # Step 1: Get the results
    # get_results(kg[:10], result_file_path, recreate_index=True)

    # Step 2: Analyze the results
    analyze_results(result_file_path, gt)
