from client.tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseRefreshWdg

from pyasm.search import Search
from pyasm.web import Table
from pyasm.widget import TextWdg

from order_builder_utils import OBScripts, get_launch_wo_source_behavior


class WorkOrderSourcesRow(BaseRefreshWdg):

    def init(my):
        my.server = TacticServerStub.get()
        my.work_order_sk = ''
        my.work_order_code = ''
        my.order_sk = ''

    def get_snapshot_file_link(my, snapshot_code):
        what_to_ret = ''
        base = '/volumes'
        rel_paths = my.server.get_all_paths_from_snapshot(snapshot_code, mode='relative')
        ctx_expr = "@GET(sthpw/snapshot['code','%s'].context)" % snapshot_code
        ctx = my.server.eval(ctx_expr)[0]
        if len(rel_paths) > 0:
            rel_path = rel_paths[0]
            splits = rel_path.split('/')
            if len(splits) < 2:
                splits = rel_path.split('\\')
            file_only = splits[len(splits) - 1]
            what_to_ret = '<a href="%s/%s">%s: %s</a>' % (base,rel_path, ctx, file_only)
        return what_to_ret

    def get_display(my):
        my.work_order_code = str(my.kwargs.get('work_order_code'))
        my.work_order_sk = str(my.kwargs.get('work_order_sk'))
        my.work_order_sk = my.server.build_search_key('twog/work_order', my.work_order_code)
        my.order_sk = str(my.kwargs.get('order_sk'))

        wsource_search = Search("twog/work_order_sources")
        wsource_search.add_filter('work_order_code', my.work_order_code)
        wo_sources = wsource_search.get_sobjects()
        table = Table()
        table.add_attr('width', '100%')
        table.add_attr('bgcolor', '#c6c6e4')
        table.add_style('border-bottom-left-radius', '10px')
        table.add_style('border-top-left-radius', '10px')
        table.add_row()
        source_limit = 4
        pass_search = Search("twog/work_order_passin")
        pass_search.add_filter('work_order_code', my.work_order_code)
        passins = pass_search.get_sobjects()
        sources = []
        inter_passins = []
        for passin in passins:
            if passin.get_value('deliverable_source_code') not in [None,'']:
                source_search = Search("twog/source")
                source_search.add_filter('code', passin.get_value('deliverable_source_code'))
                that_src = source_search.get_sobject()
                sources.append(that_src)
            elif passin.get_value('intermediate_file_code') not in [None,'']:
                inter_search = Search("twog/intermediate_file")
                inter_search.add_filter('code', passin.get_value('intermediate_file_code'))
                inter_file = inter_search.get_sobject()
                inter_passins.append(inter_file)

        seen = []
        for wo_source in wo_sources:
            source_code = wo_source.get_value('source_code')
            if source_code not in seen:
                seen.append(source_code)
                source_search = Search("twog/source")
                source_search.add_filter("code", source_code)
                source = source_search.get_sobject()
                sources.append(source)

        if len(sources) > 0:
            table.add_row()
            mr_title = table.add_cell('<b><u><i>Sources</i></u></b>')
            mr_title.add_style('font-size: 90%;')

        count = 0
        for source in sources:
            inner_table = Table()
            inner_table.add_row()

            if not source.get_value('high_security'):
                celly = inner_table.add_cell('<font color="#3e3e3e"><b><u>(%s): %s</u></b></font>' % (source.get_value('barcode'),source.get_value('title')))
            else:
                celly = inner_table.add_cell('<font color="#ff0000"><b><u>!!!(%s): %s!!!</u></b></font>' % (source.get_value('barcode'),source.get_value('title')))
            celly.add_attr('nowrap','nowrap')
            celly.add_style('cursor: pointer;')
            celly.add_style('font-size: 80%s;' % '%')
            celly.add_behavior(get_launch_wo_source_behavior(my.work_order_code, my.work_order_sk,
                                                             source.get_value('code'), my.order_sk))
            if count % source_limit == 0:
                table.add_row()
            inner_cell = table.add_cell(inner_table)
            inner_cell.add_attr('valign', 'top')
            table.add_cell(' &nbsp;&nbsp; ')
            count += 1

        inter_pass_table = Table()
        inter_pass_table.add_attr('width', '100%')
        inter_pass_table.add_attr('bgcolor', '#c6c6e4')
        if len(inter_passins) > 0:
            inter_pass_table.add_row()
            mr_title = inter_pass_table.add_cell('<b><u><i>Intermediate Sources</i></u></b>')
            mr_title.add_attr('nowrap', 'nowrap')
            mr_title.add_style('font-size: 90%;')
            if len(sources) < 1:
                inter_pass_table.add_style('border-top-left-radius', '10px')
                inter_pass_table.add_style('border-bottom-left-radius', '10px')
        count = 0
        for intermediate in inter_passins:
            inner_table = Table()
            inner_table.add_row()
            celly = inner_table.add_cell('<font color="#3e3e3e"><b><u>%s</u></b></font>' % (intermediate.get_value('title')))
            celly.add_attr('nowrap', 'nowrap')
            celly.add_style('cursor: pointer;')
            celly.add_style('font-size: 80%;')
            celly.add_behavior(get_launch_wo_inter_behavior(my.work_order_code, my.work_order_sk,
                                                            intermediate.get_value('code'), my.order_sk))
            if count % source_limit == 0:
                inter_pass_table.add_row()
            inner_cell = inter_pass_table.add_cell(inner_table)
            inner_cell.add_attr('valign','top')
            inter_pass_table.add_cell(' &nbsp;&nbsp; ')

            count += 1

        # Need to enter Interims and Delivs Here
        inter_table = Table()
        inter_table.add_attr('width', '100%')
        inter_table.add_attr('bgcolor', '#acbe49e')
        wointer_search = Search("twog/work_order_intermediate")
        wointer_search.add_filter('work_order_code', my.work_order_code)
        wointers = wointer_search.get_sobjects()
        if len(wointers) > 0:
            inter_table.add_row()
            mr_title = inter_table.add_cell('<b><u><i>Intermediate Results</i></u></b>')
            mr_title.add_attr('nowrap', 'nowrap')
            mr_title.add_style('font-size: 90%s;' % '%')
            if len(sources) < 1 and len(inter_passins) < 1:
                inter_table.add_style('border-top-left-radius', '10px')
                inter_table.add_style('border-bottom-left-radius', '10px')
        count = 0
        for wointer in wointers:
            inter_code = wointer.get_value('intermediate_file_code')
            if inter_code not in seen:
                seen.append(inter_code)
                inter_search = Search("twog/intermediate_file")
                inter_search.add_filter('code',inter_code)
                intermediate = inter_search.get_sobject()
                inner_table = Table()
                inner_table.add_row()
                celly = inner_table.add_cell('<font color="#3e3e3e"><b><u>%s</u></b></font>' % (intermediate.get_value('title')))
                celly.add_attr('nowrap','nowrap')
                celly.add_style('cursor: pointer;')
                celly.add_style('font-size: 80%s;' % '%')
                celly.add_behavior(get_launch_wo_inter_behavior(my.work_order_code, my.work_order_sk, inter_code,
                                                                my.order_sk))
                if count % source_limit == 0:
                    inter_table.add_row()
                inner_cell = inter_table.add_cell(inner_table)
                inner_cell.add_attr('valign', 'top')
                inter_table.add_cell(' &nbsp;&nbsp; ')

                count += 1

        # Need deliverables listed here
        deliv_table = Table()
        deliv_table.add_attr('width','100%s' % '%')
        deliv_table.add_attr('bgcolor','#acbe49e')
        deliv_table.add_style('border-bottom-right-radius', '10px')
        deliv_table.add_style('border-top-right-radius', '10px')
        d_search = Search("twog/work_order_deliverables")
        d_search.add_filter('work_order_code',my.work_order_code)
        wodelivs = d_search.get_sobjects()
        if len(wodelivs) > 0:
            deliv_table.add_row()
            mr_title = deliv_table.add_cell('<b><u><i>Permanent Results</i></u></b>')
            mr_title.add_attr('nowrap','nowrap')
            mr_title.add_style('font-size: 90%s;' % '%')
            if len(sources) < 1 and len(inter_passins) < 1 and len(wointers) < 1:
                deliv_table.add_style('border-top-left-radius', '10px')
                deliv_table.add_style('border-bottom-left-radius', '10px')
        count = 0
        for wodeliv in wodelivs:
            deliv_code = wodeliv.get_value('deliverable_source_code')
            if deliv_code not in seen:
                seen.append(deliv_code)
                s_search = Search("twog/source")
                s_search.add_filter('code',deliv_code)
                deliverable = s_search.get_sobjects()
                if len(deliverable) > 0:
                    deliverable = deliverable[0]
                    inner_table = Table()
                    inner_table.add_row()

                    if not deliverable.get_value('high_security'):
                        celly = inner_table.add_cell('<font color="#3e3e3e"><b><u>(%s): %s</u></b></font>' % (deliverable.get_value('barcode'), deliverable.get_value('title')))
                    else:
                        celly = inner_table.add_cell('<font color="#ff0000"><b><u>!!!(%s): %s!!!</u></b></font>' % (deliverable.get_value('barcode'), deliverable.get_value('title')))
                    celly.add_attr('nowrap','nowrap')
                    celly.add_style('cursor: pointer;')
                    celly.add_style('font-size: 80%s;' % '%')
                    celly.add_behavior(get_launch_wo_deliv_behavior(my.work_order_code, my.work_order_sk, deliv_code,
                                                                    my.order_sk))
                    if count % source_limit == 0:
                        deliv_table.add_row()
                    inner_cell = deliv_table.add_cell(inner_table)
                    inner_cell.add_attr('valign','top')
                    deliv_table.add_cell(' &nbsp;&nbsp; ')

                    count += 1
                else:
                    with open('/var/www/html/Lost_Sources','a') as lostsources:
                        lostsources.write('%s:%s SOURCE: %s\n' % (my.order_sk, my.work_order_code, deliv_code))
                        lostsources.close()

        if len(wodelivs) < 1:
            inter_table.add_style('border-bottom-right-radius', '10px')
            inter_table.add_style('border-top-right-radius', '10px')
        if len(wodelivs) < 1 and len(wointers) < 1:
            inter_pass_table.add_style('border-bottom-right-radius', '10px')
            inter_pass_table.add_style('border-top-right-radius', '10px')
        if len(inter_passins) < 1 and len(wointers) < 1 and len(wodelivs) < 1:
            table.add_style('border-bottom-right-radius', '10px')
            table.add_style('border-top-right-radius', '10px')

        table2 = Table()
        table2.add_row()
        barcode_text_wdg = TextWdg('wo_barcode_insert')
        barcode_text_wdg.add_behavior(get_wo_barcode_insert_behavior(my.work_order_code, my.work_order_sk, my.order_sk))
        bct = table2.add_cell(barcode_text_wdg)
        bct.add_attr('align', 'right')
        bct.add_attr('width', '100%')

        two_gether = Table()
        two_gether.add_row()
        if len(sources) > 0:
            srcs = two_gether.add_cell(table)
            srcs.add_attr('width', '100%')
            srcs.add_attr('valign', 'top')
        if len(inter_passins) > 0:
            ips = two_gether.add_cell(inter_pass_table)
            ips.add_attr('width', '100%')
            ips.add_attr('valign', 'top')
        if len(wointers) > 0:
            intr = two_gether.add_cell(inter_table)
            intr.add_attr('width', '100%')
            intr.add_attr('valign', 'top')
        if len(wodelivs) > 0:
            delvs = two_gether.add_cell(deliv_table)
            delvs.add_attr('width', '100%')
            delvs.add_attr('valign', 'top')
        long = two_gether.add_cell(' ')
        long.add_style('width: 100%')
        bcentry = two_gether.add_cell(table2)
        bcentry.add_attr('valign', 'top')
        bcentry.add_attr('align', 'right')

        for source in sources:
            if source.get_value('children') in [None,'']:
                update_str = ''
                for wod in wodelivs:
                    if update_str == '':
                        update_str = wod.get_value('deliverable_source_code')
                    else:
                        update_str = '%s,%s' % (update_str, wod.get_value('deliverable_source_code'))
                    d_search = Search("twog/source")
                    d_search.add_filter('code', wod.get_value('deliverable_source_code'))
                    d_src = d_search.get_sobject()
                    ancestors = d_src.get_value('ancestors')
                    if ancestors.find(source.get_value('code')) == -1:
                        if ancestors in [None,'']:
                            ancestors = source.get_value('code')
                        else:
                            ancestors = '%s,%s' % (ancestors, source.get_value('code'))
                        my.server.update(d_src.get_search_key(), {'ancestors': ancestors})
                if len(wodelivs) > 0:
                    my.server.update(source.get_search_key(), {'children': update_str})

        return two_gether


