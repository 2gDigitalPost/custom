import datetime
from pyasm.web import Table
from tactic.ui.common import BaseRefreshWdg
from common_tools.common_functions import title_case
from pyasm.search import Search
from hottoday_utils import get_date_status, get_date_status_color, get_client_img, get_platform_img


class HotTodayWdg(BaseRefreshWdg):
    """
    My attempt at rewriting the Hot Today table.
    """

    def set_header(self, table, groups):
        header_row = table.add_row()
        header_row.add_style('background-color', '#E0E0E0')

        for group in groups:
            group_cell = table.add_header(title_case(group), row=header_row)
            group_cell.add_style('padding', '10px')
            group_cell.add_style('background-color', '#F2F2F2')
            group_cell.add_style('border', '1px solid #E0E0E0')

        table.add_row()

    def set_row(self, title, table, counter, number_of_columns):
        from order_builder.order_builder import OrderBuilderLauncherWdg

        name = title.get_value('title')
        code = title.get_value('code')
        episode = title.get_value('episode')
        client = title.get_value('client_name')
        client_code = title.get_value('client_code')
        platform = title.get_value('platform')
        due_date = datetime.datetime.strptime(title.get_value('due_date'), '%Y-%m-%d %H:%M:%S')
        expected_delivery_date = datetime.datetime.strptime(title.get_value('expected_delivery_date'), '%Y-%m-%d %H:%M:%S')
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

        # First row: Number (counter) and name
        name_data = '<span style="color: #FF0000">{0}.</span> <u>{1}</u>'.format(counter, name)
        name_row = title_table.add_row()
        name_row.add_style('font-size', '14px')
        name_row.add_style('font-weight', 'bold')
        title_table.add_cell(data=name_data, row=name_row, css='title-row')

        # Second row: Title's code (TITLE#####), Client, and Platform
        code_row = title_table.add_row()
        code_row.add_style('font-size', '12px')

        # Find the client image
        client_image_src = get_client_img(client_code)

        if client_image_src:
            client_image = '<img src="{0}" title="{1}" alt="{1}" style="width: 32px; height: 32px;">'.format(client_image_src, client)
        else:
            client_image = '<b>{0}</b>'.format(client)

        client_data = '<b>Client:</b> {0}'.format(client_image)

        # Find the platform image
        # TODO: Platform image find is not working. Fix it.

        # platform_image_src = get_platform_img(platform)
        platform_image_src = ''

        if platform_image_src:
            platform_image = '<img src="{0}" title="{1}" alt="{1}" style="width: 32px; height: 32px;">'.format(platform_image_src, platform)
        else:
            platform_image = '<i>{0}</i>'.format(platform)

        platform_data = '<i>Platform: </i>{0}'.format(platform_image)

        title_table.add_cell(data=code, row=code_row)
        title_table.add_cell(data=client_data, row=code_row)
        title_table.add_cell(data=platform_data, row=code_row)

        # Third row: Deliver By Date
        deliver_by_row = title_table.add_row()

        delivery_date_status = get_date_status(expected_delivery_date)
        delivery_date_status_color = get_date_status_color(delivery_date_status)

        deliver_by_row.add_style('color', delivery_date_status_color)
        deliver_by_row.add_style('font-size', '14px')
        deliver_by_row.add_style('font-weight', 'bold')
        deliver_by_row.add_style('text-shadow', '1px 1px #000000')

        delivery_date_data = 'Deliver By: {0}'.format(expected_delivery_date)

        title_table.add_cell(data=delivery_date_data, row=deliver_by_row)

        # Fourth Row: Due Date
        due_date_row = title_table.add_row()

        due_date_status = get_date_status(due_date)
        due_date_status_color = get_date_status_color(due_date_status)

        due_date_row.add_style('color', due_date_status_color)
        due_date_row.add_style('font-size', '14px')
        due_date_row.add_style('font-weight', 'bold')
        due_date_row.add_style('text-shadow', '1px 1px #000000')

        due_date_data = 'Due Date: {0}'.format(due_date)

        title_table.add_cell(data=due_date_data, row=due_date_row)

        # TODO: Is there a better way to set the CSS? Docs aren't too clear on that.
        title_cell = table.add_cell(title_table)
        title_cell.add_style('background-color', title_cell_background_color)
        title_cell.add_style('border', '1px solid #EEE')

        for column in xrange(number_of_columns):
            row_cell = table.add_cell()
            row_cell.add_style('border', '1px solid #EEE')

        table.add_row()

    def get_display(self):
        table = Table()
        table.add_attr('class', 'bigboard')
        table.add_attr('width', '100%')
        table.add_attr('bgcolor', '#fcfcfc')
        table.add_style('font-size', '12px')
        table.add_style('font-family', 'Helvetica')
        table.add_border(style='solid', color='#F2F2F2', size='1px')

        # TODO: Get which headers to display
        header_groups = ['title', 'machine room', 'compression', 'localization', 'qc', 'vault', 'edeliveries',
                         'scheduling']

        # Minus one because title is calculated separately
        number_of_columns = len(header_groups) - 1

        self.set_header(table, header_groups)

        search_for_hot_items = Search('twog/title')
        search_for_hot_items.add_filter('bigboard', True)
        search_for_hot_items.add_filter('status', 'Completed', op='!=')
        search_for_hot_items.add_order_by('priority')
        search_for_hot_items.add_order_by('expected_delivery_date')
        hot_items = search_for_hot_items.get_sobjects()

        for counter, hot_item in enumerate(hot_items, 1):
            self.set_row(hot_item, table, counter, number_of_columns)

        return table
