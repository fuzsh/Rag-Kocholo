import os

factBench = 0
yago = 0
dbPedia = 0
total = 0

for filename in os.listdir('./docs'):
    if not os.path.exists(f"./docs/{filename}/all_docs"):
        continue
    count_files = len(os.listdir(f"./docs/{filename}/all_docs"))
    if filename.startswith("correct") or filename.startswith("wrong"):
        factBench += 1
    else:
        if filename.startswith("yago"):
            yago += 1
        else:
            dbPedia += 1
    total += count_files


def create_bar(percentage, length=10):
    filled_length = int(length * percentage // 100)
    bar = '█' * filled_length + '-' * (length - filled_length)
    return bar


print(f"FactBench\t: {factBench} out of 2800 \t {create_bar(factBench / 2800 * 100)}")
print(f"YAGO\t\t: {yago} out of 1386 \t {create_bar(yago / 1386 * 100)}")
print(f"DBpedia\t\t: {dbPedia} out of 9344 \t {create_bar(dbPedia / 9344 * 100)}")
print("=====================================")
print(f"Remaining\t: {len(os.listdir('./docs')) - (factBench + yago + dbPedia)}")
print(f"Total\t\t: {total} documents fetched")
print("=====================================")
