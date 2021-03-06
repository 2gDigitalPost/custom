"""
This file was generated automatically from a custom script found in Project -> Script Editor.
The custom script was moved to a file so that it could be integrated with GitHub.
"""

__author__ = 'Topher.Hughes'
__date__ = '04/08/2015'

import traceback


def main(server=None, input=None):
    """
    The main function of the custom script. The entire script was copied
    and pasted into the body of the try statement in order to add some
    error handling. It's all legacy code, so edit with caution.

    :param server: the TacticServerStub object
    :param input: a dict with data like like search_key, search_type, sobject, and update_data
    :return: None
    """
    if not input:
        input = {}

    try:
        # CUSTOM_SCRIPT00095
        if 'update_data' in input.keys():
            update_data = input.get('update_data') 
            if 'status_triggers' in update_data.keys():
                status_triggers = update_data.get('status_triggers')
                title = input.get('sobject')
                title_code = title.get('code')
                projs = server.eval("@SOBJECT(twog/proj['title_code','%s'])" % title_code)
                for proj in projs:
                    server.update(proj.get('__search_key__'), {'status_triggers': status_triggers})
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
