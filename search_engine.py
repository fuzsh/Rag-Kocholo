import json
import os
import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from re_ranker import re_rank

import urllib.parse
import tldextract


def get_main_domain(url):
    # Parse the URL to ensure it's properly formatted
    parsed_url = urllib.parse.urlparse(url)
    # Extract the main domain using tldextract
    extracted = tldextract.extract(parsed_url.netloc)
    # Combine the domain parts to get the main domain
    return f"{extracted.domain}.{extracted.suffix}"


EXCLUDE_URLS = [
    "wikipedia.org",
    "wikimedia.org",
    "quora.com",
    "britannica.com",  # Encyclopaedia Britannica
    "scholarpedia.org",  # Scholarpedia
    "citizendium.org",  # Citizendium
    "infoplease.com",  # Infoplease
    "howstuffworks.com",  # HowStuffWorks
    "archive.org",  # Internet Archive
    "gutenberg.org",  # Project Gutenberg
    "stanford.edu",  # Stanford Encyclopedia of Philosophy
    "newworldencyclopedia.org",  # New World Encyclopedia
    "everipedia.org",  # Everipedia
    "encyclopedia.com",  # Encyclopedia.com
    "wikibooks.org",  # Wikibooks
    "wiktionary.org",  # Wiktionary
    "wikiversity.org",  # Wikiversity
    "wikisource.org",  # Wikisource
    "wikiquote.org",  # Wikiquote
    "wikivoyage.org",  # Wikivoyage
    "merriam-webster.com",  # Merriam-Webster
    "khanacademy.org",  # Khan Academy
    "ted.com",  # TED
    "bbc.com",  # BBC
    "cnn.com",  # CNN
    "nationalgeographic.com",  # National Geographic
    "sciencedaily.com",  # ScienceDaily
    "livescience.com",  # LiveScience
    "history.com",  # History
    "bbc.co.uk",  # BBC History
    "bartleby.com",  # Bartleby
    "sparknotes.com",  # SparkNotes
    "shmoop.com",  # Shmoop
    "academia.edu",  # Academia.edu
    "jstor.org",  # JSTOR
    "researchgate.net",  # ResearchGate
    "springer.com",  # Springer
    "nature.com",  # Nature
    "sciencemag.org",  # Science
    "pbs.org",  # PBS
    "theguardian.com",  # The Guardian
    "nytimes.com",  # The New York Times
]


# Function to read all documents from a directory
def read_documents(directory, exclude_urls=None):
    if exclude_urls is None:
        exclude_urls = EXCLUDE_URLS

    urls = []
    documents = []

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                document = json.load(file)
                url = document['data']['url']
                if url not in urls and get_main_domain(url) not in exclude_urls:
                    urls.append(url)
                    document = document['data']['text']
                    if document:
                        documents.append(document)
    return documents


# Function to process queries and find relevant documents
def search_engine_TF_IDF(documents, queries, top_n=10):
    # Initialize the TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')

    # Fit and transform the documents
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Transform the queries
    query_tfidf = vectorizer.transform(queries)

    # Calculate cosine similarity between the queries and documents
    similarities = cosine_similarity(query_tfidf, tfidf_matrix)

    # Find the top_n relevant documents for each query
    results = []
    for query_idx, similarity in enumerate(similarities):
        ranked_indices = np.argsort(similarity)[::-1][:top_n]
        results.append((queries[query_idx], [(i, similarity[i]) for i in ranked_indices]))

    return results


def tokenize_documents(documents):
    return [doc.split() for doc in documents]


def search_engine_BM25(documents, queries, top_n=10):
    # Tokenize documents
    tokenized_documents = tokenize_documents(documents)

    # Initialize BM25
    bm25 = BM25Okapi(tokenized_documents)

    # Tokenize queries
    tokenized_queries = [query.split() for query in queries]

    # Get BM25 scores for each query
    results = []
    for query_idx, tokenized_query in enumerate(tokenized_queries):
        scores = bm25.get_scores(tokenized_query)
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_n]
        results.append((queries[query_idx], [(i, scores[i]) for i in ranked_indices]))

    return results


def search_engine(knowledge_graph, top_n=10):
    identifier = knowledge_graph[0]
    # Read documents from the specified directory
    documents = read_documents(f'docs/{identifier}/all_docs')

    # Define the queries
    queries = [' '.join(knowledge_graph[1])]
    with open(f"./docs/{identifier}/questions.json", "r") as f:
        questions = json.load(f)['questions']
    # get top 3 questions based on score field
    questions = sorted(questions, key=lambda x: x['score'], reverse=True)[:3]
    queries.extend([q['question'] for q in questions])

    # Get search results
    results = search_engine_BM25(documents, queries, top_n=top_n)

    selected_docs = []
    for query, result in results:
        docs = []
        for doc_idx, score in result:
            docs.append(documents[doc_idx])

        re_rank_results = re_rank(query, docs, return_documents=False)

        max_bm25_score = max([score for _, score in result])
        max_re_rank_score = max([result['score'] for result in re_rank_results])

        for idx, (doc_idx, score) in enumerate(result):
            # calculate new rank with harmonic mean between BM25 and re_ranker, also normalize the score to be between 0 and 1
            a = score / max_bm25_score
            b = re_rank_results[idx]['score'] / max_re_rank_score
            new_score = 2 * a * b / (a + b) if a + b != 0 else 0
            selected_docs.append({'doc_idx': doc_idx, 'score': new_score, "doc": documents[doc_idx]})

    selected_docs = sorted(selected_docs, key=lambda x: x['score'], reverse=True)[:10]
    for doc in selected_docs:
        with open(f"docs/{identifier}/{doc['doc_idx']}.txt", 'w', encoding='utf-8') as file:
            file.write(doc['doc'])

    print(f"Processed {identifier} documents successfully done.")


# Example usage
if __name__ == "__main__":
    # Read documents from the specified directory
    knowledge_graph = ('correct_death_00144', ['Billy Wilder', 'deathPlace', 'Beverly Hills, California'])
    search_engine(knowledge_graph)