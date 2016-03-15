from tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseTableElementWdg

from pyasm.web import Table, DivWdg

from alternative_elements.customcheckbox import *


class TitleDeletorWdg(BaseTableElementWdg):
    #This allows the scheduler to delete multiple titles all at one time
    def init(my):
        nothing = 'true'

    def get_display(my):
        server = TacticServerStub.get()
        user_name = my.kwargs.get('user')
        code = my.kwargs.get('code')
        order_name = my.kwargs.get('order_name')
        allowed_titles_str = my.kwargs.get('allowed_titles_str')
        sk = server.build_search_key('twog/order', code)
        # Get list of titles in this order
        titles_expr = "@SOBJECT(twog/title['order_code','%s']['code','in','%s'])" % (code, allowed_titles_str)
        titles = server.eval(titles_expr)
        widget = DivWdg()
        table = Table()
        table.add_style('background-color: #FF0000;')
        table.add_attr('class', 'del_titles_selector')

        toggle_behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                            var checked_img = '<img src="/context/icons/custom/custom_checked.png"/>'
                            var not_checked_img = '<img src="/context/icons/custom/custom_unchecked.png"/>'
                            var top_el = spt.api.get_parent(bvr.src_el, '.del_titles_selector');
                            inputs = top_el.getElementsByClassName('title_selector');
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
        '''}
        client_status_colors = {'Assignment': '#fcaf88', 'Pending': '#d7d7d7', 'In Progress': '#f5f3a4', 'In_Progress': '#f5f3a4', 'In Production': '#f5f3a4', 'In_Production': '#f5f3a4', 'In production': '#f5f3a4', 'In_production': '#f5f3a4', 'Waiting': '#ffd97f', 'Need Assistance': '#fc88fb', 'Need_Assistance': '#fc88fb', 'Review': '#888bfc', 'Approved': '#d4b5e7', 'On Hold': '#e8b2b8', 'On_Hold': '#e8b2b8', 'Client Response': '#ddd5b8', 'Completed': '#b7e0a5','Ready': '#b2cee8', 'Internal Rejection': '#ff0000', 'External Rejection': '#ff0000', 'Rejected': '#ff0000', 'Failed QC': '#ff0000', 'Not Set': '#d7d7d7', 'Waiting on client materials': '#ffd97f', 'Materials received': '#b2cee8', 'QC Rejected': '#ff0000', 'QC Passed': '#d4b5e7', 'QC rejected': '#ff0000', 'QC passed': '#d4b5e7', 'Fix Needed': '#c466a1', 'Need Buddy Check': '#e3701a', 'DR In_Progress': '#d6e0a4', 'DR In Progress': '#d6e0a4','Amberfin01_In_Progress':'#D8F1A8', 'Amberfin01 In Progress':'#D8F1A8', 'Amberfin02_In_Progress':'#F3D291',  'Amberfin02 In Progress':'#F3D291','BATON In_Progress': '#c6e0a4', 'BATON In Progress': '#c6e0a4','Export In_Progress': '#796999', 'Export In Progress': '#796999','Buddy Check In_Progress': '#1aade3','Buddy Check In Progress': '#1aade3', 'Not Set' : '#FFFFCC'}
        # Only need the toggler if there's more than 1 title
        if len(titles) > 1:
            toggler = CustomCheckboxWdg(name='chk_del_toggler',additional_js=toggle_behavior,value_field='toggler',id='selection_toggler',checked='false')

            table.add_row()
            table.add_cell(toggler)
            table.add_cell('<b><- Select/Deselect ALL</b>')
            table.add_cell('&nbsp;&nbsp;&nbsp;')
            table.add_cell('<b>Status</b>')
            table.add_cell('&nbsp;&nbsp;&nbsp;')
            table.add_cell('<b>Client Status</b>')
        # Display the titles to choose from
        for title in titles:
            table.add_row()

            checkbox = CustomCheckboxWdg(name='del_title_%s' % title.get('code'),value_field=title.get('code'),checked='false',dom_class='title_selector')

            ck = table.add_cell(checkbox)
            tname = title.get('title')
            if title.get('episode') not in [None,'']:
                tname = '%s: %s' % (tname, title.get('episode'))
            name = table.add_cell(tname)
            name.add_attr('nowrap','nowrap')
            table.add_cell('&nbsp;&nbsp;&nbsp;')
            tstatus = title.get('status')
            if tstatus in [None,'']:
                tstatus = 'Not Set'
            status = table.add_cell(tstatus)
            status.add_attr('nowrap','nowrap')
            table.add_cell('&nbsp;&nbsp;&nbsp;')
            tclient_status = title.get('client_status')
            if tclient_status in [None,'']:
                tclient_status = 'Not Set'
            client_status = table.add_cell(tclient_status)
            client_status.add_attr('nowrap','nowrap')

            client_status.add_style('color: %s;' % client_status_colors[tclient_status])

        if len(titles) < 1:
            table.add_row()
            table.add_cell('There are no titles in this Order')

        table.add_row()
        go_butt = ''
        # If there is nothing to delete, just show them the exit button "Continue"
        if len(titles) < 1:
            go_butt = table.add_cell('<input type="button" class="filter_titles" value="Continue"/>')
        else:
            nada = table.add_cell(' ')
            go_butt = table.add_cell('<input type="button" class="filter_titles" value="Delete"/>')
        go_butt.add_attr('sk',server.build_search_key('twog/order', code))
        go_butt.add_attr('search_type','twog/order')
        go_butt.add_attr('user',user_name)
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          if(confirm("Do You Really Want To Delete These Titles?")){
                              var server = TacticServerStub.get();
                              var my_sk = '%s';
                              var my_user = '%s';
                              var order_name = '%s';
                              var my_code = my_sk.split('code=')[1];
                              var class_name = 'order_builder.order_builder.OrderBuilder';
                              kwargs = {
                                           'sk': my_sk,
                                           'user': my_user
                              };
                              var top_el = spt.api.get_parent(bvr.src_el, '.del_titles_selector');
                              var order_el = document.getElementsByClassName('twog_order_builder_' + my_sk)[0];
                              allowed_titles = order_el.getAttribute('allowed_titles');
                              allowed_titles_arr = allowed_titles.split('|');
                              new_allowed_titles = ''
                              deleted_titles = [];
                              //Get list of titles the user wants to delete
                              checks = top_el.getElementsByClassName('title_selector');
                              for(var r = 0; r < checks.length; r++){
                                  //see which titles will be deleted, and which ones will not
                                  title_code = checks[r].getAttribute('value_field');
                                  if(checks[r].getAttribute('checked') == 'true'){
                                      deleted_titles.push(title_code)
                                  }
                              }
                              //Doublecheck for safety's sake
                              if(confirm("Seriously Now, Are You Sure You Want To Delete These " + deleted_titles.length + " Titles from this Order?")){
                                  for(var r = 0; r < deleted_titles.length; r++){
                                      title_code = deleted_titles[r];
                                      spt.app_busy.show("Deleting " + title_code + "...");
                                      title_sk = server.build_search_key('twog/title', title_code);
                                      //delete them
                                      server.retire_sobject(title_sk);
                                  }
                                  for(var r = 0; r < allowed_titles_arr.length; r++){
                                      tcode = allowed_titles_arr[r];
                                      if(deleted_titles.indexOf(tcode) == -1){
                                          if(new_allowed_titles == ''){
                                              new_allowed_titles = tcode;
                                          }else{
                                              new_allowed_titles = new_allowed_titles + '|' + tcode;
                                          }
                                      }
                                  }
                                  spt.app_busy.show("Reloading Order...");
                                  kwargs['allowed_titles'] = new_allowed_titles;
                                  cover = document.getElementsByClassName('twog_order_builder_cover_' + my_sk)[0];
                                  cover_cell = cover.getElementsByClassName('cover_cell')[0];
                                  //Reload order builder
                                  spt.api.load_panel(cover_cell, class_name, kwargs);
                                  spt.popup.close(spt.popup.get_popup(bvr.src_el));
                                  spt.app_busy.hide();
                              }
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (sk, user_name, order_name)}
        go_butt.add_behavior(behavior)
        widget.add(table)
        return widget
