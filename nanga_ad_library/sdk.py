import json
import curlify
import asyncio

from enum import Enum

from nanga_ad_library.utils import get_sdk_version
from nanga_ad_library.sessions import MetaGraphAPISession
from nanga_ad_library.ad_libraries import MetaAdLibrary
from nanga_ad_library.ad_downloaders import MetaAdDownloader
from nanga_ad_library.exceptions import PlatformRequestError


"""
The api module contains classes that make http requests to various platforms Ad Library APIs.
"""


class PlatformResponse:

    """Encapsulates a http response from the nanga Ad Library API."""

    def __init__(self, body=None, http_status=None, headers=None, call=None):
        """Initializes the object's internal data.
        Args:
            body (optional): The response body as text.
            http_status (optional): The http status code.
            headers (optional): The http headers.
            call (optional): The original call that was made.
        """
        self.__body = body
        self.__http_status = http_status
        self.__headers = headers or {}
        self.__call = call

    def body(self):
        """Returns the response body."""
        return self.__body

    def json(self):
        """Returns the response body -- in json if possible."""
        try:
            return json.loads(self.__body)
        except (TypeError, ValueError):
            return self.__body

    def headers(self):
        """Return the response headers."""
        return self.__headers

    def status(self):
        """Returns the http status code of the response."""
        return self.__http_status

    def is_success(self):
        """Returns boolean indicating if the call was successful."""
        return 200 <= self.__http_status < 300

    def is_failure(self):
        """Returns boolean indicating if the call failed."""
        return not self.is_success()

    def raise_for_status(self):
        """
        Raise a PlatformRequestError (located in the exceptions module) with
        an appropriate debug message if the request failed.
        """
        if self.is_failure():
            raise PlatformRequestError(
                "Call was not successful",
                self.__call,
                self.status(),
                self.headers(),
                self.body(),
            )


class NangaAdLibrary:

    """
    Encapsulates session attributes and methods to make API calls.
    Also downloads ad elements by scrapping Ad Library preview card with Playwright.

    Attributes:
        SDK_VERSION (class): indicating sdk version.
        HTTP_DEFAULT_HEADERS (class): Default HTTP headers for requests made by this sdk.
    """

    SDK_VERSION = get_sdk_version()

    HTTP_DEFAULT_HEADERS = {
        'User-Agent': "NangaAdLibrary/%s" % SDK_VERSION,
    }

    def __init__(self, sdk_session, ad_library, ad_downloader, verbose=None):
        """
        Initiates the sdk instance.

        Args:
            session: PlatformSession object that contains a requests interface
                and the attributes BASE_URL and LAST_VERSION.
        """
        self.__sdk_session = sdk_session
        self.__ad_library = ad_library
        self.__ad_downloader = ad_downloader

        # Global information
        self.__num_requests_succeeded = 0
        self.__num_requests_attempted = 0
        self.__verbose = verbose or False

        # Enforce different sessions for each cursors
        self.__cursor_sessions = []

    def __del__(self):
        if self.__verbose:
            print("Nanga Ad Library API object killed")
        self.__dict__.clear()

    def get_num_requests_attempted(self):
        """Returns the number of calls attempted."""
        return self.__num_requests_attempted

    def get_num_requests_succeeded(self):
        """Returns the number of calls that succeeded."""
        return self.__num_requests_succeeded

    @classmethod
    def init(cls, platform, **kwargs):
        """


        Args:
            platform: The platform of the Ad Library you want to
            **kwargs: A payload with all arguments needed to query platform Ad Library
                #TODO (add doc + provide template for the kwargs depending on the platform)

        Returns:
            A NangaAdLibrary object, ready to extract valuable data.
        """
        # Initiate instances depending on the chosen platform
        if platform == "Meta":
            # Initiate Meta Graph Session
            sdk_session = MetaGraphAPISession.init(**kwargs)

            # Initiate Meta Ad Library API
            ad_library = MetaAdLibrary.init(**kwargs)

            # Initiate Meta Ad Downloader if "download_ads" argument is set to True
            ad_downloader = MetaAdDownloader.init(**kwargs) if (kwargs.get("download_ads") == True) else None

        else:
            # To update
            raise ValueError(
                f"""{platform} is not yet available in the Nanga Ad Library API ({cls.SDK_VERSION})."""
            )

        # Initiate NangaAdLibrary
        sdk = cls(sdk_session, ad_library, ad_downloader, verbose=kwargs.get("verbose"))

        return sdk

    def get_api_version(self):
        return self.__ad_library.get_api_version()

    def update_api_version(self, version: str):
        self.__ad_library.update_api_version(version)

    def get_http_method(self):
        return self.__ad_library.get_method()

    def update_http_method(self, method: str):
        self.__ad_library.update_method(method)

    def get_payload(self):
        return self.__ad_library.get_payload()

    def reload_payload(self, payload: dict):
        self.__sdk_session.clean_params()
        self.__sdk_session.authenticate()
        self.__ad_library = self.__ad_library.init(
            payload=payload,
            version=self.__ad_library.get_api_version(),
            method=self.__ad_library.get_method()
        )

    def get_cursor_session(self, rank):
        if isinstance(rank, int) and (0 <= rank < len(self.__cursor_sessions)):
            return self.__cursor_sessions[rank]

    def call(self, session=None):
        """
        Makes an API call using a session and an ad_library object

        Returns:
            A PlatformResponse object containing the response body, headers,
            http status, and summary of the call that was made.

        Raises:
            PlatformResponse.raise_for_status() to check if the request failed.
        """

        # Increment _num_requests_attempted as soon as Call method is triggered
        self.__num_requests_attempted += 1

        # When a session is provided, do not affect if
        if not session:
            # Include API headers in http request
            self.__sdk_session.update_headers(self.HTTP_DEFAULT_HEADERS)

            # Include AdLibrary Payload to session params
            if self.__ad_library.get_payload:
                encoded_payload = json_encode_top_level_param(self.__ad_library.get_payload())
                self.__sdk_session.update_params(encoded_payload)

            session = self.__sdk_session

        # Get request response and encapsulate it in a PlatformResponse
        response = session.execute(
            method=self.__ad_library.get_method(),
            url=self.__ad_library.get_final_url()
        )

        # If debug logger enabled, print the request as CURL
        if self.__verbose:
            print(f"New HTTP request made:\n\t{curlify.to_curl(response.request)}\n")

        # Prepare response
        platform_response = PlatformResponse(
            body=response.text,
            headers=response.headers,
            http_status=response.status_code,
            call={
                'method': self.__ad_library.get_method(),
                'path': self.__ad_library.get_final_url(),
                'params': self.__sdk_session.get_params(),
                'headers': self.__sdk_session.get_headers(),
            }
        )

        # Increment the number of successful calls
        if platform_response.is_success():
            self.__num_requests_succeeded += 1

        return platform_response

    def get_results(self):
        """
        Make an API call and iterate a cursor with the response.
        """

        response = self.call()
        self.__cursor_sessions.append(self.__sdk_session.duplicate())
        results = ResultCursor(
            api=self,
            ad_downloader=self.__ad_downloader,
            cursor_num=len(self.__cursor_sessions)-1,
            response=response.json()
        )

        return results


