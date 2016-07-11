import traceback
from datetime import date

from pyasm.search import Search

from formatted_emailer import email_sender


def main(server=None, trigger_input=None):
    """
    :param server: the TacticServerStub object
    :param trigger_input: a dict with data like like search_key, search_type, sobject, and update_data
    :return: None
    """
    if not trigger_input:
        trigger_input = {}

    try:
        # Get the task
        task = trigger_input.get('sobject')

        # If this task is not a request to download a file, then skip the script
        # Not the prettiest way to make this happen, but I don't have any other ideas at the moment
        if 'Download:' not in task.get('process'):
            return

        # Only send the notification if the task is being marked as completed.
        if task.get('status') != 'Completed':
            return

        todays_date = date.today()

        # The title code should always be the last word in the process.
        download_task_name = task.get('process').split(': ')[-1]

        # Get the login id of the person who put in this request
        login = task.get('login')

        # Search for the person's data from the users table
        user_search = Search("sthpw/login")
        user_search.add_filter('login', login)
        user = user_search.get_sobject()

        # There should never be a case in which there's no user found, but you never know
        if user:
            # Email the user who put in the request
            email_address = user.get('email')

            email_template = '/opt/spt/custom/formatted_emailer/templates/generic_internal_message.html'

            context_data = {
                'to_email': email_address,
                'subject': 'Download Task "{0}" is complete'.format(download_task_name),
                'message': 'The download is now complete for task: {0}'.format(download_task_name),
                'from_email': 'TacticDebug@2gdigital.com',
                'from_name': 'Tactic',
            }

            email_file_name = 'past_due_title_notification_{0}.html'.format(todays_date)
            email_sender.send_email(template=email_template, email_data=context_data,
                                    email_file_name=email_file_name, server=server)

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
