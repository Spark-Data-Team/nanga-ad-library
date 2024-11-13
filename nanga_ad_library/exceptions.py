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
        self._message = message
        self._request_context = request_context
        self._http_status = http_status
        self._http_headers = http_headers
        try:
            self._body = json.loads(body)
        except (TypeError, ValueError):
            self._body = body

        self._api_error_code = None
        self._api_error_type = None
        self._api_error_message = None
        self._api_error_subcode = None
        self._api_blame_field_specs = None
        self._api_transient_error = False

        if self._body and 'error' in self._body:
            self._error = self._body['error']
            error_data = self._error.get('error_data', str({}))
            if not isinstance(error_data, dict):
                error_data = json.loads(error_data)
            if 'message' in self._error:
                self._api_error_message = self._error['message']
            if 'code' in self._error:
                self._api_error_code = self._error['code']
            if 'is_transient' in self._error:
                self._api_transient_error = self._error['is_transient']
            if 'error_subcode' in self._error:
                self._api_error_subcode = self._error['error_subcode']
            if 'type' in self._error:
                self._api_error_type = self._error['type']
            if isinstance(error_data, dict) and error_data.get('blame_field_specs'):
                self._api_blame_field_specs = \
                    error_data['blame_field_specs']
        else:
            self._error = None

        # We do not want to print the file bytes
        request = self._request_context
        if 'files' in self._request_context:
            request = self._request_context.copy()
            del request['files']

        super(PlatformRequestError, self).__init__(
            "\n\n" +
            "  Message: %s\n" % self._message +
            "  Method:  %s\n" % request.get('method') +
            "  Path:    %s\n" % request.get('path', '/') +
            "  Params:  %s\n" % request.get('params') +
            "\n" +
            "  Status:  %s\n" % self._http_status +
            "  Response:\n    %s" % re.sub(
                r"\n", "\n    ",
                json.dumps(self._body, indent=2)
            ) +
            "\n"
        )

    def request_context(self):
        return self._request_context

    def http_status(self):
        return self._http_status

    def http_headers(self):
        return self._http_headers

    def body(self):
        return self._body

    def api_error_message(self):
        return self._api_error_message

    def api_error_code(self):
        return self._api_error_code

    def api_error_subcode(self):
        return self._api_error_subcode

    def api_error_type(self):
        return self._api_error_type

    def api_blame_field_specs(self):
        return self._api_blame_field_specs

    def api_transient_error(self):
        return self._api_transient_error

    def get_message(self):
        return self._message
