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


class UserAgentGenerator:

    """
        Generates a realistic User Agent that can be later used in web requests.
    """

    # Store hardcoded list of elements to use in User Agent random generation
    OS_COMPATIBILITIES = {
        'Windows': ['Chrome', 'Edge', 'Opera', 'Firefox'],
        'MacOS': ['Chrome', 'Safari', 'Opera', 'Firefox'],
        'Linux': ['Chrome', 'Opera', 'Firefox'],
        'Android': ['Chrome', 'Opera', 'Firefox'],
        'iOS': ['Safari'],
    }
    USER_AGENT_TEMPLATES = {
        'Chrome': {
            'Windows': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36',
            'MacOS': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36',
            'Linux': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36',
            'Android': 'Mozilla/5.0 (Linux; Android {version}; Nexus 5 Build/{build}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Mobile Safari/537.36',
        },
        'Edge': {
            'Windows': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Edge/{edge_version} Safari/537.36',
        },
        'Opera': {
            'Windows': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Opera/{opera_version} Safari/537.36',
            'Linux': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Opera/{opera_version} Safari/537.36',
        },
        'Firefox': {
            'Windows': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{version}) Gecko/{gecko_version} Firefox/{version}',
            'MacOS': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:{version}) Gecko/{gecko_version} Firefox/{version}',
            'Linux': 'Mozilla/5.0 (X11; Linux x86_64; rv:{version}) Gecko/{gecko_version} Firefox/{version}',
            'Android': 'Mozilla/5.0 (Android {version}; Mobile; rv:{version}) Gecko/{gecko_version} Firefox/{version}',
        },
        'Safari': {
            'MacOS': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/{version} Safari/537.36',
            'iOS': 'Mozilla/5.0 (iPhone; CPU iPhone OS {version} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/{version} Safari/537.36',
        },
    }
    BROWSER_VERSIONS = {
        'Chrome': ['90.0.4430.93', '91.0.4472.124', '92.0.4515.131', '93.0.4577.82'],
        'Edge': ['90.0.818.62', '91.0.864.48', '92.0.902.67', '93.0.961.52'],
        'Opera': ['75.0.3969.243', '76.0.4017.186', '77.0.4054.273', '78.0.4093.98'],
        'Firefox': ['88.0', '89.0', '90.0', '91.0'],
        'Safari': ['14.0', '14.1', '15.0', '15.1'],
    }

    def __init__(self):
        """
        Generates a "unique" User Agent object by randomly combining available os, browsers and engines.
        """
        # Randomly choose an OS and compatible browser and version
        os = random.choice(list(self.OS_COMPATIBILITIES.keys()))
        browser = random.choice(self.OS_COMPATIBILITIES[os])
        version = random.choice(self.BROWSER_VERSIONS[browser])

        # Select a User Agent template compatible with the chosen OS
        template = self.USER_AGENT_TEMPLATES[browser].get(os)

        # Generate final User Agent
        if browser == 'Edge':
            edge_version = version.split('.')[0]
            self.user_agent = template.format(version=version, edge_version=edge_version)
        elif browser == 'Opera':
            opera_version = version.split('.')[0]
            self.user_agent = template.format(version=version, opera_version=opera_version)
        elif browser == 'Firefox':
            gecko_version = version.split('.')[0]
            self.user_agent = template.format(version=version, gecko_version=gecko_version)
        elif browser == 'Safari':
            self.user_agent = template.format(version=version)
        else:
            self.user_agent = template.format(version=version)


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



