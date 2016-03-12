from tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.panel import EditWdg

from pyasm.web import Table
from pyasm.widget import TextWdg
from pyasm.search import Search

from barcoder import Barcoder


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
        barcode_wdg.add_behavior(get_switch_by_barcode_behavior(my.work_order_code, my.order_sk, my.client_code))
        switch_table.add_cell(barcode_wdg)
        table.add_row()
        table.add_cell(switch_table)

        clone_table = Table()
        clone_table.add_row()
        nw = clone_table.add_cell('Clone Existing Asset By Barcode: ')
        nw.add_attr('nowrap','nowrap')
        barcode_wdg = TextWdg('barcode_cloner')
        barcode_wdg.add_behavior(get_clone_by_barcode_behavior(my.work_order_code, my.order_sk, my.client_code))
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


def get_switch_by_barcode_behavior(work_order_code, order_sk, client_code):
    behavior = {'css_class': 'clickme', 'type': 'change', 'cbjs_action': '''
                    try{
                      //alert('m39');
                      var server = TacticServerStub.get();
                      work_order_code = '%s';
                      order_sk = '%s';
                      client_code = '%s';
                      top_el = document.getElementsByClassName('deliverable_add_wdg')[0];
                      name_el = top_el.getElementsByClassName('deliverable_name')[0];
                      deliver_to_el = top_el.getElementsByClassName('deliver_to')[0];
                      attn_el = top_el.getElementsByClassName('deliverable_attn')[0];
                      barcode = bvr.src_el.value;
                      barcode = barcode.toUpperCase();
                      source_expr = "@SOBJECT(twog/source['barcode','" + barcode + "'])";
                      sources = server.eval(source_expr);
                      if(sources.length > 1){
                          alert('Something is wrong with inventory. There are ' + sources.length + ' sources with that barcode.');
                          bvr.src_el.value = '';
                      }else if(sources.length == 0){
                          source_expr = "@SOBJECT(twog/source['client_asset_id','" + barcode + "'])";
                          sources = server.eval(source_expr);
                          if(sources.length > 1){
                              alert('Something is wrong with inventory. There are ' + sources.length + ' sources with that client_asset_id.');
                              bvr.src_el.value = '';
                              sources = []
                          }
                      }
                      if(sources.length > 0){
                          sources_code = sources[0].code;
                          spt.popup.close(spt.popup.get_popup(bvr.src_el));
                          spt.panel.load_popup('Use Existing Element As Permanent/Deliverable', 'order_builder.DeliverableAddWdg', {'work_order_code': work_order_code, 'order_sk': order_sk, 'client_code': client_code, 'switching_to': sources_code, 'deliver_to': deliver_to_el.value, 'deliverable_attn': attn_el.value, 'deliverable_name': name_el.value});
                      }else{
                          alert('There are no sources with that barcode. Try a different barcode?');
                          bvr.src_el.value = '';
                      }


            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (work_order_code, order_sk, client_code)}
    return behavior


def get_clone_by_barcode_behavior(work_order_code, order_sk, client_code):
    behavior = {'css_class': 'clickme', 'type': 'change', 'cbjs_action': '''
                    try{
                      //alert('m39');
                      var server = TacticServerStub.get();
                      work_order_code = '%s';
                      order_sk = '%s';
                      client_code = '%s';
                      top_el = document.getElementsByClassName('deliverable_add_wdg')[0];
                      name_el = top_el.getElementsByClassName('deliverable_name')[0];
                      deliver_to_el = top_el.getElementsByClassName('deliver_to')[0];
                      attn_el = top_el.getElementsByClassName('deliverable_attn')[0];
                      barcode = bvr.src_el.value;
                      barcode = barcode.toUpperCase();
                      source_expr = "@SOBJECT(twog/source['barcode','" + barcode + "'])";
                      sources = server.eval(source_expr);
                      if(sources.length > 1){
                          alert('Something is wrong with inventory. There are ' + sources.length + ' sources with that barcode.');
                          bvr.src_el.value = '';
                      }else if(sources.length == 0){
                          source_expr = "@SOBJECT(twog/source['client_asset_id','" + barcode + "'])";
                          sources = server.eval(source_expr);
                          if(sources.length > 1){
                              alert('Something is wrong with inventory. There are ' + sources.length + ' sources with that client_asset_id.');
                              bvr.src_el.value = '';
                              sources = []
                          }
                      }
                      if(sources.length > 0){
                          sources_code = sources[0].code;
                          spt.popup.close(spt.popup.get_popup(bvr.src_el));
                          spt.panel.load_popup('Cloned Permanent/Deliverable Creation', 'order_builder.DeliverableAddWdg', {'work_order_code': work_order_code, 'order_sk': order_sk, 'client_code': client_code, 'clone_code': sources_code, 'deliver_to': deliver_to_el.value, 'deliverable_attn': attn_el.value, 'deliverable_name': name_el.value});
                      }else{
                          alert('There are no sources with that barcode. Try a different barcode?');
                          bvr.src_el.value = '';
                      }


            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (work_order_code, order_sk, client_code)}
    return behavior
