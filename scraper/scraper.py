"""
This module contains two functions that are needed for order_associator.py
Originally they were split up into two different classes (for no apparent reason). One of those classes was deleted,
since it didn't do anything. The other class is ImdbOrderAssociatorWdg, in order_associator

These functions don't rely on anything in ImdbOrderAssociatorWdg, it only passes them a string. They may also be
useful for other classes or functions, since they just parse a string returned from the imdb scraping script.
Therefore, they've been moved here rather than kept in ImdbOrderAssociatorWdg.
"""

import subprocess


def parse_scraper_string(input_string):
    """
    Take a string returned from runner.php and parse it into a list.

    :param input_string: String returned from runner.php script
    :return: List (of dictionaries)

    Originally written by MTM, edited by Tyler Standridge
    """

    titles_chunked = input_string.strip().split('-MTM_TITLE_MTM-')
    title_array = []

    # TODO: As is, this returns a massive list of massive dictionaries. Surely we need only to look for some
    # information rather than returning ALL of it...
    for title in titles_chunked:
        if len(title) > 0:
            title_dict = {}
            subarrays = title.split(':-MTM-SUBARRAY-:')

            for subarray in subarrays:
                if len(subarray) > 0:
                    array_s = subarray.split(':-::MTM::-')
                    array_name = array_s[0]
                    array_remainder = array_s[1]
                    title_dict[array_name] = {}
                    subfields = array_remainder.split(':-MTM-FIELD-:')

                    for chunk in subfields:
                        if len(chunk) > 0:
                            chunk_s = chunk.split('=>')
                            subfield = chunk_s[0]
                            subval = chunk_s[1]
                            title_dict[array_name][subfield] = subval

            title_array.append(title_dict)
    return title_array


def get_multiple_title_info(title_of_show):
    """
    Take the title of a show or movie, and call the IMDB script with subprocess.Popen. The function should wait
    until the script is finished, and then pass the resulting string into the parse_scraper_string function,
    then return the list.

    :param title_of_show: String corresponding to the title you want to search for
    :return: List

    Originally written by MTM, edited by Tyler Standridge
    """

    # TODO: There HAS to be a way to refactor this script. The string it returns is absurdly long, and we only
    # need a small portion of the returned information.
    process = subprocess.Popen('''php /opt/spt/custom/scraper/runner.php "%s"''' % title_of_show, shell=True,
                               stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    delimited_str, stderr = process.communicate()

    if 'No Titles Found' in delimited_str or delimited_str in [None, '']:
        info = []
    else:
        info = parse_scraper_string(delimited_str)

    return info
