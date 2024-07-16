import sys
import time
import random
import requests
import subprocess



class Proxy(object):
    def __init__(
            self,
            search_engines,  # List of search engines
            state=0,  # State of the proxy
            number_of_proxies=5,  # Number of proxies to generate (default is 10)
            base_url="http://localhost",  # Base URL for proxy requests (default is "http://localhost")
            logger=None  # Logger object
    ):
        """
        Initialize the Proxy object.

        :param search_engines: List of search engine names.
        :param number_of_proxies: Number of proxies to generate.
        :param base_url: Base URL for proxy requests.
        """
        self.state = state  # Initialize state to 0
        self.search_engines = search_engines  # Set search engines
        self.number_of_proxies = number_of_proxies  # Set number of proxies
        self.base_url = base_url  # Set base URL
        self.threshold = self.number_of_proxies // 2  # Set threshold for success/failure

        self.proxy_server_url = "http://localhost:8585/api"  # Set proxy server URL
        self.logger = logger  # Initialize logger

    # Method to generate proxies
    def get_proxies(self):
        """
        Generate proxy configurations.

        :return: List of proxy configurations.
        """
        proxies = []
        while not proxies:
            self._reload_proxies()  # Reload proxies
            self.state += 1  # Increment state

            while True:
                try:
                    time.sleep(10)
                    server_status = requests.get(f"{self.proxy_server_url}/containers-state").json()
                    self.logger.info("Proxy Server Status:", active=len(server_status["success"]), inactive=len(server_status["failed"]))
                    break
                except requests.exceptions.RequestException:
                    time.sleep(5)  # Wait before retrying in case of a request exception
                except Exception as e:
                    self.logger.error("Error fetching server status", error=e)
                    subprocess.run("systemctl restart vpn.service", shell=True)

            if len(server_status["success"]) >= self.threshold:
                self.logger.info("Fetched successfully", active=len(server_status["success"]))
                proxies = [{  # Return a list comprehension to generate proxy configurations
                    "url": f"{self.base_url}:{port}",
                    # Initialize search engine values to 0 for error counting
                    **{search_engine: 0 for search_engine in self.search_engines}
                } for port in server_status["success"]]

        return proxies

    # Method to reload proxies
    def _reload_proxies(self):
        """
        Reload proxies by making a request to the Proxy server with a state parameter.
        """
        try:
            requests.post(f"{self.proxy_server_url}/change-configs/{self.state}")
        except requests.exceptions.RequestException:
            sys.exit("Failed to reload proxies, exiting...")

    @staticmethod
    def get_proxy_url(proxies, search_engine):
        """
        Get a proxy URL based on the search engine.

        :param proxies: List of proxies.
        :param search_engine: Search engine name.
        :return: Proxy URL randomly selected from the list of proxies.
        """
        selected_proxy = random.choice([
            proxy for proxy in proxies
            if proxy[search_engine] == min(proxies, key=lambda x: x[search_engine])[search_engine]
        ])

        return selected_proxy['url']

    @staticmethod
    def update_proxy_status(proxies, proxy_url, search_engine):
        """
        Update the proxy status based on the search engine, because of the error (IP blocked).

        :param proxies: List of proxies.
        :param proxy_url: proxy URL that caused the error.
        :param search_engine: Search engine name.
        :return: List of updated proxies with the error count incremented.
        """
        return [
            proxy if proxy["url"] != proxy_url else {**proxy, search_engine: proxy.get(search_engine, 0) + 1}
            for proxy in proxies
        ]
