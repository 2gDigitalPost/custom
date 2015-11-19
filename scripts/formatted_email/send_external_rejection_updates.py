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
        # CUSTOM_SCRIPT00103
        # Matthew Tyler Misenhimer
        # Sends an email when a External Rejection is updated

        import os, time
        from pyasm.common import Environment
        internal_template_file = '/opt/spt/custom/formatted_emailer/external_rejection_email_template.html'
        trigger_sobject = input.get('trigger_sobject')
        event = trigger_sobject.get('event')
        is_insert = False
        if 'insert' in event:
            is_insert = True
        if not is_insert:
            update_data = input.get('update_data', {})
            prev_data = input.get('prev_data', {})
            old_status = prev_data.get('status')
            new_status = update_data.get('status')
            if old_status == new_status or new_status != 'Closed':
                # Only send the email when the status changes to Closed
                return

            external_rejection = input.get('sobject')
            order_code = external_rejection.get('order_code')
            title_code = external_rejection.get('title_code')
        
            reported_issue = external_rejection.get('reported_issue')
            reported_issue = ctu.fix_message_characters(reported_issue.replace(' ', '&nbsp;'))
            
            rcnq = "@SOBJECT(sthpw/note['search_id','%s']['process','Root Cause']['search_type','twog/external_rejection?project=twog'])" % (external_rejection.get('id'))
            root_cause_notes = server.eval(rcnq)
            root_cause = ''
            for rc in root_cause_notes:
                root_cause = '%s\n%s -- %s\n<b>Note: %s</b>\n' % (root_cause, rc.get('login'), rc.get('timestamp').split('.')[0], rc.get('note'))
            root_cause = ctu.fix_message_characters(root_cause.replace(' ', '&nbsp;'))
        
            corrective_action_notes = server.eval("@SOBJECT(sthpw/note['search_id','%s']['process','Corrective Action']['search_type','twog/external_rejection?project=twog'])" % (external_rejection.get('id')))
            corrective_action = ''
            for ca in corrective_action_notes:
                corrective_action = '%s\n%s -- %s\n<b>Note:%s</b>\n' % (corrective_action, ca.get('login'), ca.get('timestamp').split('.')[0], ca.get('note'))
            corrective_action = ctu.fix_message_characters(corrective_action.replace(' ', '&nbsp;'))

            title = external_rejection.get('title')
            episode = external_rejection.get('episode')
            po_number = external_rejection.get('po_number')
            status = external_rejection.get('status')
            addressed_to = external_rejection.get('email_list')
            replacement_order_code = external_rejection.get('replacement_order_code')
            replacement_title_code = external_rejection.get('replacement_title_code')

            order_obj = server.eval("@SOBJECT(twog/order['code','%s'])" % order_code)
            scheduler = ''
            if order_obj:
                order_obj = order_obj[0]
                scheduler = order_obj.get('login')

            title_obj = server.eval("@SOBJECT(twog/title['code','%s'])" % title_code)
            title_due_date = ''
            title_expected_delivery = ''
            title_full_name = title
            if episode not in [None, '']:
                title_full_name = '%s: %s' % (title, episode)
            if title_obj:
                title_obj = title_obj[0]
                title_due_date = title_obj.get('due_date')
                title_expected_delivery = title_obj.get('expected_delivery_date')

            message = 'Update for External Rejection on %s (%s) [%s PO#: %s]:' % (title_full_name, title_code, order_code, po_number)
            message += '<br/><br/>THIS EXTERNAL REJECTION IS NOW CLOSED'

            subject_int = 'NEW - URGENT External Rejection Closed for %s (%s) - Status: %s Scheduler: %s PO#: %s' % (title_full_name, title_code, status, scheduler, po_number)

            from formatted_emailer import EmailDirections, email_sender
            
            ed = EmailDirections(order_code=order_code)
            int_data = ed.get_internal_data()

            int_data['subject'] = subject_int
            int_data['message'] = message
            int_data['title_code'] = title_code
            int_data['title_full_name'] = title_full_name
            int_data['title_due_date'] = title_due_date
            int_data['title_expected_delivery'] = title_expected_delivery
            int_data['replacement_order_code'] = replacement_order_code
            int_data['replacement_title_code'] = replacement_title_code
            int_data['reported_issue'] = reported_issue
            int_data['root_cause'] = root_cause
            int_data['corrective_action'] = corrective_action

            cc_addresses = int_data['int_ccs'].split(';')
            if addressed_to:
                cc_addresses.extend([x for x in addressed_to.split(',') if '@2gdigital' in x])
            cc_addresses.append('Operations@2gdigital.com')
            cc_addresses.append('rejections@2gdigital.com')
            int_data['ccs'] = ';'.join(set(cc_addresses))

            # NEW WAY TO SET THE FROM FOR THE EMAIL
            login_obj = Environment.get_login()
            int_data['from_email'] = login_obj.get_value('email')
            int_data['from_name'] = '{0} {1}'.format(login_obj.get_value('first_name'), login_obj.get_value('last_name'))

            if int_data['to_email']:
                email_file_name = 'int_note_inserted_{0}.html'.format(external_rejection.get('code'))
                email_sender.send_email(template=internal_template_file, email_data=int_data,
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
