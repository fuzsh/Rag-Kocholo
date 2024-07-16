from sentence_transformers import CrossEncoder

model_name = "jinaai/jina-reranker-v1-turbo-en"
model = CrossEncoder(model_name, trust_remote_code=True)


def re_ranker(query, documents):
    """
    Re-ranker function that takes a query and a list of documents
    and returns a list of documents with their scores.
    """
    return [
        {'id': result['corpus_id'] + 1, 'score': float(result['score']), 'question': result['text']}
        for result in model.rank(query, documents, return_documents=True)
    ]


def sort_by_corpus_id(results):
    return sorted(results, key=lambda x: x['id'])


def re_rank(query, documents):
    # Process the JSON data (e.g., perform some computation)
    return sort_by_corpus_id(re_ranker(query, documents))


if __name__ == "__main__":
    query = "Shane Battier team Los Angeles Lakers"
    documents = [
        {
            "id": 1,
            "question": "What team does Shane Battier play for?"
        },
        {
            "id": 2,
            "question": "In what city do the Los Angeles Lakers play their home games?"
        },
        {
            "id": 3,
            "question": "Who is Shane Battier playing basketball for?"
        },
        {
            "id": 4,
            "question": "What sport is Shane Battier a professional player of?"
        },
        {
            "id": 5,
            "question": "Which team has Shane Battier played for?"
        },
        {
            "id": 6,
            "question": "Who plays for the Los Angeles Lakers?"
        },
        {
            "id": 7,
            "question": "In what sport is the Los Angeles Lakers a professional team of?"
        },
        {
            "id": 8,
            "question": "What position does Shane Battier play in basketball?"
        },
        {
            "id": 9,
            "question": "Who is a professional basketball player for the Los Angeles Lakers?"
        },
        {
            "id": 10,
            "question": "Which team's player is Shane Battier?"
        }
    ]
    print(re_rank(query, [doc['question'] for doc in documents]))
