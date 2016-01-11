import datetime

from pyasm.web import DivWdg, Table
from tactic.ui.common import BaseRefreshWdg
from common_tools.common_functions import title_case, abbreviate_text
from pyasm.search import Search
from hottoday_utils import get_date_status, get_date_status_color, get_client_img, get_platform_img,\
    get_launch_note_behavior, save_priorities, bring_to_top, set_scroll, get_reload
from order_builder import OrderBuilderLauncherWdg
from order_builder.taskobjlauncher import TaskObjLauncherWdg


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
        header_row.add_style('position', 'sticky')
        header_row.add_style('width', '100%')
        header_row.add_style('z-index', '0')

        # Add the title cell, it won't be included in the groups list since it should always be there by default
        groups_with_title = ['title'] + groups

        for group in groups_with_title:
            group_cell = table.add_header(title_case(group), row=header_row)
            group_cell.add_style('padding', '10px')
            group_cell.add_style('background-color', '#F2F2F2')
            group_cell.add_style('border', '1px solid #E0E0E0')

        table.add_row()

    def set_row(self, title, table, counter, header_groups, tasks):
        """
        Construct a row in the Hot Today list and add it to the table.

        :param title:
        :param table:
        :param counter:
        :param header_groups:
        :param tasks:
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

        # TODO: maybe move the block below to a function? It takes up space unnecessarily. Decide later.
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

        # Add the title table to the table row
        title_cell = table.add_cell(title_table)
        title_cell.add_style('background-color', title_cell_background_color)
        title_cell.add_style('border', '1px solid #EEE')
        title_cell.add_style('padding', '4px')
        title_cell.add_style('width', '400px')

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
            else:
                row_cell = table.add_cell()
                row_cell.add_style('border', '1px solid #EEE')

        table.add_row()

    @staticmethod
    def set_date_row(table, date, row_text):
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
        date_status_color = get_date_status_color(date_status)

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
        priority_row = table.add_cell(priority)
        priority_row.add_style('background-color', '#DCE3EE')

        table.add_row()

    @staticmethod
    def get_tasks(hot_items):
        """
        Given a list of 'titles', return all the tasks associated with those titles. Return only those marked as
        'active' and that are not marked as 'completed'.

        :param hot_items: A list of titles from 'twog/title'
        :return: List of tasks
        """
        # TODO: Figure out what 'kgroups' is supposed to be and how it's determined
        kgroups = ['ALL']

        title_codes = []

        for item in hot_items:
            title_codes.append("'{0}'".format(item.get_value('code')))

        title_codes_string = ','.join(title_codes)

        tq = Search("sthpw/task")
        tq.add_filter('bigboard', True)
        tq.add_filter('active', '1')
        tq.add_filter('search_type', 'twog/proj?project=twog')
        tq.add_filter('status', 'Completed', op="!=")
        if kgroups[0] != 'ALL':
            tq.add_where("\"assigned_login_group\" in ('{0}','{0}')".format((kgroups[0])))
        tq.add_where('\"title_code\" in ({0})'.format(title_codes_string))

        task_search_results = tq.get_sobjects()

        return task_search_results

    @staticmethod
    def get_buttons(auto_refresh, auto_scroll):
        # TODO: Rewrite this entire function...
        btns = Table()
        btns.add_attr('class', 'auto_buttons')
        btns.add_row()

        if auto_refresh:
            auto_text = 'Unset Auto-Refresh'
        else:
            auto_text = 'Set Auto-Refresh'

        auto = btns.add_cell('<input type="button" value="%s"/>' % auto_text)
        auto.add_attr('id', 'auto_refresh')
        auto.add_attr('name', 'auto_refresh')
        auto.add_attr('auto', auto_refresh)
        auto.add_behavior(get_reload())

        if auto_scroll:
            scroll_text = 'Unset Auto-Scroll'
        else:
            scroll_text = 'Set Auto-Scroll'

        scroll = btns.add_cell('<input type="button" value="%s"/>' % scroll_text)
        scroll.add_attr('id', 'scroll_el')
        scroll.add_attr('name', 'scroll_el')
        scroll.add_attr('scroll', auto_scroll)
        scroll.add_behavior(set_scroll())

        to_top = btns.add_cell('<input type="button" value="Go To Top"/>')
        to_top.add_behavior(bring_to_top())

        # if my.big_user:
        #     saveit = btns.add_cell('<input type="button" value="Save Priorities"/>')
        #     saveit.add_behavior(save_priorities())

        return btns

    def get_display(self):
        table = Table()
        table.add_attr('class', 'bigboard')
        table.add_style('width', '100%')
        table.add_style('background-color', '#FCFCFC')
        table.add_style('font-size', '12px')
        table.add_style('font-family', 'Helvetica')
        table.add_border(style='solid', color='#F2F2F2', size='1px')

        # TODO: Get which headers to display dynamically
        # 'title' is also in the headers, but since that always displays we'll leave it out here
        header_groups = ['machine room', 'compression', 'localization', 'qc', 'vault', 'edeliveries', 'scheduling']

        self.set_header(table, header_groups)

        # Search for titles that are marked as 'hot'
        search_for_hot_items = Search('twog/title')
        search_for_hot_items.add_filter('bigboard', True)
        search_for_hot_items.add_filter('status', 'Completed', op='!=')
        search_for_hot_items.add_order_by('priority')
        search_for_hot_items.add_order_by('expected_delivery_date')
        hot_items = search_for_hot_items.get_sobjects()

        tasks = self.get_tasks(hot_items)

        # Current priority will be updated each time a title has a different priority from the last value
        current_priority = 0
        title_counter = 1

        for hot_item in hot_items:
            hot_item_priority = float(hot_item.get_value('priority'))

            # Get the tasks that correspond to a title by comparing the task's title_code to the title's code
            item_tasks = [task for task in tasks if task.get_value('title_code') == hot_item.get_value('code')]

            if item_tasks:

                if current_priority < hot_item_priority:
                    self.set_priority_row(table, hot_item_priority)
                    current_priority = hot_item_priority

                self.set_row(hot_item, table, title_counter, header_groups, item_tasks)

                title_counter += 1

        # Put the table in a DivWdg, makes it fit better with the Tactic side bar
        hotlist_div = DivWdg()
        hotlist_div.add_attr('id', 'hotlist_div')
        hotlist_div.add_style('overflow-y', 'scroll')
        hotlist_div.add_style('height', '900px')

        hotlist_div.add(table)

        # Add an 'outer' div that holds the hotlist div, with the buttons below.
        outer_div = DivWdg()
        outer_div.add(hotlist_div)
        outer_div.add(self.get_buttons(False, False))

        return outer_div
