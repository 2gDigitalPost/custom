from pyasm.search import Search


def create_client_platform(server, client_code, platform):
    """
    On the insert|twog/title event, search for an existing connection from the title's client to platform.
    If no entry exists in the twog/client_platform table, create it by inserting the client_code, platform_code,
    a name, and a connection_status set to 'disconnected'.

    :param server: the TacticServerStub object
    :param trigger_input: a dict with data like like search_key, search_type, sobject, and update_data
    :return: None
    """

    # The platform_code we need is not included in the Title sobject. We have to query for it using the platform name.
    platform_code_search = Search("twog/platform")
    platform_code_search.add_filter('name', platform)
    platform_search_object = platform_code_search.get_sobject()
    platform_code = platform_search_object.get_value('code')

    # Using the client_code and platform_code, search for an existing entry.
    client_platform_connection_search = Search("twog/client_platform")
    client_platform_connection_search.add_filter('client_code', client_code)
    client_platform_connection_search.add_filter('platform_code', platform_code)
    client_platform_connection = client_platform_connection_search.get_sobject()

    # If the twog/client_platform is not found, create it. If it already exists, then nothing happens.
    if not client_platform_connection:
        # Using the client_code, get the client name (needed for the 'name' column data).
        client_name_search = Search("twog/client")
        client_name_search.add_filter('code', client_code)
        client_name = client_name_search.get_sobject().get_value('name')

        # Finally, insert the entry into the twog/client_platform table.
        server.insert('twog/client_platform', {'client_code': client_code, 'platform_code': platform_code,
                                               'name': '{0} to {1}'.format(client_name, platform),
                                               'connection_status': 'disconnected'})
