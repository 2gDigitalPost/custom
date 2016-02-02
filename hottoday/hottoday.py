import datetime

from pyasm.web import DivWdg, Table
from pyasm.search import Search
from pyasm.common import Environment
from tactic.ui.common import BaseRefreshWdg, BaseTableElementWdg
from common_tools.common_functions import title_case, abbreviate_text
from hottoday_utils import get_date_status, get_client_img, get_platform_img, get_launch_note_behavior,\
    bring_to_top, show_change, save_priorities, get_scrollbar_width
from order_builder import OrderBuilderLauncherWdg
from order_builder.taskobjlauncher import TaskObjLauncherWdg


class HotTodayRibbonWdg(BaseTableElementWdg):
    """
    This is the little red ribbon widget that appears in the bottom left corner of the title's row. It only shows
    up for users that can change priority and hot today status. Clicking on it will prompt the user to confirm
    that they want to remove the item from the Hot List. If they confirm, the item is removed from the table,
    its status as a hot item is removed, and the table is refreshed.
    """

    def init(self):
        nothing = 'true'
        self.title_name = self.kwargs.get('title_name')
        self.code = self.kwargs.get('code')
        self.bigboard = self.kwargs.get('bigboard')
        self.search_key = self.kwargs.get('search_key')

    @staticmethod
    def get_launch_behavior():
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
            try {
                var server = TacticServerStub.get();

                var my_sk = bvr.src_el.get('sk');

                var nothing_else = false;
                var changed = false;

                var unchecked_image = '/context/icons/silk/rosette_grey.png';

                if (confirm("Do you really want to take this off the Hot Today list?")) {
                    server.update(my_sk, {'bigboard': 'false'});
                    changed = true;

                    nothing_else = true;
                    //spt.app_busy.show("Refreshing...");
                    //var board_table = bvr.src_el.getParent('#bigboard');
                    //var board_table = document.getElementById('hotlist_div');
                    var board_table = bvr.src_el.getParent('#hotlist_div');
                    spt.api.refresh_panel(board_table);
                    //spt.app_busy.hide();
                }

                if (!nothing_else && changed) {
                    var inner = bvr.src_el.innerHTML;
                    in1 = inner.split('src="')[0];
                    in1 = in1 + 'src="' + unchecked_image + '"/>';
                    bvr.src_el.innerHTML = in1;
                }
            }
            catch(err) {
                spt.app_busy.hide();
                spt.alert(spt.exception.handler(err));
            }
        '''
                    }
        return behavior

    def get_display(self):
        # TODO: Rewrite the display so that it doesn't return an entire table
        table = Table()

        if self.bigboard:
            ribbon_image = '/context/icons/silk/rosette.png'
            state = 'checked'
        else:
            ribbon_image = '/context/icons/silk/rosette_grey.png'
            state = 'unchecked'

        table.add_row()
        ribbon_cell = table.add_cell(
            '<img border="0" style="vertical-align: middle" title="" src="{0}">'.format(ribbon_image))
        ribbon_cell.add_attr('id', 'title_bigboard_{0}'.format(self.code))
        ribbon_cell.add_attr('sk', self.search_key)
        ribbon_cell.add_attr('state', state)
        ribbon_cell.add_style('cursor: pointer;')

        ribbon_cell.add_behavior(self.get_launch_behavior())

        return table


class HotTodayWdg(BaseRefreshWdg):
    """
    My attempt at rewriting the Hot Today table.
    """

    TASK_COLOR_DICT = {
        'pending': '#D7D7D7',
        'ready': 'B2CEE8',
        'in progress': 'F5F3A4',
        'on hold': '#E8B2B8',
        'client response': '#DDD5B8',
        'completed': '#B7E0A5',
        'need buddy check': '#E3701A',
        'internal rejection': '#FF0000',
        'external rejection': '#FF0000',
        'failed qc': '#FF0000',
        'rejected': '#FF0000',
        'fix needed': '#C466A1',
        'dr in progress': '#D6E0A4',
        'amberfin01 in progress': '#D8F1A8',
        'amberfin02 in progress': '#F3D291',
        'baton in progress': '#C6E0A4',
        'export in progress': '#796999',
        'buddy check in progress': '#1AADE3'
    }

    DATE_STATUS_COLOR = {
        'on_time': '#66DC00',
        'due_today': '#E0B600',
        'late': '#FF0000'
    }

    @staticmethod
    def get_header_groups(tasks):
        group_order = ['machine room', 'media vault', 'onboarding', 'compression', 'edit', 'audio', 'localization',
                       'qc', 'streamz', 'vault', 'edeliveries']
        header_groups = []

        for task in tasks:
            group = task.get_value('assigned_login_group')
            if group not in header_groups:
                header_groups.append(group)

        # TODO: Refactor the line below, surely a cleaner way to get the groups in order
        header_groups = [group for group in group_order if group in header_groups]

        return header_groups

    @staticmethod
    def set_header(table, groups):
        """
        Construct the header for the Hot Today table, then add it to the table.

        :param table: The table to add the header to
        :param groups: The columns for the header
        :return: None
        """
        header_row = table.add_row()

        header_row.add_style('background-color', '#E0E0E0')
        header_row.add_style('width', '100%')
        header_row.add_style('display', 'table')

        # Add the title cell, it won't be included in the groups list since it should always be there by default
        title_cell = table.add_header(title_case('title'), row=header_row)
        title_cell.add_style('padding', '10px')
        title_cell.add_style('width', '24%')
        title_cell.add_style('background-color', '#F2F2F2')
        title_cell.add_style('border', '1px solid #E0E0E0')

        for group in groups:
            group_cell = table.add_header(title_case(group), row=header_row)
            group_cell.add_style('padding', '10px')
            group_cell.add_style('background-color', '#F2F2F2')
            group_cell.add_style('border', '1px solid #E0E0E0')
            group_cell.add_style('width', '{0}%'.format(76.0 / len(groups)))

    def set_row(self, title, table, counter, header_groups, tasks, current_priority, is_admin_user):
        """
        Construct a row in the Hot Today list and add it to the table.

        :param title: The title object
        :param table: The entire table that the row is being added to
        :param counter: Integer that displays next to the Title's name
        :param header_groups: List of each column in the table
        :param tasks: List of task objects
        :param current_priority: Decimal
        :param is_admin_user: Boolean
        :return: None
        """

        name = title.get_value('title')
        code = title.get_value('code')
        episode = title.get_value('episode')
        client = title.get_value('client_name')
        client_code = title.get_value('client_code')
        platform = title.get_value('platform')
        due_date = datetime.datetime.strptime(title.get_value('due_date'), '%Y-%m-%d %H:%M:%S')
        expected_delivery_date = datetime.datetime.strptime(title.get_value('expected_delivery_date'),
                                                            '%Y-%m-%d %H:%M:%S')
        requires_mastering_qc = title.get_value('requires_mastering_qc', False)
        is_external_rejection = title.get_value('is_external_rejection', False)
        is_redo = title.get_value('redo', False)

        # If there is an 'episode', append it to the title's name
        if episode:
            name += ' Episode ' + episode

        # TODO: Apparently is_external_rejection is either 'true' or 'false', Javascript style. Fix that.
        if is_external_rejection:
            if is_external_rejection == 'true':
                is_external_rejection = True
            elif is_external_rejection == 'false':
                is_external_rejection = False

        # Set the row's background color. Different statuses require different colors. The statuses are not necessarily
        # mutually exclusive, but they are ordered by priority.
        if is_external_rejection:
            title_cell_background_color = '#B55252'
        elif is_redo:
            title_cell_background_color = '#FFCC00'
        elif requires_mastering_qc:
            title_cell_background_color = '#C8A2C8'
        else:
            title_cell_background_color = '#D7D7D7'

        # Put together the title cell for the table. It includes the name, delivery date, status, and other info
        title_table = Table()
        title_table.add_style('width', '100%')

        # If the order requires QC Mastering, add that above the first row
        if requires_mastering_qc:
            mastering_qc_row = title_table.add_row()
            mastering_qc_row.add_style('color', 'red')
            mastering_qc_row.add_style('font-size', '14px')
            mastering_qc_row.add_style('font-weight', 'bold')

            title_table.add_cell(data='Requires QC Mastering', row=mastering_qc_row)

        # First row: Number (counter) and name
        name_row = title_table.add_row()
        name_row.add_style('font-size', '14px')
        name_row.add_style('font-weight', 'bold')

        name_data = '<span style="color: #FF0000">{0}.</span> <u>{1}</u>'.format(counter, name)

        title_table.add_cell(data=name_data, row=name_row, css='title-row')

        # Second row: Title's code (TITLE#####), Client, and Platform
        code_row = title_table.add_row()
        code_row.add_style('font-size', '12px')

        # Find the client image
        client_image_src = get_client_img(client_code)

        if client_image_src:
            client_image = '<img src="{0}" title="{1}" alt="{1}" style="width: 32px; height: 32px;">'.format(
                    client_image_src, client)
        else:
            client_image = '<b>{0}</b>'.format(client)

        client_data = '<b>Client:</b> {0}'.format(client_image)

        # Find the platform image
        platform_image_src = get_platform_img(platform)

        if platform_image_src:
            platform_image = '<img src="{0}" title="{1}" alt="{1}" style="width: 32px; height: 32px;">'.format(
                    platform_image_src, platform)
        else:
            platform_image = '<i>{0}</i>'.format(platform)

        platform_data = '<i>Platform: </i>{0}'.format(platform_image)

        code_cell = title_table.add_cell(data=code, row=code_row)
        client_cell = title_table.add_cell(data=client_data, row=code_row)
        platform_cell = title_table.add_cell(data=platform_data, row=code_row)
        code_cell.add_style('padding-right', '3px')
        client_cell.add_style('padding-left', '3px')
        client_cell.add_style('padding-right', '3px')
        platform_cell.add_style('padding-left', '3px')

        # Third Row: Deliver By Date
        self.set_date_row(title_table, expected_delivery_date, 'Deliver By')

        # Fourth Row: Due Date
        self.set_date_row(title_table, due_date, 'Due Date')

        # Last Row: Order Builder and Notes Widgets
        editing_row = title_table.add_row()

        order_builder = OrderBuilderLauncherWdg(code=title.get_value('order_code'))

        title_table.add_cell(data=order_builder, row=editing_row)

        notes = title_table.add_cell('<img src="/context/icons/silk/note_add.png"/>')
        notes.add_style('cursor: pointer;')
        notes.add_behavior(get_launch_note_behavior(title.get_search_key(), name))

        if is_admin_user:
            priority_row = title_table.add_row()
            priority_row.add_style('font-size', '16px')

            offbutt = HotTodayRibbonWdg(title_name=name, code=code, bigboard=title.get_value('bigboard'),
                                        search_key=title.get_search_key())

            dblbb = title_table.add_cell(data=offbutt, row=priority_row)
            dblbb.add_attr('width', '20px')

            dblpr = title_table.add_cell(data='Set At #: ', row=priority_row)
            dblpr.add_attr('align', 'left')

            prioid = 'prio_{0}'.format(counter)

            # TODO: Figure out how to get the external rejection search key and what it's used for
            external_rejection_search_key = ''

            ami_extr = 'false'
            row_priority = title.get_value('priority')

            if external_rejection_search_key:
                ami_extr = 'true'
                row_priority = current_priority

            dbltxt = title_table.add_cell(data='<input type="text" value="{0}" row_type="title" title_sk="{1}" current_count="{0}" current_priority="{2}" class="count_order" id="{3}" external_rejection="{4}" ext_sk="{5}" style="background-color: #FFFFFF;"/>'.format(counter, title.get_search_key(), row_priority, prioid, ami_extr, external_rejection_search_key), row=priority_row)
            dbltxt.add_attr('align', 'left')
            dbltxt.add_behavior(show_change(prioid))

        current_row = table.add_row()
        current_row.add_style('width', '100%')
        current_row.add_style('height', 'auto')
        current_row.add_style('vertical-align', 'top')

        # Add the title table to the table row
        title_cell = table.add_cell(title_table, row=current_row)
        title_cell.add_style('background-color', title_cell_background_color)
        title_cell.add_style('border', '1px solid #EEE')
        title_cell.add_style('padding', '4px')
        title_cell.add_style('width', '24%')

        # Now add the cells for each column. Add the data in each column as necessary, or just add a blank cell
        # if no data exists.
        for column in header_groups:
            column_tasks = [task for task in tasks if task.get_value('assigned_login_group') == column]
            if column_tasks:
                # Fill the cell with the tasks on this title
                task_table = Table()
                task_table.add_style('width', '100%')
                task_table.add_style('font-size', '10px')

                for task in column_tasks:
                    current_task_row = task_table.add_row()
                    current_task_row.add_style('background-color',
                                               self.TASK_COLOR_DICT.get(task.get_value('status').lower(), '#000000'))
                    current_task_row.add_style('padding', '3px')
                    current_task_row.add_style('min-height', '20px')
                    current_task_row.add_style('border-top-left-radius', '10px')
                    current_task_row.add_style('border-bottom-left-radius', '10px')
                    current_task_row.add_attr('title', task.get_value('lookup_code'))

                    inspect_button = TaskObjLauncherWdg(code=task.get_value('lookup_code'),
                                                        name=task.get_value('process'))
                    task_table.add_cell(data=inspect_button, row=current_task_row)

                    # Each task in the row will have the following properties to be displayed
                    cell_names = ['process', 'status', 'assigned', 'bid_end_date']

                    # Add each property from left to right in the current task row. Abbreviate the text to make it
                    # fit better
                    for cell_name in cell_names:
                        task_table.add_cell(data=abbreviate_text(task.get_value(cell_name), 7), row=current_task_row)

                row_cell = table.add_cell(task_table)
                row_cell.add_style('border', '1px solid #EEE')
                row_cell.add_style('vertical-align', 'top')
                row_cell.add_style('width', '{0}%'.format(76.0 / len(header_groups)))
            else:
                row_cell = table.add_cell()
                row_cell.add_style('border', '1px solid #EEE')
                row_cell.add_style('width', '{0}%'.format(76.0 / len(header_groups)))

    def set_date_row(self, table, date, row_text):
        """
        Given a table, set up a row to display the Deliver By or Due Date data. The rows are basically set up the
        same way, only the dates given and the text to display differ.

        :param table: The table to set the rows on.
        :param date: Datetime in the format '%Y-%m-%d %H:%M:%S' (other formats might work, but that's untested)
        :param row_text: String ('Deliver By'/'Due Date')
        :return:
        """
        date_row = table.add_row()

        date_status = get_date_status(date)
        date_status_color = self.DATE_STATUS_COLOR.get(date_status, '#000000')

        date_row.add_style('color', date_status_color)
        date_row.add_style('font-size', '14px')
        date_row.add_style('font-weight', 'bold')
        date_row.add_style('text-shadow', '1px 1px #000000')

        delivery_date_data = '{0}: {1}'.format(row_text, date)

        table.add_cell(data=delivery_date_data, row=date_row)

    @staticmethod
    def set_priority_row(table, priority):
        """
        Set the row showing the priority of the titles. This appears above a title row, and simply displays a decimal
        number corresponding to the following titles' priority.

        :param table: The "Hot Today" table
        :param priority: The priority of the following items (decimal)
        :return: None
        """
        current_row = table.add_row()
        current_row.add_style('width', '100%')
        current_row.add_style('height', 'auto')

        priority_row = table.add_cell(priority, row=current_row)
        priority_row.add_style('background-color', '#DCE3EE')

    @staticmethod
    def get_tasks(hot_items):
        """
        Given a list of 'titles', return all the tasks associated with those titles. Return only those marked as
        'active' and that are not marked as 'completed'.

        :param hot_items: A list of titles from 'twog/title'
        :return: List of tasks
        """
        title_codes = []

        for item in hot_items:
            title_codes.append("'{0}'".format(item.get_value('code')))

        title_codes_string = ','.join(title_codes)

        task_search = Search("sthpw/task")
        task_search.add_filter('bigboard', True)
        task_search.add_filter('active', '1')
        task_search.add_filter('search_type', 'twog/proj?project=twog')
        task_search.add_filter('status', 'Completed', op="!=")

        task_search.add_where('\"title_code\" in ({0})'.format(title_codes_string))

        task_search_results = task_search.get_sobjects()

        return task_search_results

    @staticmethod
    def get_buttons(is_admin_user):
        btns = Table()
        btns.add_attr('class', 'auto_buttons')
        btns.add_row()

        to_top = btns.add_cell('<input type="button" value="Go To Top"/>')
        to_top.add_behavior(bring_to_top())

        if is_admin_user:
            saveit = btns.add_cell('<input type="button" value="Save Priorities"/>')
            saveit.add_behavior(save_priorities())

        return btns

    def get_display(self):
        table = Table()
        table.add_attr('id', 'bigboard')
        table.add_style('width', '100%')
        table.add_style('background-color', '#FCFCFC')
        table.add_style('font-size', '12px')
        table.add_style('font-family', 'Helvetica')
        table.add_border(style='solid', color='#F2F2F2', size='1px')

        # print("GETGROUPNAMES: %s" % Environment.get_group_names())
        # if 'client' in Environment.get_group_names():
        #     return table

        # Because Tactic doesn't allow for the <thead> element (that I know of), the table header has to be split
        # into it's own <tbody>. Highly inelegant, but I don't have a choice.
        header_body = table.add_tbody()
        header_body.add_style('display', 'block')
        header_body.add_attr('id', 'thead-section')

        # Get the titles that fall under 'external rejection' (they need to be on the top of the board)
        search_for_external_rejections = Search('twog/title')
        search_for_external_rejections.add_filter('is_external_rejection', 'true')
        search_for_external_rejections.add_filter('bigboard', True)
        search_for_external_rejections.add_filters(name='status', values=['Completed'], op='not in')
        external_rejections_sobjects = search_for_external_rejections.get_sobjects()

        # Search for titles that are marked as 'hot'
        search_for_hot_items = Search('twog/title')
        search_for_hot_items.add_filter('bigboard', True)
        search_for_hot_items.add_filter('is_external_rejection', 'false')
        search_for_hot_items.add_order_by('priority')
        search_for_hot_items.add_order_by('expected_delivery_date')
        hot_items_sobjects = search_for_hot_items.get_sobjects()

        hot_items = external_rejections_sobjects
        hot_items.extend([hot_item for hot_item in hot_items_sobjects if hot_item.get_value('status') != 'Completed'])

        # hot_items = [hot_item for hot_item in hot_items if hot_item.get_value('status') != 'Completed']

        tasks = self.get_tasks(hot_items)

        # Current priority will be updated each time a title has a different priority from the last value
        current_priority = 0
        title_counter = 1

        # Get a list of all the users allowed to change priorities on the list. Only they will be able to see
        # the input box to change priority.
        is_admin_user = False

        admin_search = Search("twog/global_resource")
        admin_search.add_filter('name', 'Usernames Allowed Hot Today Changes')
        admin_search_object = admin_search.get_sobject()

        if admin_search_object:
            # The users allowed to make priority changes are stored in the 'description' section of this sobject,
            # in a comma separated list
            admin_users = admin_search_object.get_value('description').split(',')

            # Check if current user is in the list (no idea why you need get_login twice, but it doesn't work otherwise)
            if Environment.get_login().get_login() in admin_users:
                is_admin_user = True

        # 'title' is also in the headers, but since that always displays we'll leave it out here
        header_groups = self.get_header_groups(tasks)
        self.set_header(table, header_groups)

        hotlist_body = table.add_tbody()
        hotlist_body.add_style('display', 'block')
        hotlist_body.add_style('overflow-x', 'hidden')
        hotlist_body.add_style('overflow-y', 'scroll')
        hotlist_body.add_style('height', '850px')
        hotlist_body.add_style('width', '100%')
        hotlist_body.add_attr('id', 'hotlist-body')

        # Put external rejections on the board first
        # for external_rejection in external_rejections:
        #     item_tasks = [task for task in tasks if task.get_value('title_code') == external_rejection.get_value('code')]
        #     self.set_row(external_rejection, table, title_counter, header_groups, item_tasks, current_priority, is_admin_user)

        #     title_counter += 1

        for hot_item in hot_items:
            hot_item_priority = float(hot_item.get_value('priority'))

            # Get the tasks that correspond to a title by comparing the task's title_code to the title's code
            item_tasks = [task for task in tasks if task.get_value('title_code') == hot_item.get_value('code')]

            # If an item requires QC Mastering, it should go on the hot board, regardless of if it has tasks or not
            requires_mastering_qc = hot_item.get_value('requires_mastering_qc', False)

            if item_tasks or requires_mastering_qc:

                if current_priority < hot_item_priority:
                    self.set_priority_row(table, hot_item_priority)
                    current_priority = hot_item_priority

                self.set_row(hot_item, table, title_counter, header_groups, item_tasks, current_priority, is_admin_user)

                title_counter += 1

        # Put the table in a DivWdg, makes it fit better with the Tactic side bar
        hotlist_div = DivWdg()
        hotlist_div.add_attr('id', 'hotlist_div')
        hotlist_div.add_style('height', '900px')
        hotlist_div.add_attr('overflow', 'hidden')

        hotlist_div.add(table)

        # Add an 'outer' div that holds the hotlist div, with the buttons below.
        outer_div = DivWdg()
        outer_div.add(hotlist_div)
        outer_div.add(self.get_buttons(is_admin_user))
        outer_div.add_behavior(get_scrollbar_width())

        return outer_div
