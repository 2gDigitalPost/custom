__all__ = ["IndieBBSelectWdg","BigBoardSingleWOSelectWdg2","BigBoardViewWdg2","BigBoardSelectWdg2","BigBoardWOSelectWdg2","BigBoardWOSelect4MultiTitlesWdg2","BigBoardWdg2"]

import datetime
from pyasm.web import Table, DivWdg
from tactic.ui.common import BaseTableElementWdg
from tactic.ui.common import BaseRefreshWdg
from pyasm.search import Search
from pyasm.common import Environment, SPTDate
from tactic_client_lib import TacticServerStub
from common_tools.common_functions import title_case, get_current_timestamp, abbreviate_text
from order_builder.taskobjlauncher import TaskObjLauncherWdg
import hotlist_functions


def fix_date(date):
    # TODO: Move this function to a separate file
    # This is needed due to the way Tactic deals with dates (using timezone info), post v4.0
    return_date = ''
    date_obj = SPTDate.convert_to_local(date)
    if date_obj not in [None, '']:
        return_date = date_obj.strftime("%Y-%m-%d  %H:%M")
    return return_date


class IndieBBSelectWdg(BaseTableElementWdg):

    def init(my):
        nothing = 'true'
        my.server = None

    def get_stub(my):
        my.server = TacticServerStub.get()
    
    def get_launch_behavior(my, search_key, title_code, lookup_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{ 
                          var server = TacticServerStub.get();
                          var search_key = "%s";
                          var title_code = "%s";
                          var lookup_code = "%s";
                          var task_code = search_key.split('code=')[1];
                          var state = bvr.src_el.get('state');
                          var checked = '/context/icons/custom/small_blue_racecar_alpha.png';
                          var unchecked = '/context/icons/custom/small_grey_racecar_alpha.png';
                          changed = false
                          if(state == 'checked'){
                              if(confirm("Do you really want to take this off the Hot Today Board?")){
                                  img = unchecked;
                                  server.update(search_key, {'indie_bigboard': 'false'}); 
                                  indies = server.eval("@SOBJECT(twog/indie_bigboard['task_code','" + task_code + "']['indie_bigboard','true'])");
                                  for(var r = 0; r < indies.length; r++){
                                      server.update(indies[r].__search_key__, {'indie_bigboard': 'false'});
                                  }
                                  bvr.src_el.setAttribute('state', 'unchecked');
                                  changed = true
                              }
                          }else{
                              new_prio = prompt("Please assign a priority to this Work Order");
                              if(new_prio != null && new_prio != ''){
                                  if(!(isNaN(new_prio))){
                                      img = checked; 
                                      new_prio = Number(new_prio);
                                      server.update(search_key, {'indie_bigboard': 'true', 'indie_priority': new_prio}); 
                                      server.insert('twog/indie_bigboard', {'indie_bigboard': 'true', 'indie_priority': new_prio, 'title_code': title_code, 'lookup_code': lookup_code, 'task_code': task_code}); 
                                      title = server.eval("@SOBJECT(twog/title['code','" + title_code + "'])")[0];
                                      title_sk = title.__search_key__;
                                      task = server.eval("@SOBJECT(sthpw/task['code','" + task_code + "'])")[0];
                                      asl = task.assigned_login_group;
                                      adps = title.active_dept_priorities;
                                      asl_prio = asl.replace(' ','_') + '_priority';
                                      data_out = {}
                                      data_out[asl_prio] = new_prio; 
                                      if(adps.indexOf(asl) == -1){
                                          if(adps == ''){
                                              adps = asl;
                                          }else{
                                              adps = adps + ',' + asl;
                                          }
                                          data_out['active_dept_priorities'] = adps;
                                      }
                                      server.update(title_sk, data_out);
                                      bvr.src_el.setAttribute('state', 'checked');
                                      changed = true;
                                  }else{
                                      alert(new_prio + " is not a number. Work Order not placed on Hot Today.");
                                  }
                              }
                          } 
                          if(changed){
                              var inner = bvr.src_el.innerHTML;
                              in1 = inner.split('src="')[0];
                              in1 = in1 + 'src="' + img + '"/>';
                              bvr.src_el.innerHTML = in1;
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (search_key, title_code, lookup_code)}
        return behavior

    def get_display(my):
        is_on = False
        search_key = my.kwargs.get('search_key')
        task_code = search_key.split('code=')[1]
        title_code = my.kwargs.get('title_code')
        lookup_code = my.kwargs.get('lookup_code')
        if 'indie_bigboard' in my.kwargs.keys():
            if my.kwargs.get('indie_bigboard') in [True, 'true', 't', 'T', 1]:
                is_on = True
        else:
            my.get_stub()
            task = my.server.eval("@SOBJECT(sthpw/task['code','%s'])" % task_code)[0]
            if task.get('indie_bigboard') in [True, 'true', 't', 'T', 1]:
                is_on = True

        widget = DivWdg()
        table = Table()

        img = '/context/icons/custom/small_grey_racecar_alpha.png'
        state = 'unchecked'
        if is_on:
            img = '/context/icons/custom/small_blue_racecar_alpha.png'
            state = 'checked'
        table.add_row()
        cell1 = table.add_cell('<img border="0" style="vertical-align: middle" title="" src="%s">' % img)
        cell1.add_attr('search_key', search_key)
        cell1.add_attr('state', state)
        launch_behavior = my.get_launch_behavior(search_key, title_code, lookup_code)
        cell1.add_style('cursor: pointer;')
        cell1.add_behavior(launch_behavior)
        widget.add(table)
        return widget


class BigBoardSingleWOSelectWdg2(BaseTableElementWdg):

    def init(my):
        nothing = 'true'
        my.server = None

    def get_stub(my):
        my.server = TacticServerStub.get()

    def get_launch_behavior(my, search_key, title_code, lookup_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{ 
                          var server = TacticServerStub.get();
                          var search_key = "%s";
                          var title_code = "%s";
                          var lookup_code = "%s";
                          var task_code = search_key.split('code=')[1];
                          var state = bvr.src_el.get('state');
                          var checked = '/context/icons/silk/rosette.png';
                          var unchecked = '/context/icons/silk/rosette_grey.png';
                          changed = false
                          if(state == 'checked'){
                              if(confirm("Do you really want to take this off the Hot Today Board?")){
                                  img = unchecked;
                                  server.update(search_key, {'bigboard': 'false'}); 
                                  bvr.src_el.setAttribute('state', 'unchecked');
                                  changed = true
                              }
                          }else{
                              img = checked; 
                              server.update(search_key, {'bigboard': 'true'}); 
                              bvr.src_el.setAttribute('state', 'checked');
                              changed = true;
                              title = server.eval("@SOBJECT(twog/title['code','" + title_code + "'])")[0];
                              if(!(title.bigboard)){
                                  alert('Placing the Title on the BigBoard as well.');
                                  server.update(title.__search_key__, {'bigboard': 'true'});
                                  tc_str = 'title_bigboard_' + title_code;
                                  title_bbs = document.getElementById(tc_str);
                                  if(title_bbs){
                                      title_bb_inner = title_bbs.innerHTML;
                                      in1 = title_bb_inner.split('src="')[0];
                                      in1 = in1 + 'src="' + img + '"/>';
                                      title_bbs.innerHTML = in1;
                                      title_bbs.setAttribute('state','checked');
                                  }
                              }
                          } 
                          if(changed){
                              var inner = bvr.src_el.innerHTML;
                              in1 = inner.split('src="')[0];
                              in1 = in1 + 'src="' + img + '"/>';
                              bvr.src_el.innerHTML = in1;
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (search_key, title_code, lookup_code)}
        return behavior
    
    def get_display(my):
        is_on = False
        search_key = my.kwargs.get('search_key')
        task_code = search_key.split('code=')[1]
        title_code = my.kwargs.get('title_code')
        lookup_code = my.kwargs.get('lookup_code')
        if 'bigboard' in my.kwargs.keys():
            if my.kwargs.get('bigboard') in [True, 'true', 't', 'T', 1]:
                is_on = True
        else:
            my.get_stub()
            task = my.server.eval("@SOBJECT(sthpw/task['code','%s'])" % task_code)[0]
            if task.get('bigboard') in [True, 'true', 't', 'T', 1]:
                is_on = True

        widget = DivWdg()
        table = Table()

        img = '/context/icons/silk/rosette_grey.png'
        state = 'unchecked'
        if is_on:
            img = '/context/icons/silk/rosette.png'
            state = 'checked'
        table.add_row()
        cell1 = table.add_cell('<img border="0" style="vertical-align: middle" title="" src="%s">' % img)
        cell1.add_attr('search_key', search_key)
        cell1.add_attr('state', state)
        launch_behavior = my.get_launch_behavior(search_key, title_code, lookup_code)
        cell1.add_style('cursor: pointer;')
        cell1.add_behavior(launch_behavior)
        widget.add(table)
        return widget


# TODO: BigBoardViewWdg2 appears to do nothing, and is probably safe to remove
class BigBoardViewWdg2(BaseTableElementWdg):

    def init(my):
        nothing = 'true'

    def get_display(my):
        widget = DivWdg()
        table = Table()
        table.add_row()
        widget.add(table)
        return widget


class BigBoardSelectWdg2(BaseTableElementWdg):

    def init(my):
        nothing = 'true'
        my.server = None

    def get_stub(my):
        my.server = TacticServerStub.get()

    def get_launch_behavior(my, title_name, in_bigboard):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{ 
                          var server = TacticServerStub.get();
                          var title_name = "%s";
                          var in_bigboard = "%s";
                          var my_sk = bvr.src_el.get('sk');
                          var state = bvr.src_el.get('state');
                          var class_name = 'nighttime_hotlist.nighttime_hotlist2.BigBoardWOSelectWdg2';
                          var checked = '/context/icons/silk/rosette.png';
                          var unchecked = '/context/icons/silk/rosette_grey.png';
                          nothing_else = false;
                          changed = false
                          if(state == 'checked'){
                              img = unchecked;
                              if(in_bigboard != 'Yep'){
                                  if(confirm("Do you really want to take this off the Hot Today list?")){
                                      server.update(my_sk, {'bigboard': 'false'}); 
                                      bvr.src_el.setAttribute('state', 'unchecked');
                                      changed = true;
                                  }
                              }else{
                                  if(confirm("Do you really want to take this off the Hot Today list?")){
                                      server.update(my_sk, {'bigboard': 'false'}); 
                                      changed = true;
                                      var buttons_el = document.getElementsByClassName('auto_buttons')[0]; 
                                      auto_el = buttons_el.getElementById('auto_refresh');
                                      auto = auto_el.getAttribute('auto');
                                      scroll_el = buttons_el.getElementById('scroll_el');
                                      scroll = scroll_el.getAttribute('scroll');
                                      //group_el = buttons_el.getElementById('group_select');
                                      //group = group_el.value;
                                      group = 'ALL';
                                      board_els = document.getElementsByClassName('bigboard');     
                                      nothing_else = true;
                                      spt.app_busy.show("Refreshing...");
                                      spt.api.load_panel(board_els[0], 'nighttime_hotlist.BigBoardWdg2', {'auto_refresh': auto, 'auto_scroll': scroll, 'groups': group});
                                      spt.app_busy.hide();
                                  }
                              }
                          }else{
                              img = checked; 
                              server.update(my_sk, {'bigboard': 'true'}); 
                              bvr.src_el.setAttribute('state', 'checked');
                              kwargs = {
                                           'sk': my_sk
                                   };
                              spt.panel.load_popup('Select Big Board Work Orders for ' + title_name, class_name, kwargs);
                              changed = true;
                          } 
                          if(!nothing_else && changed){
                              var inner = bvr.src_el.innerHTML;
                              in1 = inner.split('src="')[0];
                              in1 = in1 + 'src="' + img + '"/>';
                              bvr.src_el.innerHTML = in1;
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (title_name, in_bigboard)}
        return behavior

    def get_display(my):
        expression_lookup = {
            'twog/title': "@SOBJECT(twog/title['code','REPLACE_ME'])",
            'twog/proj': "@SOBJECT(twog/proj['code','REPLACE_ME'].twog/title)",
            'twog/work_order': "@SOBJECT(twog/work_order['code','REPLACE_ME'].twog/proj.twog/title)",
            'twog/equipment_used': "@SOBJECT(twog/equipment_used['code','REPLACE_ME'].twog/work_order.twog/proj.twog/title)"
        }
        search_type = 'twog/title'
        code = ''
        order_name = ''
        sob_sk = ''
        not_title = True
        bad_code = False
        if 'search_type' in my.kwargs.keys():
            my.get_stub()
            search_type = str(my.kwargs.get('search_type'))
            code = str(my.kwargs.get('code'))
            sobject = my.server.eval(expression_lookup[search_type].replace('REPLACE_ME', code))
            if sobject:
                sobject = sobject[0]
                code = sobject.get('code')
                sob_sk = sobject.get('__search_key__')
        else: 
            sobject = my.get_current_sobject()
            sob_sk = sobject.get_search_key()
            code = sobject.get_code()
            not_title = False
            if 'TITLE' not in code:
                not_title = True
                my.get_stub()
                if 'WORK_ORDER' in code:
                    sobject = my.server.eval(expression_lookup['twog/work_order'].replace('REPLACE_ME', code))
                elif 'EQUIPMENT_USED' in code:
                    sobject = my.server.eval(expression_lookup['twog/equipment_used'].replace('REPLACE_ME', code))
                elif 'PROJ' in code:
                    sobject = my.server.eval(expression_lookup['twog/proj'].replace('REPLACE_ME', code))
                try:
                    if sobject:
                        sobject = sobject[0]
                        code = sobject.get('code')
                        sob_sk = sobject.get('__search_key__')
                except:
                    bad_code = True
                    pass
        widget = DivWdg()
        table = Table()
        if not bad_code:
            # TODO: Change in_bigboard from 'Nope' and 'Yep' to False/True (I can't believe I had to just write that...)
            in_bigboard = 'Nope'
            if 'in_bigboard' in my.kwargs.keys():
                if my.kwargs.get('in_bigboard') in ['Yes', 'yes', 'true', 'True']:
                    in_bigboard = 'Yep'
            img = '/context/icons/silk/rosette_grey.png'
            state = 'unchecked'
            bigboard = ''
            title_name = ''
            episode = ''
            if not not_title:
                bigboard = sobject.get_value('bigboard')
                title_name = sobject.get_value('title')
                episode = sobject.get_value('episode')
            else:
                bigboard = sobject.get('bigboard')
                title_name = sobject.get('title')
                episode = sobject.get('episode')
            if episode not in [None, '']:
                title_name = '%s Episode: %s' % (title_name, episode) 
            if bigboard is True:
                img = '/context/icons/silk/rosette.png'
                state = 'checked'
            table.add_row()
            cell1 = table.add_cell('<img border="0" style="vertical-align: middle" title="" src="%s">' % img)
            cell1.add_attr('id', 'title_bigboard_%s' % code)
            cell1.add_attr('sk', sob_sk)
            cell1.add_attr('state', state)
            launch_behavior = my.get_launch_behavior(title_name, in_bigboard)
            cell1.add_style('cursor: pointer;')
            cell1.add_behavior(launch_behavior)
        widget.add(table)
        return widget


class BigBoardWOSelect4MultiTitlesWdg2(BaseRefreshWdg):

    def init(my):
        my.server = TacticServerStub.get()
        my.title_codes = ''

    def get_switcher_behavior(my):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{ 
                          var top_el = document.getElementsByClassName('bigboard_wo_selector_multi')[0];
                          var checkboxes = top_el.getElementsByTagName('input');
                          inner = bvr.src_el.innerHTML;
                          doing = inner.split('value="')[1];
                          doing = doing.split('"')[0];
                          for(var r = 0; r < checkboxes.length; r++){
                              if(checkboxes[r].type == 'checkbox'){
                                  if(doing == 'Select All'){
                                      checkboxes[r].checked = true;
                                  }else{
                                      checkboxes[r].checked = false;
                                  }
                              }
                          }
                          if(doing == 'Select All'){
                              bvr.src_el.innerHTML = '<input type="button" value="Deselect All"/>';
                          }else{
                              bvr.src_el.innerHTML = '<input type="button" value="Select All"/>';
                          }
                          
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         '''}
        return behavior

    def get_bigboardem_behavior(my):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{ 
                          var server = TacticServerStub.get();
                          var top_el = document.getElementsByClassName('bigboard_wo_selector_multi')[0];
                          var checkboxes = top_el.getElementsByTagName('input');
                          for(var r = 0; r < checkboxes.length; r++){
                              if(checkboxes[r].type == 'checkbox'){
                                  task_sks = checkboxes[r].getAttribute('sks');
                                  sks = task_sks.split(',')
                                  cname = checkboxes[r].name;
                                  if(cname.indexOf('bigboard_wo_select_by_process') != -1){
                                      if(checkboxes[r].checked){
                                          for(var k = 0; k < sks.length; k++){
                                              server.update(sks[k], {'bigboard': 'true'});
                                          }
                                      }else{
                                          for(var k = 0; k < sks.length; k++){
                                              server.update(sks[k], {'bigboard': 'false'});
                                          }
                                      }
                                  }
                               }
                          }
                          //alert('Done adding to the BigBoard');
                          spt.popup.close(spt.popup.get_popup(bvr.src_el));
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         '''}
        return behavior

    def make_where_str(my, arr):
        where_str = ''
        for sa in arr:
            if where_str == '':
                where_str = "('%s'" % sa
            else:
                where_str = "%s,'%s'" % (where_str, sa)
        if where_str != '':
            where_str = '%s)' % where_str
        return where_str
 
    def update_titles(my, arr, dict):
        for code in arr:
            sk = my.server.build_search_key('twog/title',code)
            my.server.update(sk, dict)

    def get_display(my):
        # THE SEARCH KEY BEING PASSED IN SHOULD BELONG TO A TITLE
        from pyasm.search import Search
        from pyasm.widget import CheckboxWdg
        my.title_codes = str(my.kwargs.get('title_codes'))
        tc_split = my.title_codes.split(',')
        my.update_titles(tc_split, {'bigboard': True})
        where_str = my.make_where_str(tc_split)
        search = Search("sthpw/task")
        search.add_filter('status', 'Completed', op="!=")
        search.add_filter('active', '1')
        search.add_filter('search_type', 'twog/proj?project=twog')
        search.add_where("\"title_code\" in %s" % where_str)
        search.add_order_by("process")
        tasks = search.get_sobjects()
        
        processes = {} 
        inorder = []
        for task in tasks:
            process = task.get_value('process')
            try:
                processes[process] = '%s,%s' % (processes[process], task.get_search_key())
            except:
                processes[process] = task.get_search_key()
                inorder.append(process)
                pass

        inorder.sort()
        table = Table()
        if len(tasks) > 0:
            table.add_row()
            switcher = table.add_cell('<input type="button" value="Select All"/>')
            switcher.add_behavior(my.get_switcher_behavior())
            for process in inorder:
                table.add_row()
                checkbox = CheckboxWdg('bigboard_wo_select_by_process')
                checkbox.set_value(False) 
                checkbox.add_attr('sks', processes[process])
                checkbox.add_attr('process', process)
                table.add_cell(checkbox)
                t1 = table.add_cell(process)
                t1.add_attr('nowrap', 'nowrap')
        cover_table = Table()
        cover_table.add_attr('class', 'bigboard_wo_selector_multi')
        cover_table.add_row()
        cover_cell = cover_table.add_cell(table)
        cover_table.add_row()
        buttont = Table()
        buttont.add_row()
        c1 = buttont.add_cell(' ')
        c1.add_attr('width', '40%')
        button = buttont.add_cell('<input type="button" value="BigBoard Selected Work Orders"/>')
        button.add_behavior(my.get_bigboardem_behavior()) 
        c2 = buttont.add_cell(' ')
        c2.add_attr('width', '40%')
        cover_table.add_cell(buttont)
        return cover_table


class BigBoardWOSelectWdg2(BaseRefreshWdg):

    def init(my):
        my.sk = ''

    def get_switcher_behavior(my, title_sk):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{ 
                          var title_sk = '%s';
                          var top_el = document.getElementsByClassName('bigboard_wo_selector_' + title_sk)[0];
                          var checkboxes = top_el.getElementsByTagName('input');
                          inner = bvr.src_el.innerHTML;
                          doing = inner.split('value="')[1];
                          doing = doing.split('"')[0];
                          for(var r = 0; r < checkboxes.length; r++){
                              if(checkboxes[r].type == 'checkbox'){
                                  if(doing == 'Select All'){
                                      checkboxes[r].checked = true;
                                  }else{
                                      checkboxes[r].checked = false;
                                  }
                              }
                          }
                          if(doing == 'Select All'){
                              bvr.src_el.innerHTML = '<input type="button" value="Deselect All"/>';
                          }else{
                              bvr.src_el.innerHTML = '<input type="button" value="Select All"/>';
                          }
                          
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % title_sk}
        return behavior

    def get_bigboardem_behavior(my, title_sk):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{ 
                          var server = TacticServerStub.get();
                          var title_sk = '%s';
                          var top_el = document.getElementsByClassName('bigboard_wo_selector_' + title_sk)[0];
                          var checkboxes = top_el.getElementsByTagName('input');
                          for(var r = 0; r < checkboxes.length; r++){
                              if(checkboxes[r].type == 'checkbox'){
                                  task_sk = checkboxes[r].getAttribute('sk');
                                  cname = checkboxes[r].name;
                                  if(cname.indexOf('bigboard_wo_select_') != -1){
                                      if(checkboxes[r].checked){
                                          server.update(task_sk, {'bigboard': 'true'});
                                      }else{
                                          server.update(task_sk, {'bigboard': 'false'});
                                      }
                                  }
                               }
                          }
                          //alert('Done adding to the BigBoard');
                          spt.popup.close(spt.popup.get_popup(bvr.src_el));
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % title_sk}
        return behavior
    
    def get_display(my):   
        # THE SEARCH KEY BEING PASSED IN SHOULD BELONG TO A TITLE
        from pyasm.search import Search
        from pyasm.widget import CheckboxWdg
        my.sk = str(my.kwargs.get('sk'))
        code = my.sk.split('code=')[1]
        search = Search("sthpw/task")
        search.add_filter('title_code', code)
        search.add_filter('status', 'Completed', op="!=")
        search.add_filter('active', '1')
        search.add_filter('search_type', 'twog/proj?project=twog')
        tasks = search.get_sobjects()
        
        table = Table()
        if len(tasks) > 0:
            table.add_row()
            switcher = table.add_cell('<input type="button" value="Select All"/>')
            switcher.add_behavior(my.get_switcher_behavior(my.sk))
            for task in tasks:
                table.add_row()
                checkbox = CheckboxWdg('bigboard_wo_select_%s' % task.get_search_key())
                if task.get_value('bigboard'):
                    checkbox.set_value(True) 
                else:
                    checkbox.set_value(False)
                checkbox.add_attr('sk', task.get_search_key())
                table.add_cell(checkbox)
                assigned_login_group = task.get_value('assigned_login_group')
                assigned = task.get_value('assigned')
                if assigned_login_group in [None, '']:
                    assigned_login_group = 'No Group?'
                if assigned in [None, '']:
                    assigned = 'Unassigned'
                t1 = table.add_cell('[%s]: %s, %s, %s, %s' % (task.get_value('lookup_code'), task.get_value('process'), assigned_login_group, assigned, task.get_value('status')))
                t1.add_attr('nowrap', 'nowrap')
        cover_table = Table()
        cover_table.add_attr('class', 'bigboard_wo_selector_%s' % my.sk)
        cover_table.add_row()
        cover_cell = cover_table.add_cell(table)
        cover_table.add_row()
        buttont = Table()
        buttont.add_row()
        c1 = buttont.add_cell(' ')
        c1.add_attr('width', '40%')
        button = buttont.add_cell('<input type="button" value="BigBoard Selected Work Orders"/>')
        button.add_behavior(my.get_bigboardem_behavior(my.sk)) 
        c2 = buttont.add_cell(' ')
        c2.add_attr('width', '40%')
        cover_table.add_cell(buttont)
        return cover_table


class BigBoardWdg2(BaseRefreshWdg):
    """
    This appears to be the class in charge of making our "Hot Today" list on the front page. I say "appears" because,
    despite this class's importance, I found it completely undocumented
    """
    # TODO: Update docstring once I know what's going on here...

    def init(my):
        my.login = Environment.get_login()
        my.user = my.login.get_login()
        my.sk = ''
        my.seen_groups = []
        my.bigdict = {}
        my.indi_pct = 0.0
        # TODO: Move stat_colors to a text file/database rather than hard coding.
        my.stat_colors = {
            'Pending': '#d7d7d7',
            'In Progress': '#f5f3a4',
            'In_Progress': '#f5f3a4',
            'On Hold': '#e8b2b8',
            'On_Hold': '#e8b2b8',
            'Client Response': '#ddd5b8',
            'Completed': '#b7e0a5',
            'Need Buddy Check': '#e3701a',
            'Ready': '#b2cee8',
            'Internal Rejection': '#ff0000',
            'External Rejection': '#ff0000',
            'Fix Needed': '#c466a1',
            'Failed QC': '#ff0000',
            'Rejected': '#ff0000',
            'DR In_Progress': '#d6e0a4',
            'DR In Progress': '#d6e0a4',
            'Amberfin01_In_Progress': '#D8F1A8',
            'Amberfin01 In Progress': '#D8F1A8',
            'Amberfin02_In_Progress': '#F3D291',
            'Amberfin02 In Progress': '#F3D291',
            'BATON In_Progress': '#c6e0a4',
            'BATON In Progress': '#c6e0a4',
            'Export In_Progress': '#796999',
            'Export In Progress': '#796999',
            'Buddy Check In_Progress': '#1aade3',
            'Buddy Check In Progress': '#1aade3'
        }
        my.stat_relevance = {
            'Pending': 0,
            'In Progress': 4,
            'In_Progress': 4,
            'On Hold': 1,
            'On_Hold': 1,
            'Client Response': 2,
            'Completed': -1,
            'Need Buddy Check': 10,
            'Buddy Check In_Progress': 11,
            'Buddy Check In Progress': 11,
            'Ready': 3,
            'Internal Rejection': 12,
            'External Rejection': 13,
            'Failed QC': 14,
            'Fix Needed': 16,
            'Rejected': 15,
            'DR In_Progress': 5,
            'DR In Progress': 5,
            'BATON In_Progress': 8,
            'BATON In Progress': 8,
            'Export In_Progress': 9,
            'Export In Progress': 9,
            'Amberfin01_In_Progress': 6,
            'Amberfin01 In Progress': 6,
            'Amberfin02_In_Progress': 7,
            'Amberfin02 In Progress': 7
        }
        my.ext_colors = {
            'Open': '#ff0000',
            'Investigating': '#00ff26',
            'Waiting for Source': '#eeff00',
            'Needs Corrective Action': '#4c69fc',
            'Closed': '#597007'
        }
        my.timestamp = get_current_timestamp()
        my.date = my.timestamp.split(' ')[0]
        my.real_date = datetime.datetime.strptime(my.date, '%Y-%m-%d')
        my.big_user = False
        users_s = Search('sthpw/login')
        users_s.add_filter('location', 'internal')
        users = users_s.get_sobjects()
        my.username_lookup = {'': '', None: '', 'NOTHING': ''}
        for user in users:
            login_name = user.get_value('login')
            fname = user.get_value('first_name')
            lname = user.get_value('last_name')
            my.username_lookup[login_name] = '%s %s' % (fname, lname)
        
    def trow_top(my):
        table = Table()
        table.add_attr('width', '100%')
        table.add_attr('height', '40px')
        table.add_attr('border', '1')
        table.add_style('font-size: 12px;')
        table.add_style('font-family: Helvetica;')
        table.add_style('color: #000000;')
        table.add_style('background-color: #f2f2f2;')
        table.add_style('border-color: #444444;')
        table.add_class('spt_group_row')
        table.add_row()

        # Set up the title column (it is always shown)
        # TODO: Get rid of non-breaking spaces
        title_column = table.add_cell('&nbsp;&nbsp;&nbsp;<b>Title</b>')
        title_column.add_attr('class', 'topper')
        title_column.add_attr('group', 'title')
        # TODO: Not sure what the below line does
        title_width_percent = (my.indi_pct * 2)
        title_column.add_attr('width', '%s%s' % (title_width_percent, '%'))

        # Add all the rest of the columns
        for seen_group in my.seen_groups:
            seen_group_column = table.add_cell('&nbsp;&nbsp;&nbsp;<b>%s</b>' % title_case(seen_group))
            seen_group_column.add_attr('width', '%s%s' % ((my.indi_pct), '%'))
            seen_group_column.add_attr('class', 'topper')
            seen_group_column.add_attr('group', seen_group)

        t2 = Table()
        t2.add_attr('width', '100%')
        t2.add_style('font-size: 16px;')
        t2.add_style('font-family: Helvetica;')
        t2.add_style('color: #000000;')
        t2.add_style('background-color: #f2f2f2;')
        t2.add_row()
        t2.add_cell(table)
        t2c = t2.add_cell('&nbsp;&nbsp;&nbsp;&nbsp;')
        t2c.add_attr('width', '10px')
       
        return t2

    def get_launch_note_behavior(my,  sk, name):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                          var sk = '%s';
                          var name = '%s';
                          kwargs =  {'search_key': sk, 'append_process': 'Client Services,Redelivery/Rejection Request,Redelivery/Rejection Completed', 'chronological': true};
                          spt.panel.load_popup('Notes for ' + name, 'tactic.ui.widget.DiscussionWdg', kwargs);
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (sk, name)}
        return behavior

    def wrow(my, task, expected_delivery_date, count, client_thumbnail_clippings, platform_thumbnail_clippings, in_tbl, bgcol):
        """
        Not sure if this function ever gets called or not. Until I find out, I'm leaving it alone.

        ***UPDATE***
        When I tried moving the import statement in this function to the top of the module, the "Source"
        page broke. Apparently the order_builder.py module calls this file, and this file calls order_builder as
        well. My initial feeling is that this is causing a circular import or something like that.

        Noted on 12-29-2015 by Tyler Standridge.
        ************

        :param task:
        :param expected_delivery_date:
        :param count:
        :param client_thumbnail_clippings:
        :param platform_thumbnail_clippings:
        :param in_tbl: The table itself so far. This needs to be removed. Passing the entire table to the function
                       and appending the row to that table is really stupid. The function should just return a row,
                       which is appended to the table outside the function.
        :param bgcol: Background color for the table row
        :return:
        """
        from order_builder.order_builder import OrderBuilderLauncherWdg

        expected_delivery_date = fix_date(expected_delivery_date)
        code = task.get_value('code')
        name = task.get_value('title')
        episode = task.get_value('episode')

        if episode:
            name += ' Episode ' + episode

        better_lookin_dd, dd_color = hotlist_functions.get_dates_and_colors(expected_delivery_date,
                                                                            'NO DELIVERY DATE',
                                                                            my.real_date)
        tpct = my.indi_pct * 2
        table = in_tbl
        trower = table.add_row()
        trower.add_attr('class', 'trow')
        trower.add_attr('num', count)
        trower.add_attr('viz', 'true')
        trower.add_attr('current_priority', task.get_value('indie_priority'))
        trower.add_style('display: table-row;')
        trower.add_style('background-color: %s;' % bgcol)
        dbl = Table()
        dbl.add_attr('width', '100%')
        dbl.add_style('font-size: 16px;')
        dbl.add_style('color: #000000;')
        dbl.add_style('background-color: #d7d7d7;')
        dbl.add_style('border-bottom-right-radius', '10px')
        dbl.add_style('border-bottom-left-radius', '10px')
        dbl.add_style('border-top-right-radius', '10px')
        dbl.add_style('border-top-left-radius', '10px')
        dbl.add_row()

        # Line below looks like what determines each row's number and title, but changing it did nothing
        row_title_cell = dbl.add_cell('<span style="size: 36px; color: #ff0000;">%s.</span> <u>%s</u>' % (count, name))
        row_title_cell.add_attr('width', '100%')
        row_title_cell.add_style('font-weight: bold;')

        dbl.add_row()

        lil_tbl = Table()
        lil_tbl.add_attr('cellpadding', '5')
        lil_tbl.set_style('color: #000000; font-size: 14px;')
        lil_tbl.add_row()
        lil_tbl.add_cell(code)
        lil_tbl.add_cell("<i>Platform: %s</i>" % task.get_value('platform'))
        lil_tbl.add_cell("<b>Client: %s</b>" % task.get_value('client_name'))
        lil_tbl.add_row()

        obt = Table()
        obt.add_attr('cellpadding', '5')
        obt.set_style('color: #000000; font-size: 14px;')
        obt.add_row()

        deliver_by_cell = obt.add_cell('Deliver By: %s' % better_lookin_dd)
        deliver_by_cell.add_attr('colspan', '2')
        deliver_by_cell.add_attr('nowrap', 'nowrap')
        deliver_by_cell.add_style('text-shadow: 1px 1px #000000;')
        deliver_by_cell.add_style('font-weight: bold;')
        deliver_by_cell.add_style('color: %s' % dd_color)

        ob = OrderBuilderLauncherWdg(code=task.get_value('order_code'))
        obt.add_attr('width', '260px')
        obt.add_cell(ob)
        notes = obt.add_cell('<img src="/context/icons/silk/note_add.png"/>')
        notes.add_style('cursor: pointer;')
        tsearch = Search('twog/title')
        tsearch.add_filter('code', task.get_value('title_code'))
        task_tit = tsearch.get_sobject()
        notes.add_behavior(my.get_launch_note_behavior(task_tit.get_search_key(), name))
        lil_tbl.add_cell(obt)

        if task_tit.get_value('no_charge') and task_tit.get_value('redo'):
            lil_tbl.add_row()
            redo_no_charge_cell = lil_tbl.add_cell('REDO - NO CHARGE')
            redo_no_charge_cell.add_style('font-weight: bold;')
            redo_no_charge_cell.add_style('color: #FF0000;')

        # TODO: Find out if 'd2' actually does anything
        d2 = dbl.add_cell(lil_tbl)
        d2.add_attr('width', '100%')

        if my.big_user:
            dbl.add_row()
            offbutt = IndieBBSelectWdg(search_key=task.get_search_key(),
                                       title_code=task.get_value('title_code'),
                                       lookup_code=task.get_value('lookup_code'),
                                       indie_bigboard=task.get_value('indie_bigboard'))
            dblbb = dbl.add_cell(offbutt)
            dblbb.add_attr('width', '20px')
            dblpr = dbl.add_cell('Set At #: ')
            dblpr.add_attr('align', 'left')
            prioid = 'prio_%s' % count
            dbltxt = dbl.add_cell('<input type="text" value="%s" row_type="task" task_sk="%s" current_count="%s" current_priority="%s" class="count_order" external_rejection="false" id="%s"/>' % (count, task.get_search_key(), count, task.get_value('indie_priority'), prioid))
            dbltxt.add_attr('align', 'left')
            dbltxt.add_behavior(hotlist_functions.show_change(prioid))
        else: 
            dbl.add_row()
            dbl4 = dbl.add_cell('Priority: %s' % task.get_value('priority'))
            dbl4.add_attr('align', 'left')

        tripl = Table()
        tripl.add_attr('width', '100%')
        tripl.add_attr('height', '100%')
        tripl.add_row()

        tallboy = Table()
        tallboy.add_row()
        ctc1 = tallboy.add_cell(client_thumbnail_clippings)
        ctc1.add_attr('valign', 'top')
        ctc1.add_attr('align', 'left')
        ctc1.add_attr('width', '25px')
        tallboy.add_row()
        ctc2 = tallboy.add_cell(platform_thumbnail_clippings)
        ctc2.add_attr('valign', 'top')
        ctc2.add_attr('align', 'left')
        ctc2.add_attr('width', '25px')

        ctc = tripl.add_cell(tallboy)
        ctc.add_attr('valign', 'top')
        ctc.add_attr('align', 'left')
        ctc.add_attr('width', '25px')

        dc = tripl.add_cell(dbl)
        dc.add_attr('align', 'left')
        titl = table.add_cell(tripl)

        if count == 1:
            titl.add_attr('class', 'bottom_content')
            titl.add_attr('group', 'title')

        titl.add_attr('valign', 'top')
        titl.add_attr('width', '%s%s' % (tpct, '%'))
        for seen_group in my.seen_groups:
            if seen_group != task.get_value('assigned_login_group'):
                black = table.add_cell(' ')
                if count == 1:
                    black.add_attr('class', 'bottom_content')
                    black.add_attr('group', seen_group)
                black.add_attr('width', '%s%s' % (my.indi_pct, '%'))
                black.add_style('background-color: %s;' % bgcol)
            else:
                tat = Table()
                tat.add_attr('border', '1')
                tat.add_attr('width', '100%')
                tat.add_style('border-color: #e0e0e0;')
                tat.add_style('background-color: #0000FF;')
                tat.add_style('color: #000000;')
                tat.add_style('font-weight: bold;')
                tat.add_style('font-size: 10px;')
                wo_code = task.get_value('lookup_code')
                status = task.get_value('status')
                process = task.get_value('process')
                assigned = my.username_lookup[task.get_value('assigned')]
                due_date = fix_date(task.get_value('bid_end_date')).split(' ')[0]
                tat.add_row()
                inspect_button = TaskObjLauncherWdg(code=wo_code, name=process)
                inspect = tat.add_cell(inspect_button)
                pro = tat.add_cell(process)
                pro.add_style('background-color: %s;' % my.stat_colors[status])
                pro.add_style('color: #000000;')
                stcell = tat.add_cell(status)
                stcell.add_attr('width', '100%')
                stcell.add_style('background-color: %s;' % my.stat_colors[status])
                stcell.add_style('color: #000000;')
                tat.add_row()
                wcell = tat.add_cell(wo_code.split('WORK_ORDER')[1])
                wcell.add_attr('width', '100%')
                acell = tat.add_cell(assigned)
                acell.add_attr('width', '100%')
                acell.add_style('background-color: %s;' % my.stat_colors[status])
                acell.add_style('color: #000000;')
                dcell = tat.add_cell(due_date)
                dcell.add_attr('width', '100%')
                dcell.add_attr('nowrap', 'nowrap')
                dcell.add_style('background-color: %s;' % my.stat_colors[status])
                dcell.add_style('color: #000000;')
                tatcell1 = table.add_cell(tat) 
                if count == 1:
                    tatcell1.add_attr('class', 'bottom_content')
                    tatcell1.add_attr('group', seen_group)
                tatcell1.add_attr('valign', 'top')
                tatcell1.add_attr('width', '%s%s' % (my.indi_pct, '%'))
                tatcell1.add_style('background-color: #0000F0;')
        return table

    def trow(my, title, expected_delivery_date, count, client_thumbnail_clippings, platform_thumbnail_clippings, in_tbl, bgcol, ext_sk, curr_group_prio, ext_status=None, ext_assigned=None, ext_assigned_corrective=None):
        """
        More information coming soon. I don't fully understand how this function does what it does, but apparently
        it costructs the table and returns it.

        The function is far from pure, since it takes the table as an argument and then returns that table in an
        altered form. It would be much better if it didn't take the table at all, and just returned the created row
        instead.

        :param title: The title the row is working with. Refers to a title object in Tactic.
        :param expected_delivery_date: The expected delivery date as displayed on the row (not sure in what format).
        :param count:
        :param client_thumbnail_clippings:
        :param platform_thumbnail_clippings:
        :param in_tbl: The table itself so far. This needs to be removed. Passing the entire table to the function
                       and appending the row to that table is really stupid. The function should just return a row,
                       which is appended to the table outside the function.
        :param bgcol: Background color for the table row
        :param ext_sk:
        :param curr_group_prio:
        :param ext_status:
        :param ext_assigned:
        :param ext_assigned_corrective:
        :return: The entire table (need to change this to be just the row)
        """

        from order_builder.order_builder import OrderBuilderLauncherWdg

        due_date = fix_date(title.get_value('due_date'))
        code = title.get_value('code')
        code_str = code
        name = title.get_value('title')
        episode = title.get_value('episode')

        if episode:
            name += ' Episode ' + episode

        requires_mastering = False
        if title.get_value('requires_mastering_qc'):
            requires_mastering = True

        formatted_delivery_date, ed_color = hotlist_functions.get_dates_and_colors(expected_delivery_date,
                                                                                   'NO DELIVERY DATE',
                                                                                   my.real_date)
        formatted_due_date, dd_color = hotlist_functions.get_dates_and_colors(due_date, 'NO DUE DATE', my.real_date)
        tpct = my.indi_pct * 2

        table = in_tbl

        # TODO: Set the background color in an if/else sort of block, rather than this.
        # Default background color
        title_block_bgcol = '#D7D7D7'

        # If the order requires 'mastering', change background color
        if requires_mastering:
            title_block_bgcol = '#C8A2C8'

        # If the order was externally rejected by client, change background color
        if title.get_value('is_external_rejection') == 'true':
            title_block_bgcol = '#B55252'

        # If order is marked for redo, change background color
        if title.get_value('redo') not in [None, False]:
            title_block_bgcol = '#FFCC00'

            redo_title = ''
            redo_order = ''
            if title.get_value('redo_of_title_code') not in [None, '']:
                redo_title = title.get_value('redo_of_title_code')
                tsearch = Search('twog/title')
                tsearch.add_filter('code', redo_title)
                redone_title = tsearch.get_sobject()
                if redone_title:
                    redo_order = redone_title.get_value('order_code')
            else:        
                ext_search = Search('twog/external_rejection')
                ext_search.add_filter('replacement_title_code', code)
                ext_search.add_order_by('timestamp desc')
                old_ext = ext_search.get_sobject()
                if old_ext:
                    redo_title = old_ext.get_value('title_code')
                    redo_order = old_ext.get_value('order_code')

            if redo_title or redo_order:
                code_str = "%s:<b>%s</b> -- Redo of -- %s:%s" % (title.get_value('order_code'), code, redo_order, redo_title)

        trower = table.add_row()
        trower.add_attr('class', 'trow')
        trower.add_attr('num', count)
        trower.add_attr('viz', 'true')
        trower.add_attr('current_priority', title.get_value('priority'))
        trower.add_style('display: table-row;')
        trower.add_style('background-color: %s;' % bgcol)

        # Looks like dbl is where the order goes on the table. For some reason, it's created as a table within the
        # bigger table row. It also has its own sub-tables.
        dbl = Table()
        dbl.add_attr('width', '100%')
        dbl.add_attr('height', '100%')
        dbl.add_style('font-size: 14px;')
        dbl.add_style('color: #000000;')
        dbl.add_style('background-color: %s;' % title_block_bgcol)
        dbl.add_style('border-bottom-left-radius', '10px')
        dbl.add_style('border-top-left-radius', '10px')

        if requires_mastering:
            dbl.add_row()
            qc_mastering_cell = dbl.add_cell('Requires QC Mastering')
            qc_mastering_cell.add_attr('align', 'left')
            qc_mastering_cell.add_style('font-weight: bold')
            qc_mastering_cell.add_style('color: #FF0000')

        dbl.add_row()

        # Below line decides the row's number and title
        row_title_cell = dbl.add_cell('<span style="size: 36px; color: #ff0000;">%s.</span> <u>%s</u>' % (count, name))
        row_title_cell.add_attr('width', '100%')
        row_title_cell.add_style('font-weight: bold')

        dbl.add_row()

        lil_tbl = Table()
        lil_tbl.add_attr('height', '100%')
        lil_tbl.set_style('color: #000000; font-size: 12px;')
        lil_tbl.add_style('background-color: %s;' % bgcol)
        lil_tbl.add_row()

        lil_tbl.add_cell(code_str)
        if len(code_str) > 12:
            lil_tbl.add_row()

        if client_thumbnail_clippings == '':
            lil_tbl.add_cell("&nbsp;&nbsp;<b>Client: %s</b>" % title.get_value('client_name'))
        else:
            lil_tbl.add_cell("&nbsp;&nbsp;<b>Client:</b> %s" % client_thumbnail_clippings)

        if platform_thumbnail_clippings == '':
            lil_tbl.add_cell("&nbsp;&nbsp;<i>Platform: %s</i>" % title.get_value('platform'))
        else:
            lil_tbl.add_cell("&nbsp;&nbsp;<i>Platform:</i> %s" % platform_thumbnail_clippings)

        lil_tbl.add_row()

        # TODO: Rename 'obt' (not even sure what that means)
        obt = Table()
        obt.add_attr('cellpadding', '5')
        obt.add_attr('height', '100%')
        obt.add_style('color: #000000;')
        obt.add_style('font-size: 14px;')
        obt.add_row()

        # This next section handles how Deliver By appears
        deliver_by_cell = obt.add_cell('Deliver By: %s' % formatted_delivery_date)
        deliver_by_cell.add_attr('colspan', '2')
        deliver_by_cell.add_attr('nowrap', 'nowrap')
        deliver_by_cell.add_style('text-shadow: 1px 1px #000000;')
        deliver_by_cell.add_style('font-weight: bold')
        deliver_by_cell.add_style('color: %s;' % ed_color)

        obt.add_row()

        # This is the section for Due Date
        # TODO: Remove non breaking spaces and replace with CSS (or better table format)
        due_date_cell = obt.add_cell('Due Date:&nbsp;&nbsp;&nbsp; %s' % formatted_due_date)
        due_date_cell.add_attr('colspan', '2')
        due_date_cell.add_attr('nowrap', 'nowrap')
        due_date_cell.add_style('text-shadow: 1px 1px #000000;')
        due_date_cell.add_style('font-weight: bold')
        due_date_cell.add_style('color: %s' % dd_color)

        # #FF00F0 is a pinkish color used for several external rejection messages
        external_rejection_color = '#FF00F0'

        if title.get_value('is_external_rejection') == 'true':
            obt.add_row()
            external_rejection_cell = obt.add_cell('Received External Rejection')
            external_rejection_cell.add_attr('colspan', '2')
            external_rejection_cell.add_attr('nowrap', 'nowrap')
            external_rejection_cell.add_style('text-shadow: 1px 1px #000000;')
            external_rejection_cell.add_style('font-size: 18px;')
            external_rejection_cell.add_style('font-weight: bold;')
            external_rejection_cell.add_style('color: %s' % external_rejection_color)

        if ext_status:
            obt.add_row()
            external_rejection_status_cell = obt.add_cell('External Rejection Status: %s' % ext_status)
            external_rejection_status_cell.add_attr('align', 'left')
            external_rejection_status_cell.add_attr('nowrap', 'nowrap')
            external_rejection_status_cell.add_style('text-shadow: 1px 1px #000000;')
            external_rejection_status_cell.add_style('font-weight: bold;')
            external_rejection_status_cell.add_style('color: %s' % external_rejection_color)

        if ext_assigned:
            obt.add_row()
            assigned_cell = obt.add_cell('Assigned: %s' % ext_assigned)
            assigned_cell.add_attr('align', 'left')
            assigned_cell.add_attr('nowrap', 'nowrap')
            assigned_cell.add_style('text-shadow: 1px 1px #000000;')
            assigned_cell.add_style('font-weight: bold;')
            assigned_cell.add_style('color: %s' % external_rejection_color)

        if ext_assigned_corrective:
            obt.add_row()
            corrective_action_assigned_cell = obt.add_cell('Corrective Action Assigned: %s' % ext_assigned_corrective)
            corrective_action_assigned_cell.add_attr('align', 'left')
            corrective_action_assigned_cell.add_attr('nowrap', 'nowrap')
            corrective_action_assigned_cell.add_style('text-shadow: 1px 1px #000000;')
            corrective_action_assigned_cell.add_style('font-weight: bold;')
            corrective_action_assigned_cell.add_style('color: %s;' % external_rejection_color)

        ob = OrderBuilderLauncherWdg(code=title.get_value('order_code'))
        obt.add_attr('width', '260px')
        obt.add_cell(ob)
        notes = obt.add_cell('<img src="/context/icons/silk/note_add.png"/>')
        notes.add_style('cursor: pointer;')
        notes.add_behavior(my.get_launch_note_behavior(title.get_search_key(), name))
        lil_tbl.add_cell(obt)

        if title.get_value('no_charge') and title.get_value('redo'):
            lil_tbl.add_row()
            redo_no_charge_cell = lil_tbl.add_cell('REDO - NO CHARGE')
            redo_no_charge_cell.add_style('font-weight: bold;')
            redo_no_charge_cell.add_style('color: #FF0000;')

        # TODO: Find out if 'd2' actually does anything
        d2 = dbl.add_cell(lil_tbl)
        d2.add_attr('width', '100%')

        # I *think* this section adds the priority changer for admin users...
        if my.big_user:
            dbl.add_row()

            smtbl = Table()
            smtbl.add_attr('height', '100%')
            smtbl.add_style('font-size: 16px;')
            smtbl.add_style('color: #000000;')
            smtbl.add_row()

            offbutt = BigBoardSelectWdg2(search_type='twog/title', code=title.get_value('code'), in_bigboard='Yes')

            dblbb = dbl.add_cell(offbutt)
            dblbb.add_attr('width', '20px')

            dblpr = smtbl.add_cell('Set At #: ')
            dblpr.add_attr('align', 'left')

            prioid = 'prio_%s' % count
            ami_extr = 'false'
            row_priority = title.get_value('priority')
            if ext_sk not in [None, '']:
                ami_extr = 'true'
                row_priority = curr_group_prio
            dbltxt = smtbl.add_cell('<input type="text" value="%s" row_type="title" title_sk="%s" current_count="%s" current_priority="%s" class="count_order" id="%s" external_rejection="%s" ext_sk="%s" style="background-color: #FFFFFF;"/>' % (count, title.get_search_key(), count, row_priority, prioid, ami_extr, ext_sk))
            dbltxt.add_attr('align', 'left')
            dbltxt.add_behavior(hotlist_functions.show_change(prioid))
            dbl.add_cell(smtbl)

        tripl = Table()
        tripl.add_attr('width', '100%')
        tripl.add_attr('height', '100%')
        tripl.add_row()

        dc = tripl.add_cell(dbl)
        dc.add_attr('align', 'left')
        titl = table.add_cell(tripl)

        if count == 1:
            titl.add_attr('class', 'bottom_content')
            titl.add_attr('group', 'title')

        titl.add_attr('valign', 'top')
        titl.add_attr('width', '%s%s' % (tpct, '%'))
        group_keys = my.bigdict[code]['groups'].keys()

        for sg in my.seen_groups:
            if sg not in group_keys:
                black = table.add_cell(' ')
                if count == 1:
                    black.add_attr('class', 'bottom_content')
                    black.add_attr('group', sg)
                black.add_attr('width', '%s%s' % (my.indi_pct, '%'))
                black.add_style('background-color: %s;' % bgcol)
            else:
                tat = Table()
                tat.add_attr('width', '100%')
                tat.add_attr('height', '100%')
                tat.add_style('border-color: #e0e0e0;')
                tat.add_style('background-color: %s;' % my.bigdict[code]['groups'][sg]['relevant_status_color'])
                tat.add_style('font-size: 10px;')
                tat.add_style('border-bottom-right-radius', '10px')
                tat.add_style('border-bottom-left-radius', '10px')
                tat.add_style('border-top-right-radius', '10px')
                tat.add_style('border-top-left-radius', '10px')
                tasks = my.bigdict[code]['groups'][sg]['tasks']
                for t in tasks:
                    wo_code = t.get_value('lookup_code')
                    status = t.get_value('status')
                    process = t.get_value('process')
                    assigned = my.username_lookup[t.get_value('assigned')]
                    due_date = fix_date(t.get_value('bid_end_date')).split(' ')[0]
                    tittat = tat.add_row()
                    tittat.add_attr('title', wo_code)
                    tittat.add_attr('name', wo_code)
                    inspect_button = TaskObjLauncherWdg(code=wo_code, name=process)
                    tat.add_cell(inspect_button)

                    pro = tat.add_cell(abbreviate_text(process, 7))
                    pro.add_attr('nowrap', 'nowrap')
                    pro.add_attr('title', wo_code)
                    pro.add_attr('name', wo_code)
                    pro.add_style('background-color: %s;' % my.stat_colors[status])

                    stcell = tat.add_cell(abbreviate_text(status, 7))
                    stcell.add_attr('title', wo_code)
                    stcell.add_attr('name', wo_code)
                    stcell.add_style('background-color: %s;' % my.stat_colors[status])

                    acell = tat.add_cell(abbreviate_text(assigned, 7))
                    acell.add_style('background-color: %s;' % my.stat_colors[status])

                    dcell = tat.add_cell(due_date)
                    dcell.add_attr('nowrap', 'nowrap')
                    dcell.add_style('background-color: %s;' % my.stat_colors[status])
                tatcell1 = table.add_cell(tat) 
                if count == 1:
                    tatcell1.add_attr('class', 'bottom_content')
                    tatcell1.add_attr('group', sg)
                tatcell1.add_attr('valign', 'top')
                tatcell1.add_attr('width', '%s%s' % (my.indi_pct, '%'))
                tatcell1.add_style('background-color: %s;' % bgcol)

        return table

    def get_buttons(my, auto_refresh, auto_scroll):
        # TODO: Rewrite this entire function...
        btns = Table()
        btns.add_attr('class', 'auto_buttons')
        btns.add_row()

        if auto_refresh == 'yes':
            auto_text = 'Unset Auto-Refresh'
        else:
            auto_text = 'Set Auto-Refresh'

        auto = btns.add_cell('<input type="button" value="%s"/>' % auto_text)
        auto.add_attr('id', 'auto_refresh')
        auto.add_attr('name', 'auto_refresh')
        auto.add_attr('auto', auto_refresh)
        auto.add_behavior(hotlist_functions.get_reload())

        if auto_scroll == 'yes':
            scroll_text = 'Unset Auto-Scroll'
        else:
            scroll_text = 'Set Auto-Scroll'

        scroll = btns.add_cell('<input type="button" value="%s"/>' % scroll_text)
        scroll.add_attr('id', 'scroll_el')
        scroll.add_attr('name', 'scroll_el')
        scroll.add_attr('scroll', auto_scroll)
        scroll.add_behavior(hotlist_functions.set_scroll())

        to_top = btns.add_cell('<input type="button" value="Go To Top"/>')
        to_top.add_behavior(hotlist_functions.bring_to_top())

        if my.big_user:
            saveit = btns.add_cell('<input type="button" value="Save Priorities"/>')
            saveit.add_behavior(hotlist_functions.save_priorities())

        return btns

    def get_display(my):
        from operator import itemgetter

        search = Search("twog/global_resource")
        search.add_filter('name', 'Usernames Allowed Hot Today Changes')
        allowed = search.get_sobjects()
        if allowed:
            allowed = allowed[0].get_value('description').split(',')
            if my.user in allowed:
                my.big_user = True

        auto_refresh = 'no'
        auto_scroll = 'no'
        kgroups = ['ALL']

        if 'auto_refresh' in my.kwargs.keys():
            auto_refresh = my.kwargs.get('auto_refresh')

        if 'auto_scroll' in my.kwargs.keys():
            auto_scroll = my.kwargs.get('auto_scroll')

        # The whole view sits in this DivWdg
        divvy = DivWdg()

        if auto_refresh == 'yes':
            auto_refresh_behavior = {'type': 'load', 'cbjs_action': hotlist_functions.get_onload()}
            divvy.add_behavior(auto_refresh_behavior)

        if 'groups' in my.kwargs.keys():
            kgroups = my.kwargs.get('groups').split(',')

        search = Search("sthpw/login_group")
        search.add_where("\"login_group\" not in ('client','default','user')")

        thumbnail_clippings = {}

        divvy2 = DivWdg()
        divvy2.add_behavior(hotlist_functions.get_scroll_by_row())

        table = Table()
        table.add_attr('class', 'bigboard')
        table.add_attr('width', '100%')
        table.add_attr('bgcolor', '#fcfcfc')
        table.add_style('color: #000000;')
        table.add_style('font-family: Helvetica;')

        inorder = []
        bigbox = {}
        bigbox_prios = []
        search = Search("twog/title")
        search.add_filter('bigboard', True)
        search.add_filter('status', 'Completed', op='!=') #MTM ADDED THIS RESTRAINT 6/26/2015
        search.add_order_by("priority")
        search.add_order_by("expected_delivery_date")
        bigboarders = search.get_sobjects()

        external_rejection_search = Search("twog/external_rejection")
        external_rejection_search.add_where("\"status\" not in ('Closed','Waiting for Source')")
        external_rejection_search.add_order_by("priority")
        external_rejection_search.add_order_by("expected_delivery_date")
        external_rejections = external_rejection_search.get_sobjects()
        ext_2tit_dict = {}
        tit_2ext_dict = {}

        # TODO: What is all this for?
        if len(external_rejections) > 0:
            tempo = []
            for m in external_rejections:
                mtitle_s = Search("twog/title")
                mtitle_s.add_filter('code',m.get_value('title_code'))
                mtitle = mtitle_s.get_sobject()
                if mtitle:
                    if mtitle.get('is_external_rejection') == 'true':
                        mtitle_code = mtitle.get_code()
                        mcode = m.get_code()
                        if mcode not in ext_2tit_dict.keys():
                            ext_2tit_dict[mcode] = mtitle 
                        if mtitle_code not in tit_2ext_dict:
                            tit_2ext_dict[mtitle_code] = m
        
                        for b in bigboarders:
                            if m.get_value('priority') < b.get_value('priority') and m not in tempo:
                                tempo.append(m)
                            elif m.get_value('priority') == b.get_value('priority'):
                                if m.get_value('expected_delivery_date') <= b.get_value('expected_delivery_date') and m not in tempo:
                                    tempo.append(m)
                                elif b not in tempo:
                                    tempo.append(b)
                            elif b not in tempo:
                                tempo.append(b)
            if len(tempo) > 0:
                bigboarders = tempo

        search2 = Search("twog/indie_bigboard")
        search2.add_filter('indie_bigboard', True)
        search2.add_order_by("indie_priority")
        bigboarders2 = search2.get_sobjects()

        for b2 in bigboarders2:
            task_code = b2.get_value('task_code')
            ts = Search("sthpw/task")
            ts.add_filter('code', task_code)
            ts.add_filter('search_type', 'twog/proj?project=twog')
            b2_task = ts.get_sobject()
            alg = b2_task.get_value('assigned_login_group')
            if kgroups[0] == 'ALL' or kgroups[0] in alg:
                bigbox[task_code] = b2_task
                bigbox_prios.append({'code': task_code, 'priority': b2.get_value('indie_priority')}) 
                if alg not in my.seen_groups and 'supervisor' not in alg:
                    my.seen_groups.append(alg)

        tit_to_task = {}

        # TODO: I guess string concatenation was beyond this programmer's grasp...
        in_str = ''
        for bb in bigboarders:
            code = bb.get_value('code')
            if in_str == '':
                in_str = "('%s'" % code
            else:
                in_str = "%s,'%s'" % (in_str, code)
        in_str = "%s)" % in_str

        tq = Search("sthpw/task")
        tq.add_filter('bigboard', True)
        tq.add_filter('active', '1')
        tq.add_filter('search_type', 'twog/proj?project=twog')
        tq.add_filter('status','Completed', op="!=")
        if kgroups[0] != 'ALL':
            tq.add_where("\"assigned_login_group\" in ('%s','%s')" % (kgroups[0], kgroups[0]))
        tq.add_where("\"title_code\" in %s" % in_str)

        # TODO: Figure out what "bigkids" and "bk" are supposed to be. Now I want Burger King for lunch...
        bigkids4 = tq.get_sobjects()
        bkcounter = 0

        for bk in bigkids4:
            titcode = bk.get_value('title_code')
            ord = bk.get_value('order_in_pipe')
            asslg = bk.get_value('assigned_login_group')
            proj_code_linked = bk.get('proj_code')
            ord_name = '%s_%s_%s_%s' % (ord, proj_code_linked, asslg, bkcounter) 
            try:
                tit_to_task[titcode][ord_name] = bk        
            except:
                tit_to_task[titcode] = {ord_name: bk}        
                pass
            bkcounter += 1

        gorder = ['machine room', 'media vault', 'onboarding', 'compression', 'edit',
                  'audio', 'localization', 'qc', 'streamz', 'vault', 'edeliveries']
        bbc = 0

        for bb in bigboarders:
            code = bb.get_value('code') 
            as_ext = False
            if 'EXTERNAL_REJECTION' in code:
                as_ext = True
                real_title = ext_2tit_dict[code]
                code = real_title.get_code()
            else:
                real_title = bb

            if code in tit_to_task.keys():
                tobs = tit_to_task[code]
            else:
                tobs = {}
            tob_keys = tobs.keys()
            tob_keys.sort()

            bigkids = []
            for tk in tob_keys:
                bigkids.append(tobs[tk])
            if len(bigkids) > 0:
                my.bigdict[code] = {'title_obj': real_title, 'groups': {}}
                for bigkid in bigkids:
                    alg = bigkid.get_value('assigned_login_group')
                    status = bigkid.get_value('status')
                    if kgroups[0] == 'ALL':
                        if alg not in my.bigdict[code]['groups'].keys() and 'supervisor' not in alg:
                            my.bigdict[code]['groups'][alg] = {'tasks': [], 'relevant_status': 0, 'relevant_status_color': ''}
                        if alg not in my.seen_groups and 'supervisor' not in alg:
                            my.seen_groups.append(alg)
                        if my.stat_relevance[status] >= my.bigdict[code]['groups'][alg]['relevant_status']:
                            my.bigdict[code]['groups'][alg]['relevant_status'] = my.stat_relevance[status]
                            my.bigdict[code]['groups'][alg]['relevant_status_color'] = my.stat_colors[status]
                        my.bigdict[code]['groups'][alg]['tasks'].append(bigkid)
                        if code not in inorder:
                            inorder.append(code)
                            bigbox[code] = bb
                            bigbox_prios.append({'code': code, 'priority': bb.get_value('priority')}) 
                    else:
                        if kgroups[0] in alg:
                            if alg not in my.bigdict[code]['groups'].keys() and 'supervisor' not in alg:
                                my.bigdict[code]['groups'][alg] = {'tasks': [], 'relevant_status': 0, 'relevant_status_color': ''}
                            if alg not in my.seen_groups and 'supervisor' not in alg:
                                my.seen_groups.append(alg)
                            if my.stat_relevance[status] >= my.bigdict[code]['groups'][alg]['relevant_status']:
                                my.bigdict[code]['groups'][alg]['relevant_status'] = my.stat_relevance[status]
                                my.bigdict[code]['groups'][alg]['relevant_status_color'] = my.stat_colors[status]
                            my.bigdict[code]['groups'][alg]['tasks'].append(bigkid)
                            if code not in inorder:
                                inorder.append(code)
                                bigbox[code] = bb
                                bigbox_prios.append({'code': code, 'priority': bb.get_value('priority')}) 
            elif as_ext:
                my.bigdict[code] = {'title_obj': real_title, 'groups': {}, 'is_ext': 'true'}
                if code not in inorder:
                    inorder.append(code)
                    bigbox[code] = real_title
                    ext_priority = bb.get_value('priority')
                    if ext_priority in [None, '']:
                        ext_priority = 0
                    bigbox_prios.append({'code': code, 'priority': ext_priority, 'is_ext': 'true'}) 
            elif bb.get_value('requires_mastering_qc') not in ['False', 'false', '0', None, False]:
                my.bigdict[code] = {'title_obj': real_title, 'groups': {}}
                if code not in inorder:
                    inorder.append(code)
                    bigbox[code] = bb
                    bigbox_prios.append({'code': code, 'priority': bb.get_value('priority')}) 
            bbc += 1

        tmparr = my.seen_groups
        my.seen_groups = []

        for g in gorder:
            if g in tmparr:
                my.seen_groups.append(g)
        for guy in tmparr:
            if guy not in gorder:
                my.seen_groups.append(guy)

        if len(kgroups) > 0 and kgroups[0] != 'ALL':
            my.seen_groups = kgroups

        sg_len = len(my.seen_groups)
        col_len = sg_len + 2
        my.indi_pct = float(100/col_len)

        # This is where the buttons for auto-refresh, auto-scroll, and go to top get set.
        # TODO: Rewrite this to accept True and False params rather than 'yes' or 'no'
        btns = my.get_buttons(auto_refresh, auto_scroll)
        table.add_cell(btns)

        # TODO: Rewrite table head and body to be part of same table
        toprow = table.add_row()
        toprow.add_attr('class', 'trow_nomove')
        table.add_cell(my.trow_top())

        # Table body starts here
        t2 = Table()
        t2.add_attr('width', '100%')
        t2.add_attr('bgcolor', '#fcfcfc')
        t2.add_attr('border', '1')
        t2.add_style('border-color: #444444;')
        t2.add_style('color: #000000;')
        t2.add_style('font-family: Helvetica;')

        # Need to alternate row colors starting at fcfcfc, then going to ffffff
        if my.seen_groups:
            new_ordering = sorted(bigbox_prios, key=itemgetter('priority')) 
            count = 1
            grouping_prio = -1
            for bp in new_ordering:
                is_ext = False
                external_r = None
                ext_prio = 0
                if 'is_ext' in bp.keys():
                    is_ext = True
                    external_r = tit_2ext_dict[bp.get('code')]
                    ext_prio = external_r.get_value('priority')
                    if ext_prio in [None, '']:
                        ext_prio = 0
                code = bp.get('code')
                client_thumbnail_clippings = ''
                platform_thumbnail_clippings = ''
                bgcol = '#fcfcfc'
                if count % 2 == 0:
                    bgcol = '#ffffff'
                if 'TITLE' in code:
                    bb = my.bigdict[code]['title_obj']
                    curr_group_prio = bb.get_value('priority')
                    if 'is_ext' in my.bigdict[code].keys():
                        curr_group_prio = ext_prio
                    if curr_group_prio != grouping_prio:
                        grouping_prio = curr_group_prio
                        grouping_row = t2.add_row()
                        grouping_cell = t2.add_cell(grouping_prio)
                        grouping_cell.add_attr('colspan', len(my.seen_groups) + 1)
                        grouping_row.add_attr('current_priority', grouping_prio)
                        grouping_row.add_attr('state', 'opened')
                        grouping_row.add_style('background-color: #dce3ee;')
                        grouping_row.add_behavior(hotlist_functions.toggle_groupings())
                        
                    client_code = bb.get_value('client_code')
                    client_name = bb.get_value('client_name')

                    if not client_code:
                        # Set to default if no client assigned
                        client_code = 'CLIENT00286'

                    # TODO: Check if thumbnail_clippings even does anything, pretty sure it doesn't
                    if client_code not in thumbnail_clippings.keys():
                        img_path = hotlist_functions.get_client_img(client_code)
                        if img_path not in [None, '']:
                            img_str = '<img src="%s" alt="%s" title="%s" style="width: 32px; height: 32px;"/>' % (img_path, client_name, client_name)
                            thumbnail_clippings[client_code] = img_str
                            client_thumbnail_clippings = img_str
                    else:
                        client_thumbnail_clippings = thumbnail_clippings[client_code]
                    platform = bb.get_value('platform', '0')

                    if not platform:
                        # If no platform specified, set to default 0
                        platform = '0'

                    # Looks like this is where the platform icon and text is decided
                    if platform not in thumbnail_clippings.keys():
                        img_path = hotlist_functions.get_platform_img(platform)

                        if img_path not in [None, '']:
                            img_str = '<img src="%s" alt="%s" title="%s" style="width: 32px; height: 32px;"/>' % (img_path, platform, platform)
                        else:
                            img_str = platform

                        thumbnail_clippings[platform] = img_str
                        platform_thumbnail_clippings = img_str
                    else:
                        platform_thumbnail_clippings = thumbnail_clippings[platform]
                    expected_delivery_date = bb.get_value('expected_delivery_date')
                    external_status = None
                    ext_sk = None
                    ext_assigned = None
                    ext_assigned_corrective = None
                    if is_ext:
                        expected_delivery_date = external_r.get_value('expected_delivery_date')
                        external_status = external_r.get_value('status')
                        ext_sk = external_r.get_search_key()
                        ext_assigned = external_r.get_value('assigned')
                        ext_assigned_corrective = external_r.get_value('corrective_action_assigned')
                        if ext_assigned == '--Select--':
                            ext_assigned = None
                        if ext_assigned_corrective == '--Select--':
                            ext_assigned_corrective = None
                    t2 = my.trow(bb, expected_delivery_date, count, client_thumbnail_clippings, platform_thumbnail_clippings, t2, bgcol, ext_sk, curr_group_prio, external_status, ext_assigned, ext_assigned_corrective)
                    count += 1
                else:
                    # TODO: Does this ever get called? Haven't seen a non-title in the hot today list so far...
                    bb = bigbox[code]
                    curr_group_prio = bb.get_value('indie_priority')
                    if curr_group_prio != grouping_prio:
                        grouping_prio = curr_group_prio
                        grouping_row = t2.add_row()
                        grouping_cell = t2.add_cell(grouping_prio)
                        grouping_cell.add_attr('colspan', len(my.seen_groups) + 1)
                        grouping_row.add_attr('current_priority', grouping_prio)
                        grouping_row.add_attr('state', 'opened')
                        grouping_row.add_style('background-color: #dce3ee;')
                        grouping_row.add_behavior(hotlist_functions.toggle_groupings())
                    client_code = bb.get_value('client_code')
                    if client_code not in thumbnail_clippings.keys():
                        img_path = hotlist_functions.get_client_img(client_code)
                        if img_path not in [None, '']:
                            img_str = '<img src="%s" style="width: 32px; height: 32px;"/>' % img_path
                            thumbnail_clippings[client_code] = img_str      
                            client_thumbnail_clippings = img_str
                    else:
                        client_thumbnail_clippings = thumbnail_clippings[client_code]
                    platform = bb.get_value('platform', '0')

                    if platform not in thumbnail_clippings.keys():
                        img_path = hotlist_functions.get_platform_img(platform)
                        if img_path not in [None, '']:
                            img_str = '<img src="%s" style="width: 32px; height: 32px;"/>' % img_path
                            thumbnail_clippings[platform] = img_str      
                            platform_thumbnail_clippings = img_str
                    else:
                        platform_thumbnail_clippings = thumbnail_clippings[platform]
                    search = Search("twog/order")
                    search.add_filter('code', bb.get_value('order_code'))
                    task_order = search.get_sobjects()
                    expected_delivery_date = bb.get_value('bid_end_date')
                    if task_order:
                        task_order = task_order[0]
                        expected_delivery_date = task_order.get_value('expected_delivery_date')
                    t2 = my.wrow(bb, expected_delivery_date, count, client_thumbnail_clippings, platform_thumbnail_clippings, t2, bgcol)
                    count += 1
        t2.add_behavior({
                'type': 'load',
                'cbjs_action': '''
                realign_timer = function(timelen){
                    setTimeout('realign_headers()', timelen);
                }
                realign_headers = function(){
                    tops = document.getElementsByClassName('topper');
                    bottoms = document.getElementsByClassName('bottom_content');
                    for(var r = 0; r < tops.length; r++){
                        top_group = tops[r].getAttribute('group');
                        for(var y = 0; y < bottoms.length; y++){
                            bottom_group = bottoms[y].getAttribute('group');
                            if(bottom_group == top_group){
                                bottom_size = bottoms[y].getSize();
                                //tops[r].setStyle('width',bottom_size.x - 1);
                                tops[r].setStyle('width',bottom_size.x + 1);
                            }
                        }
                    } 
                }
                window.onresize = function() {
                    realign_headers();
                }
                realign_headers();
                realign_timer(1000);

                '''
        })

        t2div = DivWdg()
        t2div.add_attr('id', 'title_body')
        t2div.add_attr('width', '100%')
        t2div.add_attr('bgcolor', '#fcfcfc')
        t2div.add_style('color: #000000;')
        t2div.add_style('font-family: Helvetica;')
        t2div.add_style('overflow-y: scroll;')
        t2div.add_style('height: 900px;')

        t2div.add(t2)
        table.add_row()
        table.add_cell(t2div)
        table.add_row()

        # Buttons on the bottom of the table
        btns = my.get_buttons(auto_refresh, auto_scroll)

        table.add_row()
        table.add_cell(btns)

        divvy2.add(table)
        divvy.add(divvy2)

        return divvy
