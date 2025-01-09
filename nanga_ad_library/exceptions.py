"""
The exceptions module contains Exception subclasses whose instances might be
raised.
"""

import json
import re


class PlatformError(Exception):
    """
    All errors specific to platforms api (Meta, Tiktok, ...) requests will be
    subclassed from PlatformError which is subclassed from Exception.
    """
    pass


class PlatformRequestError(PlatformError):
    """
    Raised when an api request fails. Returned by raise_for_status() method on a
    PlatformResponse object returned through a callback function (relevant
    only for failure callbacks) if not raised at the core api call method.
    """

    def __init__(
        self, message,
        request_context,
        http_status,
        http_headers,
        body
    ):
        self.__message = message
        self.__request_context = request_context
        self.__http_status = http_status
        self.__http_headers = http_headers
        try:
            self.__body = json.loads(body)
        except (TypeError, ValueError):
            self.__body = body

        self.__api_error_code = None
        self.__api_error_type = None
        self.__api_error_message = None
        self.__api_error_subcode = None
        self.__api_blame_field_specs = None
        self.__api_transient_error = False

        if self.__body and 'error' in self.__body:
            self.__error = self.__body['error']
            error_data = self.__error.get('error_data', str({}))
            if not isinstance(error_data, dict):
                error_data = json.loads(error_data)
            if 'message' in self.__error:
                self.__api_error_message = self.__error['message']
            if 'code' in self.__error:
                self.__api_error_code = self.__error['code']
            if 'is_transient' in self.__error:
                self.__api_transient_error = self.__error['is_transient']
            if 'error_subcode' in self.__error:
                self.__api_error_subcode = self.__error['error_subcode']
            if 'type' in self.__error:
                self.__api_error_type = self.__error['type']
            if isinstance(error_data, dict) and error_data.get('blame_field_specs'):
                self.__api_blame_field_specs = \
                    error_data['blame_field_specs']
        else:
            self.__error = None

        # We do not want to print the file bytes
        request = self.__request_context
        if 'files' in self.__request_context:
            request = self.__request_context.copy()
            del request['files']

        super(PlatformRequestError, self).__init__(
            "\n\n" +
            "  Message: %s\n" % self.__message +
            "  Method:  %s\n" % request.get('method') +
            "  Path:    %s\n" % request.get('path', '/') +
            "  Params:  %s\n" % request.get('params') +
            "\n" +
            "  Status:  %s\n" % self.__http_status +
            "  Response:\n    %s" % re.sub(
                r"\n", "\n    ",
                json.dumps(self.__body, indent=2)
            ) +
            "\n"
        )

    def request_context(self):
        return self.__request_context

    def http_status(self):
        return self.__http_status

    def http_headers(self):
        return self.__http_headers

    def body(self):
        return self.__body

    def api_error_message(self):
        return self.__api_error_message

    def api_error_code(self):
        return self.__api_error_code

    def api_error_subcode(self):
        return self.__api_error_subcode

    def api_error_type(self):
        return self.__api_error_type

    def api_blame_field_specs(self):
        return self.__api_blame_field_specs

    def api_transient_error(self):
        return self.__api_transient_error

    def get_message(self):
        return self.__message
