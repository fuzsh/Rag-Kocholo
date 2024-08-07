import os
import json


count_missing = 0
count_missing_docs = 0
for directory in os.listdir('docs'):
    identifier = directory
    try:
        if len(os.listdir(f'docs/{identifier}/all_docs')) < 20:
            print(f'{identifier} has less than 20 files', len(os.listdir(f'docs/{identifier}/all_docs')))
            count_missing_docs += 1
        with open(f'docs/{identifier}/questions.json', 'r') as file:
            data = json.load(file)
            if len(data['questions']) < 5:
                # print(f'{identifier} has less than 5 questions')
                count_missing += 1
    except Exception as e:
        print(f'{identifier} is missing')
        count_missing += 1

print(f'Total missing: {count_missing}')
print(f'Total missing: {count_missing_docs}')


# remove all docs for that folders
# remove the HTML pages that we fetch for them
# remove the folder itself
# reconstruct everything from scratch
