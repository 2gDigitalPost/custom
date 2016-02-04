from tactic.ui.common import BaseRefreshWdg

from pyasm.search import Search
from pyasm.web import Table
from pyasm.widget import SelectWdg


class GlobalReplacerWdg(BaseRefreshWdg):

    def init(my):
        my.order_sk = ''
        my.allowed_titles_str = ''
        my.user_name = ''

    def get_commit(my, user_name):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        function replaceAll(find, replace, str) {
                          find = find.replace('[','\\\[').replace(']','\\\]').replace('+','\\\+');
                          return str.replace(new RegExp(find, 'g'), replace);
                        }
                        function encode_utf8( s )
                        {
                            return unescape( encodeURIComponent( s ) );
                        }
                        try{
                          var server = TacticServerStub.get();
                          var order_sk = '%s';
                          var user_name = '%s';
                          pop_el = document.getElementsByClassName('globalreplacer_' + order_sk)[0];
                          process_el = null;
                          work_hours_el = pop_el.getElementsByClassName('replace_wo_work_hours')[0];
                          instructions_el = pop_el.getElementsByClassName('replace_wo_instructions')[0];
                          start_el = pop_el.getElementsByClassName('replace_start')[0];
                          stop_el = pop_el.getElementsByClassName('replace_end')[0];
                          work_group_el = null;
                          selects = pop_el.getElementsByTagName('select');
                          for(var r = 0; r < selects.length; r++){
                              if(selects[r].name == 'replace_wo_work_group'){
                                  work_group_el = selects[r];
                              }
                              if(selects[r].name == 'replace_wo_process'){
                                  process_el = selects[r];
                              }
                          }
                          process = process_el.value;
                          work_hours = work_hours_el.value;
                          instructions = instructions_el.value;
                          instructions = encode_utf8(instructions);
                          work_group = work_group_el.value;
                          start_str = start_el.value;
                          stop_str = stop_el.value;
                          wos = server.eval("@SOBJECT(twog/work_order['code','in','" +  process + "'])");
                          changes_made = false;
                          spt.app_busy.show('Applying Changes...')
                          if(start_str != '' && start_str != null){
                              for(var r = 0; r < wos.length; r++){
                                  spt.app_busy.show('Applying Changes to ' + wos[r].process + ' (' + wos[r].code + ')');
                                  wo_inst = wos[r].instructions;
                                  //new_inst = wo_inst.replace(start_str, stop_str);
                                  new_inst = replaceAll(start_str, stop_str, wo_inst);
                                  server.update(wos[r].__search_key__, {'instructions': new_inst});
                                  changes_made = true;

                              }
                          }else{
                              update_data = {}
                              if(work_hours != '' && work_hours != null){
                                  update_data['estimated_work_hours'] = work_hours;
                              }
                              if(work_group != '' && work_group != null && work_group != '--Select--'){
                                  update_data['work_group'] = work_group;
                              }
                              if(instructions != null && instructions != ''){
                                  update_data['instructions'] = instructions;
                              }
                              if(update_data != {} && update_data != null){
                                  for(var r= 0; r < wos.length; r++){
                                      spt.app_busy.show('Applying Changes to ' + wos[r].process + ' (' + wos[r].code + ')');
                                      server.update(wos[r].__search_key__, update_data);
                                      changes_made = true;
                                  }
                              }
                          }
                          spt.app_busy.hide();
                          if(changes_made){
                              spt.app_busy.show('Reloading Panels...');
                              var top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                              display_mode = top_el.getAttribute('display_mode');
                              user = top_el.getAttribute('user');
                              groups_str = top_el.get('groups_str');
                              allowed_titles = top_el.getAttribute('allowed_titles');
                              for(var r= 0; r < wos.length; r++){
                                  wo_cell = top_el.getElementsByClassName('cell_' + wos[r].__search_key__)[0];
                                  parent_sid = wo_cell.get('parent_sid');
                                  parent_sk = wo_cell.get('parent_sk');
                                  sk = wos[r].__search_key__;
                                  reload_data = {'parent_sk': parent_sk, 'parent_sid': parent_sid, 'sk': sk, 'order_sk': order_sk, display_mode: display_mode, user: user, groups_str: groups_str, allowed_titles: allowed_titles};
                                  spt.api.load_panel(wo_cell, 'order_builder.WorkOrderRow', reload_data);
                              }
                              start_el.value = '';
                              stop_el.value = '';
                          }
                          spt.app_busy.hide();

                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (my.order_sk, user_name)}
        return behavior

    def get_display(my):
        my.user_name = str(my.kwargs.get('user_name'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        my.allowed_titles_str = str(my.kwargs.get('allowed_titles_str'))
        split_allow = my.allowed_titles_str.split('|')
        allowed_search_titles = ''
        for sa in split_allow:
            if allowed_search_titles == '':
                allowed_search_titles = "('%s'" % sa
            else:
                allowed_search_titles = "%s,'%s'" % (allowed_search_titles, sa)
        if allowed_search_titles != '':
            allowed_search_titles = '%s)' % allowed_search_titles
        wo_search = Search("twog/work_order")
        wo_search.add_where("\"title_code\" in %s" % allowed_search_titles)
        wos = wo_search.get_sobjects()
        process_sel = SelectWdg('replace_wo_process')
        proc_count = {}
        seen_procs = []
        piped_names = {'ALL': ''}
        total_count = 0
        for wo in wos:
            total_count += 1
            proc = wo.get_value('process')
            if piped_names['ALL'] == '':
                piped_names['ALL'] = wo.get_value('code')
            else:
                piped_names['ALL'] = '%s|%s' % (piped_names['ALL'], wo.get_value('code'))
            if proc not in seen_procs:
                seen_procs.append(proc)
                proc_count[proc] = 1
                piped_names[proc] = wo.get_value('code')
            else:
                proc_count[proc] += + 1
                piped_names[proc] = '%s|%s' % (piped_names[proc], wo.get_value('code'))
        process_sel.append_option('ALL Work Orders (%s)' % total_count, piped_names['ALL'])
        seen_procs = sorted(seen_procs)
        for sp in seen_procs:
            process_sel.append_option('%s (%s)' % (sp, proc_count[sp]), piped_names[sp])
        table = Table()
        table.add_attr('class', 'globalreplacer_%s' % my.order_sk)
        group_search = Search("sthpw/login_group")
        group_search.add_where("\"login_group\" not in ('user','client')")
        group_search.add_order_by('login_group')
        groups = group_search.get_sobjects()
        group_sel = SelectWdg('replace_wo_work_group')
        group_sel.append_option('--Select--', '--Select--')
        for group in groups:
            group_sel.append_option(group.get_value('login_group'), group.get_value('login_group'))
        table.add_row()
        tp = table.add_cell('<b>Select Work Order Name</b>')  # Should be a select wdg
        tp.add_attr('nowrap', 'nowrap')
        tp.add_attr('colspan', '2')
        tp.add_attr('align', 'center')
        tp.add_style('font-size: 22px;')
        table.add_row()
        nw = table.add_cell('For Work Orders Named: ')  # Should be a select wdg
        nw.add_attr('nowrap', 'nowrap')
        table.add_cell(process_sel)
        table.add_row()
        hr1 = table.add_cell('<hr/>')
        hr1.add_attr('colspan', '2')
        table.add_row()
        chnk_top = table.add_cell('<b>Apply To All Work Orders With Same Name As Selected Above</b>')
        chnk_top.add_attr('colspan', '2')
        chnk_top.add_style('font-size: 14px;')
        table.add_row()
        table.add_cell('Work Group: ')
        table.add_cell(group_sel)
        table.add_row()
        nw = table.add_cell('Estimated Work Hours: ')
        nw.add_attr('nowrap', 'nowrap')
        table.add_cell('<input type="text" class="replace_wo_work_hours"/>')
        table.add_row()
        table.add_cell('Instructions: ')
        table.add_cell('<textarea cols="50" rows="10" class="replace_wo_instructions"></textarea>')
        table.add_row()
        sep = table.add_cell('<hr/>')
        sep.add_attr('colspan', '2')
        table.add_row()
        septop1 = table.add_cell('<b>-OR-</b>')
        septop1.add_attr('colspan', '2')
        septop1.add_attr('align', 'center')
        septop1.add_style('font-size: 18px;')
        table.add_row()
        septop2 = table.add_cell('<b>For Selected Work Orders, Do Instructions Find & Replace:</b>')
        septop2.add_attr('colspan', '2')
        septop2.add_style('font-size: 14px;')
        reptbl = Table()
        reptbl.add_row()
        reptbl.add_cell('Replace')
        reptbl.add_cell('<input type="text" class="replace_start"/>')
        reptbl.add_cell('With')
        reptbl.add_cell('<input type="text" class="replace_end"/>')
        table.add_row()
        part2 = table.add_cell(reptbl)
        part2.add_attr('colspan', '2')
        table.add_row()
        sep2 = table.add_cell('<hr/>')
        sep2.add_attr('colspan', '2')
        table.add_row()
        button = table.add_cell('<input type="button" value="Apply"/>')
        button.add_behavior(my.get_commit(my.user_name))
        button.add_attr('align', 'center')
        button.add_attr('width', '100%')

        return table
