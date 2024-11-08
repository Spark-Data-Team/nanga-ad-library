import os
import re
import warnings

from nanga_ad_library.utils.ad_libraries_config import platforms_api_versions

"""
Deals with APIs versions and SDK version
"""


def check_version_format(version: str):
    """
    Check that the provided version is matching the standard pattern (v12.34 for instance)

    :param version: The string to check: must match the standard pattern.
    :raise:
        Raise a ValueError if the provided version is not matching the standard pattern for API versions.
    """

    # Use the version regexp to check if the provided version string is matching the pattern
    version_regexp = r"v\d+\.\d+"

    if not re.match(version_regexp, version):
        # To update
        raise ValueError(
            f"""The provided string ({version}) is not matching the standard pattern for API versions."""
        )


def compare_version_to_default(required_version: str, default_version: str):
    """
    Check that the version the user asked for is anterior or equal to the latest version used in the SDK.

    :param required_version: The version required by the user.
    :param default_version: The version stored in api_config file.
    :return:
        The version the user asked for if it is consistent with the default version stored.
        Else raise a warning and return the default version.
    """

    # Use the version regexp to split each version in two parts
    version_regexp = r"v(\d+)\.(\d+)"

    # Split versions
    req_match = re.match(version_regexp, required_version)
    def_match = re.match(version_regexp, default_version)

    # Check if the user's version is anterior or equal to the stored version
    final_version = required_version
    if req_match and def_match:
        main_req_v, main_def_v = int(req_match.group(1)), int(def_match.group(1))
        # Compare the main part of each version to know if required version is valid
        if main_req_v >= main_def_v:
            error_found = True
            # Compare then the secondary part of each version
            if main_req_v == main_def_v:
                sec_req_v, sec_def_v = int(req_match.group(2)), int(def_match.group(2))
                if sec_req_v <= sec_def_v:
                    error_found = False

            # If required version is more recent than the one stored as default, use the default one and raise a warning
            if error_found:
                final_version = default_version
                # To update ?
                warnings.warn(
                    f"""The latest available API version is {default_version}, you asked for a more recent one."""
                    f"""{default_version} will be used to make requests to the API."""
                )

    else:
        wrong_version = required_version if not req_match else default_version
        # To update
        raise ValueError(
            f"""{wrong_version} is not matching the standard API version pattern."""
        )

    return final_version


def get_default_api_version(api_name: str):
    """
    Retrieve the latest API version from ad_libraries_config file using api_name.

    :param api_name: Name of the platform API.
    :return:
        The version of the API stored in ad_libraries_config file.
    """

    # Extract API version from platforms_api_versions dict
    version = platforms_api_versions.get(api_name)

    # Check that the stored version is valid
    if not version:
        # To update
        raise ValueError(
            f"""Cannot find '{api_name}' API version in ad_libraries_config file."""
        )
    else:
        check_version_format(version)

    return version


def get_sdk_version():
    """
    Retrieve the version of the SDK from __init__ file.

    :return:
        The stored version of the SDK.
    """

    # Retrieve __init__ repo file
    this_dir = os.path.dirname(__file__)
    package_init_filename = os.path.join(this_dir, '../__init__.py')

    # Extract __version__ from the init file
    version = None
    with open(package_init_filename, 'r') as handle:
        file_content = handle.read()
        version = re.search(
            r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
            file_content, re.MULTILINE
        ).group(1)

    # Check that the stored version is valid
    if not version:
        # To update
        raise ValueError(
            """Cannot find SDK version in __init__ file."""
        )
    else:
        check_version_format(version)

    return version
