from tactic.ui.common import BaseRefreshWdg

from pyasm.search import Search
from pyasm.web import Table

from alternative_elements.customcheckbox import *


class IntermediatePassinAddWdg(BaseRefreshWdg):

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
        table.add_attr('class', 'intermediate_passin_add_wdg')
        wos_search = Search("twog/work_order")
        wos_search.add_filter('proj_code', my.proj_code)
        wos_search.add_filter('code', my.work_order_code, op="!=")
        wos_search.add_order_by('order_in_pipe')
        all_wos = wos_search.get_sobjects()
        all_wo_is = []
        for a in all_wos:
            wi_search = Search("twog/work_order_intermediate")
            wi_search.add_filter('work_order_code', a.get_value('code'))
            wo_inters = wi_search.get_sobjects()
            for woi in wo_inters:
                int_search = Search("twog/intermediate_file")
                int_search.add_filter('code', woi.get_value('intermediate_file_code'))
                inter = int_search.get_sobject()
                all_wo_is.append([a.get_value('code'), woi.get_value('code'), woi.get_value('title'),
                                  '%s: %s' % (inter.get_value('title'), inter.get_value('episode')),
                                  inter.get_value('code')])
        for b in all_wo_is:
            table.add_row()

            checkbox = CustomCheckboxWdg(name='selecta_perm_%s' % b[1], value_field=b[1], checked='false',
                                         dom_class='inter_passin_selector', code=b[1], woi_code=b[1], inter_code=b[4])

            ck = table.add_cell(checkbox)
            ck.add_attr('align', 'center')
            nw1 = table.add_cell('From Work Order: %s' % b[0])
            nw1.add_attr('nowrap', 'nowrap')
            table.add_cell(' &nbsp;&nbsp; ')
            nw2 = table.add_cell('Intermediate: %s (%s)' % (b[3], b[2]))
            nw2.add_attr('nowrap', 'nowrap')
        table.add_row()
        passin_butt = table.add_cell('<input type="button" value="Add As Pass-in(s) to Work Order"/>')
        passin_butt.add_behavior(get_assign_intermediate_passins_behavior(my.work_order_code, my.order_sk))

        return table


def get_assign_intermediate_passins_behavior(work_order_code, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    var server = TacticServerStub.get();
    var work_order_code = '%s';
    var order_sk = '%s';
    var top_el = spt.api.get_parent(bvr.src_el, '.intermediate_passin_add_wdg');
    checks = top_el.getElementsByClassName('inter_passin_selector');
    for(var r = 0; r < checks.length; r++) {
        if(checks[r].getAttribute('checked') == 'true') {
            woi_code = checks[r].getAttribute('woi_code');
            inter_code = checks[r].getAttribute('inter_code');
            server.insert('twog/work_order_passin', {'work_order_code': work_order_code, 'intermediate_file_code': inter_code, 'work_order_intermediate_code': woi_code})
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
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (work_order_code, order_sk)}
    return behavior
