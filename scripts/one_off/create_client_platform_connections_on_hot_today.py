from tactic_client_lib import TacticServerStub
import ConfigParser
import argparse


def main(testing_flag):
    config = ConfigParser.ConfigParser()
    config.read('config.ini')

    # Get credentials from config file
    user = config.get('credentials', 'user')
    password = config.get('credentials', 'password')
    project = config.get('credentials', 'project')

    # If the testing flag is passed, use the test server, otherwise use the live server
    if testing_flag:
        url = config.get('server', 'test')
    else:
        url = config.get('server', 'live')

    # Get a server object to perform queries
    server = TacticServerStub(server=url, project=project, user=user, password=password)

    # Get titles marked as 'hot' items
    hot_titles = server.eval("@SOBJECT(twog/title['bigboard', 'True']['status', '!=', 'Completed'])")

    # Iterate through the titles, getting the client code and platform for each one
    for title in hot_titles:
        client_code = title.get('client_code')
        platform_name = title.get('platform')

        # Unfortunately, Titles hold the platform name, not the code, so a query has to be done to get that
        platform_code_search = server.eval("@SOBJECT(twog/platform['name', '{0}'])".format(platform_name))

        # This search returns a list (since multiple matches by 'name' is possible). Since this is just a quick, dirty
        # script to insert some example connections, we will take only the first result and ignore the rest.
        if platform_code_search:
            platform_code = platform_code_search[0].get('code')
        else:
            continue

        existing_connection_search = server.eval("@SOBJECT(twog/client_platform['client_code', '{0}']['platform_code', '{1}'])".format(client_code, platform_code))

        if not existing_connection_search:
            client_name_search = server.eval("@SOBJECT(twog/client['code', '{0}'])".format(client_code))

            if client_name_search:
                client_name = client_name_search[0].get('name')

                # Finally, insert the entry into the twog/client_platform table.
                server.insert('twog/client_platform', {'client_code': client_code, 'platform_code': platform_code,
                                                       'name': '{0} to {1}'.format(client_name, platform_name),
                                                       'connection_status': 'disconnected'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add some entries into the client_platform table, just to get it'
                                                 'started.')
    parser.add_argument('-t', '--testing', action='store_true')
    args = parser.parse_args()

    main(args.testing)
