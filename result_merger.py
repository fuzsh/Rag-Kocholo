import json

LLM_MODELS = [
    "Gemma2",
    "Llama3_1",
    "Mistral",
    "Qwen2"
]


def merge_results(task_category=None):
    results = {}
    for llm in LLM_MODELS:
        with open(f"results/{llm}/FactBench_modified.json", "r") as f:
            data = json.load(f)

        for key, value in data.items():
            if task_category is not None and task_category not in key.split('_'):
                continue
            data_obj = {llm: value['short_ans']}
            if key in results:
                results[key].update(data_obj)
            else:
                results[key] = data_obj

    final_eval = {}
    for key, value in results.items():
        llm_answers = value.values()
        zeros, ones = list(llm_answers).count(0), list(llm_answers).count(1)
        if zeros == ones:
            final_evaluation = -1
        elif ones > len(llm_answers) / 2:
            final_evaluation = 1
        else:
            final_evaluation = 0

        final_eval[key] = {
            "short_ans": final_evaluation,
            "full_ans": value
        }

    with open("results/final_eval.json", "w") as f:
        json.dump(final_eval, f, indent=4)


if __name__ == "__main__":
    merge_results(task_category="starring")
