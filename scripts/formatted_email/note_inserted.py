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
        # CUSTOM_SCRIPT00061
        # Matthew Tyler Misenhimer
        # This code is run when a note is inserted
        # It emails the note to the groups or individuals associated with the objects the note is attached to
        def make_right_code_ending(sid):
            ending = str(sid)
            ending_len = len(ending)
            if ending_len < 5:
                zeros = 5 - ending_len
                for num in range(0, zeros):
                    ending = '0%s' % ending
            return ending

        import os, time, sys
        from pyasm.common import Environment
        allow_client_emails = True
        external_template_file = '/opt/spt/custom/formatted_emailer/external_email_template.html'
        internal_template_file = '/opt/spt/custom/formatted_emailer/note_inserted_email_template.html'
        note_dict = input.get('sobject')
        search_type = note_dict.get('search_type').split('?')[0]
        search_id = note_dict.get('search_id')
        login = note_dict.get('login')
        process = note_dict.get('process')
        note = note_dict.get('note')

        if 'Corrective Action' in process or 'Root Cause' in process or 'Cloned WO:' in process:
            return

        # If there are no attached files, then send the note
        # If there are attached files, the file insertion trigger will email the note
        if 'HASATTACHEDFILES' not in note and process not in ['Billing', 'Closed']:
            note = note.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
            note = note.replace('\n', '<br/>')
            note = note.replace('  ', '&nbsp;&nbsp;')
            note_id = note_dict.get('id')
            timestamp = note_dict.get('timestamp').split('.')[0]
            addressed_to = note_dict.get('addressed_to')
            parent_tall_str = search_type.split('/')[1].upper()
            order = None
            title = None
            proj = None
            title_row = ''
            proj_row = ''
            is_external_rejection = False
            if parent_tall_str in ['ORDER', 'TITLE', 'PROJ', 'WORK_ORDER']:
                from formatted_emailer import EmailDirections, email_sender
                right_ending = make_right_code_ending(search_id)
                parent_code = '%s%s' % (parent_tall_str, right_ending)
                parent = server.eval("@SOBJECT(%s['code','%s'])" % (search_type, parent_code))
                if parent:
                    parent = parent[0]
                going_to_client = False
                if parent_tall_str == 'WORK_ORDER':
                    proj = server.eval("@SOBJECT(twog/work_order['code','%s'].twog/proj)" % parent_code)[0]
                    title = server.eval("@SOBJECT(twog/work_order['code','%s'].twog/proj.twog/title)" % parent_code)[0]
                    order = server.eval("@SOBJECT(twog/order['code','%s'])" % title.get('order_code'))[0]
                elif parent_tall_str == 'PROJ':
                    proj = parent
                    title = server.eval("@SOBJECT(twog/proj['code','%s'].twog/title)" % parent_code)[0]
                    order = server.eval("@SOBJECT(twog/order['code','%s'])" % title.get('order_code'))[0]
                elif parent_tall_str == 'TITLE':
                    title = parent
                    order = server.eval("@SOBJECT(twog/order['code','%s'])" % title.get('order_code'))[0]
                elif parent_tall_str == 'ORDER':
                    order = server.eval("@SOBJECT(twog/order['code','%s'])" % parent_code)[0]
                if parent_tall_str == 'ORDER' and process == 'client':
                    order = parent
                    going_to_client = True
                elif parent_tall_str == 'TITLE' and process == 'client':
                    going_to_client = True
                display_heirarchy = ''

                ed = EmailDirections(order_code=order.get('code'))
                int_data = ed.get_internal_data()
                int_data['info_text_color'] = '#06C'
                ext_data = ed.get_external_data()

                if title:
                    title_display = title.get('title')
                    if title.get('episode') not in [None, '']:
                        title_display = '%s: %s' % (title_display, title.get('episode'))
                    display_heirarchy = '"%s" in %s' % (title_display, display_heirarchy)
                if parent_tall_str in ['ORDER', 'TITLE']:
                    ident_str = '%s PO# %s' % (display_heirarchy, ext_data['po_number'])
                else:
                    ident_str = '%s (%s)' % (parent_code, ext_data['po_number'])
                subject = '2G-NOTE FOR %s' % ident_str
                if 'External Rejection' in process:
                    # Then it is a Title, for sure
                    is_external_rejection = True
                    title_name = parent.get('title')
                    if parent.get('episode') not in [None, '']:
                        title_name = '%s: %s' % (title_name, parent.get('episode'))
                    subject = '%s on %s' % (process, title_name)
                if 'MTMSUBJECT' in note:
                    snote = note.split('MTMSUBJECT')
                    subject = snote[0]
                    note = snote[1]
                subject_int = subject
                if title:
                    if title.get('login') not in [None, '']:
                        subject_int = '%s Scheduler: %s' % (subject_int, title.get('login'))
                else:
                    if order.get('login') not in [None, '']:
                        subject_int = '%s Scheduler: %s' % (subject_int, order.get('login'))

                if ext_data['to_email'] == '' and ext_data['ext_ccs'] == '' and ext_data['location'] == 'external':
                    subject = 'NOT SENT TO CLIENT!? %s' % subject
                    subject_int = 'NOT SENT TO CLIENT!? %s' % subject_int
                subject_see = subject
                subject = subject.replace(' ', '..')
                subject_int = subject_int.replace(' ', '..')
                note = ctu.fix_message_characters(note)
                message = '%s has added a new note for %s:<br/><br/><p style="font-size: 16px;"><b>Note:</b><i><br/>%s<br/>%s</i></p>' % (ext_data['from_name'], ident_str, note, timestamp)
                if going_to_client and allow_client_emails:
                    ext_template = open(external_template_file, 'r')
                    filled = ''
                    for line in ext_template:
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
                    ext_template.close()
                    filled_in_email = '/var/www/html/formatted_emails/ext_note_inserted_%s.html' % note_id
                    filler = open(filled_in_email, 'w')
                    filler.write(filled)
                    filler.close()
                    if addressed_to not in [None, '']:
                        adt = addressed_to.split(',')
                        for adta in adt:
                            if '@2gdigital' not in adta and adta not in ext_data['ext_ccs']:
                                if ext_data['ext_ccs'] == '':
                                    ext_data['ext_ccs'] = adta
                                else:
                                    ext_data['ext_ccs'] = '%s;%s' % (ext_data['ext_ccs'], adta)
                    the_command = "php /opt/spt/custom/formatted_emailer/trusty_emailer.php '''%s''' '''%s''' '''%s''' '''%s''' '''%s''' '''%s'''" % (filled_in_email, ext_data['to_email'], ext_data['from_email'], ext_data['from_name'], subject, ext_data['ext_ccs'].replace(';','#Xs*'))
                    if ext_data['to_email'] not in [None, ''] and ext_data['ext_ccs'] not in [None, '', ';']:
                        os.system(the_command)

                # Now do internal email
                details = order.get('details', '')
                if details:
                    int_data['order_hyperlink'] += ' - ' + details
                if title:
                    full_title = title.get('title')
                    if title.get('episode') not in [None, '']:
                        full_title = '%s: %s' % (full_title, title.get('episode'))
                    title_row = "<tr><td align='left' style='color: #06C; font-size: 16px;'>Title: <strong>%s</strong> | Title Code: <strong>%s</strong></td></tr>" % (full_title, title.get('code'))
                if proj:
                    proj_row = "<tr><td align='left' style='color: #06C; font-size: 16px;'>Project: <strong>%s</strong> | Project Code: <strong>%s</strong></td></tr>" % (proj.get('process'), proj.get('code'))
                if is_external_rejection:
                    int_data['info_text_color'] = '#FF0000'
                    title_row = title_row.replace('#06C', '#FF0000')
                    proj_row = proj_row.replace('#06C', '#FF0000')

                int_data['subject'] = subject_int
                int_data['message'] = message
                int_data['title_row'] = title_row
                int_data['proj_row'] = proj_row
                int_data['start_date'] = ctu.fix_date(int_data['start_date'])
                int_data['due_date'] = ctu.fix_date(int_data['due_date'])

                cc_addresses = int_data['int_ccs'].split(';')
                if addressed_to:
                    cc_addresses.extend([x for x in addressed_to.split(',') if '@2gdigital' in x])
                if is_external_rejection:
                    cc_addresses.append('rejections@2gdigital.com')
                cc_addresses.append('Operations@2gdigital.com')
                int_data['ccs'] = ';'.join(set(cc_addresses))

                login_email = server.eval("@GET(sthpw/login['login','{0}'].email)".format(login))
                if login_email:
                    int_data['from_email'] = login_email[0]

                if int_data['to_email']:
                    email_sender.send_email(template=internal_template_file, email_data=int_data,
                                            email_file_name='int_note_inserted_{0}.html'.format(note_id), server=server)

            elif 'WHATS_NEW' in parent_tall_str:
                subject = 'Updates have been made to Tactic'
                subject_int = subject.replace(' ', '..')
                message = 'Changes have been made to Tactic. Please see the "Whats New" section in Tactic to see what has changed.'
                internal_template_file = '/opt/spt/custom/formatted_emailer/whats_new_email.html'
                int_template = open(internal_template_file, 'r')
                filled = ''
                for line in int_template:
                    line = line.replace('[MESSAGE]', message)
                    filled = '%s%s' % (filled, line)
                int_template.close()
                filled_in_email = '/var/www/html/formatted_emails/whats_new_email_%s.html' % search_id
                filler = open(filled_in_email, 'w')
                filler.write(filled)
                filler.close()
                addressed_to = '2gstaff@2gdigital.com'
                from_email = 'tacticIT@2gdigital.com'
                the_command = "php /opt/spt/custom/formatted_emailer/trusty_emailer.php '''%s''' '''%s''' '''%s''' '''%s''' '''%s''' '''%s'''" % (filled_in_email, addressed_to, from_email, 'Admin', subject_int, 'administrator@2gdigital.com')
                os.system(the_command)
            elif 'CLIENT' in parent_tall_str:
                subject = 'A client has been put on a billing hold'
                subject_int = subject.replace(' ', '..')
                note = ctu.fix_message_characters(note)
                message = '%s' % note
                internal_template_file = '/opt/spt/custom/formatted_emailer/whats_new_email.html'
                int_template = open(internal_template_file, 'r')
                filled = ''
                for line in int_template:
                    line = line.replace('[MESSAGE]', message)
                    filled = '%s%s' % (filled, line)
                int_template.close()
                filled_in_email = '/var/www/html/formatted_emails/whats_new_email_%s.html' % search_id
                filler = open(filled_in_email, 'w')
                filler.write(filled)
                filler.close()
                addressed_to = note_dict.get('addressed_to')
                from_email = 'accounting@2gdigital.com'
                the_command = "php /opt/spt/custom/formatted_emailer/trusty_emailer.php '''%s''' '''%s''' '''%s''' '''%s''' '''%s''' '''%s'''" % (filled_in_email, addressed_to, from_email, 'Accounting', subject_int, 'matt.misenhimer@2gdigital.com')
                os.system(the_command)
            elif 'EXTERNAL_REJECTION' in parent_tall_str:
                note = ctu.fix_message_characters(note)
                right_ending = make_right_code_ending(search_id)
                parent_code = '%s%s' % (parent_tall_str, right_ending)
                parent = server.eval("@SOBJECT(%s['code','%s'])" % (search_type, parent_code))[0]
                if process == 'Root Cause':
                    server.update(parent.get('__search_key__'), {'root_cause': note})
                elif process == 'Corrective Action':
                    server.update(parent.get('__search_key__'), {'corrective_action': note})
                else:
                    email_list = parent.get('email_list')
                    server.update(parent.get('__search_key__'), {'email_list': email_list})

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
