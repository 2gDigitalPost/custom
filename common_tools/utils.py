"""
Common utility functions for tactic.
"""

__author__ = 'topher.hughes'
__date__ = '02/09/2015'

from tactic_client_lib import tactic_server_stub


def get_server():
    """

    :return:
    """
    try:
        server = tactic_server_stub.TacticServerStub.get()
    except tactic_server_stub.TacticApiException as e:
        # TODO: get a server object some other way
        raise e

    return server


def get_project_setting(key, search_type=None, server=None):
    """

    :param key:
    :param search_type:
    :return:
    """
    if not server:
        server = get_server()


def replace_multiple(string, rep_dict):
    """Does the equivalent of multiple string replaces all at once.
    Note that it's simultaneous and not in order.

    :param string: the string to replace
    :param rep_dict: dictionary of {'old': 'new'}
    :return: the new string with applied replaces
    """
    import re
    pattern = re.compile("|".join([re.escape(k) for k in rep_dict.keys()]), re.M)
    return pattern.sub(lambda x: rep_dict[x.group(0)], string)


def fix_date(date):
    # This is needed due to the way Tactic deals with dates (using timezone info), post v4.0
    from pyasm.common import SPTDate
    return_date = ''
    date_obj = SPTDate.convert_to_local(date)
    if date_obj not in [None, '']:
        return_date = date_obj.strftime("%Y-%m-%d  %H:%M")
    return return_date


def get_sobject_type(search_key):
    """Get the sobject type from the search key or search_type.
    This essentially strips the project and code, returning only
    the sobject's type, like 'order', 'title', 'proj', 'work_order'

    Ex. 'twog/order?project=twog&code=ORDER19297' will return 'order'

    :param search_key: an sobject search key
    :return: the sobject type as a string
    """
    sobject_type = search_key.split('?')[0].split('/')[1]
    return sobject_type
