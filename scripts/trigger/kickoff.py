"""
This file was generated automatically from a custom script found in Project -> Script Editor.
The custom script was moved to a file so that it could be integrated with GitHub.
"""

__author__ = 'Topher.Hughes'
__date__ = '04/08/2015'

import traceback


def make_timestamp():
    from pyasm.common import SPTDate
    # Makes a Timestamp for postgres
    import datetime
    now = SPTDate.convert_to_local(datetime.datetime.now())
    return now


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
        # CUSTOM_SCRIPT00091
        #
        # Created by Matthew Misenhimer
        #

        def no_incompletes_preceding(new_sob, initial_sob_code):
            comes_from = new_sob.get('comes_from').split('|^|')
            for c in comes_from:
                if initial_sob_code not in c:
                    task_code = c.split(',')[1]
                    task_code = task_code.replace(']', '').replace('[', '')
                    task_status = server.eval("@GET(sthpw/task['code','{0}'].status)".format(task_code))[0]
                    if task_status != 'Completed':
                        return False
            return True

        from pyasm.common import TacticException, Environment
        # input and server are assumed variables
        # define some constants here
        COMPLETE = 'Completed'
        READY = 'Ready'
        PENDING = 'Pending'
        sobj = input.get('sobject')
        this_process = sobj.get('process')
        this_lookup = sobj.get('lookup_code')
        sk = input.get('search_key')
        task_code = sobj.get('code')
        # These are the new values
        update_data = input.get('update_data')
        old_status = ''
        if 'prev_data' in input:
            # These are the old values
            prev_data = input.get('prev_data')
            old_status = prev_data.get('status', '')
        new_status = update_data.get('status')
        login = Environment.get_login()
        user_name = login.get_login()
        assigned_login_group = sobj.get('assigned_login_group')
        proj = None
        title = None
        order = None
        if 'PROJ' in this_lookup:
            # Parent Obj is the Proj attached to the task
            parent_obj = server.eval("@SOBJECT(twog/proj['code','{0}'])".format(this_lookup))[0]
            proj = parent_obj
            title = server.eval("@SOBJECT(twog/title['code','{0}'])".format(parent_obj.get('title_code')))[0]
            order = server.eval("@SOBJECT(twog/order['code','{0}'])".format(title.get('order_code')))[0]
        elif 'WORK_ORDER' in this_lookup:
            # Parent Obj is the Work Order attached to the task
            parent_obj = server.eval("@SOBJECT(twog/work_order['code','{0}'])".format(this_lookup))[0]
            work_order = parent_obj
            proj = server.eval("@SOBJECT(twog/proj['code','{0}'])".format(work_order.get('proj_code')))[0]
            title = server.eval("@SOBJECT(twog/title['code','{0}'])".format(proj.get('title_code')))[0]
            order = server.eval("@SOBJECT(twog/order['code','{0}'])".format(title.get('order_code')))[0]
        if 'PROJ' in this_lookup and title.get('priority_triggers') != 'No':
            pass
        elif 'WORK_ORDER' in this_lookup:
            if new_status == COMPLETE:
                # Make sure they have set the assigned person to the work order.
                if sobj.get('assigned') in [None, '']:
                    raise TacticException('Before completing a work order, someone must be assigned to it.')
                # Make sure they have added work hours. If not, error out.
                total_time = server.eval("@SUM(sthpw/work_hour['task_code','{0}'].straight_time)".format(task_code))
                if total_time < 0.001:  # account for floating point inaccuracy
                    raise TacticException('You need to save the hours you worked on this before you can set the status to "Completed".')
            # This is for the completion ratio on title
            t_wo_completed = title.get('wo_completed')
            # This is for the completion ratio on order
            o_wo_completed = order.get('wo_completed')
            if new_status == COMPLETE:
                # This is for a potential alert/exception
                title_str = title.get('title')
                if title.get('episode') not in [None, '']:
                    title_str = '{0}: {1}'.format(title_str, title.get('episode'))
                # Block QC and Edel from completing their work orders if the TRT or TRT w/Textless are not filled in
                if 'qc' in assigned_login_group or 'edeliveries' in assigned_login_group:
                    total_program_runtime = title.get('total_program_runtime')
                    total_runtime_w_textless = title.get('total_runtime_w_textless')
                    invalid_runtime = total_program_runtime in [None, ''] or total_runtime_w_textless in [None, '']
                    say_str = ''
                    say_str2 = ''
                    if invalid_runtime:
                        if total_program_runtime in [None, '']:
                            say_str = 'Total Program Runtime has'
                        if total_runtime_w_textless in [None, '']:
                            if say_str == '':
                                say_str = 'Total Runtime With Textless has'
                            else:
                                say_str = '%s and Total Runtime With Textless have' % (say_str[:-4])
                        say_str2 = "%s (%s)'s %s not been filled. You must enter this data before trying to complete this work order." % (title_str, title.get('code'), say_str)
                    if 'qc' in assigned_login_group:
                        if invalid_runtime:
                            raise TacticException(say_str2)
                        else:
                            # They were filled in, so finish completing the task and send a note
                            from pyasm.biz import Note
                            from pyasm.search import Search
                            # This is the type of object required for Note creation
                            title_obj2 = Search.get_by_search_key(title.get('__search_key__'))
                            note_text = '%s (%s) has been Passed and Completed by %s in QC' % (sobj.get('process'), this_lookup, user_name)
                            note = Note.create(title_obj2, note_text, context='QC Completed', process='QC Completed')
                    elif 'edeliveries' in assigned_login_group and invalid_runtime:
                        raise TacticException(say_str2)
                t_wo_completed += 1
                o_wo_completed += 1
                # Update the completion ratios attached, since there were no blocking exceptions
                server.update(title.get('__search_key__'), {'wo_completed': t_wo_completed})
                server.update(order.get('__search_key__'), {'wo_completed': o_wo_completed})
            elif old_status == COMPLETE:
                t_wo_completed -= 1
                o_wo_completed -= 1
                # Reduce the completion ratio, since it was completed but has now been taken off that status
                server.update(title.get('__search_key__'), {'wo_completed': t_wo_completed})
                server.update(order.get('__search_key__'), {'wo_completed': o_wo_completed})

        now_timestamp = make_timestamp()
        # Since there have been no blocking exceptions, record the status change
        stat_log_dict = {'login': user_name, 'timestamp': now_timestamp, 'from_status': old_status,
                         'status': new_status, 'task_code': task_code, 'lookup_code': this_lookup,
                         'order_code': sobj.get('order_code'), 'title_code': sobj.get('title_code'),
                         'process': this_process}
        server.insert('twog/status_log', stat_log_dict)
        if new_status == COMPLETE:
            # Record the completion date on the work order, and take it off the BigBoard
            updict = {'actual_end_date': make_timestamp()}
            do_indie = False
            if 'WORK_ORDER' in this_lookup:
                updict['bigboard'] = False
                if sobj.get('indie_bigboard') in [True, 'true', 't', 'T', 1]:
                    updict['indie_bigboard'] = False
                    do_indie = True
            server.update(sk, updict)
            if do_indie:
                indies = server.eval("@SOBJECT(twog/indie_bigboard['task_code','{0}'])".format(task_code))
                for indie in indies:
                    indie_dict = {'indie_bigboard': False}
                    if indie.get('removal_login') in [None, '']:
                        indie_dict['removal_login'] = user_name
                    if indie.get('removal_login') in [None, '']:
                        indie_dict['removal_timestamp'] = now_timestamp
                    server.update(indie.get('__search_key__'), indie_dict)
        elif new_status not in ['Pending', 'Ready', 'Completed'] and 'WORK_ORDER' in this_lookup:
            server.update(server.build_search_key('sthpw/task', proj.get('task_code')), {'status': new_status})
        if 'PROJ' in sobj.get('lookup_code'):
            # MTM: This annoying section is for passing Proj's their task's status.
            # I don't know if this is needed at all anymore. Will have to check other triggers and reports.
            # The "tripwire" stuff was just to keep it from infinitely passing statuses from proj to task, task to proj
            do_it = True
            if update_data.get('tripwire', '') == 'No Send Back':
                do_it = False
                # Empty the tripwire and do nothing
                server.update(input.get('search_key'), {'tripwire': ''}, triggers=False)
                server.update(proj.get('__search_key__'), {'tripwire': '', 'status': sobj.get('status')},
                              triggers=False)
            if do_it and proj:
                server.update(proj.get('__search_key__'), {'status': new_status})
        if title.get('priority_triggers') != 'No':
            # Update Title Priority for On Hold Status, or having that status removed -- BEGIN
            if sobj.get('status') in ['On_Hold', 'On Hold']:
                title_priority = title.get('priority')
                server.update(title.get('__search_key__'), {'saved_priority': title_priority, 'priority': 200},
                              triggers=False)
            elif old_status in ['On_Hold', 'On Hold']:
                saved_priority = title.get('saved_priority')
                server.update(title.get('__search_key__'), {'priority': saved_priority}, triggers=False)
            # Update Title Priority for On Hold Status, or having that status removed -- END

            # Update Title Priority for Client Response Status, or having that status removed -- BEGIN
            if sobj.get('status') == 'Client Response':
                title_priority = title.get('priority')
                crc = title.get('client_response_count')
                crc_num = 0
                if crc not in [None, '']:
                    crc_num = int(crc)
                crc_num += 1
                title_update_data = {'saved_priority': title_priority, 'priority': 300,
                                     'client_response_count': crc_num}
                server.update(title.get('__search_key__'), title_update_data, triggers=False)
            elif old_status == 'Client Response':
                saved_priority = title.get('saved_priority')
                crc = title.get('client_response_count')
                crc_num = 0
                if crc not in [None, '']:
                    crc_num = int(crc)
                if crc_num > 0:
                    crc_num -= 1
                title_update_data = {'priority': saved_priority, 'client_response_count': crc_num}
                server.update(title.get('__search_key__'), title_update_data, triggers=False)
            # Update Title Priority for Client Response Status, or having that status removed -- END

        statuses = ['In_Progress', 'In Progress', 'DR In_Progress', 'DR In Progress', 'Amberfin01_In_Progress',
                    'Amberfin01 In Progress', 'Amberfin02_In_Progress', 'Amberfin02 In Progress', 'BATON In_Progress',
                    'BATON In Progress', 'Export In_Progress', 'Export In Progress', 'Buddy Check In_Progress',
                    'Buddy Check In Progress', 'Need Buddy Check', 'In Review']
        if sobj.get('status') in statuses + ['Completed'] and old_status not in statuses:
            # Update the actual start date if they just set the status to 'In Progress'
            if sobj.get('actual_start_date') in ['', None]:
                now_timestamp = make_timestamp()
                server.update(sk, {'actual_start_date': now_timestamp, 'flag_future_changes': True})
        if sobj.get('status') in ['Ready', 'In_Progress', 'In Progress', 'In Review'] and 'WORK_ORDER' in sobj.get('lookup_code'):
            if title.get('client_status') != 'In Production':
                server.update(title.get('__search_key__'),
                              {'client_status': 'In Production', 'status': 'In Production'})
        elif sobj.get('status') in ['Rejected', 'Fix Needed'] and 'WORK_ORDER' in sobj.get('lookup_code'):
            from pyasm.biz import Note
            from pyasm.search import Search
            prod_error = {'error_type': sobj.get('status'), 'process': sobj.get('process'),
                          'work_order_code': sobj.get('lookup_code'), 'title': title.get('title'),
                          'episode': title.get('episode'), 'title_code': title.get('code'),
                          'order_code': order.get('code'), 'order_name': order.get('name'),
                          'po_number': order.get('po_number'), 'proj_code': proj.get('code'),
                          'scheduler_login': sobj.get('creator_login'), 'operator_login': user_name, 'login': user_name}
            server.insert('twog/production_error', prod_error, triggers=False)
            if sobj.get('status') == 'Rejected':
                server.update(title.get('__search_key__'), {'client_status': 'QC Rejected'})
                if title.get('priority_triggers') != 'No':
                    server.update(title.get('__search_key__'), {'priority': 90}, triggers=False)

        status_triggers = proj.get('status_triggers')
        if status_triggers in [None, '']:
            status_triggers = title.get('status_triggers')
        if sobj.get('status') == COMPLETE and status_triggers != 'No':
            # Now we need to set the next task(s) statuses to 'Ready'
            goes_to = sobj.get('goes_to').split('|^|')
            for gt in goes_to:
                if ',' not in gt:
                    continue

                next_task_code = gt.split(',')[1].replace('[', '').replace(']', '')
                nt_expr = "@SOBJECT(sthpw/task['code','{0}'])".format(next_task_code)
                next_task = server.eval(nt_expr)
                if next_task:
                    next_task = next_task[0]
                    if next_task.get('status') != 'Pending':
                        continue

                    if no_incompletes_preceding(next_task, task_code):
                        server.update(next_task.get('__search_key__'), {'status': READY})
                        if 'PROJ' not in next_task.get('lookup_code'):
                            continue

                        oip = next_task.get('order_in_pipe')
                        if oip in [None, '', 0]:
                            oip = 1
                        else:
                            oip = int(oip)
                        smallest_wo = (oip * 1000) + 10
                        nwt_expr = "@GET(twog/work_order['proj_code','{0}']['order_in_pipe','<=','{1}'].WT:sthpw/task['status','Pending']['@ORDER_BY','order_in_pipe desc'].__search_key__)"
                        task_search_keys = server.eval(nwt_expr.format(next_task.get('lookup_code'), smallest_wo))
                        task_update_data = dict.fromkeys(task_search_keys, {'status': READY})
                        server.update_multiple(task_update_data, triggers=False)

        # Now see if all wos under proj or all projs under title are completed.
        # If so, make their parent's status completed
        prj = None
        if new_status not in [COMPLETE, PENDING]:
            return

        if 'WORK_ORDER' in this_lookup:
            wo = server.eval("@SOBJECT(twog/work_order['code','{0}'])".format(sobj.get('lookup_code')))
            wo = wo[0]
            other_wotasks_expr = "@SOBJECT(twog/proj['code','{0}'].twog/work_order.WT:sthpw/task)".format(wo.get('proj_code'))
            other_wo_tasks = server.eval(other_wotasks_expr)
            all_wos_completed = True
            all_wos_pending = True
            if new_status == PENDING:
                all_wos_completed = False
            elif new_status == COMPLETE:
                all_wos_pending = False
            un_indie = False
            if sobj.get('indie_bigboard') in [True, 'true', 't', 'T', 1]:
                un_indie = True
            for owt in other_wo_tasks:
                if owt.get('lookup_code') != wo.get('code'):
                    if owt.get('status') != COMPLETE:
                        all_wos_completed = False
                    if owt.get('status') != PENDING:
                        all_wos_pending = False
                    if owt.get('indie_bigboard') in [True, 'true', 't', 'T', 1] and (owt.get('assigned_login_group') == sobj.get('assigned_login_group')):
                        un_indie = False
            # HERE NEED TO DETERMINE WHICH DEPT THIS WAS FOR AND SEE IF ANY OTHER WOs
            # IN THE SAME DEPT ARE STILL INDIE. IF NOT, THEN TAKE THE DEPT NAME OUT OF
            # active_dept_priorities ON THE TITLE
            if un_indie:
                that_dept = sobj.get('assigned_login_group').replace(' supervisor', '')
                adps = title.get('active_dept_priorities')
                adps = adps.replace(',%s' % that_dept, '').replace('%s,' % that_dept, '').replace(that_dept, '')
                indie_data = {'active_dept_priorities': adps}
                prio_name = '%s_priority' % that_dept.replace(' ', '_')
                indie_data[prio_name] = title.get('priority')
                server.update(title.get('__search_key__'), indie_data)
            prj = server.eval("@SOBJECT(twog/proj['code','{0}'])".format(wo.get('proj_code')))
            prj = prj[0] if prj else None
            if (all_wos_completed or all_wos_pending) and prj not in [None, '']:
                prj_task = server.eval("@SOBJECT(sthpw/task['lookup_code','{0}'])".format(prj.get('code')))
                if prj_task:
                    server.update(prj_task[0].get('__search_key__'), {'status': new_status})
        elif 'PROJ' in this_lookup:
            prj = server.eval("@SOBJECT(twog/proj['code','{0}'])".format(this_lookup))
            prj = prj[0] if prj else None

        all_projs_completed = True
        all_projs_pending = True
        all_titles_completed = False
        all_titles_pending = False
        if prj in [None, '']:
            return

        title_proj_tasks = server.eval("@SOBJECT(twog/title['code','{0}'].twog/proj.PT:sthpw/task)".format(prj.get('title_code')))
        for tpt in title_proj_tasks:
            if tpt.get('status') != COMPLETE:
                all_projs_completed = False
            if tpt.get('status') != PENDING:
                all_projs_pending = False
        title_updated = False
        if all_projs_completed:
            title_sk = server.build_search_key('twog/title', prj.get('title_code'))
            server.update(title_sk, {'status': COMPLETE, 'client_status': COMPLETE,
                                     'bigboard': False, 'priority': 5000})
            titles_completed = order.get('titles_completed')
            title_codes_completed = order.get('title_codes_completed')
            if title.get('code') not in title_codes_completed:
                if titles_completed in [None, '']:
                    titles_completed = 0
                else:
                    titles_completed = int(titles_completed)
                titles_completed += 1
                if title_codes_completed == '':
                    title_codes_completed = title.get('code')
                else:
                    title_codes_completed = '%s,%s' % (title_codes_completed, title.get('code'))
                server.update(order.get('__search_key__'), {'titles_completed': titles_completed,
                                                            'title_codes_completed': title_codes_completed})
                title_updated = True
            all_titles_completed = True
            title = server.eval("@SOBJECT(twog/title['code','{0}'])".format(prj.get('title_code')))
            if title and title_updated:
                title = title[0]
                other_titles = server.eval("@SOBJECT(twog/order['code','{0}'].twog/title)".format(title.get('order_code')))
                for ot in other_titles:
                    if title.get('code') != ot.get('code') and ot.get('status') != COMPLETE:
                        all_titles_completed = False
                        break
            else:
                all_titles_completed = False

        if all_projs_pending:
            title_sk = server.build_search_key('twog/title', prj.get('title_code'))
            if title.get('priority_triggers') != 'No' and title.get('status_triggers') != 'No':
                server.update(title_sk, {'status': '', 'bigboard': False})
                title_codes_completed = order.get('title_codes_completed')
                if title.get('code') in title_codes_completed:
                    title_codes_completed = title_codes_completed.replace(',%s' % title.get('code'), '').replace('%s,' % title.get('code'), '').replace('%s' % title.get('code'), '')
                    titles_completed = order.get('titles_completed')
                    if titles_completed in [None, '']:
                        titles_completed = 0
                    else:
                        titles_completed = int(titles_completed) - 1
                    server.update(order.get('__search_key__'), {'titles_completed': titles_completed,
                                                                'title_codes_completed': title_codes_completed})
                title_updated = True
            all_titles_pending = True
            title = server.eval("@SOBJECT(twog/title['code','{0}'])".format(prj.get('title_code')))
            if title and title_updated:
                title = title[0]
                other_titles = server.eval("@SOBJECT(twog/order['code','{0}'].twog/title)".format(title.get('order_code')))
                for ot in other_titles:
                    if title.get('code') != ot.get('code') and ot.get('status') != '':
                        all_titles_pending = False
                        break
            else:
                all_titles_pending = False

        if all_titles_pending:
            server.update(server.build_search_key('twog/order', title.get('order_code')),
                          {'needs_completion_review': False})
        if all_titles_completed:
            server.update(server.build_search_key('twog/order', title.get('order_code')),
                          {'needs_completion_review': True})

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
