from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Environment
from pyasm.search import Search
from pyasm.web import Table

from alternative_elements.customcheckbox import *
from widget.new_icon_wdg import CustomIconWdg
from widget.button_small_new_wdg import ButtonSmallNewWdg

from order_builder_utils import get_open_intermediate_behavior, get_open_deliverable_behavior


class OutFilesWdg(BaseRefreshWdg):

    def init(my):
        my.work_order_sk = ''
        my.work_order_code = ''
        my.client_code = ''
        my.order_sk = ''
        my.x_butt = "<img src='/context/icons/common/BtnKill_Black.gif' title='Delete' name='Delete'/>"
        my.is_master = False
        my.is_master_str = 'false'

    def get_display(my):
        my.work_order_sk = str(my.kwargs.get('work_order_sk'))
        my.work_order_code = str(my.kwargs.get('work_order_code'))
        my.client_code = str(my.kwargs.get('client_code'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        order_code = my.order_sk.split('code=')[1]
        overhead = Table()
        overhead.add_attr('class', 'out_overhead_%s' % my.work_order_code)
        overhead.add_attr('client_code', my.client_code)

        wo_search = Search("twog/work_order")
        wo_search.add_filter('code', my.work_order_code)
        work_order = wo_search.get_sobject()
        delivs_search = Search("twog/work_order_deliverables")
        delivs_search.add_filter('work_order_code', my.work_order_code)
        delivs = delivs_search.get_sobjects()
        inter_search = Search("twog/work_order_intermediate")
        inter_search.add_filter('work_order_code', my.work_order_code)
        inters = inter_search.get_sobjects()

        user_group_names = Environment.get_group_names()
        groups_str = ''
        for mg in user_group_names:
            if groups_str == '':
                groups_str = mg
            else:
                groups_str = '%s,%s' % (groups_str, mg)
        user_is_scheduler = False
        if 'scheduling' in groups_str:
            user_is_scheduler = True

        if 'is_master' in my.kwargs.keys():
            my.is_master_str = my.kwargs.get('is_master')
            if my.is_master_str == 'true':
                my.is_master = True
        else:
            order_search = Search("twog/order")
            order_search.add_filter('code',order_code)
            order = order_search.get_sobject()
            order_classification = order.get_value('classification')
            if order_classification in ['master','Master']:
                my.is_master = True
                my.is_master_str = 'true'
        table = Table()
        table.add_row()
        table.add_cell('<font size="4"><b><u>Intermediates</u></b></font>')
        add_inter = table.add_cell('<input type="button" value="Add Intermediate File"/>')
        add_inter.add_attr('nowrap','nowrap')
        add_inter.add_style('cursor: pointer;')
        add_inter.add_behavior(get_add_inter_behavior(my.work_order_code, my.client_code, my.is_master_str,
                                                      my.order_sk))
        inters_tbl = Table()
        for inter1 in inters:
            i_search = Search("twog/intermediate_file")
            i_search.add_filter('code',inter1.get_value('intermediate_file_code'))
            inter = i_search.get_sobject()
            inters_tbl.add_row()
            if user_is_scheduler:
                killer = inters_tbl.add_cell(my.x_butt)
                killer.add_style('cursor: pointer;')
                killer.add_behavior(get_intermediate_killer_behavior(inter1.get_value('code'), inter.get_value('title'),
                                                                     my.work_order_code, my.is_master_str, my.order_sk))
            alabel = inters_tbl.add_cell('Intermediate: ')
            alabel.add_attr('align','center')
            popper = inters_tbl.add_cell('<u>%s</u>' % inter.get_value('title'))
            popper.add_attr('nowrap','nowrap')
            popper.add_style('cursor: pointer;')
            popper.add_behavior(get_open_intermediate_behavior(inter.get_value('code'), my.work_order_code,
                                                               my.client_code, my.order_sk))

            if str(inter1.get_value('satisfied')) == 'True':
                check_val = 'true'
            else:
                check_val = 'false'
            checkbox = CustomCheckboxWdg(name='satisfied_%s' % inter.get_value('code'),
                                         value_field=inter.get_value('code'), checked=check_val,
                                         dom_class='inter_selector', code=inter.get_value('code'),
                                         additional_js=get_change_inter_satisfied_behavior(inter1.get_value('code'),
                                                                                           my.work_order_code,
                                                                                           my.client_code,
                                                                                           str(inter1.get_value('satisfied')),
                                                                                           my.order_sk))

            ck = inters_tbl.add_cell(checkbox)
            ck.add_attr('align','center')
            inters_tbl.add_cell(' &nbsp; ')
            if my.is_master:
                if inter.get_value('intermediate_file_templ_code') in [None,'']:
                    template_button = ButtonSmallNewWdg(title="Template This Intermediate File", icon=CustomIconWdg.icons.get('TEMPLATE'))
                    template_button.add_behavior(get_template_intermediate_behavior(inter.get_value('code'),
                                                                                    my.work_order_code, my.order_sk))
                else:
                    template_button = '<img border="0" style="vertical-align: middle" title="Templated" name="Templated" src="/context/icons/silk/tick.png">'
                tb = inters_tbl.add_cell(template_button)
                tb.add_class('inter_templ_%s' % inter.get_value('code'))
        table.add_row()
        intr = table.add_cell(inters_tbl)
        intr.add_attr('colspan','2')
        table.add_row()
        table.add_cell('<hr/>')
        table.add_row()
        table.add_cell('<font size="4"><b><u>Permanents</u></b></font>')
        add_delv = table.add_cell('<input type="button" value="Add Permanent Element"/>')
        add_delv.add_style('cursor: pointer;')
        add_delv.add_behavior(get_add_deliverable_behavior(my.work_order_code, my.client_code, my.order_sk))
        delv_tbl = Table()
        client_search = Search("twog/client")
        client_search.add_order_by('name desc')
        clients = client_search.get_sobjects()
        client_sel = '<select class="deliver_to_DELIV_CODE"><option value="">--Select--</option>'
        for client in clients:
            client_sel = '%s<option value="%s">%s</option>' % (client_sel, client.get_value('name'),
                                                               client.get_value('name'))
        client_sel = '%s</select>' % client_sel
        for deliv1 in delivs:
            d_search = Search("twog/source")
            d_search.add_filter('code',deliv1.get_value('deliverable_source_code'))
            deliv = d_search.get_sobject()
            deliv_name = '%s, Episode: %s, Type: %s' % (deliv.get_value('title'), deliv.get_value('episode'),
                                                        deliv.get_value('source_type'))
            delv_tbl.add_row()
            if user_is_scheduler:
                killer = delv_tbl.add_cell(my.x_butt)
                killer.add_style('cursor: pointer;')
                killer.add_behavior(get_deliverable_killer_behavior(deliv1.get_value('code'), my.work_order_code,
                                                                    deliv1.get_value('title_code'),
                                                                    deliv.get_value('code'),
                                                                    '%s (%s: %s)' % (deliv1.get_value('name'),
                                                                                     deliv.get_value('title'),
                                                                                     deliv.get_value('episode')),
                                                                    my.is_master_str, my.order_sk))
            alabel = delv_tbl.add_cell('Permanent: ')
            alabel.add_attr('align','center')
            popper = delv_tbl.add_cell('<u>%s</u>' % deliv.get_value('title'))
            popper.add_attr('nowrap','nowrap')
            popper.add_style('cursor: pointer;')
            popper.add_behavior(get_open_deliverable_behavior(deliv.get_value('code'), my.work_order_code,
                                                              deliv1.get_value('title_code'), my.client_code,
                                                              my.order_sk))

            if str(deliv1.get_value('satisfied')) == 'True':
                check_val = 'true'
            else:
                check_val = 'false'
            checkbox = CustomCheckboxWdg(name='satisfied_%s' % deliv.get_value('code'),
                                         value_field=deliv.get_value('code'), checked=check_val,
                                         dom_class='deliv_selector', code=deliv.get_value('code'),
                                         additional_js=get_change_deliverable_satisfied_behavior(deliv1.get_value('code'),
                                                                                                 my.work_order_code,
                                                                                                 deliv1.get_value('title_code'),
                                                                                                 str(deliv1.get_value('satisfied')),
                                                                                                 my.client_code,
                                                                                                 my.order_sk))

            ck = delv_tbl.add_cell(checkbox)
            ck.add_attr('align','center')
            delv_tbl.add_cell(' &nbsp; ')
            if my.is_master:
                if deliv.get_value('templ_code') in [None,'']:
                    template_button = ButtonSmallNewWdg(title="Template This Intermediate File",
                                                        icon=CustomIconWdg.icons.get('TEMPLATE'))
                    template_button.add_behavior(get_template_deliverable_behavior(deliv1.get_value('code'),
                                                                                   work_order.get_value('work_order_templ_code'),
                                                                                   deliv1.get_value('deliverable_source_code'),
                                                                                   my.work_order_code))
                else:
                    template_button = '<img border="0" style="vertical-align: middle" title="Templated" name="Templated" src="/context/icons/silk/tick.png">'
                tb = delv_tbl.add_cell(template_button)
                tb.add_class('deliverable_templ_%s' % deliv1.get_value('code'))
            bot_delv = Table()
            bot_delv.add_row()
            bot_delv.add_cell('Name: ')
            bot_delv.add_cell('<input type="text" class="deliv_name_%s" value="%s"/>' % (deliv1.get_value('code'), deliv1.get_value('name')))
            bot_delv.add_row()
            nw = bot_delv.add_cell('Deliver To: ')
            nw.add_attr('nowrap','nowrap')
            this_client_sel = client_sel.replace('DELIV_CODE',deliv1.get_value('code'))
            this_client_sel = this_client_sel.replace('value="%s"' % deliv1.get_value('deliver_to'), 'value="%s" selected="selected"' % deliv1.get_value('deliver_to'))
            bot_delv.add_cell(this_client_sel)
            bot_delv.add_row()
            bot_delv.add_cell('Attn: ')
            bot_delv.add_cell('<input type="text" class="deliv_attn_%s" value="%s"/>' % (deliv1.get_value('code'), deliv1.get_value('attn')))
            bot_delv.add_row()
            save_cell = bot_delv.add_cell('<input type="button" value="Save Permanent Element Info"/>')
            save_cell.add_behavior(get_save_deliv_info_behavior(deliv1.get_value('code'), my.work_order_code,
                                                                deliv1.get_value('title_code'), my.client_code,
                                                                my.is_master_str, my.order_sk))

            delv_tbl.add_row()
            bot = delv_tbl.add_cell(bot_delv)
            bot.add_attr('colspan','4')
        table.add_row()
        delv = table.add_cell(delv_tbl)
        delv.add_attr('colspan', '2')
        overhead.add_row()
        oh_cell = overhead.add_cell(table)
        oh_cell.add_attr('class','out_list_cell')
        return overhead


def get_add_inter_behavior(work_order_code, client_code, is_master, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    var server = TacticServerStub.get();
    work_order_code = '%s';
    client_code = '%s';
    is_master = '%s';
    order_sk = '%s';
    spt.panel.load_popup('Create New Intermediate File', 'order_builder.IntermediateFileAddWdg', {'work_order_code': work_order_code, 'order_sk': order_sk, 'client_code': client_code, 'is_master': is_master});
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (work_order_code, client_code, is_master, order_sk)}
    return behavior


def get_intermediate_killer_behavior(inter_link_code, inter_title, work_order_code, is_master, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try{
    var server = TacticServerStub.get();
    inter_link_code = '%s';
    inter_title = '%s';
    work_order_code = '%s';
    is_master = '%s';
    order_sk = '%s';

    if(confirm("Do you really want to delete intermediate file: " + inter_title)){
        inter_link_sk = server.build_search_key('twog/work_order_intermediate', inter_link_code);
        work_order_sk = server.build_search_key('twog/work_order', work_order_code);
        var overhead_el = spt.api.get_parent(bvr.src_el, '.out_overhead_' + work_order_code);
        client_code = overhead_el.getAttribute('client_code');
        wo_interm_expr = "@SOBJECT(twog/work_order_intermediate['code','" + inter_link_code + "'])";
        wo_interm = server.eval(wo_interm_expr)[0];
        int_file_code = wo_interm.intermediate_file_code;
        server.retire_sobject(inter_link_sk);
        if(is_master == 'true'){
            inter_templ_code = '';
            inter = server.eval("@SOBJECT(twog/intermediate_file['code','" + int_file_code + "'])")
            if(inter.length > 0){
                inter_templ_code = inter[0].intermediate_file_templ_code;
                server.update(inter.__search_key__, {'intermediate_file_templ_code': ''});
            }
            wot_code = server.eval("@GET(twog/work_order['code','" + work_order_code + "'].work_order_templ_code)")[0];
            wot = server.eval("@SOBJECT(twog/work_order_templ['code','" + wot_code + "'])")[0];
            new_str = '';
            interm_codes = wot.intermediate_file_templ_codes.split(',');
            for(var r = 0; r < interm_codes.length; r++){
                if(interm_codes[r] != inter_templ_code){
                    if(new_str == ''){
                        new_str = interm_codes[r];
                    }else{
                        new_str = new_str + ',' + interm_codes[r];
                    }
                }
            }
            server.update(wot.__search_key__, {'intermediate_file_templ_codes': new_str})
        }
        var sources_line = document.getElementsByClassName('wo_sources_' + work_order_sk)[0];
        spt.api.load_panel(sources_line, 'order_builder.WorkOrderSourcesRow', {'work_order_code': work_order_code, 'order_sk': order_sk});
        var out_cell = overhead_el.getElementsByClassName('out_list_cell')[0];
        spt.api.load_panel(out_cell, 'order_builder.OutFilesWdg', {'work_order_code': work_order_code, 'work_order_sk': work_order_sk, 'client_code': client_code, 'order_sk': order_sk});
    }
}
catch(err){
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (inter_link_code, inter_title, work_order_code, is_master, order_sk)}

    return behavior


def get_change_inter_satisfied_behavior(inter_link_code, work_order_code, client_code, current_state, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    var server = TacticServerStub.get();
    inter_link_code = '%s';
    work_order_code = '%s';
    client_code = '%s';
    state = '%s';
    order_sk = '%s';
    new_val = '';
    if(state == 'False') {
        new_val = 'True';
    } else {
        new_val = 'False';
    }
    server.update(server.build_search_key('twog/work_order_intermediate', inter_link_code), {'satisfied': new_val});
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
    ''' % (inter_link_code, work_order_code, client_code, current_state, order_sk)}

    return behavior


def get_template_intermediate_behavior(intermediate_file_code, work_order_code, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    function oc(a){
                        var o = {};
                        for(var i=0;i<a.length;i++){
                            o[a[i]]='';
                        }
                        return o;
                    }
                    try{
                      //alert('m25');
                      var server = TacticServerStub.get();
                      intermediate_file_code = '%s';
                      work_order_code = '%s';
                      order_sk = '%s';
                      intermediate_file = server.eval("@SOBJECT(twog/intermediate_file['code','" + intermediate_file_code + "'])")[0]
                      work_order = server.eval("@SOBJECT(twog/work_order['code','" + work_order_code + "'])")[0]
                      work_order_templ = server.eval("@SOBJECT(twog/work_order_templ['code','" + work_order.work_order_templ_code + "'])")[0]
                      existing_codes = work_order_templ.intermediate_file_templ_codes;
                      codes_list = existing_codes.split(',');
                      templ = server.insert('twog/intermediate_file_templ', {'title': intermediate_file.title, 'description': intermediate_file.description})
                      templ_code = templ.code;
                      server.update(intermediate_file.__search_key__, {'intermediate_file_templ_code': templ_code});
                      if(!(templ_code in oc(codes_list))){
                          new_codes = ''
                          for(var r = 0; r < codes_list.length; r++){
                              if(new_codes == ''){
                                  new_codes = codes_list[r];
                              }else{
                                  new_codes = new_codes + ',' + codes_list[r];
                              }
                          }
                          if(new_codes == ''){
                              new_codes = templ_code;
                          }else{
                              new_codes = new_codes + ',' + templ_code;
                          }
                          server.update(work_order_templ.__search_key__, {'intermediate_file_templ_codes': new_codes});
                      }
                      var top_el = spt.api.get_parent(bvr.src_el, '.out_overhead_' + work_order_code);
                      var cell = top_el.getElementsByClassName('inter_templ_' + intermediate_file_code)[0];
                      cell.innerHTML = '<img border="0" style="vertical-align: middle" title="Templated" name="Templated" src="/context/icons/silk/tick.png">';
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (intermediate_file_code, work_order_code, order_sk)}
    return behavior


def get_add_deliverable_behavior(work_order_code, client_code, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      //alert('m16');
                      var server = TacticServerStub.get();
                      work_order_code = '%s';
                      client_code = '%s';
                      order_sk = '%s';
                      spt.panel.load_popup('Create New Permanent Element', 'order_builder.DeliverableAddWdg', {'work_order_code': work_order_code, 'order_sk': order_sk, 'client_code': client_code});
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (work_order_code, client_code, order_sk)}
    return behavior


def get_deliverable_killer_behavior(wo_deliverable_code, work_order_code, title_code, source_code, my_title, is_master,
                                    order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      var server = TacticServerStub.get();
                      wo_deliverable_code = '%s';
                      work_order_code = '%s';
                      title_code = '%s';
                      source_code = '%s';
                      my_title = '%s';
                      is_master = '%s';
                      order_sk = '%s';
                      var overhead_el = spt.api.get_parent(bvr.src_el, '.out_overhead_' + work_order_code);
                      var oh_cell = overhead_el.getElementsByClassName('deliverable_list_cell')[0];
                      deliv_sk = server.build_search_key('twog/work_order_deliverables', wo_deliverable_code);
                      work_order_sk = server.build_search_key('twog/work_order', work_order_code);
                      if(confirm("Are you sure you want to delete " + my_title + "?")){
                              server.retire_sobject(deliv_sk);
                              //also need to remove title code from the source "deliverable_for"                         //maybe this should be a trigger?
                              source = server.eval("@SOBJECT(twog/source['code','" + source_code + "'])")[0];
                              deliv_for = source.deliverable_for.split(',');
                              new_deliv_str = ''
                              for(var r = 0; r < deliv_for.length; r++){
                                  if(deliv_for[r] != title_code && deliv_for[r] != work_order_code){
                                      if(new_deliv_str == ''){
                                          new_deliv_str = deliv_for[r];
                                      }else{
                                          new_deliv_str = new_deliv_str + ',' + deliv_for[r];
                                      }
                                  }
                              }
                              server.update(source.__search_key__, {'deliverable_for': new_deliv_str});
                              if(is_master == 'true'){
                                  wot_code = server.eval("@GET(twog/work_order['code','" + work_order_code + "'].work_order_templ_code)")[0];
                                  wot = server.eval("@SOBJECT(twog/work_order_templ['code','" + wot_code + "'])")[0];
                                  new_str = '';
                                  deliv_codes = wot.deliverable_templ_codes.split(',');
                                  for(var r = 0; r < deliv_codes.length; r++){
                                      d_templ = server.eval("@SOBJECT(twog/deliverable_templ['code','" + deliv_codes[r] + "'])")[0];
                                      if(d_templ.work_order_deliverables_code != wo_deliverable_code){
                                          if(new_str == ''){
                                              new_str = deliv_codes[r];
                                          }else{
                                              new_str = new_str + ',' + deliv_codes[r];
                                          }
                                      }
                                  }
                                  server.update(wot.__search_key__, {'deliverable_templ_codes': new_str})
                              }
                              full_title_name = ''
                              title = server.eval("@SOBJECT(twog/title['code','" + title_code + "'])")[0];
                              full_title_name = title.title;
                              if(title.episode != '' && title.episode != null){
                                  full_title_name = full_title_name + ': ' + title.episode;
                              }
                              spt.api.load_panel(oh_cell, 'order_builder.DeliverableWdg', {title_code: title_code, order_sk: order_sk});
                              top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                              var count_cell = top_el.getElementsByClassName('deliverable_count_' + title_code)[0];
                              spt.api.load_panel(count_cell, 'order_builder.DeliverableCountWdg', {title_code: title_code, order_sk: order_sk, full_title: full_title_name});
                              var sources_line = document.getElementsByClassName('wo_sources_' + work_order_sk)[0];
                              spt.api.load_panel(sources_line, 'order_builder.WorkOrderSourcesRow', {'work_order_code': work_order_code, 'order_sk': order_sk});
                              var out_cell = overhead_el.getElementsByClassName('out_list_cell')[0];
                              spt.api.load_panel(out_cell, 'order_builder.OutFilesWdg', {'work_order_code': work_order_code, 'work_order_sk': work_order_sk, 'client_code': client_code, 'order_sk': order_sk});
                      }
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (wo_deliverable_code, work_order_code, title_code, source_code, my_title, is_master, order_sk)}
    return behavior


def get_change_deliverable_satisfied_behavior(wo_deliverable_code, work_order_code, title_code, current_state,
                                              client_code, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      var server = TacticServerStub.get();
                      wo_deliverable_code = '%s';
                      work_order_code = '%s';
                      title_code = '%s';
                      state = '%s';
                      client_code = '%s';
                      order_sk = '%s';
                      new_val = '';
                      if(state == 'False'){
                          new_val = 'True';
                      }else{
                          new_val = 'False';
                      }
                      server.update(server.build_search_key('twog/work_order_deliverables', wo_deliverable_code), {'satisfied': new_val});
                      var overhead_el = spt.api.get_parent(bvr.src_el, '.out_overhead_' + work_order_code);
                      var oh_cell = overhead_el.getElementsByClassName('deliverable_list_cell')[0];
                      spt.api.load_panel(oh_cell, 'order_builder.DeliverableWdg', {title_code: title_code, order_sk: order_sk});
                      top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                      var count_cell = top_el.getElementsByClassName('deliverable_count_' + title_code)[0];
                      title = server.eval("@SOBJECT(twog/title['code','" + title_code + "'])")[0];
                      full_title_name = title.title;
                      if(title.episode != '' && title.episode != null){
                          full_title_name = full_title_name + ': ' + title.episode;
                      }
                      spt.api.load_panel(count_cell, 'order_builder.DeliverableCountWdg', {title_code: title_code, order_sk: order_sk, full_title: full_title_name});
                      var out_cell = overhead_el.getElementsByClassName('out_list_cell')[0];
                      work_order_sk = server.build_search_key('twog/work_order', work_order_code)
                      spt.api.load_panel(out_cell, 'order_builder.OutFilesWdg', {'work_order_code': work_order_code, 'work_order_sk': work_order_sk, 'client_code': client_code, 'order_sk': order_sk});
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
            }
     ''' % (wo_deliverable_code, work_order_code, title_code, current_state, client_code, order_sk)}
    return behavior


def get_template_deliverable_behavior(wo_deliverable_code, wo_templ_code, deliverable_source_code, work_order_code):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      //alert('m24');
                      var server = TacticServerStub.get();
                      wo_deliverable_code = '%s';
                      wo_templ_code = '%s';
                      //alert(wo_templ_code);
                      deliverable_source_code = '%s';
                      work_order_code = '%s';
                      wo_deliverable_expr = "@SOBJECT(twog/work_order_deliverables['code','" + wo_deliverable_code + "'])";
                      wo_deliverable = server.eval(wo_deliverable_expr)[0];

                      deliverable_expr = "@SOBJECT(twog/source['code','" + deliverable_source_code + "'])";
                      deliverable = server.eval(deliverable_expr)[0];
                      data = {};
                      data['aspect_ratio'] = deliverable.aspect_ratio;
                      data['color_space'] = deliverable.color_space;
                      data['title'] = deliverable.title;
                      data['file_type'] = deliverable.file_type;
                      data['format'] = deliverable.format;
                      data['frame_rate'] = deliverable.frame_rate;
                      data['standard'] = deliverable.standard;
                      data['total_run_time'] = deliverable.total_run_time;
                      data['source_type'] = deliverable.source_type;
                      data['subtitles'] = deliverable.subtitles;
                      data['captioning'] = deliverable.captioning;
                      data['textless'] = deliverable.textless;
                      data['generation'] = deliverable.generation;
                      data['audio_ch_1'] = deliverable.audio_ch_1;
                      data['audio_ch_2'] = deliverable.audio_ch_2;
                      data['audio_ch_3'] = deliverable.audio_ch_3;
                      data['audio_ch_4'] = deliverable.audio_ch_4;
                      data['audio_ch_5'] = deliverable.audio_ch_5;
                      data['audio_ch_6'] = deliverable.audio_ch_6;
                      data['audio_ch_7'] = deliverable.audio_ch_7;
                      data['audio_ch_8'] = deliverable.audio_ch_8;
                      data['audio_ch_9'] = deliverable.audio_ch_9;
                      data['audio_ch_10'] = deliverable.audio_ch_10;
                      data['audio_ch_11'] = deliverable.audio_ch_11;
                      data['audio_ch_12'] = deliverable.audio_ch_12;
                      data['audio_ch_13'] = deliverable.audio_ch_13;
                      data['audio_ch_14'] = deliverable.audio_ch_14;
                      data['audio_ch_15'] = deliverable.audio_ch_15;
                      data['audio_ch_16'] = deliverable.audio_ch_16;
                      data['audio_ch_17'] = deliverable.audio_ch_17;
                      data['audio_ch_18'] = deliverable.audio_ch_18;
                      data['audio_ch_19'] = deliverable.audio_ch_19;
                      data['audio_ch_20'] = deliverable.audio_ch_20;
                      data['audio_ch_21'] = deliverable.audio_ch_21;
                      data['audio_ch_22'] = deliverable.audio_ch_22;
                      data['audio_ch_23'] = deliverable.audio_ch_23;
                      data['audio_ch_24'] = deliverable.audio_ch_24;
                      data['work_order_templ_code'] = wo_templ_code;
                      data['work_order_deliverables_code'] = wo_deliverable_code;
                      data['attn'] = wo_deliverable.attn;
                      data['name'] = wo_deliverable.name;
                      data['deliver_to'] = wo_deliverable.deliver_to;
                      res = server.insert('twog/deliverable_templ', data);
                      d_templ_code = res.code;
                      server.update(wo_deliverable.__search_key__, {'deliverable_templ_code': res.code});
                      templ_expr = "@SOBJECT(twog/work_order_templ['code','" + wo_templ_code + "'])";
                      wo_templ = server.eval(templ_expr)[0];
                      del_templ_codes = wo_templ.deliverable_templ_codes;
                      if(del_templ_codes == ''){
                          del_templ_codes = d_templ_code;
                      }else{
                          del_templ_codes = del_templ_codes + ',' + d_templ_code;
                      }
                      server.update(wo_templ.__search_key__, {'deliverable_templ_codes': del_templ_codes})
                      var top_el = spt.api.get_parent(bvr.src_el, '.out_overhead_' + work_order_code);
                      var cell = top_el.getElementsByClassName('deliverable_templ_' + wo_deliverable_code)[0];
                      cell.innerHTML = '<img border="0" style="vertical-align: middle" title="Templated" name="Templated" src="/context/icons/silk/tick.png">';
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (wo_deliverable_code, wo_templ_code, deliverable_source_code, work_order_code)}

    return behavior

def get_save_deliv_info_behavior(wo_deliverable_code, work_order_code, title_code, client_code, is_master, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      var server = TacticServerStub.get();
                      wo_deliverable_code = '%s';
                      work_order_code = '%s';
                      title_code = '%s';
                      client_code = '%s';
                      is_master = '%s';
                      order_sk = '%s';
                      wo_del_sk = server.build_search_key('twog/work_order_deliverables', wo_deliverable_code);
                      var overhead_el = spt.api.get_parent(bvr.src_el, '.out_overhead_' + work_order_code);
                      name_el = overhead_el.getElementsByClassName('deliv_name_' + wo_deliverable_code)[0];
                      attn_el = overhead_el.getElementsByClassName('deliv_attn_' + wo_deliverable_code)[0];
                      deliver_to_el = overhead_el.getElementsByClassName('deliver_to_' + wo_deliverable_code)[0];
                      server.update(wo_del_sk, {'attn': attn_el.value, 'name': name_el.value, 'deliver_to': deliver_to_el.value})
                      if(is_master == 'true'){
                         delv_tmpls = server.eval("@SOBJECT(twog/deliverable_templ['work_order_deliverables_code','" + wo_deliverable_code + "'])")
                         if(delv_templs.length > 0){
                             server.update(delv_templs[0].__search_key__, {'attn': attn_el.value, 'name': name_el.value, 'deliver_to': deliver_to_el.value})
                         }
                      }
                      top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                      var count_cell = top_el.getElementsByClassName('deliverable_count_' + title_code)[0];
                      full_title_name = ''
                      title = server.eval("@SOBJECT(twog/title['code','" + title_code + "'])")[0];
                      full_title_name = title.title;
                      if(title.episode != '' && title.episode != null){
                          full_title_name = full_title_name + ': ' + title.episode;
                      }
                      spt.api.load_panel(count_cell, 'order_builder.DeliverableCountWdg', {title_code: title_code, order_sk: order_sk, full_title: full_title_name});
                      var out_cell = overhead_el.getElementsByClassName('out_list_cell')[0];
                      work_order_sk = server.build_search_key('twog/work_order', work_order_code)
                      spt.api.load_panel(out_cell, 'order_builder.OutFilesWdg', {'work_order_code': work_order_code, 'work_order_sk': work_order_sk, 'client_code': client_code, 'order_sk': order_sk});
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
            }
     ''' % (wo_deliverable_code, work_order_code, title_code, client_code, is_master, order_sk)}
    return behavior
