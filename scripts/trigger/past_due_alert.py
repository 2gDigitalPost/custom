import traceback
from datetime import date, timedelta


def main(server=None, input=None):
    """
    :param server: the TacticServerStub object
    :param input: a dict with data like like search_key, search_type, sobject, and update_data
    :return: None
    """

    try:
        from formatted_emailer import EmailDirections, email_sender

        todays_date = date.today()
        one_week_ago = (todays_date - timedelta(days=7)).strftime('%Y-%m-%d')

        past_due_titles = server.eval("@SOBJECT(twog/title['expected_delivery_date', 'is before', '{0}']['expected_delivery_date', 'is after', '{1}'])".format(todays_date, one_week_ago))
        number_of_titles_past_due = len(past_due_titles)
        past_due_titles = [title.get('code') for title in past_due_titles]

        email_subject = 'There are {0} Titles that are past due'.format(number_of_titles_past_due)
        message = "The following titles are past due.<br/><br/>{0}<br/><br/>Please log into Tactic and change the " \
                  "due date on these Titles. If you don't know when that's supposed to be, you can just change it " \
                  "to today's date.".format(', '.join(past_due_titles))
        recipients = ['tyler.standridge@2gdigital.com']

        context_data = {
            'to_email': 'Tyler.Standridge@2gdigital.com',
            'subject': email_subject,
            'message': message,
            'from_email': 'Tyler.Standridge@2gdigital.com',
            'from_name': 'Tactic',
            'ccs': ';'.join(recipients)
        }

        internal_template_file = '/opt/spt/custom/formatted_emailer/templates/past_due_title_notification.html'

        if context_data['to_email']:
            email_file_name = 'past_due_title_notification_{0}.html'.format(todays_date)
            email_sender.send_email(template=internal_template_file, email_data=context_data,
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
