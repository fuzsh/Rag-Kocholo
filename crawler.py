import grequests
import json
import os
import random
import codecs
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from newspaper import Article
from newspaper.configuration import Configuration
from newspaper.mthreading import fetch_news

from utils.proxy import Proxy
from search_engine.utils import ProxyError
from utils.loggers import LoggingConfigurator
from search_engine.engines import search_engines_dict

log = LoggingConfigurator.get_logger(__name__)
ua = UserAgent(os=['windows'], browsers=["chrome", "edge", "firefox"], platforms=["pc"])


def should_avoid(url, avoid_extensions):
    extension = os.path.splitext(url)[1]
    return extension.lower() in avoid_extensions


# List of file extensions to avoid
avoid_extensions = [
    '.cfm', '.jsp', '.cgi', '.exe', '.bat', '.cmd', '.sh', '.pl',
    '.py', '.rb', '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.rss'
]


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
            return True

        try:
            article = Article(url_data['url'], language='en', config=config)
            article.download()
            article.parse()

            with open(f"docs/{identifier}/all_docs/query_{i}-link_{url_data['rank']}.json", 'w') as f:
                json.dump({
                    "id": f"{identifier}_{i}",
                    "rank": url_data['rank'],
                    "data": json.loads(article.to_json())
                }, f, indent=4, ensure_ascii=False)

            log.info(f"Downloaded {url_data['url']} for {identifier}")
            return True
        except Exception as e:
            log.error(f"Error downloading {url_data['url']} for {identifier}", error=e)
            retries -= 1
    return False


def _get_url(urls, url):
    for u in urls:
        if u['url'] == url:
            return u


def fetch_article(identifier, question_id, url, response, config):
    try:
        if os.path.exists(f"docs/{identifier}/all_docs/query_{question_id}-link_{url['rank']}.json"):
            log.warning(f"Skipping", identifier=identifier, reason="file exists")
            return

        article = Article(url['url'], language='en', config=config)
        article.download(input_html=response.text)
        article.parse()

        with open(f"docs/{identifier}/all_docs/query_{question_id}-link_{url['rank']}.json", 'w') as f:
            json.dump({
                "id": f"{identifier}_{question_id}",
                "rank": url['rank'],
                "data": json.loads(article.to_json())
            }, f, indent=4, ensure_ascii=False)

        log.info(f"Download", identifier=identifier, url=url['url'], status="success")
    except Exception as e:
        log.error(f"Error downloading {url['url']} for {identifier}", error=e)


def get_article_from_query(kg, search_engine="google"):
    identifier = kg[0]

    os.makedirs(f"docs/{identifier}/all_docs", exist_ok=True)
    # TODO: FIX - count the number of files in the directory, if it is greater than 100, skip | BULLSHIT IDEA
    files = os.listdir(f"docs/{identifier}/all_docs")
    files_length = len(files)
    if files_length > 50:
        log.info(f"Skipping {identifier} with {files_length} files")
        return

    config = Configuration()
    config.request_timeout = 5
    config.fetch_images = False
    config.memorize_articles = False
    for i in range(0, 4):
        try:
            config.browser_user_agent = ua.random
            with open(f"data/{search_engine}/{identifier}_{i}.html", 'r') as f:
                soup = BeautifulSoup(f, 'html.parser')

            urls = _get_urls(soup, search_engine)
            urls = [url for url in urls if not should_avoid(url['url'], avoid_extensions)]
            urls = [url for url in urls if not os.path.exists(f"docs/{identifier}/all_docs/query_{i}-link_{url['rank']}.json")]

            # APPROACH 2
            rs = [grequests.get(u['url'], timeout=3, headers={
                "User-Agent": ua.random
            }) for u in urls]
            for index, response in grequests.imap_enumerated(rs, size=50):
                if response is None or response.status_code != 200:
                    continue
                url = urls[index]
                if 'text/html' not in response.headers.get('Content-Type', '').lower():
                    log.warning("Skipping", identifier=identifier, reason="not html", url=url['url'])
                    continue
                log.info(f"Download", identifier=identifier, url=url['url'], status="started")
                # result_queue = multiprocessing.Queue()
                process = multiprocessing.Process(
                    target=fetch_article,
                    args=(identifier, i, url, response, config)
                )
                process.start()
                process.join(timeout=10)  # Timeout in seconds

                if process.is_alive():
                    process.terminate()
                    process.join()
                    log.warning(
                        "Skipping", identifier=identifier, reason="Timeout occurred while processing the article.", url=url['url']
                    )

                # fetch_article(identifier, i, url, response, config)

            # Approach 3
            # results = fetch_news([Article(u['url'], language='en', config=config) for u in urls], threads=20)
            # log.info(f"Total urls: {len(urls)}, Total results: {len(results)}")
            # for result in results:
            #     url = _get_url(urls, result.url)
            #     with open(f"docs/{identifier}/all_docs/query_{i}-link_{url['rank']}.json", 'w') as f:
            #         json.dump({
            #             "id": f"{identifier}_{i}",
            #             "rank": url['rank'],
            #             "data": json.loads(result.to_json())
            #         }, f, indent=4, ensure_ascii=False)
            #
            #     log.info(f"Downloaded {url['url']} for {identifier}")
            # for j in range(0, len(urls), 1):
            #     status = fetch_url(urls[j], config, identifier, i, retries=1)
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
        except Exception as e:
            log.error(f"Error fetching urls for {identifier}", error=e)
            # shutil.rmtree(f"docs/{identifier}")
            continue


if __name__ == "__main__":
    pass