def get_launch_wo_inter_behavior(work_order_code, work_order_sk, wo_inter, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      //alert('m41');
                      var server = TacticServerStub.get();
                      var work_order_code = '%s';
                      var work_order_sk = '%s';
                      var wo_inter = '%s';
                      var order_sk = '%s';
                      var inter_sk = server.build_search_key('twog/intermediate_file',wo_inter);
                      var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                      var wo_cell = top_el.getElementsByClassName('cell_' + work_order_sk)[0];
                      var proj_cell = top_el.getElementsByClassName('cell_' + wo_cell.getAttribute('parent_sk'))[0];
                      var title_sk = proj_cell.getAttribute('parent_sk');
                      var title_cell = top_el.getElementsByClassName('cell_' + title_sk)[0];
                      var client_code = top_el.getAttribute('client_code');
                      var title_code = title_sk.split('code=')[1];
                      spt.panel.load_popup('Intermediate File Portal', 'order_builder.IntermediateEditWdg', {'order_sk': order_sk, 'work_order_code': work_order_code, 'intermediate_code': wo_inter, 'client_code': client_code});
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (work_order_code, work_order_sk, wo_inter, order_sk)}
    return behavior


def get_launch_wo_deliv_behavior(work_order_code, work_order_sk, wo_deliv, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      //alert('m40');
                      var server = TacticServerStub.get();
                      var work_order_code = '%s';
                      var work_order_sk = '%s';
                      var wo_deliv = '%s';
                      var order_sk = '%s';
                      spt.panel.load_popup('Permanent Source Portal', 'order_builder.SourceEditWdg', {'code': wo_deliv, 'order_sk': order_sk});
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (work_order_code, work_order_sk, wo_deliv, order_sk)}
    return behavior