class ObjectParser:
    """
    ObjectParser instances are initialized with a dictionary describing their attributes.
        Usage example:
            >>> dict_to_parse = {"name": "nanga", "description": "the best digital marketing SaaS available"}
            >>> ad_library = ObjectParser(**dict_to_parse)
            >>> print(f"Welcome to {ad_library.name}: {ad_library.description}")
            Welcome to nanga: the best digital marketing SaaS available

    Attributes can be accessed using object.field, object["field"], or object.get("field").
    It also have the standard dict methods: .keys(), .values() and .items()
    """

    def __repr__(self):
        return json.dumps(self.__dict__)

    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    def __getitem__(self, key):
        return self.__dict__[key]

    def get(self, key):
        return self.__dict__.get(key)

    def update(self, new_dict):
        self.__dict__.update(new_dict)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()


class ResultCursor:
    """
    Cursor is a cursor over an object's connections.
    """

    def __init__(self, api, cursor_num, ad_downloader=None, response=None):
        """
        Initializes a cursor with a PlatformResponse
        """
        self.__api = api
        self.__cursor_num = cursor_num
        self.__ad_downloader = ad_downloader
        self.__queue = []
        self.__after_token = None
        self.__process_new_response(response)

    def __repr__(self):
        return str(self.__queue)

    def __len__(self):
        return len(self.__queue)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.__queue and not self.__load_next_page():
            raise StopIteration()

        return self.__queue.pop(0)

    def __getitem__(self, index):
        return self.__queue[index]

    def __process_new_response(self, response):
        """ [Hidden method]
        Add new API response to the cursor queue (first download and add to response ad elements if needed).
        Stores the "after_token" (if any) to be able to query the following records from API.
        """
        if "data" in response:
            new_batch = [ObjectParser(**row) for row in response["data"]]
            if self.__ad_downloader:
                new_batch = asyncio.run(self.__ad_downloader.download_from_new_batch(new_batch))
            self.__queue += new_batch
        if (
                'paging' in response and
                'cursors' in response['paging'] and
                'after' in response['paging']['cursors'] and
                'next' in response['paging']
        ):
            self.__after_token = response["paging"]["cursors"]["after"]
        else:
            self.__after_token = None

    def __load_next_page(self):
        """ [Hidden method]
        Queries server for more nodes and loads them into the internal queue.

        Returns:
            True if successful, else False.
        """

        if not self.__after_token:
            return False

        session = self.__api.get_cursor_session(self.__cursor_num)
        if session:
            session.update_params({"after": self.__after_token})
            platform_response = self.__api.call(session)
            self.__process_new_response(platform_response.json())

        return len(self.__queue) > 0


"""
Enum classes: 
    Used to check given parameters for each platform session class
"""


class HttpMethod(Enum):
    """
    Available HTTP methods (cf https://en.wikipedia.org/wiki/HTTP#Request_methods)
    """
    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    CONNECT = "CONNECT"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    PATCH = "PATCH"

    @classmethod
    def check_method(cls, method):
        valid_methods = [member.value for member in cls]
        if method not in valid_methods:
            # To update
            raise ValueError(
                f"""{method} is not a valid HTTP method."""
                f"""It should be one of the following: {valid_methods}"""
            )


"""
Some useful functions.
"""


def json_encode_top_level_param(params):
    """
    Encodes certain types of values in the `params` dictionary into JSON format.

    Args:
        params: A dictionary containing the parameters to encode.

    Returns:
        A dictionary with some parameters encoded in JSON.
    """
    # Create a copy of the parameters to avoid modifying the original
    params = params.copy()

    # Iterate over each key-value pair in the dictionary
    for param, value in params.items():
        # Check if the value is a collection type or a boolean, while ensuring it's not a string
        if isinstance(value, (dict, list, tuple, bool)) and not isinstance(value, str):
            # Encode the value as a JSON string with sorted keys and no unnecessary spaces
            params[param] = json.dumps(
                value,
                sort_keys=True,
                separators=(',', ':'),  # Use compact separators to minimize string size
            )
        else:
            # Leave the value unchanged if it doesn't match the types eligible for JSON encoding
            params[param] = value

    return params
