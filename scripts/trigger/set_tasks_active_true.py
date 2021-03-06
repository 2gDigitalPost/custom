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
        # CUSTOM_SCRIPT00020
        def make_timestamp():
            import datetime
            now = datetime.datetime.now()
            return now.strftime("%Y-%m-%d %H:%M:%S")

        def are_no_hackpipes_preceding(sob):
            boolio = True
            matcher = ''
            if 'PROJ' in sob.get('code'):
                matcher = 'PROJ'
            elif 'WORK_ORDER' in sob.get('code'):
                matcher = 'WORK_ORDER'
            pre_hacks_expr = "@SOBJECT(twog/hackpipe_out['out_to','%s'])" % sob.get('code')
            pre_hacks = server.eval(pre_hacks_expr)
            for ph in pre_hacks:
                if matcher in ph.get('lookup_code'):
                    ph_task = server.eval("@SOBJECT(sthpw/task['lookup_code','%s'])" % ph.get('lookup_code'))
                    if ph_task:
                        ph_task = ph_task[0]
                        if ph_task.get('status') != 'Completed':
                            boolio = False
            return boolio

        def do_wo_loop(proj, active):
            # Get all work orders under the proj so we can determine
            # which one of them should be turned on (set to ready)
            wos = server.eval("@SOBJECT(twog/work_order['proj_code','%s'])" % proj.get('code'))
            updated_wo_count = 0
            for wo in wos:
                if wo.get('creation_type') not in ['hackpipe', 'hackup']:
                    # Get the process information surrounding this wo's process from the project's pipeline
                    info2 = server.get_pipeline_processes_info(proj.get('__search_key__'),
                                                               related_process=wo.get('process'))
                    if 'input_processes' in info2.keys():
                        input_processes2 = info2.get('input_processes')
                        # WHACKER
                        whack_says = are_no_hackpipes_preceding(wo)
                        # END WHACKER
                        # If there are no input_processes, this must be one of the work orders to set to ready
                        # (unless hackpipe says otherwise)
                        if len(input_processes2) < 1 and whack_says:
                            wtask_code = wo.get('task_code')
                            # Get the task associated with the work order
                            wtask = server.eval("@SOBJECT(sthpw/task['code','%s'])" % wtask_code)
                            if wtask:
                                wtask = wtask[0]
                                wdata = {'active': active}
                                # If the task has not been raised above 'Pending' yet, and if active should be true,
                                # update the status to 'Ready'
                                if wtask.get('status') == 'Pending' and active:
                                    wdata['status'] = 'Ready'
                                server.update(wtask.get('__search_key__'), wdata, triggers=False)
                                updated_wo_count += 1
            # Get all the hack work orders stemming directly off of the proj
            hwos_expr = "@SOBJECT(twog/hackpipe_out['lookup_code','%s'])" % proj.get('code')
            hack_wos = server.eval(hwos_expr)
            for how in hack_wos:
                # If this is a work order, continue. If not, don't
                if 'WORK' in how.get('out_to'):
                    wo = server.eval("@SOBJECT(twog/work_order['code','%s'])" % how.get('out_to'))
                    if wo:
                        wo = wo[0]
                        wtask = server.eval("@SOBJECT(sthpw/task['code','%s'])" % wo.get('task_code'))
                        if wtask:
                            wtask = wtask[0]
                            wdata = {'active': active}
                            if wtask.get('status') == 'Pending' and active:
                                wdata['status'] = 'Ready'
                            server.update(wtask.get('__search_key__'), wdata, triggers=False)
                            updated_wo_count += 1
            if updated_wo_count == 0:
                wo_dict = {}
                for wo in wos:
                    if wo.get('creation_type') not in ['hackpipe', 'hackup']:
                        info = server.get_pipeline_processes_info(server.build_search_key('twog/proj', proj.get('code')),
                                                                  related_process=wo.get('process'))
                        input_processes = info.get('input_processes')
                        if wo.get('code') not in wo_dict.keys():
                            wo_dict[wo.get('code')] = 0
                        for in_p in input_processes:
                            wo_alive_expr = "@SOBJECT(twog/work_order['proj_code','%s']['process','%s'])" % (proj.get('code'), in_p)
                            wo_alive = server.eval(wo_alive_expr)
                            wo_dict[wo.get('code')] += len(wo_alive)
                for pd in wo_dict.keys():
                    if wo_dict[pd] == 0:
                        wtask = server.eval("@SOBJECT(sthpw/task['lookup_code','%s']['status','Pending'])" % pd)
                        if wtask:
                            wtask = wtask[0]
                            server.update(wtask.get('__search_key__'), {'status': 'Ready'}, triggers=False)

        def loop_innerds(proj, hack, active):
            got_one = False
            # Get the object representing the proj's title
            parent = server.get_parent(proj.get('__search_key__'))
            # Get the pipeline information about which processes lead into and out of the proj process
            input_processes = []
            if not hack:
                info = server.get_pipeline_processes_info(parent.get('__search_key__'),
                                                          related_process=proj.get('process'))
                input_processes = info.get('input_processes')
            else:
                hack_rez = are_no_hackpipes_preceding(proj)
                if not hack_rez:
                    input_processes.append("TRIPWIRE")
            # If there are no input processes for this, it must be one of the proj's that should be set to 'Ready'
            # (but we'll need to check hackpipe first)
            if input_processes is not None and len(input_processes) < 1:
                ptask_code = proj.get('task_code')
                # Get the actual task associated with the proj
                ptask = server.eval("@SOBJECT(sthpw/task['code','%s'])" % ptask_code)
                if ptask:
                    ptask = ptask[0]
                    # We'll be setting active to on or off anyway...
                    pdata = {'active': active}
                    # PHACKER
                    phack_says = are_no_hackpipes_preceding(proj)
                    # END PHACKER
                    if ptask.get('status') == 'Pending' and active and phack_says:
                        pdata['status'] = 'Ready'
                        got_one = True
                        server.update(ptask.get('__search_key__'), pdata, triggers=False)
                        do_wo_loop(proj, active)
            return got_one

        from pyasm.common import TacticException
        from pyasm.common import SPTDate
        update_data = input.get('update_data')
        prev_data = input.get('prev_data')
        old_classification = prev_data.get('classification').replace(' ', '_').lower()
        classification = update_data.get('classification').replace(' ', '_').lower()
        sobject = input.get('sobject')
        sob_code = sobject.get('code')
        is_in_production = False
        errors_bool = False
        error_count = {}
        order_sk = ''
        titles = []
        # Need to disallow going to 'completed' from anything other than 'in_production'
        if classification == 'completed' and old_classification != 'in_production':
            raise TacticException("You can only select 'Completed' if your order's current classification is 'in_production'.")
        elif classification == 'completed' and old_classification == 'in_production':
            server.update(input.get('search_key'), {'completion_date': SPTDate.convert_to_local(make_timestamp()),
                                                    'needs_completion_review': False})
        # Need to force the order checker to check if going into in_production from anything other than 'completed'  
        if classification == 'in_production':
            is_in_production = True
            wo_under = server.eval("@GET(twog/title['order_code','%s'].twog/proj.twog/work_order.code)" % sob_code)
            if len(wo_under) < 1:
                raise TacticException("You have to build your order before you can put it into production.")
            else:
                order_sk = server.build_search_key('twog/order', sob_code)
                titles = server.eval("@SOBJECT(twog/title['order_code','%s'])" % sob_code)
                work_order_count_update = {}
                total_order_wos = 0
                total_order_completed = 0
                for title in titles:
                    title_code = title.get('code')
                    tasks_total = server.eval("@COUNT(sthpw/task['title_code','%s']['lookup_code','~','WORK_ORDER'])" % title_code)
                    tasks_completed = server.eval("@COUNT(sthpw/task['title_code','%s']['lookup_code','~','WORK_ORDER']['status','Completed'])" % title_code)
                    if tasks_total in ['', None]:
                        tasks_total = 0
                    if tasks_completed in ['', None]:
                        tasks_completed = 0
                    work_order_data = {'wo_count': tasks_total, 'wo_completed': tasks_completed}
                    work_order_count_update[title.get('__search_key__')] = work_order_data
                    total_order_wos = total_order_wos + tasks_total
                    total_order_completed = total_order_completed + tasks_completed
                work_order_count_update[order_sk] = {'wo_count': total_order_wos, 'wo_completed': total_order_completed}
                # I have no idea if triggers should be ignored on this update_multiple
                server.update_multiple(work_order_count_update)

            if old_classification != 'completed':
                from order_builder import OrderCheckerWdg
                ocw = OrderCheckerWdg(sk=input.get('search_key'))
                error_count = ocw.return_error_count_dict()
                if error_count['Critical'] > 0:
                    errors_bool = True
        # GET ALL TITLE CODES ATTACHED THE THE SOBJ (The Order)
        title_codes = server.eval("@GET(twog/title['order_code','%s'].code)" % sob_code)
        if is_in_production and not errors_bool:
            for tcode in title_codes:
                # Get all projs attached to each title
                projs_expr = "@SOBJECT(twog/proj['title_code','%s'])" % tcode
                projs = server.eval(projs_expr)
                good_projs = 0
                for project in projs:
                    created_by_hack = project.get('creation_type') in ['hackpipe', 'hackup']
                    if loop_innerds(project, created_by_hack, is_in_production):
                        good_projs += 1
                if good_projs == 0:
                    proj_dict = {}
                    for project in projs:
                        if project.get('creation_type') not in ['hackpipe', 'hackup']:
                            info = server.get_pipeline_processes_info(server.build_search_key('twog/title', tcode),
                                                                      related_process=project.get('process'))
                            input_processes = info.get('input_processes')
                            if project.get('code') not in proj_dict.keys():
                                proj_dict[project.get('code')] = 0
                            for in_p in input_processes:
                                proj_alive_expr = "@SOBJECT(twog/proj['title_code','%s']['process','%s'])" % (tcode, in_p)
                                proj_alive = server.eval(proj_alive_expr)
                                proj_dict[project.get('code')] += len(proj_alive)
                    for pd in proj_dict.keys():
                        if proj_dict[pd] == 0:
                            ptask = server.eval("@SOBJECT(sthpw/task['lookup_code','%s']['status','Pending'])" % pd)
                            if ptask:
                                ptask = ptask[0]
                                server.update(ptask.get('__search_key__'), {'status': 'Ready'}, triggers=False)
                                for project in projs:
                                    if project.get('code') == ptask.get('lookup_code'):
                                        do_wo_loop(project, is_in_production)

        if errors_bool:
            raise TacticException('You still have %s critical errors with your order. You may put this into production once you fix the errors.' % error_count['Critical'])
        else:
            # now make sure that all tasks under this order are set to active or off active
            task_search_keys = server.eval("@GET(sthpw/task['order_code','{0}'].__search_key__)".format(sob_code))
            task_update_data = dict.fromkeys(task_search_keys, {'active': is_in_production})
            server.update_multiple(task_update_data, triggers=False)
            if classification == 'in_production':
                from pyasm.common import Environment
                from cost_builder.cost_calculator import CostCalculator
                login = Environment.get_login()
                user = login.get_login()
                ccw = CostCalculator(order_code=sob_code, user=user)
                cost_arr = ccw.update_costs()
                # Update actual start dates for the order and titles
                datetime_now = SPTDate.convert_to_local(make_timestamp())
                update_start_date_keys = [title.get('__search_key__') for title in titles]
                update_start_date_keys.insert(0, order_sk)
                update_start_date_data = dict.fromkeys(update_start_date_keys, {'actual_start_date': datetime_now})
                # I have no idea if triggers should be ignored on this update_multiple
                server.update_multiple(update_start_date_data)

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
