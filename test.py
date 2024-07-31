from data_loader import load_dataset
from model import *
from concurrent.futures import ThreadPoolExecutor, as_completed

init_llm()


# Function to append a JSON object to a file
def append_json(file_path, new_data):
    # Check if the file exists
    if os.path.exists(file_path):
        # Open the file and load the existing data
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = []  # If the file is empty or not a valid JSON, initialize as an empty list
    else:
        data = []  # If the file doesn't exist, initialize as an empty list

    # Append the new data
    data.append(new_data)

    # Write the updated data back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file)


kg, gt = load_dataset(dataset_name="DBpedia")
steps = 5
for i in range(0, len(kg) - 1, steps):
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

    append_json('output.json', results)
