import datetime
from pyasm.web import Table
from tactic.ui.common import BaseRefreshWdg
from common_tools.common_functions import title_case
from pyasm.search import Search
from hottoday_utils import get_delivery_date_status, get_delivery_date_status_color


def trow_top():
    indi_pct = 20

    table = Table()
    table.add_attr('width', '100%')
    table.add_attr('height', '40px')
    table.add_attr('border', '1')
    table.add_style('font-size: 12px;')
    table.add_style('font-family: Helvetica;')
    table.add_style('color: #000000;')
    table.add_style('background-color: #f2f2f2;')
    table.add_style('border-color: #BBBBBB')
    table.add_class('spt_group_row')
    table.add_row()

    # Set up the title column (it is always shown)
    # TODO: Get rid of non-breaking spaces
    title_column = table.add_cell('&nbsp;&nbsp;&nbsp;<b>Title</b>')
    title_column.add_attr('class', 'topper')
    title_column.add_attr('group', 'title')
    # TODO: Not sure what the below line does
    title_width_percent = (indi_pct * 2)
    title_column.add_attr('width', '%s%s' % (title_width_percent, '%'))

    # Add all the rest of the columns
    for seen_group in ['machine room', 'compression', 'localization', 'qc', 'vault', 'edeliveries', 'scheduling']:
        seen_group_column = table.add_cell('&nbsp;&nbsp;&nbsp;<b>%s</b>' % title_case(seen_group))
        seen_group_column.add_attr('width', '%s%s' % ((indi_pct), '%'))
        seen_group_column.add_attr('class', 'topper')
        seen_group_column.add_attr('group', seen_group)

    return table


class HotTodayWdg(BaseRefreshWdg):
    """
    My attempt at rewriting the Hot Today table.
    """

    def get_row(self, title, table):
        from order_builder.order_builder import OrderBuilderLauncherWdg

        name = title.get_value('title')
        code = title.get_value('code')
        episode = title.get_value('episode')
        client = title.get_value('client_name')
        platform = title.get_value('platform')
        due_date = datetime.datetime.strptime(title.get_value('due_date'), '%Y-%m-%d %H:%M:%S')
        expected_delivery_date = title.get_value('expected_delivery_date')
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

        delivery_date_status = get_delivery_date_status(due_date)
        delivery_date_status_color = get_delivery_date_status_color(delivery_date_status)

        # Put together the title cell for the table. It includes the name, delivery date, status, and other info
        title_table = Table()

        name_row = title_table.add_row()
        title_table.add_cell(data=name, row=name_row)

        code_row = title_table.add_row()
        title_table.add_cell(data=code, row=code_row)
        title_table.add_cell(data=client, row=code_row)
        title_table.add_cell(data=platform, row=code_row)

        status_row = title_table.add_row()
        title_table.add_cell(data=delivery_date_status, row=status_row)

        deliver_by_row = title_table.add_row()
        title_table.add_cell(data=expected_delivery_date, row=deliver_by_row)

        due_date_row = title_table.add_row()
        title_table.add_cell(data=due_date, row=due_date_row)

        # TODO: Is there a better way to set the CSS? Docs aren't too clear on that.
        title_cell = table.add_cell(title_table)
        title_cell.add_style('background-color', title_cell_background_color)

    def get_display(self):
        table = Table()
        table.add_attr('class', 'bigboard')
        table.add_attr('width', '100%')
        table.add_attr('bgcolor', '#fcfcfc')
        table.add_style('color: #BBBBBB;')
        table.add_style('font-family: Helvetica;')

        table.add_cell(trow_top())

        table.add_tbody()

        search_for_hot_items = Search('twog/title')
        search_for_hot_items.add_filter('bigboard', True)
        search_for_hot_items.add_filter('status', 'Completed', op='!=')
        search_for_hot_items.add_order_by('priority')
        search_for_hot_items.add_order_by('expected_delivery_date')
        hot_items = search_for_hot_items.get_sobjects()

        for hot_item in hot_items:
            self.get_row(hot_item, table)

        return table
