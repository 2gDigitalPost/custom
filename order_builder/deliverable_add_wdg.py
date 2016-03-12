from tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.panel import EditWdg

from pyasm.web import Table
from pyasm.widget import TextWdg
from pyasm.search import Search

from barcoder import Barcoder
from order_builder_utils import OBScripts


class DeliverableAddWdg(BaseRefreshWdg):

    def init(my):
        my.server = TacticServerStub.get()
        my.work_order_code = ''
        my.order_sk = ''
        my.client_code = ''

    def get_display(my):
        my.work_order_code = str(my.kwargs.get('work_order_code'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        switching = False
        switch_code = ''
        clone_code = ''
        deliver_to = ''
        deliverable_name = ''
        deliverable_attn = ''
        not_clone_fields = ['id','code','barcode','timestamp','barcode']
        if 'switching_to' in my.kwargs.keys():
            switching = True
            switch_code = str(my.kwargs.get('switching_to'))
        if 'deliver_to' in my.kwargs.keys():
            deliver_to = str(my.kwargs.get('deliver_to'))
        if 'deliverable_name' in my.kwargs.keys():
            deliverable_name = str(my.kwargs.get('deliverable_name'))
        if 'deliverable_attn' in my.kwargs.keys():
            deliverable_attn = str(my.kwargs.get('deliverable_attn'))
        if 'clone_code' in my.kwargs.keys():
            clone_code = str(my.kwargs.get('clone_code'))
        obs = OBScripts(order_sk=my.order_sk)
        my.client_code = str(my.kwargs.get('client_code'))
        table = Table()
        table.add_attr('class','deliverable_add_wdg')
        table.add_attr('work_order_code',my.work_order_code)
        table.add_attr('order_sk',my.order_sk)
        table.add_attr('client_code',my.client_code)
        table.add_row()
        delv_tbl = Table()
        delv_tbl.add_row()
        delv_tbl.add_cell('Name: ')
        name_cell = delv_tbl.add_cell('<input type="text" class="deliverable_name" value="%s"/>' % deliverable_name)

        client_search = Search("twog/client")
        client_search.add_order_by('name desc')
        clients = client_search.get_sobjects()
        client_sel = '<select class="deliver_to" out_code="OUT_CODE"><option value="">--Select--</option>'
        for client in clients:
            is_seld = ''
            if client.get_value('name') == deliver_to:
                is_seld = 'selected="selected"'
            client_sel = '%s<option value="%s" %s>%s</option>' % (client_sel, client.get_value('name'), is_seld, client.get_value('name'))
        client_sel = '%s</select>' % client_sel
        dt = delv_tbl.add_cell('Deliver To: ')
        dt.add_attr('nowrap','nowrap')
        deliver_to_cell = delv_tbl.add_cell(client_sel)
        delv_tbl.add_cell('Attn: ')
        attn_cell = delv_tbl.add_cell('<input type="text" class="deliverable_attn" value="%s"/>' % deliverable_attn)
        table.add_cell(delv_tbl)
        switch_table = Table()
        switch_table.add_row()
        nw = switch_table.add_cell('Switch Asset To Existing Asset By Barcode: ')
        nw.add_attr('nowrap','nowrap')
        barcode_wdg = TextWdg('barcode_switcher')
        barcode_wdg.add_behavior(obs.get_switch_by_barcode_behavior(my.work_order_code, my.order_sk, my.client_code))
        switch_table.add_cell(barcode_wdg)
        table.add_row()
        table.add_cell(switch_table)

        clone_table = Table()
        clone_table.add_row()
        nw = clone_table.add_cell('Clone Existing Asset By Barcode: ')
        nw.add_attr('nowrap','nowrap')
        barcode_wdg = TextWdg('barcode_cloner')
        barcode_wdg.add_behavior(obs.get_clone_by_barcode_behavior(my.work_order_code, my.order_sk, my.client_code))
        clone_table.add_cell(barcode_wdg)
        table.add_row()
        table.add_cell(clone_table)

        table.add_row()
        insert_wdg = None
        if not switching:
            default = {}
            barcoder = Barcoder()
            default['barcode'] = barcoder.get_new_barcode('true')
            if clone_code not in [None,'']:
                cloner = my.server.eval("@SOBJECT(twog/source['code','%s'])" % clone_code)[0]
                for k in cloner.keys():
                    if k not in not_clone_fields:
                        default[k] = cloner.get(k)
            insert_wdg = EditWdg(element_name='general', mode='insert', search_type='twog/source', title='Create Permanent Element', view='insert', widget_key='edit_layout', default=default, cbjs_insert_path='builder/new_deliverable')
        else:
            insert_wdg = EditWdg(element_name='general', mode='edit', search_type='twog/source', code=switch_code, title='Create Permanent Element', view='edit', widget_key='edit_layout', cbjs_edit_path='builder/new_deliverable')
        table.add_cell(insert_wdg)

        return table
