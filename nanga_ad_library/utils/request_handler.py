import os
import json
import random

from enum import Enum

from nanga_ad_library.exceptions import PlatformRequestError

"""
Useful classes and functions to make http requests and handle their responses.
"""


class PlatformResponse:

    """
    Encapsulates a http response from the nanga Ad Library API.
    """

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


class UserAgent:

    """
    Generates a realistic User Agent that can be later used in web requests.
    """

    USER_AGENTS_FILENAME = "user_agents.txt"

    def __init__(self):
        """Nothing to do at first"""

    def pick(self):
        """
        Pick a user agent from a list stored in user_agents.txt
            (file source is https://gist.github.com/pzb/b4b6f57144aea7827ae4)
        """

        # Find file path
        repo_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(repo_dir, self.USER_AGENTS_FILENAME)

        # Open file and pick a random user-agent
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                user_agents = [line.strip() for line in file if line.strip()]
            return random.choice(user_agents) if user_agents else None
        except:
            return None


# ~~~~  Other useful functions  ~~~~
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



