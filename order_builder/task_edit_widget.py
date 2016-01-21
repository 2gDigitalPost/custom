from pyasm.common import Environment
from pyasm.widget import SelectWdg
from pyasm.search import Search
from pyasm.web import Table

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import CalendarInputWdg

from order_builder_utils import get_save_task_info_behavior
from common_tools.common_functions import fix_date


class TaskEditWdg(BaseRefreshWdg):
    def init(self):
        self.task_code = self.kwargs.get('task_code', '')
        self.task_pipelines = ''
        self.parent_sk = self.kwargs.get('parent_sk', '')
        self.parent_pyclass = ''
        self.order_sk = self.kwargs.get('order_sk', '')
        self.groups = Environment.get_group_names()

        if 'user' in self.kwargs.keys():
            self.user = str(self.kwargs.get('user'))
        else:
            self.user = Environment.get_user_name()

    def get_assigned_group_select(self, assigned):
        where_str = "('user','client','compression supervisor','edit supervisor','machine room supervisor','media vault supervisor','qc supervisor','sales supervisor','scheduling supervisor','streamz','executives','admin','management','office employees','it')"
        group_search = Search("sthpw/login_group")
        group_search.add_where("\"login_group\" not in %s" % where_str)
        groups = group_search.get_sobjects()

        group_sel = SelectWdg('task_assigned_group_select')
        if len(groups) > 0:
            group_sel.append_option('--Select--', '')
            if assigned:
                group_sel.set_value(assigned)
            else:
                group_sel.set_value('')
            for group in groups:
                group_sel.append_option(group.get_value('login_group'), group.get_value('login_group'))
        return group_sel

    def get_assigned_select(self, assigned):
        workers_search = Search("sthpw/login")
        workers_search.add_filter('location', 'internal')
        workers_search.add_filter('license_type', 'user')
        workers = workers_search.get_sobjects()
        work_sel = SelectWdg('task_assigned_select')
        if len(workers) > 0:
            work_sel.append_option('--Select--', '')
            if assigned:
                work_sel.set_value(assigned)
            else:
                work_sel.set_value('')
            for worker in workers:
                work_sel.append_option(worker.get_value('login'), worker.get_value('login'))
        return work_sel

    def get_statuses_select_from_task_pipe(self, status, pipe_code, search_type, task_sk, user_is_scheduler):
        # gets the processes from the sobject's pipeline
        statuses = ['Pending', 'Ready', 'On Hold', 'Client Response', 'Fix Needed', 'Rejected', 'In Progress',
                    'DR In Progress', 'Amberfin01 In Progress', 'Amberfin02 In Progress', 'BATON In Progress',
                    'Export In Progress', 'Need Buddy Check', 'Buddy Check In Progress', 'Completed']
        task_select = SelectWdg('task_stat_select')
        task_select.add_attr('old_status', status)
        task_select.add_attr('id', 'status_{0}'.format(task_sk))
        if len(statuses) > 0:
            task_select.append_option('--Select--', '')
            task_select.set_value(status)
            for stat in statuses:
                if stat == 'On Hold' and user_is_scheduler:
                    task_select.append_option(stat, stat)
                if stat == 'Approved':
                    task_select.append_option('Rejected', 'Rejected')
                task_select.append_option(stat, stat)
                if stat == 'Approved':
                    task_select.append_option('Completed', 'Completed')

        return task_select

    def get_display(self):
        pyclass_dict = {
            'twog/title': 'TitleRow',
            'twog/order': 'OrderTable',
            'twog/proj': 'ProjRow',
            'twog/work_order': 'WorkOrderRow',
            'twog/equipment_used': 'EquipmentUsedRow'
        }

        groups_str = ''
        user_group_names = Environment.get_group_names()
        for mg in user_group_names:
            if groups_str == '':
                groups_str = mg
            else:
                groups_str = '%s,%s' % (groups_str, mg)

        if 'scheduling' in groups_str:
            user_is_scheduler = True
        else:
            user_is_scheduler = False

        table = Table()
        table.add_attr('class', 'task_table')
        table.add_attr('width', '100%')
        if self.task_code in ['', None]:
            table.add_row()
            table.add_cell('')
        else:
            self.parent_pyclass = pyclass_dict[self.parent_sk.split('?')[0]]
            table.add_style('background-color: 90a0b5;')
            task_search = Search("sthpw/task")
            task_search.add_filter('code', self.task_code)
            tasks_found = task_search.get_sobjects()
            if len(tasks_found) > 0:
                task = tasks_found[0]
                hours_search = Search('sthpw/work_hour')
                hours_search.add_filter('task_code', task.get_code())
                hours = hours_search.get_sobjects()
                hours_added = 0
                for hour in hours:
                    hour_num = hour.get_value('straight_time')
                    if hour_num in [None, '']:
                        hour_num = 0
                    hour_num = float(hour_num)
                    hours_added = float(hours_added) + hour_num
                pipe_code = task.get_value('pipeline_code')
                if 'task' not in pipe_code:
                    pipe_code = 'task'
                task_select = self.get_statuses_select_from_task_pipe(task.get_value('status'),
                                                                      pipe_code,
                                                                      'sthpw/pipeline',
                                                                      task.get_search_key(),
                                                                      user_is_scheduler)
                worker_select = self.get_assigned_select(task.get_value('assigned'))
                group_select = self.get_assigned_group_select(task.get_value('assigned_login_group'))
                table.add_row()
                top = table.add_cell('<b>Assignment Information<b>')
                top.add_attr('colspan', '4')
                top.add_attr('align', 'center')
                top.add_style('background-color: #6789b7;')
                table.add_row()
                table.add_cell('Status: ')
                table.add_cell(task_select)
                table.add_cell('Assigned: ')
                table.add_cell(worker_select)
                table.add_row()
                table.add_cell('Hours Added:')
                table.add_cell(hours_added)
                table.add_cell('Add Hours:')
                table.add_cell('<input type="text" class="hour_adder" value=""/>')
                table.add_row()
                table.add_cell('Priority: ')
                table.add_cell('<input type="text" class="priority_setter" value="%s"/>' % task.get_value('priority'))
                table.add_cell('Assigned Group: ')
                table.add_cell(group_select)
                bid_start = CalendarInputWdg(name='task_bid_start')  # 4.2
                bid_start.set_option('show_time', 'true')
                bid_start.set_option('show_activator', 'true')
                bid_start.set_option('display_format', 'MM/DD/YYYY HH:MM')
                bid_start.set_option('time_input_default', '5:00 PM')
                if task.get_value('bid_start_date') not in ['', None]:
                    bid_start.set_option('default', fix_date(task.get_value('bid_start_date')))
                bid_end = CalendarInputWdg(name='task_bid_end')  # 4.2
                bid_end.set_option('show_time', 'true')
                bid_end.set_option('show_activator', 'true')
                bid_end.set_option('display_format', 'MM/DD/YYYY HH:MM')
                bid_end.set_option('time_input_default', '5:00 PM')
                if task.get_value('bid_end_date') not in ['', None]:
                    bid_end.set_option('default', fix_date(task.get_value('bid_end_date')))
                table.add_row()
                bs = table.add_cell('Bid Start: ')
                bs.add_attr('nowrap', 'nowrap')
                table.add_cell(bid_start)
                be = table.add_cell('Due Date: ')
                be.add_attr('nowrap', 'nowrap')
                table.add_cell(bid_end)
                table.add_row()
                acs = table.add_cell('Actual Start: ')
                acs.add_attr('nowrap', 'nowrap')
                acsv = fix_date(task.get_value('actual_start_date'))
                if acsv in ['', None]:
                    acsv = 'Has not begun'
                table.add_cell(acsv)
                ace = table.add_cell('Actual End: ')
                acev = fix_date(task.get_value('actual_end_date'))
                if acev in ['', None]:
                    acev = 'Has not ended'
                ace.add_attr('nowrap', 'nowrap')
                table.add_cell(acev)
                table.add_row()

                doubl = table.add_cell('<input type="button" value="Save"/>')
                doubl.add_attr('colspan', '4')
                doubl.add_attr('align', 'center')
                doubl.add_behavior(get_save_task_info_behavior(task.get_search_key(), self.parent_sk,
                                                               self.parent_pyclass, self.order_sk, 'false', self.user))
            else:
                table.add_row()
                table.add_cell('')

        return table
