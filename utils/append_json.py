import os
import json


def get_file_data(file_path):
    # Check if the file exists
    if os.path.exists(file_path):
        # Open the file and load the existing data
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}  # If the file is empty or not a valid JSON, initialize as an empty list
    else:
        data = {}  # If the file doesn't exist, initialize as an empty list

    return data


def append_json(file_path, new_data):
    # Get the existing data from the file
    data = get_file_data(file_path)

    # Append the new data
    data.update(new_data)

    # Write the updated data back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
