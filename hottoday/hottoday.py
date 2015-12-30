import datetime
from pyasm.web import Table
from tactic.ui.common import BaseRefreshWdg
from common_tools.common_functions import title_case
from pyasm.search import Search
from hottoday_utils import get_delivery_date_status


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
        due_date = datetime.datetime.strptime(title.get_value('due_date'), '%Y-%m-%d %H:%M:%S')
        requires_mastering_qc = title.get_value('requires_mastering_qc', False)
        is_external_rejection = title.get_value('is_external_rejection', False)
        is_redo = title.get_value('redo', False)

        # Set the row's background color. Different statuses require different colors. The statuses are not necessarily
        # mutually exclusive, but they are ordered by priority.
        if is_external_rejection:
            # TODO: Add 'Requires QC Mastering' to the row
            row_background_color = '#B55252'
        elif is_redo:
            row_background_color = '#FFCC00'
        elif requires_mastering_qc:
            row_background_color = 'C8A2C8'
        else:
            row_background_color = '#D7D7D7'

        data_to_display = [name, code, episode, client, due_date]

        # TODO: Pass the row background color in the css argument
        current_row = table.add_row()
        # current_row = table.add_row(css={'background-color': row_background_color})

        delivery_date_status = get_delivery_date_status(due_date)

        for data in data_to_display:
            table.add_cell(data=data, row=current_row)

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

            # current_row = table.add_row()
            # table.add_cell('test', row=current_row)

        return table
