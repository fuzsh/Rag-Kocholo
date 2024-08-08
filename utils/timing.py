import json
import os

for directory in os.listdir('./results/timing'):
    with open(f'./results/timing/{directory}', 'r') as f:
       data = json.load(f)

    val = sum(data.values())
    print(f"Average time for model {' '.join(directory.split('-'))} is {val/len(data)} seconds")
