from tactic.ui.common import BaseRefreshWdg

from pyasm.search import Search
from pyasm.web import Table

from alternative_elements.customcheckbox import *


class DeliverablePassinAddWdg(BaseRefreshWdg):

    def init(my):
        my.work_order_code = ''
        my.order_sk = ''
        my.proj_code = ''
        my.wo_templ_code = ''

    def get_display(my):
        my.work_order_code = str(my.kwargs.get('work_order_code'))
        my.proj_code = str(my.kwargs.get('proj_code'))
        my.wo_templ_code = str(my.kwargs.get('wo_templ_code'))
        my.order_sk = str(my.kwargs.get('order_sk'))

        table = Table()
        table.add_attr('class', 'deliverable_passin_add_wdg')
        wo_search = Search("twog/work_order")
        wo_search.add_filter('proj_code', my.proj_code)
        wo_search.add_filter('code', my.work_order_code,op="!=")
        wo_search.add_order_by('order_in_pipe')
        all_wos = wo_search.get_sobjects()
        all_wo_ds = []
        for a in all_wos:
            deliv_search = Search("twog/work_order_deliverables")
            deliv_search.add_filter("work_order_code", a.get_value('code'))
            wo_delivs = deliv_search.get_sobjects()
            for wod in wo_delivs:
                src_search = Search("twog/source")
                src_search.add_filter('code', wod.get_value('deliverable_source_code'))
                src = src_search.get_sobject()
                all_wo_ds.append([a.get_value('code'), wod.get_value('code'), wod.get_value('name'),
                                  '%s: %s' % (src.get_value('title'), src.get_value('episode')), src.get_value('code')])
        for b in all_wo_ds:
            table.add_row()

            checkbox = CustomCheckboxWdg(name='selecta_perm_%s' % b[1], value_field=b[1], checked='false',
                                         dom_class='deliverable_passin_selector', code=b[1], wod_code=b[1],
                                         src_code=b[4])

            ck = table.add_cell(checkbox)
            ck.add_attr('align', 'center')
            nw1 = table.add_cell('From Work Order: %s' % b[0])
            nw1.add_attr('nowrap', 'nowrap')
            table.add_cell(' &nbsp;&nbsp; ')
            nw2 = table.add_cell('Permanent: %s (%s)' % (b[3], b[2]))
            nw2.add_attr('nowrap', 'nowrap')
        table.add_row()
        passin_butt = table.add_cell('<input type="button" value="Add As Pass-in(s) to Work Order"/>')
        passin_butt.add_behavior(get_assign_deliverable_passins_behavior(my.work_order_code, my.order_sk))

        return table


def get_assign_deliverable_passins_behavior(work_order_code, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                       //alert('m5');
                       var server = TacticServerStub.get();
                       var work_order_code = '%s';
                       var order_sk = '%s';
                       //alert(order_sk);
                       var top_el = spt.api.get_parent(bvr.src_el, '.deliverable_passin_add_wdg');
                       checks = top_el.getElementsByClassName('deliverable_passin_selector');
                       for(var r = 0; r < checks.length; r++){
                           if(checks[r].getAttribute('checked') == 'true'){
                               wod_code = checks[r].getAttribute('wod_code');
                               src_code = checks[r].getAttribute('src_code');
                               //alert(src_code);
                               server.insert('twog/work_order_passin', {'work_order_code': work_order_code, 'deliverable_source_code': src_code, 'work_order_deliverables_code': wod_code})
                           }
                       }
                       work_order_sk = server.build_search_key('twog/work_order', work_order_code);
                       var sources_line = document.getElementsByClassName('wo_sources_' + work_order_sk)[0];
                       spt.api.load_panel(sources_line, 'order_builder.WorkOrderSourcesRow', {'work_order_code': work_order_code, 'order_sk': order_sk});
                       var sp = document.getElementsByClassName('sp_overhead_' + work_order_code)[0];
                       parent_pipe = sp.getAttribute('parent_pipe');
                       client_code = sp.getAttribute('client_code');
                       is_master = sp.getAttribute('is_master');
                       var sp_el = sp.getElementsByClassName('sp_list_cell')[0];
                       spt.api.load_panel(sp_el, 'order_builder.SourcePortalWdg', {'work_order_code': work_order_code, 'parent_pipe': parent_pipe, 'client_code': client_code, 'is_master': is_master, 'order_sk': order_sk});
                       spt.popup.close(spt.popup.get_popup(bvr.src_el));


            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (work_order_code, order_sk)}
    return behavior