from dateutil import parser

"""
Checks parameters validity and return transformed parameter when needed.
"""


def check_param_value(param: str, value: str, accepted_values: list, is_list: bool):
    """
    Checks that the parameter value is one of the expected value (platform Ad Library API request).

    Args:
        param: Parameter name (used to query platform API).
        value: Parameter value.
        accepted_values: List of accepted values for this param.
        is_list: Indicates if the param value is expected to be a list.
            If True checks that all elements are one of the expected value.

    Raises:
        ValueError if parameter value is not available.
    """
    # Stringify the list of accepted values (to display in error if needed)
    accepted_values_str = "\n\t- ".join(accepted_values)

    # For lists, check that all elements are of one of the expected types
    if is_list:
        # Check if value really is a list
        if isinstance(value, list):
            # Check that all elements are of one of the expected types
            if accepted_values and not all([x in accepted_values for x in value]):
                # TO UPDATE
                raise ValueError(
                    f"""{value} is not a valid value for parameter {param}.\n"""
                    f"""It should be a list of elements from the following:"""
                    f"""\n\t- {accepted_values_str}"""
                )
        else:
            # TO UPDATE
            raise ValueError(
                f"""'{value}' is not a valid value for parameter {param}.\n"""
                f"""It should be a list."""
            )
    # Else check that value is of one of the expected types
    elif accepted_values and value not in accepted_values:
        # TO UPDATE
        raise ValueError(
            f"""'{value}' is not a valid value for parameter {param}.\n"""
            f"""It's type should be one of the following:"""
            f"""\n\t- {accepted_values_str}."""
        )


def check_param_type(param: str, value: str, types: tuple, is_list: bool):
    """
    Checks that the parameter value is of one of the expected types (platform Ad Library API request).

    Args:
        param: Parameter name (used to query platform API).
        value: Parameter value.
        types: Expected types of the param value.
            If empty then all types are accepted.
        is_list: Indicates if the param value is expected to be a list.
            If True checks that all elements are of one of the expected types.

    Raises:
        ValueError if parameter value is not available.
    """

    # For lists, check that all elements are of one of the expected types
    if is_list:
        # Check if value really is a list
        if isinstance(value, list):
            # Check that all elements are of one of the expected types
            if types and not all([isinstance(x, types) for x in value]):
                # TO UPDATE
                raise ValueError(
                    f"""{value} is not a valid value for parameter {param}.\n"""
                    f"""It should be a list of elements which type is one of the following: {types}."""
                )
        else:
            # TO UPDATE
            raise ValueError(
                f"""'{value}' is not a valid value for parameter {param}.\n"""
                f"""It should be a list."""
            )
    # Else check that value is of one of the expected types
    elif types and not isinstance(value, types):
        # TO UPDATE
        raise ValueError(
            f"""'{value}' is not a valid value for parameter {param}.\n"""
            f"""It's type should be one of the following: {types}."""
        )


def enforce_date_param_format(param: str, value: str, date_format="%Y-%m-%d"):
    """
    Checks that the parameter value is a valid date and format it using date_format.

    Args:
        param: Parameter name (used to query platform API).
        value: Parameter value.
        date_format: Date format expected in the API.

    Returns:
        The date string to use in request (reformatted using date_format format if needed).

    Raises:
        ValueError if parameter value is not available.
    """

    try:
        # Try to parse the given date string (used format is not known but needs to be standard)
        dt = parser.parse(value)

        return dt.strftime(date_format)

    except:
        # TO UPDATE
        raise ValueError(
            f"""'{value}' is not a valid value for parameter {param}.\n"""
            f"""It should be a date string using standard format."""
        )
