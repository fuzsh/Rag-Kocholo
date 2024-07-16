from os import path as os_path, pardir as os_pardir, name as os_name
from sys import version_info
from fake_useragent import UserAgent

# Python version 
PYTHON_VERSION = version_info.major

# Maximum number or pages to search
SEARCH_ENGINE_RESULTS_PAGES = 1

# HTTP request timeout 
TIMEOUT = 10

ua = UserAgent(os=['windows'], browsers=["chrome", "edge", "firefox"], platforms=["pc"])

# Default User-Agent string 
USER_AGENT = ua.random

# Fake User-Agent string - Google doesn't like the default user-agent
FAKE_USER_AGENT = ua.random

# Proxy server 
PROXY = None

_base_dir = os_path.abspath(os_path.dirname(os_path.abspath(__file__)))

