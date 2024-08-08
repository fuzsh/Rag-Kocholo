RAG_TEMPLATE = """\
Context information is below.
---------------------
{context_str}
---------------------
Given the context information and without prior knowledge, \
Evaluate whether the information in the documents supports the triple. \
Please provide your answer in the form of a structured JSON format containing \
a key \"output\" with the value as \"yes\" or \"no\". \
If the triple is correct according to the documents, the value should be \"yes\". \
If the triple is incorrect, the value should be \"no\". \

{few_shot_examples}

Query: {query_str}
Answer: \
"""


def QUESTION_GENERATION_TEMPLATE(query):
    return """\
You are an intelligent system with access to a vast amount of information. \
I will provide you with a knowledge graph in the form of triples (subject, predicate, object). \
Your task is to generate ten questions based on the knowledge graph. The questions should assess understanding and insight into the information presented in the graph. \
Provide the output in JSON format, with each question having a unique identifier. \
Instructions: \
    1. Analyze the provided knowledge graph. \
    2. Generate ten questions that are relevant to the information in the knowledge graph. \
    3. Provide the questions in JSON format, each with a unique identifier. \

Input Knowledge Graph: \
    Albert Einstein bornIn Ulm \
Expected Response: \
{
    "questions": [
        {"id": 1, "question": "Where was Albert Einstein born?"},
        {"id": 2, "question": "What is Albert Einstein known for?"},
        {"id": 3, "question": "In what year was the Theory of Relativity published?"},
        {"id": 4, "question": "Where did Albert Einstein work?"},
        {"id": 5, "question": "What prestigious award did Albert Einstein win?"},
        {"id": 6, "question": "Which theory is associated with Albert Einstein?"},
        {"id": 7, "question": "Which university did Albert Einstein work at?"},
        {"id": 8, "question": "What did Albert Einstein receive the Nobel Prize in?"},
        {"id": 9, "question": "In what field did Albert Einstein win a Nobel Prize?"},
        {"id": 10, "question": "Name the city where Albert Einstein was born."}
]}""" + f"""\
Considering the above information, please respond to this Knowledge Graph: {query} \
The output should be in JSON format with each question having a unique identifier and question doesn't contain term knowledge graph, without any additional information 
"""


def FORMAL_SENTENCE_TEMPLATE(knowledge_graph):
    return """\
Task Description: \
Convert a knowledge graph triple into a meaningful human-readable sentence. \

Instructions: \
    Given a subject, predicate, and object from a knowledge graph, form a grammatically correct and meaningful sentence that conveys the relationship between them. \

Examples: \
Input: \
    Subject: Alexander_III_of_Russia \
    Predicate: isMarriedTo \
    Object:  Maria_Feodorovna__Dagmar_of_Denmark_ \
    Output: {"output" : "Alexander III of Russia is married to Maria Feodorovna, also known as Dagmar of Denmark."} \

Input: \
    Subject: Quentin_Tarantino \
    Predicate: produced \
    Object: From_Dusk_till_Dawn \
    Output: {"output": "Quentin Tarantino produced the film From Dusk till Dawn."} \

Input: \
    Subject: Joseph_Heller \
    Predicate: created \
    Object: Catch-22 \
    Output: {"output": "Joseph Heller created the novel Catch-22."} \
"""+f"""\
Do the following: \
Input: \
Subject: {knowledge_graph[1][0]} \
Predicate: {knowledge_graph[1][1]} \
Object: {knowledge_graph[1][2]} \
The output should be a JSON object with the key "output" and the value as the sentence. The sentence should be human-readable and grammatically correct. The subject, predicate, and object can be any valid string without having extra information.
"""
