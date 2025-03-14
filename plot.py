import json
import os
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

from data_loader import load_dataset

LLM_MODELS = ["Gemma2", "Llama3_1", "Mistral", "Qwen2"]


def load_and_process_data(models, gt):
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for model in models:
        file_path = os.path.join(f"results/{model}", "FactBench_modified.json")
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            for key, value in json_data.items():
                category = key.split('_')[1] if 'wrong_mix_' not in key else \
                    key.replace("wrong_mix_", "").split("_", 2)[1]
                result_type = 'wrong' if 'wrong_mix_' in key else 'correct'
                is_correct = int(value['short_ans'] == gt[key])
                data[model][result_type][category].append(is_correct)
    return data


def prepare_data(data):
    processed_data = defaultdict(lambda: defaultdict(list))

    for model, types in data.items():
        for result_type, categories in types.items():
            for category, results in categories.items():
                count_true = sum(results)
                count_false = len(results) - count_true
                processed_data[result_type][category].append((model, count_true, count_false))
                processed_data['combined'][category].append((model, count_true, count_false))

    return processed_data


def merge_and_sum(data):
    merged_data = defaultdict(list)

    for category, results in data.items():
        category_totals = defaultdict(lambda: [0, 0])

        for model, count_true, count_false in results:
            category_totals[model][0] += count_true
            category_totals[model][1] += count_false

        merged_data[category] = [(model, *counts) for model, counts in category_totals.items()]

    return merged_data


def plot_data(data, title, file_name, output_dir="results",):
    accuracies = defaultdict(list)
    data = defaultdict(list, sorted(data.items()))

    for category, values in data.items():
        for model_name, correct, wrong in values:
            accuracy = correct / (correct + wrong)
            accuracies[category].append((model_name, accuracy))

    categories = list(accuracies.keys())
    models = [model for model, _ in accuracies[categories[0]]]

    fig, ax = plt.subplots(figsize=(15, 10))
    bar_width = 0.2
    index = np.arange(len(categories))

    for i, model in enumerate(models):
        model_accuracies = [accuracies[category][i][1] for category in categories]
        bar_positions = index + i * bar_width
        ax.bar(bar_positions, model_accuracies, bar_width, label=model)

    ax.set_xlabel('Category')
    ax.set_ylabel('Accuracy')
    ax.set_title(title)
    ax.set_xticks(index + bar_width * (len(models) - 1) / 2)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.set_ylim(0, 1)
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, file_name))
    plt.close()
    # plt.show()


def plot_radar_chart(data, models, title, file_name, output_dir="results" ):
    categories = list(data.keys())
    num_vars = len(categories)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    for model in models:
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        values = []
        for category in categories:
            model_data = next((item for item in data[category] if item[0] == model), None)
            if model_data:
                correct, wrong = model_data[1], model_data[2]
                accuracy = correct / (correct + wrong)
                values.append(accuracy)
            else:
                values.append(0)
        values += values[:1]

        ax.plot(angles, values, linewidth=2, linestyle='solid', label=model)
        ax.fill(angles, values, alpha=0.25)

        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_title(f"{title} - {model}", size=20, color='black', y=1.1)
        ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        plt.savefig(os.path.join(output_dir, f"{model}_{file_name}"))
        plt.close()


def plot_all_radar_charts(data, title, models, filename, output_dir="results"):
    # sort data by their category
    data = defaultdict(list, sorted(data.items()))
    plot_radar_chart(data, models, title, filename, output_dir)


def plot_radar_chart_2(data, models, title, filename, output_dir="results"):
    categories = list(data.keys())
    num_vars = len(categories)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    for model in models:
        values = []
        for category in categories:
            model_data = next((item for item in data[category] if item[0] == model), None)
            if model_data:
                correct, wrong = model_data[1], model_data[2]
                accuracy = correct / (correct + wrong)
                values.append(accuracy)
            else:
                values.append(0)
        values += values[:1]

        ax.plot(angles, values, linewidth=2, linestyle='solid', label=model)
        ax.fill(angles, values, alpha=0.25)

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_title(title, size=20, color='black', y=1.1)
    ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.savefig(os.path.join(output_dir, f"combined_{filename}"))
    plt.close()


def plot_all_radar_charts_2(data, title, models, filename, output_dir="results"):
    # sort data by their category
    data = defaultdict(list, sorted(data.items()))
    plot_radar_chart_2(data, models, title, filename, output_dir)


# Main Execution
kg, gt = load_dataset('FactBench')
raw_data = load_and_process_data(LLM_MODELS, gt)
processed_data = prepare_data(raw_data)


plot_data(processed_data['correct'], "Model Accuracy by Category for Correct Labels", "Figure_1.png")
plot_data(processed_data['wrong'], "Model Accuracy by Category for Wrong Labels", "Figure_2.png")
plot_data(merge_and_sum(processed_data['combined']), "Model Accuracy by Category for All", "Figure_3.png")


plot_all_radar_charts(processed_data['correct'], "Model Accuracy by Category (Correct Labels)", LLM_MODELS, "correct_radar_chart.png")
plot_all_radar_charts(processed_data['wrong'], "Model Accuracy by Category (Wrong Labels)", LLM_MODELS, "wrong_radar_chart.png")
plot_all_radar_charts(merge_and_sum(processed_data['combined']), "Model Accuracy by Category", LLM_MODELS, f"radar_chart.png")


plot_all_radar_charts_2(processed_data['correct'], "Model Accuracy by Category (Correct Labels)", LLM_MODELS, "correct_radar_chart.png")
plot_all_radar_charts_2(processed_data['wrong'], "Model Accuracy by Category (Wrong Labels)", LLM_MODELS, "wrong_radar_chart.png")
plot_all_radar_charts_2(merge_and_sum(processed_data['combined']), "Model Accuracy by Category", LLM_MODELS, f"radar_chart.png")


def generate_markdown(data, title, file_path):
    # Calculate accuracy for each model in each category
    accuracies = defaultdict(dict)
    for category, values in data.items():
        for model_name, correct, wrong in values:
            accuracy = correct / (correct + wrong)
            accuracies[model_name][category] = accuracy

    data = defaultdict(list, sorted(data.items()))

    # Prepare data for markdown
    categories = list(data.keys())
    models = list(accuracies.keys())

    # Create the markdown table
    markdown_content = f"### {title}\n\n"
    markdown_content += "| Model     | " + " | ".join(categories) + " | Total |\n"
    markdown_content += "|-----------|" + "|".join(["----------"] * (len(categories) + 1)) + "|\n"


# for model in models:
    #     accuracies_list = [f"{accuracies[model].get(category, 0):.2f}" for category in categories]
    #     markdown_content += f"| {model} | " + " | ".join(accuracies_list) + " |\n"

    for model in models:
        accuracies_list = [accuracies[model].get(category, 0) for category in categories]
        accuracies_list.append(sum(accuracies_list) / len(categories))
        markdown_content += f"| {model} | " + " | ".join([f"{acc:.2f}" for acc in accuracies_list]) + " |\n"

    # Write to a markdown file
    with open(file_path, "w") as file:
        file.write(markdown_content)

#
generate_markdown(processed_data['correct'], "Model Accuracy by Category (Correct Labels)", "correct_table.md")
generate_markdown(processed_data['wrong'], "Model Accuracy by Category (Wrong Labels)", "wrong_table.md")
generate_markdown(merge_and_sum(processed_data['combined']), "Model Accuracy by Category", f"table.md")

