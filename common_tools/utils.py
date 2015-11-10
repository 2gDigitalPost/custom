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


def get_project_setting(key, search_type=None, server=None, return_raw=False, additional_filters=None):
    """Get a setting from the config/prod_setting table. The type of the return value
    depends on the type of the project setting: string -> str, sequence -> list, map -> dict
    In the future I would like to implement int, float, and bool values as well.

    Note: there is also the ProdSetting in pyasm.prod.biz,
    but it doesn't work on client machines.
    color_dict = ProdSetting.get_dict_by_key('status_color_map')

    :param key: the key for the setting you want to get
    :param search_type: an optional search type filter
    :param server: a TacticServerStub object
    :param return_raw: bool to return the string instead of list, dict, etc.
    :param additional_filters: a list of additional filters to apply
    :return: the project setting for the specified key
    """
    if not server:
        server = get_server()

    filters = [('key', key)]
    if search_type:
        filters.append(('search_type', search_type))
    if additional_filters:
        filters.extend(additional_filters)

    setting = server.query('config/prod_setting', filters=filters)
    if not setting:
        return None
    elif len(setting) > 1:
        # You can't have multiple settings with the same key
        raise Exception("Multiple settings found with key [{0}]. You may need to pass a search type.".format(key))
    elif return_raw:
        return setting[0].get('value')

    value_string = setting[0].get('value')
    value_type = setting[0].get('type')
    if value_type == 'sequence':
        return value_string.split('|')
    elif value_type == 'map':
        # I would like this to be an OrderedDict, but I can't figure out how to
        # update to python 2.7, there's nothing in the docs or forums
        pairs = value_string.split('|')
        setting_dict = {}
        for pair in pairs:
            try:
                k, v = pair.split(':')
                setting_dict[k] = v
            except Exception as e:
                print "Cannot convert project setting [{0}] into a dictionary.".format(key)
                raise e
        return setting_dict
    else:
        # If the type is 'string' or anything else
        return value_string


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


def replace_non_ascii_characters(string):
    """Replace the illegal characters with their ascii equivalent.

    :param string: the input string to replace
    :return: the new string with fixed ascii characters
    """
    replace_dict = {u'\u2018': "'", u'\u2019': "'", u'\u201c': '"', u'\u201d': '"',
                    u'\xa0': u' ', u'\u2013': '-', u'\u2014': '-'}
    fixed_string = replace_multiple(string, replace_dict)
    return fixed_string


def fix_date(date):
    # This is needed due to the way Tactic deals with dates (using timezone info), post v4.0
    from pyasm.common import SPTDate
    return_date = ''
    date_obj = SPTDate.convert_to_local(date)
    if date_obj not in [None, '']:
        return_date = date_obj.strftime("%Y-%m-%d  %H:%M")
    return return_date


def fix_message_characters(message):
    """Fixes the escaped characters and replaces them with equivalents
    that are formatted for html.

    :param message: the message as a string
    :return: the html-formatted string
    """
    if isinstance(message, bool):
        return str(message)

    import sys
    from json import dumps as jsondumps
    if message not in [None, '']:
        if sys.stdout.encoding:
            message = message.decode(sys.stdout.encoding)
    message = jsondumps(message)

    tab = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
    newline = '<br/>'
    # OrderedDict does not exist in python 2.6, so do this the long way for now
    message = message.replace('||t', tab)
    message = message.replace('\\\\t', tab)
    message = message.replace('\\\t', tab)
    message = message.replace('\\t', tab)
    message = message.replace('\t', tab)
    message = message.replace('||n', newline)
    message = message.replace('\\\\n', newline)
    message = message.replace('\\\n', newline)
    message = message.replace('\\n', newline)
    message = message.replace('\n', newline)
    message = message.replace('\\"', '"')
    message = message.replace('\"', '"')

    return message


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


def get_base_url(server=None, project='twog'):
    """
    Gets the base url for tactic. This would be used to get the
    beginning of a custom url (like for the order_builder).

    Note: the server from the browser already has .2gdigital.com

    :param server: a TacticServerStub object
    :param project: the project as a string
    :return: the base url as a string
    """
    if not server:
        server = get_server()

    url = 'http://{0}/tactic/{1}/'.format(server.server_name, project)
    return url


def get_edit_wdg_from_search_key(search_key, server=None, project='twog'):
    """
    Convenience function for getting the edit widget url from a search key.

    Ex. get_edit_wdg_from_search_key('twog/source?project=twog&code=SOURCE178165')
    -> 'http://tactic01.2gdigital.com/tactic/twog/sobject/twog/source/SOURCE178165'

    :param search_key: the search key of an sobject
    :param server: a tactic server stub object
    :param project: the project as a string
    :return: a url to the sobject's view
    """
    search_type = search_key.split('?')[0]
    sobject_code = search_key.split('code=')[1]
    return get_edit_wdg_url(search_type, sobject_code, server, project)


def get_edit_wdg_url(search_type, sobject_code, server=None, project='twog'):
    """
    Gets the url for the view/edit widget

    Ex. get_edit_wdg_url('twog/title', 'TITLE1337')
    -> 'http://tactic01.2gdigital.com/tactic/twog/sobject/twog/title/TITLE1337'

    :param search_type: the tactic search type
    :param sobject_code: the sobject's code
    :param server: a tactic server stub object
    :param project: the project as a string
    :return: a url to the sobject's view
    """
    if not server:
        server = get_server()

    base_url = get_base_url(server, project)
    return "{0}sobject/{1}/{2}".format(base_url, search_type, sobject_code)


def get_edit_wdg_hyperlink(search_type, sobject_code, sobject_name='', server=None, project='twog'):
    """
    Convenience function to get the hyperlink for the view/edit widget.

    Ex. get_edit_wdg_url('twog/title', 'TITLE1337', 'Awesome Movie')
    -> '<a href="http://tactic01.2gdigital.com/tactic/twog/sobject/twog/title/TITLE1337">Awesome Movie</a>'

    :param search_type: the tactic search type
    :param sobject_code: the sobject's code
    :param sobject_name: the name of the sobject, to use for the link
    :param server: a tactic server stub object
    :param project: the project as a string
    :return: a url to the sobject's view
    """
    if not server:
        server = get_server()

    href = '<a href="{0}">{1}</a>'
    url = get_edit_wdg_url(search_type, sobject_code, server=server, project=project)
    if not sobject_name:
        sobject_name = sobject_code

    return href.format(url, sobject_name)


def get_order_builder_url(order_code, server=None, project='twog'):
    """
    Gets the order builder url for the given order code.
    Note that this does not format it as a hyperlink.

    Ex. get_order_builder_url('ORDER12345')
    -> 'http://tactic01.2gdigital.com/tactic/twog/order_builder/ORDER12345'

    :param order_code: the order code as a string
    :param server: a tactic server stub object
    :param project: the project as a string
    :return: a url to the order builder page
    """
    if not server:
        server = get_server()

    base_url = get_base_url(server, project)
    return "{0}order_builder/{1}".format(base_url, order_code)
