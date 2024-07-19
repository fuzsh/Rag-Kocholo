import json
import os
import random
import codecs
import shutil

from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from newspaper import Article
from newspaper.configuration import Configuration

from utils.proxy import Proxy
from search_engine.utils import ProxyError
from utils.loggers import LoggingConfigurator
from search_engine.engines import search_engines_dict

log = LoggingConfigurator.get_logger(__name__)
ua = UserAgent(os=['windows'], browsers=["chrome", "edge", "firefox"], platforms=["pc"])


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
    for search_engine in search_engines:
        dir_path = f"data/{search_engine}"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        processed_queries[search_engine] = set(os.listdir(dir_path))
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


def _get_urls(soup, engine):
    search_engine = engine.lower()
    engine = search_engines_dict[search_engine]
    return [{"url": result['url'], "rank": res_id} for res_id, result in enumerate(engine().get_organic_results(soup))]


def fetch_url(url_data, config, identifier, i, retries=3):
    retries = retries
    while retries > 0:
        # if file exists, skip
        if os.path.exists(f"docs/{identifier}/all_docs/query_{i}-link_{url_data['rank']}.json"):
            log.info(f"Skipping {url_data['url']} for {identifier}")
            # return True

        try:
            article = Article(url_data['url'], language='en', config=config)
            article.download()
            article.parse()

            with open(f"docs/{identifier}/all_docs/query_{i}-link_{url_data['rank']}.json", 'w') as f:
                json.dump({
                    "id": f"{identifier}_{i}",
                    "rank": url_data['rank'],
                    "data": article.to_json()
                }, f, indent=4, ensure_ascii=False)

            log.info(f"Downloaded {url_data['url']} for {identifier}")
            return True
        except Exception as e:
            log.error(f"Error downloading {url_data['url']} for {identifier}", error=e)
            retries -= 1
    return False


def get_article_from_query(kg, search_engine="google"):
    identifier = kg[0]
    config = Configuration()
    config.request_timeout = 5
    config.fetch_images = False
    for i in range(0, 4):
        config.browser_user_agent = ua.random
        os.makedirs(f"docs/{identifier}/all_docs", exist_ok=True)

        with open(f"data/{search_engine}/{identifier}_{i}.html", 'r') as f:
            soup = BeautifulSoup(f, 'html.parser')

        steps = 10
        urls = _get_urls(soup, search_engine)
        for j in range(0, len(urls), 1):
            status = fetch_url(urls[j], config, identifier, i, retries=1)
            # with ThreadPoolExecutor(max_workers=10) as executor:
            #     thread_results = executor.map(
            #         fetch_url,
            #         urls[j:j + steps],
            #         [identifier] * len(urls[j:j + steps]),
            #         [i] * len(urls[j:j + steps])
            #     )
            #     # get the list of that failed
            #     failed_urls = [query for query, status in zip(urls[i:i + steps], thread_results) if not status]
            #     # add the failed urls to the list of urls to be processed
            #     # urls.extend(failed_urls)
            #     log.warning(f"Failed queries length is: {len(failed_urls)}")


if __name__ == "__main__":
    pass

# iterate over the directory to get the queries and remove all the folder name with all_docs
import shutil
import os
for folder in os.listdir("docs"):
    try:
        for fo in os.listdir(f"docs/{folder}"):
            if fo == "all_docs":
                print(f"Removing {folder}")
                shutil.rmtree(f"docs/{folder}/{fo}")
    except Exception as e:
        print(e)
        continue