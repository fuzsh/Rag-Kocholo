import os
import random
import codecs

from concurrent.futures import ThreadPoolExecutor

from utils.proxy import Proxy
from search_engine.utils import ProxyError
from utils.loggers import LoggingConfigurator
from search_engine.engines import search_engines_dict

log = LoggingConfigurator.get_logger(__name__)


def search_query(query, proxies, retries=3):
    retries = retries

    search_engine = query['se'].lower()
    engine = search_engines_dict[search_engine]

    while retries > 0:
        proxy_url = Proxy.get_proxy_url(proxies, search_engine)
        try:
            engine(proxy=proxy_url, logger=log).search(query['text'], query['id'])
            return True
        except ProxyError as e:
            proxies = Proxy.update_proxy_status(proxies, proxy_url, search_engine)
            log.warning(f"Retrying with another proxy,", query=query['id'], retries=retries)
            retries -= 1
    return False


def load_file(file_name):
    with codecs.open(file_name, 'rb', 'utf-8') as f:
        return f.readlines()


def crawler(queries):
    search_engines = ["google"]

    queries = [{
        "id": query['id'], "text": query['text'], "se": search_engine
    } for query in queries for search_engine in search_engines]

    log.info(f"Total queries: {len(queries) // len(search_engines)}")

    # Iterate over directories to see if the query is already processed or not,
    # directory name is the "query id.html" in the search engine folder
    processed_queries = {}
    with open('data/crawled_queries.txt', 'r') as f:
        search_engine = "google"
        for line in f:
            query_id = line.strip()
            processed_queries[search_engine].add(query_id)
        log.info(f"Total processed queries for {search_engine}: {len(processed_queries[search_engine])}")

    # Remove the processed queries from the list for search engine
    for search_engine, pq in processed_queries.items():
        queries = [
            query for query in queries
            if not (f"{query['id']}.html" in pq and query["se"] == search_engine)
        ]

    log.info(f"Total queries to process: {len(queries) // len(search_engines)}")

    proxy_manager = Proxy(search_engines, number_of_proxies=6, state=random.randint(0, 1000), logger=log)
    proxies = proxy_manager.get_proxies()

    # send 10 request by each proxy for each search engine
    steps = len(proxies) * len(search_engines) * 8

    if True:
        # Determine the number of CPU cores
        number_of_cores = os.cpu_count()
        # Calculate optimal thread count based on task nature
        optimal_threads_for_io_bound = number_of_cores * 4

    for i in range(0, len(queries), steps):
        queries_len = len(queries[i:i + steps])

        # Using ThreadPoolExecutor to manage threads
        with ThreadPoolExecutor(max_workers=min(steps, optimal_threads_for_io_bound)) as executor:
            thread_results = executor.map(search_query, queries[i:i + steps], [proxies] * queries_len)
            # get the list of that failed
            failed_queries = [query for query, status in zip(queries[i:i + steps], thread_results) if not status]
            # add the failed queries to the list of queries to be processed
            queries.extend(failed_queries)
            log.warning(f"Failed queries length is: {len(failed_queries)}")

        log.warning("Start fetching new proxies...")
        # Change the proxy if the search engine blocks the IP
        proxies = proxy_manager.get_proxies()


if __name__ == "__main__":
    pass
