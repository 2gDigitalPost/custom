import datetime

from pyasm.web import DivWdg, Table
from pyasm.search import Search
from pyasm.common import Environment
from tactic.ui.common import BaseRefreshWdg, BaseTableElementWdg
from common_tools.common_functions import title_case, abbreviate_text
from hottoday_utils import get_date_status, get_client_img, get_platform_img, get_launch_note_behavior_for_hotlist, \
    bring_to_top, show_change, save_priorities, get_scrollbar_width, open_client_platform_connection_tab, \
    show_platform_connection
from order_builder import OrderBuilderLauncherWdg
from order_builder.taskobjlauncher import TaskObjLauncherWdg

from tactic_client_lib import TacticServerStub
from manual_updaters.client_platform_create import create_client_platform


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

    @staticmethod
    def set_extra_info_row(info_text, color, table):
        extra_info_row = table.add_row()
        extra_info_row.add_style('color', color)
        extra_info_row.add_style('font-size', '14px')
        extra_info_row.add_style('font-weight', 'bold')

        table.add_cell(data=info_text, row=extra_info_row)

    @staticmethod
    def set_connection_row(parent_table, row_text, row_color):
        connection_task_row = parent_table.add_row()
        connection_task_row.add_style('padding', '3px')
        connection_task_row.add_style('min-height', '20px')
        connection_task_row.add_style('border-top-left-radius', '10px')
        connection_task_row.add_style('border-bottom-left-radius', '10px')
        connection_task_row.add_style('background-color', row_color)

        connection_icon = parent_table.add_cell('<img border="0" style="vertical-align: middle" title="Inspect" name="Inspect" src="/context/icons/silk/information.png">')
        connection_icon.add_behavior(open_client_platform_connection_tab())
        connection_icon.add_style('cursor', 'pointer')

        connection_text = parent_table.add_cell(data=row_text, row=connection_task_row)
        connection_text.add_attr('colspan', '4')

    def set_row(self, title, table, counter, header_groups, tasks, current_priority, is_admin_user,
                is_external_rejection=False):
        """
        Construct a row in the Hot Today list and add it to the table.

        :param title: The title object
        :param table: The entire table that the row is being added to
        :param counter: Integer that displays next to the Title's name
        :param header_groups: List of each column in the table
        :param tasks: List of task objects
        :param current_priority: Decimal
        :param is_admin_user: Boolean
        :param is_external_rejection: Boolean (False by default)
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
        is_redo = title.get_value('redo', False)
        is_repurpose = title.get_value('repurpose', False)
        is_imf = title.get_value('imf', False)

        # If there is an 'episode', append it to the title's name
        if episode:
            name += ' Episode ' + episode

        # TODO: The way external rejections are recorded in the database is painfully stupid. Because of this, we're
        # passing in is_external_rejection into the function, rather than checking the title for the
        # is_external_rejection column. This should be fixed sooner rather than later.
        # is_external_rejection = title.get_value('is_external_rejection', False)
        # if is_external_rejection:
            # if is_external_rejection == 'true':
                # is_external_rejection = True
            # elif is_external_rejection == 'false':
                # is_external_rejection = False

        # Set the row's background color. Different statuses require different colors. The statuses are not necessarily
        # mutually exclusive, but since we can only have one background color, they are ordered by priority.
        if is_external_rejection:
            title_cell_background_color = '#B55252'
        elif is_redo:
            title_cell_background_color = '#FFCC00'
        elif requires_mastering_qc:
            title_cell_background_color = '#C8A2C8'
        elif is_repurpose:
            title_cell_background_color = '#4190B7'
        elif is_imf:
            title_cell_background_color = '#4D7D35'
        else:
            title_cell_background_color = '#D7D7D7'

        # Put together the title cell for the table. It includes the name, delivery date, status, and other info
        title_table = Table()
        title_table.add_style('width', '100%')

        # Repurposed titles and titles requiring Mastering QC need another row at the top of their table denoting
        # their special status
        if is_repurpose:
            self.set_extra_info_row('Repurposed Title', '#0C2FB7', title_table)
        if requires_mastering_qc:
            self.set_extra_info_row('Requires Mastering QC', 'red', title_table)
        if is_imf:
            self.set_extra_info_row('IMF', 'red', title_table)

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

        platform_data = '<b>Platform: </b>{0}'.format(platform_image)

        # The platform_code we need is not included in the Title sobject. We have to query for it using the platform name.
        platform_code_search = Search("twog/platform")
        platform_code_search.add_filter('name', platform)
        platform_search_object = platform_code_search.get_sobject()

        if platform_search_object:
            platform_code = platform_search_object.get_value('code')
        else:
            platform_code = ''

        if show_platform_connection():
            # Using the client_code and platform_code, search for an existing entry.
            client_platform_connection_search = Search("twog/client_platform")
            client_platform_connection_search.add_filter('client_code', client_code)
            client_platform_connection_search.add_filter('platform_code', platform_code)
            client_platform_connection = client_platform_connection_search.get_sobject()

        code_cell = title_table.add_cell(data='<strong>Title code:</strong> {0}'.format(code), row=code_row)
        code_cell.add_style('padding-top', '3px')
        code_cell.add_style('padding-bottom', '3px')
        code_cell.add_style('padding-left', '3px')

        client_row = title_table.add_row()

        client_cell = title_table.add_cell(data=client_data, row=client_row)
        platform_cell = title_table.add_cell(data=platform_data, row=client_row)

        client_cell.add_style('padding-left', '3px')
        client_cell.add_style('padding-right', '3px')
        client_cell.add_style('width', '35%')
        platform_cell.add_style('padding-left', '3px')

        # Third Row: A table containing the Client Deliver By and Expected Due Date dates
        self.set_dates_table(title_table, expected_delivery_date, due_date)

        # Last Row: Order Builder and Notes Widgets
        editing_row = title_table.add_row()

        order_builder = OrderBuilderLauncherWdg(code=title.get_value('order_code'))

        title_table.add_cell(data=order_builder, row=editing_row)

        notes = title_table.add_cell('<img src="/context/icons/silk/note_add.png"/>')
        notes.add_style('cursor: pointer;')
        notes.add_behavior(get_launch_note_behavior_for_hotlist(title.get_search_key(), name))

        if is_admin_user:
            priority_row = title_table.add_row()
            priority_row.add_style('font-size', '16px')

            offbutt = HotTodayRibbonWdg(title_name=name, code=code, bigboard=title.get_value('bigboard'),
                                        search_key=title.get_search_key())

            dblbb = title_table.add_cell(data=offbutt, row=priority_row)
            dblbb.add_attr('width', '20px')

            prioid = 'prio_{0}'.format(counter)

            # TODO: Figure out how to get the external rejection search key and what it's used for
            external_rejection_search_key = ''

            ami_extr = 'false'
            row_priority = title.get_value('priority')

            if external_rejection_search_key:
                ami_extr = 'true'
                row_priority = current_priority

            dbltxt = title_table.add_cell(data='Set At #: <input type="text" value="{0}" row_type="title" title_sk="{1}" current_count="{0}" current_priority="{2}" class="count_order" id="{3}" external_rejection="{4}" ext_sk="{5}" style="background-color: #FFFFFF;"/>'.format(counter, title.get_search_key(), row_priority, prioid, ami_extr, external_rejection_search_key), row=priority_row)
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
            if tasks:
                column_tasks = tasks.get(column)
            else:
                column_tasks = []

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
                    cell_names = ['process', 'status']

                    # Add each property from left to right in the current task row. Abbreviate the text to make it
                    # fit better
                    for cell_name in cell_names:
                        task_table.add_cell(data=abbreviate_text(task.get_value(cell_name), 7), row=current_task_row)

                if show_platform_connection() and column == 'edeliveries' and client_platform_connection:
                    connection_status = client_platform_connection.get_value('connection_status')

                    if connection_status == 'testing':
                        self.set_connection_row(task_table, 'Platform Status: Testing', 'yellow')
                    elif connection_status == 'disconnected':
                        self.set_connection_row(task_table, 'Platform Status: Disconnected', 'red')

                row_cell = table.add_cell(task_table)
                row_cell.add_style('border', '1px solid #EEE')
                row_cell.add_style('vertical-align', 'top')
                row_cell.add_style('width', '{0}%'.format(76.0 / len(header_groups)))
            else:
                task_table = Table()
                task_table.add_style('width', '100%')
                task_table.add_style('font-size', '10px')

                if show_platform_connection() and column == 'edeliveries' and client_platform_connection:
                    connection_status = client_platform_connection.get_value('connection_status')

                    if connection_status == 'testing':
                        self.set_connection_row(task_table, 'Platform Status: Testing', 'yellow')
                    elif connection_status == 'disconnected':
                        self.set_connection_row(task_table, 'Platform Status: Disconnected', 'red')

                    row_cell = table.add_cell(task_table)
                else:
                    row_cell = table.add_cell()

                row_cell.add_style('border', '1px solid #EEE')
                row_cell.add_style('width', '{0}%'.format(76.0 / len(header_groups)))

    def set_dates_table(self, parent_table, client_deliver_by_date, expected_due_date):
        """
        Sets a table showing the Client Deliver By and Expected Due Date. Both rows have a color depending on whether
        or not the title is past due, due today, or neither. Dates are displayed in a more human readable format.

        :param parent_table: The table containing the date table
        :param client_deliver_by_date: Timestamp in '%Y-%m-%d %H:%M:%S' format
        :param expected_due_date: Timestamp in '%Y-%m-%d %H:%M:%S' format
        :return: None
        """

        date_row = parent_table.add_row()

        date_table = Table()
        date_table.add_style('margin', '2px 0px')

        client_deliver_by_date_status = get_date_status(client_deliver_by_date)
        expected_due_date_status = get_date_status(expected_due_date)

        # Get the color statuses of each date. Set to black if no status found
        client_deliver_by_date_status_color = self.DATE_STATUS_COLOR.get(client_deliver_by_date_status, '#000000')
        expected_due_date_status_color = self.DATE_STATUS_COLOR.get(expected_due_date_status, '#000000')

        # The tr's for our td's in the table
        expected_due_date_row = date_table.add_row()
        client_deliver_by_row = date_table.add_row()

        # Set the row's color
        client_deliver_by_row.add_style('color', client_deliver_by_date_status_color)
        expected_due_date_row.add_style('color', expected_due_date_status_color)

        # Both rows will have the following styles
        for each_row in [client_deliver_by_row, expected_due_date_row]:
            each_row.add_style('font-size', '14px')
            each_row.add_style('font-weight', 'bold')
            each_row.add_style('text-shadow', '1px 1px #000000')

        # Set the td's for Client Deliver By row, get the second cell for the padding-left function below
        date_table.add_cell(data='Client Deliver By:', row=expected_due_date_row)
        expected_due_date_cell = date_table.add_cell(data=expected_due_date.strftime('%m-%d-%Y %I:%M %p'),
                                                     row=expected_due_date_row)

        # Set the td's for Expected Due Date row, get the second cell for the padding-left function below
        date_table.add_cell(data='Expected Due Date:', row=client_deliver_by_row)
        client_deliver_by_cell = date_table.add_cell(data=client_deliver_by_date.strftime('%m-%d-%Y %I:%M %p'),
                                                     row=client_deliver_by_row)

        # Add left side padding to each of the td's with the dates (looks a little better when rendered)
        map(lambda x: x.add_style('padding-left', '5px'), [client_deliver_by_cell, expected_due_date_cell])

        # Append the date table to the parent table and we're done
        parent_table.add_cell(data=date_table, row=date_row)

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

        # Because Tactic doesn't allow for the <thead> element (that I know of), the table header has to be split
        # into it's own <tbody>. Highly inelegant, but I don't have a choice.
        header_body = table.add_tbody()
        header_body.add_style('display', 'block')
        header_body.add_attr('id', 'thead-section')

        # Get the titles that fall under 'external rejection' (they need to be on the top of the board)
        search_for_external_rejections = Search('twog/title')
        search_for_external_rejections.add_filter('is_external_rejection', 'true')
        external_rejections_sobjects = search_for_external_rejections.get_sobjects()

        external_rejections = [hot_item for hot_item in external_rejections_sobjects if hot_item.get_value('status') != 'Completed']

        search_in_external_rejection_database = Search('twog/external_rejection')
        search_in_external_rejection_database.add_filter('status', 'Open')
        external_rejection_title_codes = [item.get_value('title_code') for item in search_in_external_rejection_database.get_sobjects()]
        external_rejection_title_codes = [code for code in external_rejection_title_codes if code not in [item.get_value('code') for item in external_rejections]]

        search_for_external_rejection_extra_titles = Search('twog/title')
        search_for_external_rejection_extra_titles.add_filters('code', external_rejection_title_codes)
        external_rejections.extend([item for item in search_for_external_rejection_extra_titles.get_sobjects()])

        # Search for titles that are marked as 'hot'
        search_for_hot_items = Search('twog/title')
        search_for_hot_items.add_filter('bigboard', True)
        search_for_hot_items.add_filter('is_external_rejection', 'false')
        search_for_hot_items.add_order_by('priority')
        search_for_hot_items.add_order_by('expected_delivery_date')
        hot_items_sobjects = search_for_hot_items.get_sobjects()

        hot_items = [hot_item for hot_item in hot_items_sobjects if hot_item.get_value('status') != 'Completed']

        # The database query for tasks will fail if there are no external rejections being passed in, causing the
        # whole hotlist to crash. This if/else prevents that.
        if external_rejections:
            external_rejection_tasks = self.get_tasks(external_rejections)
        else:
            external_rejection_tasks = []

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

        dictionary_of_tasks = {}
        dictionary_of_external_rejection_tasks = {}

        for task in external_rejection_tasks:
            task_title_code = task.get_value('title_code')
            task_header = task.get_value('assigned_login_group')

            if task_title_code not in dictionary_of_external_rejection_tasks.keys():
                dictionary_of_external_rejection_tasks[task_title_code] = {task_header: None}

            if not dictionary_of_external_rejection_tasks[task_title_code].get(task_header):
                dictionary_of_external_rejection_tasks[task_title_code][task_header] = [task]
            else:
                dictionary_of_external_rejection_tasks[task_title_code][task_header].append(task)

        for task in tasks:
            task_title_code = task.get_value('title_code')
            task_header = task.get_value('assigned_login_group')

            if task_title_code not in dictionary_of_tasks.keys():
                dictionary_of_tasks[task_title_code] = {task_header: None}

            if not dictionary_of_tasks[task_title_code].get(task_header):
                dictionary_of_tasks[task_title_code][task_header] = [task]
            else:
                dictionary_of_tasks[task_title_code][task_header].append(task)

        # Put external rejections on the board first
        for external_rejection in external_rejections:
            item_tasks = dictionary_of_external_rejection_tasks.get(external_rejection.get_value('code'))
            self.set_row(external_rejection, table, title_counter, header_groups, item_tasks, current_priority,
                         is_admin_user, True)

            title_counter += 1

        for hot_item in hot_items:
            hot_item_priority = float(hot_item.get_value('priority'))

            # Get the tasks that correspond to a title by comparing the task's title_code to the title's code
            # item_tasks = (task for task in tasks if task.get_value('title_code') == hot_item.get_value('code'))
            item_tasks = dictionary_of_tasks.get(hot_item.get_value('code'))

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
