import json


def load_dataset(dataset_name: str = "FactBench"):
    print('Load {} dataset.'.format(dataset_name))
    # get target dataset
    with open('./dataset/' + dataset_name + '/data/kg.json', 'r') as f:
        id2triple = json.load(f)

    # set KG as [(id, triple), ...]
    kg = [(k, v) for k, v in id2triple.items()]

    if dataset_name in ["FactBench"]:
        kg = [(k, v[0]) for k, v in id2triple.items()]
        kg = [p for p in kg if
              'correct_' in p[0] or
              'wrong_mix_domain' in p[0] or
              'wrong_mix_range' in p[0] or
              'wrong_mix_domainrange' in p[0] or
              'wrong_mix_property' in p[0] or
              'wrong_mix_random' in p[0]]

    with open('./dataset/' + dataset_name + '/data/gt.json', 'r') as f:  # get ground truth
        gt = json.load(f)

    gt = {k: v for k, v in gt.items() if k in dict(kg)}

    return kg, gt


if __name__ == "__main__":
    load_dataset()
