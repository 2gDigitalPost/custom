from tactic.ui.common import BaseTableElementWdg
from tactic.ui.widget import CalendarInputWdg

from pyasm.web import Table, DivWdg
from pyasm.search import Search

from alternative_elements.customcheckbox import CustomCheckboxWdg
from common_tools.common_functions import fix_date


class TitleDuePrioBBWdg(BaseTableElementWdg):
    #This is a widget that will allow you to change the due date, priority and bigboard values on multiple orders at the same time
    def init(my):
        nothing = 'true'
        my.checked = '/context/icons/silk/rosette.png'
        my.unchecked = '/context/icons/silk/rosette_grey.png'

    def get_display(my):
        user_name = my.kwargs.get('user')
        code = my.kwargs.get('code')
        sk = my.kwargs.get('sk')

        t_search = Search("twog/title")
        t_search.add_filter('order_code',code)
        titles = t_search.get_sobjects()
        widget = DivWdg()
        table = Table()
        table.add_attr('cellpadding','10')
        table.add_attr('class','change_titles_selector')
        # Turn all checkboxes on or off
        toggle_behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                            var checked_img = '<img src="%s"/>'
                            var not_checked_img = '<img src="%s"/>'
                            var top_el = spt.api.get_parent(bvr.src_el, '.change_titles_selector');
                            inputs = top_el.getElementsByClassName('change_title_selector');
                            var curr_val = bvr.src_el.getAttribute('checked');
                            image = '';
                            if(curr_val == 'false'){
                                curr_val = false;
                                image = not_checked_img;
                            }else if(curr_val == 'true'){
                                curr_val = true;
                                image = checked_img;
                            }
                            for(var r = 0; r < inputs.length; r++){
                                inputs[r].setAttribute('checked',curr_val);
                                inputs[r].innerHTML = image;
                            }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
        ''' % (my.checked, my.unchecked)}
        # No need for toggler if there are less than 2 titles
        if len(titles) > 1:
            toggler = CustomCheckboxWdg(name='chk_change_toggler',additional_js=toggle_behavior,value_field='toggler',id='selection_toggler',checked='false',checked_img=my.checked,unchecked_img=my.unchecked)

            table.add_row()
            cs = table.add_cell('<b>BigBoard Select/Deselect ALL -></b>')
            cs.add_attr('colspan','6')
            cs.add_attr('align','right')
            table.add_cell(toggler)
            dupe = CustomCheckboxWdg(name='duplicate_bigboard_wos',value_field='duplicate_bigboard_wos',id='duplicate_bigboard_wos',checked='false')
            cs2 = table.add_cell('<b>Work Order Bigboarding Duplication</b>')
            cs2.add_attr('align','right')
            table.add_cell(dupe)

        # display the column heads
        if len(titles) > 0:
            table.add_row()
            table.add_cell('<b>Code</b>')
            table.add_cell('<b>Name</b>')
            sd = table.add_cell('<b>Start Date</b>')
            sd.add_attr('nowrap','nowrap')
            dd = table.add_cell('<b>Due Date</b>')
            dd.add_attr('nowrap','nowrap')
            edd = table.add_cell('<b>Expected Delivery Date</b>')
            edd.add_attr('nowrap','nowrap')
            table.add_cell('<b>Priority</b>')
            table.add_cell('<b>BigBoard</b>')
        # Display the list of titles and values that can be changed
        for title in titles:
            table.add_row()
            tisk = title.get_search_key()
            tname = title.get_value('title')
            if title.get_value('episode') not in [None,'']:
                tname = '%s: %s' % (tname, title.get_value('episode'))

            cc = table.add_cell(title.get_code())

            name = table.add_cell(tname)
            name.add_attr('nowrap','nowrap')

            start = CalendarInputWdg('start_dateFORMRSK%s' % tisk)
            start.set_option('show_time', 'true')
            start.set_option('show_activator', 'true')
            start.set_option('display_format', 'MM/DD/YYYY HH:MM')
            start.set_option('time_input_default','5:00 PM')
            sd_fixed = fix_date(title.get_value('start_date'))
            if title.get_value('start_date') not in [None,'']:
                start.set_option('default', sd_fixed)

            due = CalendarInputWdg('due_dateFORMRSK%s' % tisk)
            due.set_option('show_time', 'true')
            due.set_option('show_activator', 'true')
            due.set_option('display_format', 'MM/DD/YYYY HH:MM')
            due.set_option('time_input_default','5:00 PM')
            dd_fixed = fix_date(title.get_value('due_date'))
            if title.get_value('due_date') not in [None,'']:
                due.set_option('default', dd_fixed)

            expected_delivery = CalendarInputWdg('expected_delivery_dateFORMRSK%s' % tisk)
            expected_delivery.set_option('show_time', 'true')
            expected_delivery.set_option('show_activator', 'true')
            expected_delivery.set_option('display_format', 'MM/DD/YYYY HH:MM')
            expected_delivery.set_option('time_input_default', '5:00 PM')
            ed_fixed = fix_date(title.get_value('expected_delivery_date'))
            if title.get_value('expected_delivery_date') not in [None,'']:
                expected_delivery.set_option('default', ed_fixed)

            d1 = table.add_cell(start)
            d1.add_attr('valign', 'top')
            d2 = table.add_cell(due)
            d2.add_attr('valign', 'top')
            d3 = table.add_cell(expected_delivery)
            d3.add_attr('valign', 'top')

            pr = table.add_cell('<input type="text" value="%s" current_val="%s" name="priorityFORMRSK%s" class="priority"/>' % (title.get_value('priority'), title.get_value('priority'), title.get_search_key()))
            pr.add_attr('valign', 'top')

            check_val = 'false'
            if title.get_value('bigboard') in [True,'1','t','true','yes','Yes']:
                check_val = 'true'
            else:
                check_val = 'false'
            # Want to remove all Checkboxes from Order Builder, since they query the database and make everything a little slower
            checkbox = CustomCheckboxWdg(name='bigboard_title_%s' % tisk,alert_name=tname,value_field=title.get_code(),checked=check_val,dom_class='change_title_selector',checked_img=my.checked,unchecked_img=my.unchecked)
            ck = table.add_cell(checkbox)
            ck.add_attr('valign','top')

        if len(titles) < 1:
            table.add_row()
            table.add_cell('There are no titles in this Order')

        table.add_row()
        go_butt = ''
        if len(titles) > 0:
            nada = table.add_cell(' ')
            nada.add_attr('colspan','6')
            go_butt = table.add_cell('<input type="button" class="change_titles" value="Apply Changes"/>')
            go_butt.add_attr('sk',sk)
            go_butt.add_attr('search_type','twog/order')
            go_butt.add_attr('user',user_name)
            behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                            function oc(a){
                                var o = {};
                                for(var i=0;i<a.length;i++){
                                    o[a[i]]='';
                                }
                                return o;
                            }
                            try{
                              var my_sk = '%s';
                              var my_user = '%s';
                              var my_code = my_sk.split('code=')[1];
                              var class_name = 'nighttime_hotlist.nighttime_hotlist.BigBoardWOSelectWdg';
                              if(confirm("Do You Really Want To Change These Title Values?")){
                                  var server = TacticServerStub.get();
                                  var top_el = spt.api.get_parent(bvr.src_el, '.change_titles_selector');
                                  proceed = true;
                                  titles_to_bb = [];
                                  titles_to_unbb = [];
                                  title_names = [];
                                  title_changes = {};
                                  tca = [];
                                  if(proceed){
                                      var inputs = top_el.getElementsByTagName('input');
                                      for(var r = 0; r < inputs.length; r++){
                                          if(inputs[r].name != 'chk_change_toggler' && inputs[r].type != 'button'){
                                              //get the name of the field and the value, save for the update
                                              name = inputs[r].getAttribute('name');
                                              current_val = inputs[r].getAttribute('current_val');
                                              type = name.split('FORMRSK')[0];
                                              sk = name.split('FORMRSK')[1];
                                              value = inputs[r].value;
                                              if(value == null){
                                                  value = '';
                                              }
                                              if(value != current_val){
                                                  //Create a dict (array) of the title values if not already there
                                                  //If it already exitst, just add to the entry
                                                  if(!(sk in oc(tca))){
                                                      tca.push(sk)
                                                      title_changes[sk] = {}
                                                  }else{
                                                      title_changes[sk][type] = value;
                                                  }
                                                  inputs[r].setAttribute('current_val',value);
                                              }
                                          }
                                      }
                                      checks = top_el.getElementsByClassName('change_title_selector');
                                      for(var r = 0; r < checks.length; r++){
                                          //see which titles will be bigboarded, and which ones will not
                                          title_code = checks[r].getAttribute('value_field');
                                          if(checks[r].getAttribute('checked') == 'true'){
                                              title_name = checks[r].getAttribute('alert_name');
                                              titles_to_bb.push(title_code)
                                              title_names.push(title_name);
                                          }else{
                                              titles_to_unbb.push(title_code)
                                          }
                                      }
                                      duplicate_bigboard_wos_el = top_el.getElementById('duplicate_bigboard_wos');
                                      duplicate_bigboard_wos = duplicate_bigboard_wos_el.getAttribute('checked');
                                      if(duplicate_bigboard_wos == 'true'){
                                          class_name = 'nighttime_hotlist.nighttime_hotlist2.BigBoardWOSelect4MultiTitlesWdg2';
                                      }
                                      //Submit the changes
                                      for(var r= 0; r < tca.length; r++){
                                          server.update(tca[r], title_changes[tca[r]]);
                                      }
                                      apply_to_all = false;
                                      copy_title_code = '';
                                      copy_names = [];
                                      copy_names_str = '';
                                      copy_names_no = [];
                                      copy_names_no_str = '';
                                      //Make sure the titles that shouldn't be bigboarded now (per user's selection), are not bigboarded
                                      for(var r = 0; r < titles_to_unbb.length; r++){
                                          server.update(server.build_search_key('twog/title', titles_to_unbb[r]), {'bigboard': 'false'});
                                      }
                                      if(duplicate_bigboard_wos != 'true'){
                                          //If the Title is going to be bigboarded, load the list of work orders per title to select for the bigboard
                                          for(var r = 0; r < titles_to_bb.length; r++){
                                              this_title_code = titles_to_bb[r];
                                              this_title_sk = server.build_search_key('twog/title',this_title_code);
                                              server.update(this_title_sk, {'bigboard': 'true'});
                                              if(!apply_to_all){
                                                  kwargs = {
                                                      'sk': this_title_sk
                                                  };
                                                  spt.panel.load_popup('Select Big Board Work Orders for ' + title_names[r], class_name, kwargs);
                                              }else{
                                                  //This section looks stupid and needs to be fixed
                                                  if(copy_names.length == 0){
                                                      tasks_w_bb = server.eval("@SOBJECT(sthpw/task['title_code','" + copy_title_code + "']['bigboard','True'])");
                                                      for(var x = 0; x < tasks_w_bb.length; x++){
                                                          copy_names.push(tasks_w_bb[x].process);
                                                          if(copy_names_str == ''){
                                                              copy_names_str = tasks_w_bb[x].process;
                                                          }else{
                                                              copy_names_str = copy_names_str + '|' + tasks_w_bb[x].process;
                                                          }
                                                      }
                                                      tasks_wo_bb = server.eval("@SOBJECT(sthpw/task['title_code','" + copy_title_code + "']['bigboard','not in','True'])");
                                                      for(var x = 0; x < tasks_wo_bb.length; x++){
                                                          copy_names_no.push(tasks_wo_bb[x].process);
                                                          if(copy_names_no_str == ''){
                                                              copy_names_no_str = tasks_wo_bb[x].process;
                                                          }else{
                                                              copy_names_no_str = copy_names_no_str + '|' + tasks_wo_bb[x].process;
                                                          }
                                                      }

                                                  }
                                                  //This will update all of the tasks to be bigboarded, if in copy names str
                                                  this_tt = server.eval("@SOBJECT(sthpw/task['title_code','" + this_title_code + "']['search_type','twog/proj?project=twog']['process','" + copy_names_str + "'])");
                                                  for(var w = 0; w < this_tt.length; w++){
                                                      server.update(this_tt[w].__search_key__, {'bigboard': 'true'});
                                                  }
                                                  //This will update all of the tasks to be un-bigboarded, if in copy_names_no_str
                                                  this_tt = server.eval("@SOBJECT(sthpw/task['title_code','" + this_title_code + "']['search_type','twog/proj?project=twog']['process','" + copy_names_no_str + "'])");
                                                  for(var w = 0; w < this_tt.length; w++){
                                                      server.update(this_tt[w].__search_key__, {'bigboard': 'false'});
                                                  }
                                              }
                                          }
                                      }else{
                                          title_codes = titles_to_bb.join();
                                          if(title_codes != '' && title_codes != ','){
                                              kwargs = {
                                                  'title_codes': title_codes
                                              };
                                              spt.panel.load_popup('Select Big Board Work Orders for the Selected Titles', class_name, kwargs);
                                          }
                                      }
                                      spt.popup.close(spt.popup.get_popup(bvr.src_el));
                                  }
                              }
                    }
                    catch(err){
                              spt.app_busy.hide();
                              spt.alert(spt.exception.handler(err));
                              //alert(err);
                    }
             ''' % (sk, user_name)}
            go_butt.add_behavior(behavior)
        widget.add(table)
        return widget