def get_wo_barcode_insert_behavior(wo_code, wo_sk, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'change', 'cbjs_action': '''
                    function oc(a){
                        var o = {};
                        for(var i=0;i<a.length;i++){
                            o[a[i]]='';
                        }
                        return o;
                    }
                    try{
                      //alert('m38');
                      var server = TacticServerStub.get();
                      wo_code = '%s';
                      wo_sk = '%s';
                      order_sk = '%s';
                      wo = server.eval("@SOBJECT(twog/work_order['code','" + wo_code + "'])")[0];
                      title_code = server.eval("@GET(twog/proj['code','" + wo.proj_code + "'].title_code)")[0];
                      title_sk = server.build_search_key('twog/title', title_code);
                      var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                      var source_el = top_el.getElementsByClassName('wo_sources_' + wo_sk)[0];
                      var title_source_el = top_el.getElementsByClassName('sources_' + title_sk)[0];
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
                          source = sources[0];
                          title_sources = server.eval("@GET(twog/title_origin['title_code','" + title_code + "'].source_code)");
                          if(!(source.code in oc(title_sources))){
                              server.insert('twog/title_origin', {title_code: title_code, source_code: source.code});
                              spt.api.load_panel(title_source_el, 'order_builder.SourcesRow', {title_code: title_code, title_sk: title_sk, order_sk: order_sk});
                          }
                          wo_sources = server.eval("@GET(twog/work_order_sources['work_order_code','" + wo_code + "'].source_code)");
                          wo_passins = server.eval("@SOBJECT(twog/work_order_passin['work_order_code','" + wo_code + "'])");
                          for(var r = 0; r < wo_passins.length; r++){
                              if(wo_passins[r].deliverable_source_code != ''){
                                  wo_sources.push(wo_passins[r].deliverable_source_code);
                              }
                          }
                          if(!(source.code in oc(wo_sources))){
                              server.insert('twog/work_order_sources', {work_order_code: wo_code, source_code: source.code});
                              spt.api.load_panel(source_el, 'order_builder.WorkOrderSourcesRow', {work_order_code: wo_code, work_order_sk: wo_sk, order_sk: order_sk});

                              work_o_sources_expr = "@SOBJECT(twog/work_order_sources['work_order_code','" + wo_code + "'])";
                              work_o_sources = server.eval(work_o_sources_expr);
                              work_o_passins = server.eval("@SOBJECT(twog/work_order_passin['work_order_code','" + wo_code + "'])");
                              work_o_deliverables_expr = "@SOBJECT(twog/work_order_deliverables['work_order_code','" + wo_code + "'])";
                              work_o_deliverables = server.eval(work_o_deliverables_expr);
                              my_sources = []
                              my_deliverables = []
                              for(var r = 0; r < work_o_sources.length; r++){
                                  source_expr = "@SOBJECT(twog/source['code','" + work_o_sources[r].source_code + "'])";
                                  source = server.eval(source_expr)
                                  if(source.length > 0){
                                      my_sources.push(source[0])
                                  }
                              }
                              for(var r = 0; r < work_o_passins.length; r++){
                                  var dsc = work_o_passins[r].deliverable_source_code;
                                  if(dsc != '' && dsc != null){
                                      source_expr = "@SOBJECT(twog/source['code','" + dsc + "'])";
                                      source = server.eval(source_expr);
                                      if(source.length > 0){
                                          my_sources.push(source[0]);
                                      }
                                  }
                              }
                              for(var r = 0; r < work_o_deliverables.length; r++){
                                  source_expr = "@SOBJECT(twog/source['code','" + work_o_deliverables[r].deliverable_source_code + "'])";
                                  source = server.eval(source_expr);
                                  if(source.length > 0){
                                       my_deliverables.push(source[0])
                                  }
                              }
                              for(var r = 0; r < my_sources.length; r++){
                                  kids = my_sources[r].children.split(',');
                                  new_str = my_sources[r].children;
                                  for(var t = 0; t < my_deliverables.length; t++){
                                      if(!(my_deliverables[t].code in oc(kids))){
                                          if(new_str == '' || new_str == null){
                                              new_str = my_deliverables[t].code;
                                          }else{
                                              new_str = new_str + ',' + my_deliverables[t].code;
                                          }
                                      }
                                  }
                                  server.update(my_sources[r].__search_key__, {'children': new_str});
                              }
                              for(var r = 0; r < my_deliverables.length; r++){
                                  ancestors = my_deliverables[r].ancestors.split(',');
                                  new_str = my_deliverables[r].ancestors;
                                  for(var t = 0; t < my_sources.length; t++){
                                      if(!(my_sources[t].code in oc(ancestors))){
                                          if(new_str == '' || new_str == null){
                                              new_str = my_sources[t].code;
                                          }else{
                                              new_str = new_str + ',' + my_sources[t].code;
                                          }
                                      }
                                  }
                                  server.update(my_deliverables[r].__search_key__, {'ancestors': new_str});
                              }

                          }
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
     ''' % (wo_code, wo_sk, order_sk)}
    return behavior
