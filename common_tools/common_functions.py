"""
A collection of functions that are used throughout the custom tactic modules.

The goal is to remove as much redundant functions from the custom directory as possible. Thanks to a certain someone,
there's a lot of that currently. Many functions are methods in classes when they clearly don't need to be. That's
what will be put in here for the most part.
"""

import datetime
from pyasm.common import SPTDate


def get_current_timestamp():
    """
    There are way too many classes that have a method called 'make_timestamp' (that all do the exact same thing: return
    the current timestamp). This function attempts to replace them.

    :return: A timestamp corresponding to the current time, in format "%Y-%m-%d %H:%M:%S"
    """

    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def title_case(string):
    """
    Replaces function in nighttime_hotlist2.BigBoardWdg2.camel_case()

    The function was a misnomer, it didn't camel case a string. Rather, it capitalized the first letter in each word
    of the string and lower cased the rest. This is used to display the column names in the "Hot Today" list.

    :param string: A string
    :return: A string with capitalized first letters
    """

    strings_list = string.split(' ')

    # Get a list of all the words, with the first letter capitalized and the rest lower cased
    title_case_strings = [each_string[0].upper() + each_string[1:].lower() for each_string in strings_list]

    # Join the list back on an empty space and return
    return ' '.join(title_case_strings)


def abbreviate_text(string, max_len):
    """
    Take a string and return an abbreviated version, cut off at max_len. Note that the "..." is factored into max_len.
    If the last character is a space, remove it.

    Examples:
    abbreviate_text("Testing this function", 8) => "Testing..."
    abbreviate_text("This is my example", 10) => "This is my..."

    :param string: A string
    :param max_len: The desired length for the abbreviated text
    :return:
    """

    if len(string) > max_len:
        abbreviated_string = string[:max_len]

        # Remove trailing space, if exists
        if abbreviated_string[-1] == ' ':
            abbreviated_string = abbreviated_string[:-1]

        return abbreviated_string + '...'
    else:
        return string


def fix_date(date):
    # TODO: Move this function to a separate file
    # This is needed due to the way Tactic deals with dates (using timezone info), post v4.0
    return_date = ''
    date_obj = SPTDate.convert_to_local(date)
    if date_obj not in [None, '']:
        return_date = date_obj.strftime("%Y-%m-%d  %H:%M")
    return return_date
