from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Environment
from pyasm.web import Table
from pyasm.search import Search

from widget.new_icon_wdg import CustomIconWdg
from widget.button_small_new_wdg import ButtonSmallNewWdg

from order_builder_utils import get_open_intermediate_behavior, get_launch_wo_source_behavior


class SourcePortalWdg(BaseRefreshWdg):

    def init(my):
        my.work_order_code = ''
        my.client_code = ''
        my.parent_pipe = ''
        my.order_sk = ''
        my.is_master = ''
        my.x_butt = "<img src='/context/icons/common/BtnKill_Black.gif' title='Delete' name='Delete'/>"

    def get_display(my):
        my.work_order_code = str(my.kwargs.get('work_order_code'))
        my.client_code = str(my.kwargs.get('client_code'))
        my.parent_pipe = str(my.kwargs.get('parent_pipe'))
        my.is_master = str(my.kwargs.get('is_master'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        wo_search = Search("twog/work_order")
        wo_search.add_filter('code', my.work_order_code)
        work_order = wo_search.get_sobject()
        wo_sk = work_order.get_search_key()
        proj_code = work_order.get_value('proj_code')
        wo_templ_code = work_order.get_value('work_order_templ_code')
        ws_search = Search("twog/work_order_sources")
        ws_search.add_filter("work_order_code", my.work_order_code)
        work_order_sources = ws_search.get_sobjects()

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

        ignore_processes = work_order.get_value('process')
        other_search = Search("twog/work_order")
        other_search.add_filter('proj_code', work_order.get_value('proj_code'))
        other_search.add_filter('process', ignore_processes, op="!=")
        all_other_wos = other_search.get_sobjects()

        all_other_interms = {}
        for other in all_other_wos:
            or_search = Search("twog/work_order_intermediate")
            or_search.add_filter('work_order_code',other.get_value('code'))
            other_reals = or_search.get_sobjects()
            for otr in other_reals:
                intermediate_file_code = otr.get_value('intermediate_file_code')
                inter_search = Search("twog/intermediate_file")
                inter_search.add_filter('code', intermediate_file_code)
                intermediate_file = inter_search.get_sobject()
                inter_title = intermediate_file.get_value('inter_file')
                if other.get_value('code') not in all_other_interms.keys():
                    all_other_interms[other.get_value('code')] = []
                all_other_interms[other.get_value('code')].append([inter_title, intermediate_file.get_value('code')])

        order_code = my.order_sk.split('code=')[1]
        overhead = Table()
        overhead.add_attr('class','sp_overhead_%s' % my.work_order_code)
        overhead.add_attr('client_code', my.client_code)
        overhead.add_attr('is_master', my.is_master)
        overhead.add_attr('parent_pipe', my.parent_pipe)

        table = Table()
        src_tbl = Table()
        for sc in work_order_sources:
            src_search = Search("twog/source")
            src_search.add_filter('code', sc.get_value('source_code'))
            src = src_search.get_sobjects()
            if len(src) > 0:
                src = src[0]
                src_tbl.add_row()
                if user_is_scheduler:
                    killer = src_tbl.add_cell(my.x_butt)
                    killer.add_style('cursor: pointer;')
                    killer.add_behavior(get_source_killer_behavior(sc.get_value('code'), my.work_order_code,
                                                                   my.parent_pipe, my.client_code, my.is_master,
                                                                   '%s: %s' % (src.get_value('title'),
                                                                               src.get_value('episode')),
                                                                   my.order_sk))
                alabel = src_tbl.add_cell('Source: ')
                alabel.add_attr('align', 'center')
                popper = src_tbl.add_cell('<u>%s: %s</u>' % (src.get_value('title'), src.get_value('episode')))
                popper.add_attr('nowrap', 'nowrap')
                popper.add_style('cursor: pointer;')
                popper.add_behavior(get_launch_wo_source_behavior(my.work_order_code, wo_sk, src.get_value('code'),
                                                                  my.order_sk))
        table.add_row()
        table.add_cell(src_tbl)

        pass_search = Search("twog/work_order_passin")
        pass_search.add_filter('work_order_code', my.work_order_code)
        passins = pass_search.get_sobjects()

        table.add_row()
        table.add_cell(' ')
        table.add_cell(' ')
        add_deliv_passin_butt = table.add_cell('<input type="button" value="Add Permanent Element Pass-in"/>')
        add_deliv_passin_butt.add_attr('colspan', '2')
        add_deliv_passin_butt.add_behavior(get_add_deliverable_passin_behavior(my.work_order_code, wo_templ_code,
                                                                               proj_code, my.order_sk))
        # Now do passed in permanent sources, which can be templated
        dsrc_tbl = Table()
        for p in passins:
            if p.get_value('deliverable_source_code') not in [None,'']:
                ds_search = Search("twog/source")
                ds_search.add_filter('code', p.get_value('deliverable_source_code'))
                d_source = ds_search.get_sobjects()
                if len(d_source) > 0:
                    d_source = d_source[0]
                    dsrc_tbl.add_row()
                    if user_is_scheduler:
                        killer = dsrc_tbl.add_cell(my.x_butt)
                        killer.add_style('cursor: pointer;')
                        killer.add_behavior(get_deliverable_passin_killer_behavior(p.get_value('code'),
                                                                                   my.work_order_code, wo_templ_code,
                                                                                   my.parent_pipe, my.client_code,
                                                                                   my.is_master,
                                                                                   '%s: %s' % (d_source.get_value('title'),
                                                                                               d_source.get_value('episode')),
                                                                                   my.order_sk))
                    alabel = dsrc_tbl.add_cell('Source: ')
                    alabel.add_attr('align', 'center')
                    popper = dsrc_tbl.add_cell('<u>%s: %s</u>' % (d_source.get_value('title'),
                                                                  d_source.get_value('episode')))
                    popper.add_attr('nowrap', 'nowrap')
                    popper.add_style('cursor: pointer;')
                    popper.add_behavior(get_launch_wo_source_behavior(my.work_order_code, wo_sk,
                                                                      d_source.get_value('code'), my.order_sk))
                    if my.is_master in [True,'true','True',1,'t']:
                        if p.get_value('passin_templ_code') in [None,'']:
                            template_button = ButtonSmallNewWdg(title="Template This Passed-in Source", icon=CustomIconWdg.icons.get('TEMPLATE'))
                            if my.is_master == 'true':
                                template_button.add_behavior(get_template_deliverable_passin_behavior(my.work_order_code, wo_templ_code, p.get_value('code')))
                        else:
                            template_button = '<img border="0" style="vertical-align: middle" title="Templated" name="Templated" src="/context/icons/silk/tick.png">'
                        tb = dsrc_tbl.add_cell(template_button)
                        tb.add_attr('class', 'sp_templ_%s' % p.get_value('code'))
        if my.is_master in [True, 'true', 'True', 1, 't']:
            table.add_row()
            table.add_cell(dsrc_tbl)

        table.add_row()
        divider = table.add_cell('<hr/>')
        divider.add_attr('colspan', '4')
        table.add_row()
        table.add_cell(' ')
        table.add_cell(' ')
        adinter_fm_butt = table.add_cell('<input type="button" value="Add Intermediate Pass-in"/>')
        adinter_fm_butt.add_attr('colspan', '2')
        adinter_fm_butt.add_behavior(get_add_intermediate_passin_behavior(my.work_order_code, wo_templ_code, proj_code,
                                                                          my.order_sk))
        inter_tbl = Table()
        for p in passins:
            if p.get_value('intermediate_file_code') not in [None,'']:
                in_search = Search("twog/intermediate_file")
                in_search.add_filter('code', p.get_value('intermediate_file_code'))
                inter_f = in_search.get_sobjects()
                if len(inter_f) > 0:
                    inter_f = inter_f[0]
                    inter_tbl.add_row()
                    if user_is_scheduler:
                        killer = inter_tbl.add_cell(my.x_butt)
                        killer.add_style('cursor: pointer;')
                        killer.add_behavior(get_intermediate_passin_killer_behavior(p.get_value('code'),
                                                                                    my.work_order_code, wo_templ_code,
                                                                                    my.parent_pipe, my.client_code,
                                                                                    my.is_master,
                                                                                    inter_f.get_value('title'),
                                                                                    my.order_sk))
                    alabel = inter_tbl.add_cell('Intermediate: ')
                    alabel.add_attr('align','center')
                    popper = inter_tbl.add_cell('<u>%s</u>' % (inter_f.get_value('title')))
                    popper.add_attr('nowrap','nowrap')
                    popper.add_style('cursor: pointer;')
                    popper.add_behavior(get_open_intermediate_behavior(inter_f.get_value('code'),my.work_order_code, my.client_code, my.order_sk))
                    if my.is_master in [True,'true','True',1,'t']:
                        if p.get_value('passin_templ_code') in [None,'']:
                            template_button = ButtonSmallNewWdg(title="Template This Passed-in Intermediate File", icon=CustomIconWdg.icons.get('TEMPLATE'))
                        if my.is_master == 'true':
                            template_button.add_behavior(get_template_intermediate_passin_behavior(my.work_order_code, wo_templ_code, p.get_value('code')))
                        else:
                            template_button = '<img border="0" style="vertical-align: middle" title="Templated" name="Templated" src="/context/icons/silk/tick.png">'
                        tb = inter_tbl.add_cell(template_button)
                        tb.add_attr('class', 'sp_templ_%s' % p.get_value('code'))


        table.add_row()
        table.add_cell(inter_tbl)

        overhead.add_row()
        oh_cell = overhead.add_cell(table)
        oh_cell.add_attr('class', 'sp_list_cell')

        return overhead


def get_source_killer_behavior(wo_source_code, work_order_code, parent_pipe, client_code, is_master, title, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      //alert('m44');
                      var server = TacticServerStub.get();
                      wo_source_code = '%s';
                      work_order_code = '%s';
                      parent_pipe = '%s';
                      client_code = '%s';
                      is_master = '%s';
                      title = '%s';
                      order_sk = '%s';
                      if(confirm("Are you sure you want to delete " + title + " from this work order?")){
                          wo_source_sk = server.build_search_key('twog/work_order_sources', wo_source_code);
                          server.retire_sobject(wo_source_sk);
                          var top_el = spt.api.get_parent(bvr.src_el, '.sp_overhead_' + work_order_code);
                          reload_cell = top_el.getElementsByClassName('sp_list_cell')[0];
                          spt.api.load_panel(reload_cell, 'order_builder.SourcePortalWdg', {'work_order_code': work_order_code, 'parent_pipe': parent_pipe, 'client_code': client_code, 'is_master': is_master, 'order_sk': order_sk});
                          wo_sk = server.build_search_key('twog/work_order', work_order_code);
                          var source_el = document.getElementsByClassName('wo_sources_' + wo_sk)[0];
                          spt.api.load_panel(source_el, 'order_builder.WorkOrderSourcesRow', {'work_order_code': work_order_code, 'work_order_sk': wo_sk, 'order_sk': order_sk});
                      }

            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (wo_source_code, work_order_code, parent_pipe, client_code, is_master, title, order_sk)}
    return behavior


def get_deliverable_passin_killer_behavior(passin_code, work_order_code, wo_templ_code, parent_pipe, client_code,
                                           is_master, title, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                       //alert('m2');
                       var server = TacticServerStub.get();
                       var passin_code = '%s';
                       var work_order_code = '%s';
                       var wo_templ_code = '%s';
                       var parent_pipe = '%s';
                       client_code = '%s';
                       is_master = '%s';
                       title = '%s';
                       var order_sk = '%s';
                       if(confirm("Are you sure you want to delete '" + title + "' from this work order's Passed-in elements?")){
                           passin = server.eval("@SOBJECT(twog/work_order_passin['code','" + passin_code + "'])")[0];
                           if(is_master == 'true'){
                               if(passin.passin_templ_code != ''){
                                   pass_templ_sk = server.build_search_key('twog/work_order_passin_templ', passin.passin_templ_code);
                                   server.retire_sobject(pass_templ_sk);
                               }
                           }
                           server.retire_sobject(passin.__search_key__);
                           var top_el = spt.api.get_parent(bvr.src_el, '.sp_overhead_' + work_order_code);
                           reload_cell = top_el.getElementsByClassName('sp_list_cell')[0];
                           spt.api.load_panel(reload_cell, 'order_builder.SourcePortalWdg', {'work_order_code': work_order_code, 'parent_pipe': parent_pipe, 'client_code': client_code, 'is_master': is_master, 'order_sk': order_sk});
                           wo_sk = server.build_search_key('twog/work_order', work_order_code);
                           var source_el = document.getElementsByClassName('wo_sources_' + wo_sk)[0];
                           spt.api.load_panel(source_el, 'order_builder.WorkOrderSourcesRow', {'work_order_code': work_order_code, 'work_order_sk': wo_sk, 'order_sk': order_sk});
                       }

            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (passin_code, work_order_code, wo_templ_code, parent_pipe, client_code, is_master, title, order_sk)}
    return behavior


def get_template_deliverable_passin_behavior(work_order_code, work_order_templ_code, passin_code):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      //alert('m23');
                      var server = TacticServerStub.get();
                      work_order_code = '%s';
                      work_order_templ_code = '%s';
                      passin_code = '%s';
                      //alert(passin_code);
                      passin = server.eval("@SOBJECT(twog/work_order_passin['code','" + passin_code + "'])")[0];
                      //alert(passin);
                      wod_code = passin.work_order_deliverables_code;
                      //alert(wod_code);
                      wod = server.eval("@SOBJECT(twog/work_order_deliverables['code','" + wod_code + "'])")[0];
                      dts = server.eval("@SOBJECT(twog/deliverable_templ['work_order_deliverables_code','" + wod_code + "'])");
                      deliverable_templ_code = '';
                      //alert(wod);
                      //alert(dts.length);
                      for(var r = 0; r < dts.length; r++){
                          //alert("dNAME = " + dts[r].name + " dATTN = " + dts[r].attn + " dDELIVER_TO = " + dts[r].deliver_to + " || wodNAME = " + wod.name + " wodATTN = " + wod.attn + " wodDELIVER_TO = " + wod.deliver_to);
                          if(dts[r].name == wod.name && dts[r].attn == dts[r].attn && dts[r].deliver_to == wod.deliver_to){
                              deliverable_templ_code = dts[r].code;
                          }
                      }
                      //alert(deliverable_templ_code);
                      if(deliverable_templ_code != ''){
                          //alert("poink");
                          var pt_ins = server.insert('twog/work_order_passin_templ', {'work_order_templ_code': work_order_templ_code, 'deliverable_templ_code': deliverable_templ_code});
                          server.update(passin.__search_key__, {'passin_templ_code': pt_ins.code});
                          var top_el = spt.api.get_parent(bvr.src_el, '.sp_overhead_' + work_order_code);
                          var cell = top_el.getElementsByClassName('sp_templ_' + passin_code)[0];
                          cell.innerHTML = '<img border="0" style="vertical-align: middle" title="Templated" name="Templated" src="/context/icons/silk/tick.png">';
                      }
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (work_order_code, work_order_templ_code, passin_code)}
    return behavior


def get_add_intermediate_passin_behavior(work_order_code, wo_templ_code, proj_code, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                       var server = TacticServerStub.get();
                       var work_order_code = '%s';
                       var wo_templ_code = '%s';
                       var proj_code = '%s';
                       var order_sk = '%s';
                       spt.panel.load_popup('Choose an Intermediate File to Add as a Source', 'order_builder.IntermediatePassinAddWdg', {'work_order_code': work_order_code, 'order_sk': order_sk, 'wo_templ_code': wo_templ_code, 'proj_code': proj_code});
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (work_order_code, wo_templ_code, proj_code, order_sk)}
    return behavior


def get_intermediate_passin_killer_behavior(passin_code, work_order_code, wo_templ_code, parent_pipe, client_code,
                                            is_master, title, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                       //alert('m3');
                       var server = TacticServerStub.get();
                       var passin_code = '%s';
                       var work_order_code = '%s';
                       var wo_templ_code = '%s';
                       var parent_pipe = '%s';
                       var client_code = '%s';
                       var is_master = '%s';
                       var title = '%s';
                       var order_sk = '%s';
                       //alert('got me');
                       if(confirm("Are you sure you want to delete '" + title + "' from this work order's Passed-in elements?")){
                           passin = server.eval("@SOBJECT(twog/work_order_passin['code','" + passin_code + "'])")[0];
                           if(is_master == 'true'){
                               if(passin.passin_templ_code != ''){
                                   pass_templ_sk = server.build_search_key('twog/work_order_passin_templ', passin.passin_templ_code);
                                   server.retire_sobject(pass_templ_sk);
                               }
                           }
                           server.retire_sobject(passin.__search_key__);
                           var top_el = spt.api.get_parent(bvr.src_el, '.sp_overhead_' + work_order_code);
                           reload_cell = top_el.getElementsByClassName('sp_list_cell')[0];
                           spt.api.load_panel(reload_cell, 'order_builder.SourcePortalWdg', {'work_order_code': work_order_code, 'parent_pipe': parent_pipe, 'client_code': client_code, 'is_master': is_master, 'order_sk': order_sk});
                           wo_sk = server.build_search_key('twog/work_order', work_order_code);
                           var source_el = document.getElementsByClassName('wo_sources_' + wo_sk)[0];
                           spt.api.load_panel(source_el, 'order_builder.WorkOrderSourcesRow', {'work_order_code': work_order_code, 'work_order_sk': wo_sk, 'order_sk': order_sk});
                       }
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (passin_code, work_order_code, wo_templ_code, parent_pipe, client_code, is_master, title, order_sk)}
    return behavior


def get_template_intermediate_passin_behavior(work_order_code, work_order_templ_code, passin_code):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      //alert('m22');
                      var server = TacticServerStub.get();
                      work_order_code = '%s';
                      work_order_templ_code = '%s';
                      passin_code = '%s';
                      passin = server.eval("@SOBJECT(twog/work_order_passin['code','" + passin_code + "'])")[0];
                      woi_code = passin.work_order_intermediate_code;
                      woi = server.eval("@SOBJECT(twog/work_order_intermediate['code','" + woi_code + "'])")[0];
                      intf = server.eval("@SOBJECT(twog/intermediate_file['code','" + woi.intermediate_file_code + "'])");
                      intermediate_file_templ_code = '';
                      if(intf.length > 0){
                              intermediate_file_templ_code = intf[0].intermediate_file_templ_code;
                              //alert(intermediate_file_templ_code);
                              if(intermediate_file_templ_code != ''){
                                  var pt_ins = server.insert('twog/work_order_passin_templ', {'work_order_templ_code': work_order_templ_code, 'intermediate_file_templ_code': intermediate_file_templ_code});
                                  server.update(passin.__search_key__, {'passin_templ_code': pt_ins.code});
                                  var top_el = spt.api.get_parent(bvr.src_el, '.sp_overhead_' + work_order_code);
                                  var cell = top_el.getElementsByClassName('sp_templ_' + passin_code)[0];
                                  cell.innerHTML = '<img border="0" style="vertical-align: middle" title="Templated" name="Templated" src="/context/icons/silk/tick.png">';
                              }
                      }
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (work_order_code, work_order_templ_code, passin_code)}
    return behavior


def get_add_deliverable_passin_behavior(work_order_code, wo_templ_code, proj_code, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                       var server = TacticServerStub.get();
                       var work_order_code = '%s';
                       var wo_templ_code = '%s';
                       var proj_code = '%s';
                       var order_sk = '%s';
                       spt.panel.load_popup('Choose a Permanent Element to Add as a Source', 'order_builder.DeliverablePassinAddWdg', {'work_order_code': work_order_code, 'order_sk': order_sk, 'wo_templ_code': wo_templ_code, 'proj_code': proj_code});
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (work_order_code, wo_templ_code, proj_code, order_sk)}
    return behavior
