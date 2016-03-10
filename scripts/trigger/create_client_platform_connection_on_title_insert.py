import traceback


def main(server=None, trigger_input=None):
    """
    :param server: the TacticServerStub object
    :param trigger_input: a dict with data like like search_key, search_type, sobject, and update_data
    :return: None
    """
    if not trigger_input:
        trigger_input = {}

    try:
        print("BEFORE IMPORT")
        from pyasm.search import Search
        print("PLEASE DO SOMETHING")

        sob = trigger_input.get('sobject')
        client_code = sob.get('client_code')
        platform = sob.get('platform')

        platform_id_search = Search("twog/platform")
        platform_id_search.add_filter('name', platform)
        platform_search_object = platform_id_search.get_sobject()
        platform_code = platform_search_object.get_value('code')

        client_name_search = Search("twog/client")
        client_name_search.add_filter('code', client_code)
        client_name = client_name_search.get_sobject().get_value('name')

        client_platform_connection_search = Search("twog/client_platform")
        client_platform_connection_search.add_filter('client_code', client_code)
        client_platform_connection_search.add_filter('platform_code', platform_code)
        client_platform_connection = client_platform_connection_search.get_sobject()

        if not client_platform_connection:
            # Entry in twog/client_platform does not exist; create it
            server.insert('twog/client_platform', {'client_code': client_code, 'platform_code': platform_code,
                                                   'name': '{0} to {1}'.format(client_name, platform),
                                                   'connection_status': 'disconnected'})
    except AttributeError as e:
        traceback.print_exc()
        print str(e) + '\nMost likely the server object does not exist.'
        raise e
    except KeyError as e:
        traceback.print_exc()
        print str(e) + '\nMost likely the input dictionary does not exist.'
        raise e
    except Exception as e:
        traceback.print_exc()
        print str(e)
        raise e


if __name__ == '__main__':
    main()
