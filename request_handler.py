import grequests
import requests
from bs4 import BeautifulSoup

from crawler import _get_urls


def get_response(urls):
    rs = (grequests.get(u) for u in urls)
    return grequests.map(rs)
    # rs = [grequests.get(f'https://httpbin.org/status/{code}') for code in range(200, 206)]
    # for index, response in grequests.imap_enumerated(rs, size=5):
    #     print(index, response)


if __name__ == "__main__":
    knowledge_graph = ('correct_death_00144', ['Billy Wilder', 'deathPlace', 'Beverly Hills, California'])
    identifier = knowledge_graph[0]
    search_engine = "google"

    with open(f"data/google/{identifier}_{1}.html", 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')

    urls = _get_urls(soup, search_engine)
    rs = [grequests.get(u['url']) for u in urls]
    for index, response in grequests.imap_enumerated(rs, size=20):
        print(index, response)
