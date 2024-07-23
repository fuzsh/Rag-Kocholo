import os

wrong_docs = 0
correct_docs = 0
total_correct = 0
total_wrong = 0
total_processed_queries = 0

for filename in os.listdir('./docs'):
    if not os.path.exists(f"./docs/{filename}/all_docs"):
        continue
    count_files = len(os.listdir(f"./docs/{filename}/all_docs"))
    if filename.startswith("wrong"):
        wrong_docs += 1
        total_wrong += count_files
    else:
        correct_docs += 1
        total_correct += count_files
    total_processed_queries += 1

print("===================================================================")
print(f"Correct docs\t\t: {correct_docs}")
print(f"Wrong docs\t\t: {wrong_docs}")
print(f"Total processed queries\t: {total_processed_queries}")
print(f"Total fetched files\t: {total_wrong + total_correct}")
print("===================================================================")
print(f"Avg. docs per correct query\t: {(total_correct / correct_docs):.2f}")
print(f"Avg. docs per wrong query\t: {(total_wrong / wrong_docs):.2f}")
print("===================================================================")
