"""
This file was generated automatically from a custom script found in Project -> Script Editor.
The custom script was moved to a file so that it could be integrated with GitHub.
"""

__author__ = 'Topher.Hughes'
__date__ = '04/08/2015'

import traceback
import common_tools.utils as ctu


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
        # CUSTOM_SCRIPT00060
        # Matthew Tyler Misenhimer
        # This was made to report by email that a new order has been inserted
        # Do not send external if location is internal

        import os
        from pyasm.common import Environment
        from pyasm.common import SPTDate
        from formatted_emailer import EmailDirections, email_sender
        allow_client_emails = True
        internal_template_file = '/opt/spt/custom/formatted_emailer/order_inserted_email_template.html'
        external_template_file = '/opt/spt/custom/formatted_emailer/external_email_template.html'
        order = input.get('sobject')
        order_code = order.get('code')
        client = order.get('client_code')
        if client not in [None, '']:
            # Get the valid recipients for this work, both internal and external
            ed = EmailDirections(order_code=order_code)
            int_data = ed.get_internal_data()
            subject = '2G-ORDER-CREATED-"%s" PO#: %s' % (int_data['order_name'], int_data['po_number'])
            subject_see = subject
            subject = subject.replace(' ', '..')
            initial_po_upload_list = order.get('initial_po_upload_list')
            message = '%s has uploaded a new PO.' % int_data['from_name'].replace('.', ' ')
            # The initial po upload list was created to handle uploads by clients,
            # as the files will not exist for querying until after this trigger has been run.
            # These are the files the client uploaded to the order,
            # inserted into the initial_po_upload_list after being selected by the client
            if initial_po_upload_list not in [None, '']:
                message = '%s<br/>Uploaded PO File: %s' % (message, initial_po_upload_list)
            message = ctu.fix_message_characters(message)

            int_data['subject'] = subject
            int_data['message'] = message
            int_data['start_date'] = ctu.fix_date(int_data['start_date'])
            int_data['due_date'] = ctu.fix_date(int_data['due_date'])

            email_sender.send_email(template=internal_template_file, email_data=int_data,
                                    email_file_name='int_order_inserted_{0}.html'.format(order_code), server=server)

            if int_data['location'] == 'external' and allow_client_emails:
                ext_data = ed.get_external_data()
                # Open the external template file and create a new file to send as email
                template = open(external_template_file, 'r')
                filled = ''
                for line in template:
                    line = line.replace('[ORDER_CODE]', ext_data['order_code'])
                    line = line.replace('[PO_NUMBER]', ext_data['po_number'])
                    line = line.replace('[CLIENT_EMAIL]', ext_data['client_email'])
                    line = line.replace('[EMAIL_CC_LIST]', ext_data['ext_ccs'])
                    line = line.replace('[SCHEDULER_EMAIL]', ext_data['scheduler_email'])
                    line = line.replace('[SUBJECT]', subject_see)
                    line = line.replace('[MESSAGE]', message)
                    line = line.replace('[CLIENT]', ext_data['client_name'])
                    line = line.replace('[CLIENT_LOGIN]', ext_data['client_login'])
                    line = line.replace('[ORDER_NAME]', ext_data['order_name'])
                    line = line.replace('[START_DATE]', ctu.fix_date(ext_data['start_date']))
                    line = line.replace('[DUE_DATE]', ctu.fix_date(ext_data['due_date']))
                    filled = '%s%s' % (filled, line)
                template.close()
                filled_in_email = '/var/www/html/formatted_emails/ext_order_inserted_%s.html' % order_code
                filler = open(filled_in_email, 'w')
                filler.write(filled)
                filler.close()
                # Send the External Email
                the_command = "php /opt/spt/custom/formatted_emailer/inserted_order_email.php '''%s''' '''%s''' '''%s''' '''%s''' '''%s''' '''%s'''" % (filled_in_email, ext_data['to_email'], ext_data['from_email'], ext_data['from_name'], subject, ext_data['ccs'].replace(';','#Xs*'))
                os.system(the_command)
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
