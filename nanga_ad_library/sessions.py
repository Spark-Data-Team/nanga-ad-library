import hashlib
import hmac

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from enum import Enum

"""
The purpose of the session module is to encapsulate authentication classes and utilities.

Based on Session module of Requests package (https://pypi.org/project/requests/)
"""


class ApiSession(object):

    DEFAULT_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}
    MAX_RETRIES = 5
    BACKOFF_FACTOR = 1

    def __init__(
        self,
        cert_path=None, proxies=None, headers=None, params=None,
        max_retries=None, backoff_factor=None,
        timeout=None,
        verbose=False
    ):
        """
        Initializes a requests session
        """

        # Initiate requests Session
        self.__requests_session = requests.Session()
        self.__params = params or {}
        self.__timeout = timeout
        self.__max_retries, self.__backoff_factor = None, None
        self.__verbose = False

        # Update all needed session attributes
        self.update_headers(
            headers or self.DEFAULT_HEADERS
        )
        self.update_retries(
            max_retries or self.MAX_RETRIES,
            backoff_factor or self.BACKOFF_FACTOR
        )
        self.update_ssl_config(cert_path)
        self.update_proxies(proxies)

        # Print a message if verbose
        self.__verbose = verbose or False
        self.__log_update(creation=True)

    def __del__(self):
        if self.__verbose:
            print("API session object killed")
        self.__requests_session.close()
        self.__dict__.clear()

    def __log_update(self, creation=False):
        if self.__verbose:
            print("New API session initiated" if creation else "API session updated")
            self.display_session_attributes()

    def get_headers(self):
        return self.__requests_session.headers

    def update_headers(self, headers):
        if headers:
            self.__requests_session.headers.update(headers)
            self.__log_update()

    def clean_headers(self):
        self.__requests_session.headers = self.DEFAULT_HEADERS
        self.__log_update()

    def get_retries_params(self):
        return self.__max_retries, self.__backoff_factor

    def update_retries(self, max_retries, backoff_factor):
        if max_retries and backoff_factor:
            retries = Retry(
                total=max_retries,
                backoff_factor=backoff_factor,
                status_forcelist=[500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retries)
            self.__requests_session.mount("http://", adapter)
            self.__requests_session.mount("https://", adapter)
            self.__max_retries, self.__backoff_factor = max_retries, backoff_factor
            self.__log_update()

    def remove_retries(self):
        self.__requests_session.adapters.clear()
        self.__max_retries, self.__backoff_factor = None, None
        self.__log_update()

    def get_ssl_config(self):
        return self.__requests_session.verify

    def update_ssl_config(self, cert_path):
        self.__requests_session.verify = cert_path if cert_path else True
        self.__log_update()

    def remove_ssl_config(self):
        self.__requests_session.verify = True
        self.__log_update()

    def get_proxies(self):
        return self.__requests_session.proxies

    def update_proxies(self, proxies):
        if proxies:
            self.__requests_session.proxies.update(proxies)
            self.__log_update()

    def clean_proxies(self):
        self.__requests_session.proxies = {}
        self.__log_update()

    def get_params(self):
        return self.__params

    def update_params(self, params):
        if params:
            self.__params.update(params)
            self.__log_update()

    def clean_params(self):
        self.__params = {}
        self.__log_update()

    def get_timeout(self):
        return self.__timeout

    def update_timeout(self, timeout):
        if timeout:
            self.__timeout = timeout
            self.__log_update()

    def remove_timeout(self):
        self.__timeout = None
        self.__log_update()

    def display_session_attributes(self):
        max_retries, backoff_factor = self.get_retries_params()
        print(
            f"""Session attributes:\n"""
            f"""\tSSL Config:\t{self.get_ssl_config()}\n"""
            f"""\tProxies:\t{self.get_proxies()}\n"""
            f"""\tHeaders:\t{self.get_headers()}\n"""
            f"""\tParams:\t\t{self.get_params()}\n"""
            f"""\tTimeout:\t{self.get_timeout()}\n"""
            f"""\tRetries:\tRetry on error (up to {max_retries} times) every {backoff_factor}\n"""
        )

    def execute(self, method, url):
        # Prepare request arguments
        kwargs = {
            "method": method,
            "url": url,
        }
        if self.__timeout:
            kwargs["timeout"] = self.__timeout
        if self.__params:
            if method in ["GET", "HEADERS", "DELETE"]:
                kwargs["params"] = self.__params
            else:
                kwargs["data"] = self.__params

        # Launch request
        response = self.__requests_session.request(**kwargs)

        return response

    def duplicate(self):
        """
        Initiate a new Api Session object with the same attributes as self.
        """
        new_api_session = ApiSession(
            cert_path=self.__requests_session.verify,
            proxies=self.__requests_session.proxies,
            headers=self.__requests_session.headers,
            params=self.__params,
            max_retries=self.__max_retries,
            backoff_factor=self.__backoff_factor,
            timeout=self.__timeout,
            verbose=self.__verbose
        )

        return new_api_session


class MetaGraphAPISession(ApiSession):
    """
    MetaGraphAPISession manages the Graph API authentication and https
    connection.

    Attributes:
        access_token: The access token.
        app_secret: The application secret.
    """

    def __init__(
        self,
        access_token, app_secret=None,
        cert_path=None, proxies=None, headers=None,
        max_retries=None, backoff_factor=None,
        timeout=None,
        verbose=False,
    ):
        """
        Store the authentication tokens and initiate an ApiSession object
        """
        # Init parent
        super().__init__(
            cert_path=cert_path, proxies=proxies, headers=headers, params=None,
            max_retries=max_retries, backoff_factor=backoff_factor,
            timeout=timeout,
            verbose=verbose
        )

        # Store authentication tokens
        self.access_token = access_token
        self.app_secret = app_secret

    def __gen_app_secret_proof(self):
        """
        Generate a secret proof for Meta GRAPH API using app_secret and access_token.
        """
        h = hmac.new(
            self.app_secret.encode('utf-8'),
            msg=self.access_token.encode('utf-8'),
            digestmod=hashlib.sha256
        )

        return h.hexdigest()

    def authenticate(self):
        """
        Allow Meta GRAPH API authentication adding tokens to session params.
        """
        # Store new access_token and appsecret_proof (if app_secret is provided)
        params = {
            "access_token": self.access_token,
        }
        if self.app_secret:
            params["appsecret_proof"] = self.__gen_app_secret_proof()
        # Update Api Session params with params dict
        self.update_params(params)

    @classmethod
    def init(cls, **kwargs):
        """
        Initiate an API requests session and authenticate using auth tokens
        """

        # Check that mandatory parameters are provided
        MetaSessionMandatoryArgs.check_arguments(**kwargs)

        # Initiate a requests session for Meta GRAPH API
        meta_session = cls(
            kwargs.get("access_token"),
            app_secret=kwargs.get("app_secret"),
            cert_path=kwargs.get("cert_path"),
            proxies=kwargs.get("proxies"),
            headers=kwargs.get("headers"),
            max_retries=kwargs.get("max_retries"),
            backoff_factor=kwargs.get("backoff_factor"),
            timeout=kwargs.get("timeout"),
            verbose=kwargs.get("verbose")
        )

        # Authenticate using access token and app_secret (if provided)
        meta_session.authenticate()

        return meta_session


"""
Needed arguments for each platform session class
"""


class MetaSessionMandatoryArgs(Enum):
    """
    Mandatory arguments for class MetaGraphAPISession init.
    """
    ACCESS_TOKEN = "access_token"

    @classmethod
    def check_arguments(cls, **kwargs):
        """
        Check that all arguments needed to initiate a MetaGraphAPISession are provided in kwargs.

        Args:
            kwargs: Args dict received during NANGA_AD_LIBRARY initiation.

        Returns:
             Whether all mandatory arguments are provided.

        Raises:
            ValueError if some mandatory arguments are missing.
        """
        needed_args = {member.value for member in cls}
        provided_args = set(kwargs.keys())

        if not needed_args.issubset(provided_args):
            missing_args_str = "\n\t- ".join(list(needed_args - provided_args))
            # To update
            raise ValueError(
                f"""Missing mandatory arguments to initiate Meta Graph Session:\n\t- {missing_args_str}"""
            )


__all__ = ['MetaGraphAPISession']
