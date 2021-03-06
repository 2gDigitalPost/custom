"""
This sends notifications to the assigned login group when work orders are created,
or when the assigned group is changed. The custom script in the database simply
calls the main function of this file, that way it can be integrated with GitHub.
"""

__author__ = 'Topher.Hughes'
__date__ = '03/09/2015'

import traceback
import common_tools.utils as ctu


def get_notification_setting(login_group, server):
    """Get the notification setting for the login group.
    Return True if the group should get the notification.

    :param login_group: the login group name as a string
    :param server: a TacticServerStub object
    :return: boolean if group should get notification or not
    """
    notification_settings = ctu.get_project_setting('department_work_order_notification', server=server)
    department_setting = notification_settings.get(login_group, 'False')

    return department_setting == 'True'


def get_update_message(prev_data, update_data):
    """Get the formatted message body with the updates.

    :param prev_data: dict of the previous data
    :param update_data: dict of the updated data
    :return: a string
    """
    update_line = '<tr><td><b>{0}&nbsp;-&nbsp;</b></td><td>From:&nbsp;<i>{1}</i>&nbsp;</td><td>To:&nbsp;<i>{2}</i></td></tr>'
    updates = []
    for column in update_data:
        column_name = column.replace('_', ' ').title()
        old_value = prev_data.get(column, 'None')
        new_value = update_data.get(column)
        updates.append(update_line.format(column_name, old_value, new_value))

    message = '<table>' + ''.join(updates) + '</table>'

    return message


def get_sobjects(server, event_data):
    """
    Get the required variables for this trigger. Accounts for when the triggering
    sobject is a work order or a task.

    :param server: a tactic server stub object
    :param event_data: the event dictionary
    :return: work order sobject, task sobject
    """
    sobject = event_data.get('sobject')
    sobject_type = ctu.get_sobject_type(sobject.get('__search_key__'))
    work_order = {}
    task = {}
    if sobject_type == 'work_order':
        work_order = sobject
        results = server.query('sthpw/task', filters=[('code', work_order.get('task_code'))])
        if results:
            task = results[0]
    elif sobject_type == 'task' and 'WORK_ORDER' in sobject.get('lookup_code'):
        task = sobject
        results = server.query('twog/work_order', filters=[('code', task.get('lookup_code'))])
        if results:
            work_order = results[0]

    return work_order, task


def get_department_email(assigned_group, server):
    """
    Get the email address for the assigned department.

    :param assigned_group: the assigned group as a string
    :param server: a TacticServerStub object
    :return: a formatted email address
    """
    # Eventually this should get the emails from tactic, but I'm hesitant to
    # modify the login group object before I can thoroughly test it.
    return '{0}@2gdigital.com'.format(assigned_group)


def get_is_insert(update_data):
    """
    The 'insert' logic had to change because work orders are not ready when they are created.
    It is counted as an insert when the task status is updated to 'Ready'.

    :param update_data: dictionary of updated columns
    :return: boolean
    """
    return update_data.get('status') == 'Ready'


def main(server=None, event_data=None):
    """
    The main function of the custom script.

    :param server: the TacticServerStub object
    :param event_data: a dict with data like search_key, search_type, sobject, and update_data
    :return: None
    """
    if not event_data:
        event_data = {}

    try:
        # CUSTOM_SCRIPT00107
        work_order, task = get_sobjects(server, event_data)
        if not task or task.get('status') == 'Pending':
            # They don't care about updates if the work order is not ready yet
            return

        assigned_group = work_order.get('work_group')
        if assigned_group and get_notification_setting(assigned_group, server):
            from formatted_emailer import EmailDirections, email_sender
            ed = EmailDirections(order_code=work_order.get('order_code'))
            internal_data = ed.get_internal_data()
            title = server.query('twog/title', filters=[('code', work_order.get('title_code'))])
            title = title[0] if title else {}

            # to_email should be the department distribution group
            internal_data['to_email'] = get_department_email(assigned_group, server)
            if get_is_insert(event_data.get('update_data')):
                subject = 'Work Order "{0}" assigned to "{1}"'.format(work_order.get('process'), assigned_group)
                message = work_order.get('instructions')
                internal_data['message_type'] = 'INSTRUCTIONS:'
            else:
                subject = 'Work Order "{0}" has been updated'.format(work_order.get('process'))
                message = get_update_message(event_data.get('prev_data'), event_data.get('update_data'))
                internal_data['message_type'] = 'UPDATES:'

            internal_data['subject'] = subject
            internal_data['message'] = message
            internal_data['work_order_code'] = work_order.get('code')
            internal_data['work_order_name'] = work_order.get('process')
            internal_data['title_code'] = title.get('code')
            internal_data['title_name'] = title.get('title')
            title_hyperlink = ctu.get_edit_wdg_hyperlink('twog/title', title.get('code'),
                                                         sobject_name=title.get('title'), server=server)
            internal_data['title_hyperlink'] = title_hyperlink
            internal_data['start_date'] = ctu.fix_date(internal_data.get('start_date'))
            internal_data['due_date'] = ctu.fix_date(internal_data.get('due_date'))

            email_template = '/opt/spt/custom/formatted_emailer/work_order_email_template.html'
            email_file_name = 'work_order_inserted/work_order_{0}.html'.format(work_order.get('code'))
            email_sender.send_email(template=email_template, email_data=internal_data,
                                    email_file_name=email_file_name, server=server)

    except AttributeError as e:
        traceback.print_exc()
        print str(e) + '\nMost likely the server object does not exist.'
        raise e
    except KeyError as e:
        traceback.print_exc()
        print str(e) + '\nMost likely the event dictionary does not exist.'
        raise e
    except Exception as e:
        traceback.print_exc()
        print str(e)
        raise e


if __name__ == '__main__':
    main()
