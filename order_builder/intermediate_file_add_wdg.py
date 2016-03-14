from tactic.ui.common import BaseRefreshWdg
from tactic.ui.panel import EditWdg

from pyasm.web import Table


class IntermediateFileAddWdg(BaseRefreshWdg):
    def init(my):
        my.work_order_code = ''
        my.order_sk = ''
        my.client_code = ''
        my.is_master = ''

    def get_display(my):
        my.work_order_code = str(my.kwargs.get('work_order_code'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        my.client_code = str(my.kwargs.get('client_code'))
        my.is_master = str(my.kwargs.get('is_master'))
        table = Table()
        table.add_attr('class', 'intermediate_file_add_wdg')
        table.add_attr('work_order_code', my.work_order_code)
        table.add_attr('order_sk', my.order_sk)
        table.add_attr('client_code', my.client_code)
        table.add_attr('is_master', my.is_master)
        table.add_row()

        insert_wdg = EditWdg(element_name='general', mode='insert', search_type='twog/intermediate_file',
                             title='Create Intermediate File', view='insert', widget_key='edit_layout',
                             cbjs_insert_path='builder/new_inter_file')
        table.add_cell(insert_wdg)

        return table
