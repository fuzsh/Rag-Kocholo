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
# import json
#
# with open('results/FactBench.json', 'r') as f:
#     data = json.load(f)
#
# new_obj = {}
# for key, value in data.items():
#     if value["full_ans"] != "Empty Response":
#         new_obj[key] = value
#
#
# with open('results/FactBench_modified.json', 'w') as f:
#     json.dump(new_obj, f, indent=4)
# from collections import defaultdict
#
# import pandas as pd
#
# # with open("results/analysis.md", 'r') as f:
# #     md_io = f.read()
#
# # Read the Markdown table into a DataFrame
# df = pd.read_csv("results/analysis.md", sep='|', skipinitialspace=True)
#
# # Clean up the DataFrame
# df.columns = df.columns.str.strip()  # Remove extra spaces from column names
# # df = df.drop(columns=[''])  # Drop any empty columns
# df = df.reset_index(drop=True)  # Reset index to clean up any extra indexing
#
# data = {}
# df = df[1:]
# for index, row in df.iterrows():
#     category = row["Category"].split("_")[-1]
#     if category in data:
#         data[category][0] = data[category][0] + int(row["Correct"])
#         data[category][1] = data[category][1] + int(row["Incorrect"]) + int(row["Not understandable"])
#     else:
#         data[category] = [int(row["Correct"]), int(row["Incorrect"]) + int(row["Not understandable"])]
#
# data = defaultdict(list, sorted(data.items()))
#
# for d,r in data.items():
#     print(f"category:\t {d} \t {(r[0]/ (r[0]+r[1])):.2f}")
import os
import json
dbPedia = 0
total = 0
fucked_files = 0
double_fucked_files = 0

db = 0

for filename in os.listdir('./docs'):
    # if not filename.startswith("yago"):
    #     continue
    if not os.path.exists(f"./docs/{filename}/all_docs"):
        continue
    count_files = len(os.listdir(f"./docs/{filename}/all_docs"))

    dbPedia += 1

    local_double_fucked = 0
    for sq in os.listdir(f"./docs/{filename}/all_docs"):
        try:
            with open(f"./docs/{filename}/all_docs/{sq}") as f:
                data = json.load(f)
                text = data["data"]['text']
                if text == "" or len(text) < 50 or 'robot' in text or 'captcha' in text:
                    # if 'captcha' in text:
                    #     print(data)
                    local_double_fucked += 1
        except Exception as e:
            # print(e)
            local_double_fucked += 1
            continue
    # print(f"{filename},\t {count_files},\t {local_double_fucked}\t, {count_files - local_double_fucked}")
    if count_files - local_double_fucked < 30:
        print(f"{filename},\t {count_files - local_double_fucked}")
        fucked_files += 1
        if filename.startswith("dbpedia"):
            db += 1

    double_fucked_files += local_double_fucked
    total += count_files

print(f"DBpedia\t\t: {dbPedia} out of 9344, {total} documents fetched")
print(fucked_files)
print(double_fucked_files)
print(total - double_fucked_files)
print(db)