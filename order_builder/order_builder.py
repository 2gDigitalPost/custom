__all__ = ["OrderBuilderLauncherWdg", "TitleSelectorWdg", "TitleCloneSelectorWdg",
           "TitleDeletorWdg", "TitleProjStatusTriggerWdg", "OrderBuilder", "TitleRow", "AddWorkOrderWdg",
           "AddProjWdg", "EditHackPipe", "HackPipeConnectWdg", "DeliverableWdg",
           "IntermediateEditWdg", "DeliverableEditWdg", "WorkOrderSourceAddWdg", "TwogEasyCheckinWdg",
           "OutsideBarcodesListWdg", "NewSourceWdg", "SourceEditWdg", "ProjDueDateChanger",
           "IntermediatePassinAddWdg", "DeliverablePassinAddWdg", "DeliverableAddWdg",
           "IntermediateFileAddWdg", "EquipmentUsedAdderWdg", "EquipmentUsedMultiAdderWdg",
           "OperatorErrorDescriptPopupWdg", "ExternalRejectionReasonWdg", "Barcoder", "TitleRedoWdg"]

import tacticenv
from tactic_client_lib import TacticServerStub
from pyasm.common import Environment
from pyasm.biz import *
from pyasm.web import Table, DivWdg
from pyasm.widget import SelectWdg, TextWdg, CheckboxWdg
from pyasm.search import Search

from tactic.ui.common import BaseTableElementWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.panel import EditWdg
from custom_piper import CustomPipelineToolWdg
from tactic.ui.widget import CalendarInputWdg, ActionButtonWdg
from tactic.ui.widget.button_new_wdg import ButtonRowWdg
from work_order_printer import WorkOrderPrintLauncherWdg
from order_checker import OrderCheckerLauncherWdg
from alternative_elements.customcheckbox import *
from widget.new_icon_wdg import CustomIconWdg
from widget.button_small_new_wdg import ButtonSmallNewWdg

from common_tools.full_instructions import FullInstructionsLauncherWdg
from common_tools.common_functions import fix_date
from builder_tools_wdg import BuilderTools
from task_edit_widget import TaskEditWdg
from title_row import TitleRow
from order_builder_utils import OBScripts, get_upload_behavior, get_open_intermediate_behavior
from order_table_wdg import OrderTable
from quick_edit_wdg import QuickEditWdg


class OrderBuilderLauncherWdg(BaseTableElementWdg):
    #This is the button that launches the TitleSelectorWdg

    def init(my):
        nothing = 'true'

    def get_launch_behavior(my):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                          var my_code = bvr.src_el.get('code');
                          var my_title_code = bvr.src_el.get('title_code');
                          var class_name = 'order_builder.order_builder.TitleSelectorWdg';
                          kwargs = {
                                           'code': my_code
                                   };
                          if(my_title_code != ''){
                              kwargs['title_code'] = my_title_code;
                              server = TacticServerStub.get();
                              kwargs['code'] = server.eval("@GET(twog/title['code','" + my_title_code + "'].order_code)")[0];
                          }
                          spt.panel.load_popup('Select Titles', class_name, kwargs);
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         '''}
        return behavior

    def get_display(my):
        if 'code' in my.kwargs.keys():
            code = my.kwargs.get('code') 
        else: 
            sobject = my.get_current_sobject()
            code = sobject.get_code()
        title_code = ''
        if 'title_code' in my.kwargs.keys():
            title_code = my.kwargs.get('title_code')
            
        widget = DivWdg()
        table = Table()
        table.add_attr('width', '50px')
        table.add_row()
        cell1 = table.add_cell('<img border="0" style="vertical-align: middle" title="" src="/context/icons/custom/work.png">')
        cell1.add_attr('code', code)
        cell1.add_attr('title_code', title_code)
        launch_behavior = my.get_launch_behavior()
        cell1.add_style('cursor: pointer;')
        cell1.add_behavior(launch_behavior)
        widget.add(table)

        return widget

class TitleSelectorWdg(BaseTableElementWdg):
    # This is the widget that lets you pick which Titles to load into order builder
    def init(my):
        nothing = 'true'

    def get_display(my):
        user_name = Environment.get_user_name() 
        expression_lookup = {
            'twog/order': "@SOBJECT(twog/order['code','REPLACE_ME'])",
            'twog/title': "@SOBJECT(twog/title['code','REPLACE_ME'].twog/order)",
            'twog/proj': "@SOBJECT(twog/proj['code','REPLACE_ME'].twog/title.twog/order)",
            'twog/work_order': "@SOBJECT(twog/work_order['code','REPLACE_ME'].twog/proj.twog/title.twog/order)",
            'twog/equipment_used': "@SOBJECT(twog/equipment_used['code','REPLACE_ME'].twog/work_order.twog/proj.twog/title.twog/order)",
            'twog/status_log': "@SOBJECT(twog/order['code','REPLACE_ME'])"
        }
        server = TacticServerStub.get()
        code = my.kwargs.get('code')
        order_code = ''
        order = None
        #Depending on the code of the object passed in (could be a work order, project, title, order, etc), get the order object
        if 'ORDER' in code and 'WORK_ORDER' not in code:
            order_code = code
            o_eval = "@SOBJECT(twog/order['code','%s'])" % code
            order = server.eval(o_eval)
        elif 'WORK_ORDER' in code:
            order = server.eval(expression_lookup['twog/work_order'].replace('REPLACE_ME',code))
        elif 'EQUIPMENT_USED' in code:
            order = server.eval(expression_lookup['twog/equipment_used'].replace('REPLACE_ME',code))
        elif 'PROJ' in code:
            order = server.eval(expression_lookup['twog/proj'].replace('REPLACE_ME',code))
        elif 'TITLE' in code: 
            order = server.eval(expression_lookup['twog/title'].replace('REPLACE_ME',code))
        elif 'STATUS_LOG' in code:
            sobject = server.eval("@SOBJECT(twog/status_log['code','%s'])" % code)[0] 
            o_eval = "@SOBJECT(twog/order['code','%s'])" % sobject.get('order_code')
            order = server.eval(o_eval)
        elif 'PRODUCTION_ERROR' in code:
            wo_code = server.eval("@GET(twog/production_error['code','%s'].work_order_code)" % code)[0]
            order = server.eval(expression_lookup['twog/work_order'].replace('REPLACE_ME',wo_code)) 
        elif 'EXTERNAL_REJECTION' in code:
            sobject = server.eval("@SOBJECT(twog/external_rejection['code','%s'])" % code)[0] 
            o_eval = "@SOBJECT(twog/order['code','%s'])" % sobject.get('order_code')
            order = server.eval(o_eval)
        if order:
            order = order[0]

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
        order_sk = order.get('__search_key__')
        order_code = order.get('code')
        current_titles = ''
        #If a list of title codes is passed in, pre-select them
        if 'allowed_titles' in my.kwargs.keys():
            current_titles = my.kwargs.get('allowed_titles')
        operator_titles = ''
        if 'title_code' in my.kwargs.keys():
            operator_titles = my.kwargs.get('title_code')
        order_name = order.get('name') 
        client_name = 'NO CLIENT SELECTED'
        client_str = "This order CANNOT BE BUILT due to a possible billing issue with CLIENT_NAME.<br/>Please contact 2G's Accounting Dept and let them handle this issue.<br/>PLEASE, DO NOT SPEAK TO THE CLIENT ABOUT THIS ISSUE UNLESS YOU ARE TOLD WHAT TO SAY BY ACCOUNTING.<br/>Thank you."
        client_booking = 'On Hold - Do Not Book'
        show = False
        client_color = '#e31919'
        client_expr = "@SOBJECT(twog/client['code','%s'])" % order.get('client_code')
        client = server.eval(client_expr)
        #Make sure this client isn't blocked from having us do more work for them
        if client:
            client = client[0]
            client_booking = client.get('billing_status')
            client_name = client.get('name')
            if 'Do Not Ship' in client_booking:
                client_color = '#ffaa00'
                client_str = "This order CANNOT BE SHIPPED due to possible billing issues with CLIENT_NAME.<br/>Please contact 2G's Accounting Dept and notify them of this issue.<br/>Go ahead and build the order and put it into production, but make sure the Accounting Dept knows of the issue before setting the classification to 'In Production'.<br/>Lastly, PLEASE DO NOT TELL THE CLIENT ABOUT THIS ISSUE. LET THE ACCOUNTING DEPT HANDLE IT." 
                show = True
            elif 'No Billing Problems' in client_booking:
                client_color = '' 
                client_str = ''
                show = True
        client_str = client_str.replace('CLIENT_NAME',client_name)
        #Get the titles
        titles_expr = "@SOBJECT(twog/title['order_code','%s'])" % order_code
        if not user_is_scheduler and operator_titles not in [None,'']:
            titles_expr = "@SOBJECT(twog/title['code','%s'])" % (operator_titles)
        titles = server.eval(titles_expr)
        widget = DivWdg()
        table = Table()
        table.add_attr('class','allowed_titles_selector')
        table.add_row()
        table.add_cell('<b><u>ORDER NAME: %s</u></b>' % order_name)
        #If a color is set, then there is an issue with the client
        if client_color != '':
            table.add_style('background-color: %s;' % client_color)
            table.add_row()
            topcell = table.add_cell('<b>%s</b>' % client_str)
            topcell.add_attr('nowrap','nowrap')
            topcell.add_attr('colspan','6')
        #If there aren't too man problems with the client, show the selection of titles part
        if show:
            table.add_row()
            table.add_cell(' ')
            display_mode_selector = SelectWdg('display_mode_selector')
            display_mode_selector.add_style('width: 100px;')
            display_mode_selector.append_option('Normal','Normal')
            if user_is_scheduler:
                display_mode_selector.append_option('Quick Edit','Small')
            table.add_cell(display_mode_selector)
            #Toggle behavior sets all checkboxes to selected or not selected

            toggle_behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                            try{
                                var checked_img = '<img src="/context/icons/custom/custom_checked.png"/>'
                                var not_checked_img = '<img src="/context/icons/custom/custom_unchecked.png"/>'
                                var top_el = spt.api.get_parent(bvr.src_el, '.allowed_titles_selector');
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
            # No need for the toggler if there's only 1 title or less
            if len(titles) > 1:
                toggler = CustomCheckboxWdg(name='chk_toggler',additional_js=toggle_behavior,value_field='toggler',id='selection_toggler',checked='true',text='<b><- Select/Deselect ALL</b>',text_spot='right',text_align='left',nowrap='nowrap')

                table.add_row()
                table.add_cell(toggler)
                table.add_cell('&nbsp;&nbsp;&nbsp;')
                table.add_cell('<b>Status</b>')
                table.add_cell('&nbsp;&nbsp;&nbsp;')
                table.add_cell('<b>Client Status</b>')
            # Display the selection list of titles
            for title in titles:
                table.add_row()

                tname = title.get('title')
                if title.get('episode') not in [None,'']:
                    tname = '%s: %s' % (tname, title.get('episode'))

                if title.get('code') in current_titles or current_titles == '':
                    check_val = 'true'
                else:
                    check_val = 'false'
                checkbox = CustomCheckboxWdg(name='allowed_titles_%s' % title.get('code'),value_field=title.get('code'),checked=check_val,text=tname,text_spot='right',text_align='left',nowrap='nowrap',dom_class='title_selector') 

                ck = table.add_cell(checkbox)

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
            #Get the verbiage right
            if len(titles) < 1: 
                go_butt = table.add_cell('<input type="button" class="filter_titles" value="Continue"/>') 
            else:
                nada = table.add_cell(' ')
                go_butt = table.add_cell('<input type="button" class="filter_titles" value="Load"/>') 
            go_butt.add_attr('sk',order_sk)
            go_butt.add_attr('search_type','twog/order')
            go_butt.add_attr('user',user_name)
            behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                            try{
                              var server = TacticServerStub.get();
                              var current_titles = '%s';
                              var my_sk = '%s';
                              var my_user = '%s';
                              var order_name = '%s';
                              var my_code = my_sk.split('code=')[1];
                              var class_name = 'order_builder.order_builder.OrderBuilder';
                              allowed_titles = '';
                              var top_el = spt.api.get_parent(bvr.src_el, '.allowed_titles_selector');
                              display_mode_selector = top_el.getElementsByTagName('select')[0];
                              display_mode = display_mode_selector.value;
                              kwargs = {
                                           'sk': my_sk,
                                           'display_mode': display_mode,
                                           'user': my_user
                              };
                              //get the title codes of the selected checkboxes
                              var checks = top_el.getElementsByClassName('title_selector');
                              for(var r = 0; r < checks.length; r++){
                                  if(checks[r].getAttribute('checked') == 'true'){
                                      title_code = checks[r].getAttribute("name").split('_')[2];
                                      if(allowed_titles == ''){
                                          allowed_titles = title_code;
                                      }else{
                                          allowed_titles = allowed_titles + '|' + title_code;
                                      }
                                  }
                              }
                              kwargs['allowed_titles'] = allowed_titles;
                              if(current_titles == ''){
                                  // Create a new tab for the new order builder
                                  spt.tab.add_new('order_builder_' + my_code, 'Order Builder For ' + order_name, class_name, kwargs);
                              }else{
                                  // Reload the order builder
                                  cover = document.getElementsByClassName('twog_order_builder_cover_' + my_sk)[0];
                                  cover_cell = cover.getElementsByClassName('cover_cell')[0];
                                  spt.api.load_panel(cover_cell, class_name, kwargs); 
    
                              } 
                              //kill this popup
                              spt.popup.close(spt.popup.get_popup(bvr.src_el));
                    }
                    catch(err){
                              spt.app_busy.hide();
                              spt.alert(spt.exception.handler(err));
                    }
             ''' % (current_titles, order_sk, user_name, order_name)}
            go_butt.add_behavior(behavior)
        widget.add(table)
        return widget


class TitleCloneSelectorWdg(BaseTableElementWdg):
    # This allows the uset to select titles to clone and attach to new orders or existing orders
    # Will copy everything (minus unique stuff) from one title and create another exactly like it
    def init(my):
        nothing = 'true'

    def get_clone_here(my, order_code):
        # This just makes it so that the titles can easily be cloned to the same order the user is in currently
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                            order_code = '%s';
                            var top_el = spt.api.get_parent(bvr.src_el, '.clone_titles_selector');
                            order_el = top_el.getElementById('clone_order_name');
                            order_el.value = order_code;
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
        ''' % order_code}
        return behavior
 
    def get_display(my):
        user_name = my.kwargs.get('user')
        code = my.kwargs.get('code')
        sk = my.kwargs.get('sk')

        t_search = Search("twog/title")
        t_search.add_filter('order_code',code)
        titles = t_search.get_sobjects()
        widget = DivWdg()
        table = Table()
        table.add_attr('class','clone_titles_selector')
        # Select all or none
        toggle_behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                            var checked_img = '<img src="/context/icons/custom/custom_checked.png"/>'
                            var not_checked_img = '<img src="/context/icons/custom/custom_unchecked.png"/>'
                            var top_el = spt.api.get_parent(bvr.src_el, '.clone_titles_selector');
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
        # Here need textbox for either an order code to clone to, or if the order code is invalid then create a new order with what is in the textbox as its name
        table2 = Table()
        table2.add_row()
        uto = table2.add_cell('<input type="button" value="Clone to Same Order"/>')
        uto.add_behavior(my.get_clone_here(code))
        table2.add_row()
        # User can enter a new name, which will create a new order with that name and place the clones inside
        # Or user can provide an exiting order code, so the cloned titles will go into that one
        t22 = table2.add_cell('Order Code or New Name:')
        t22.add_attr('nowrap','nowrap')
        namer = table2.add_cell('<input type="text" id="clone_order_name"/>')
        charge_sel = SelectWdg("charge_sel")
        charge_sel.add_style('width: 120px;')
        charge_sel.add_attr('id','charge_sel')
        charges = ['New','Redo','Redo - No Charge']
        # Allow the user to tell us whether this is a normal order, a redo, or a redo with no charge
        for ch in charges:
            charge_sel.append_option(ch,ch)
        table2.add_cell(' Type: ')
        table2.add_cell(charge_sel)
        table2.add_cell('Count: ')
        table2.add_cell('<input type="text" value="1" id="clone_order_count"/>')
        yn = SelectWdg('duplicate_order_vals')
        yn.add_style('width: 100px;')
        yn.append_option('No','No')
        yn.append_option('Yes','Yes')
        tac = table2.add_cell('Duplicate Order Values? ')
        tac.add_attr('nowrap','nowrap')
        table2.add_cell(yn)
        table.add_row()
        ncell = table.add_cell(table2)
        t2b = Table()
        t2b.add_attr('id','t2b')
        # Put the toggler in if there are more than 1 titles
        if len(titles) > 1:
            t2b.add_row()
            toggler = CustomCheckboxWdg(name='chk_clone_toggler',additional_js=toggle_behavior,value_field='toggler',id='selection_toggler',checked='false')

            t2b.add_row()
            t2b.add_cell(toggler)
            t2b.add_cell('<b><- Select/Deselect ALL</b>')
        table.add_row()
        table.add_cell(t2b)
        t3b = Table()
        t3b.add_attr('id','t3b')
        # Display list of titles to choose from
        for title in titles:
            t3b.add_row()
            t3b.add_row()

            tname = title.get_value('title')
            if title.get_value('episode') not in [None,'']:
                tname = '%s: %s' % (tname, title.get_value('episode'))
            checkbox = CustomCheckboxWdg(name='clone_title_%s' % title.get_code(),value_field=title.get_code(),checked='false',text=tname,text_spot='right',text_align='left',nowrap='nowrap',dom_class='title_selector') 

            ck = t3b.add_cell(checkbox)

            cter = t3b.add_cell(' --- Count: ')
            # This is how many clones you want to add of each title
            inser = t3b.add_cell('<input type="text" value="1" id="clone_count_%s" style="width: 40px;"/>' % title.get_code())
        table.add_row()
        table.add_cell(t3b)

        if len(titles) < 1:
            table.add_row()
            table.add_cell('There are no titles in this Order')

        table.add_row()
        go_butt = ''
        if len(titles) > 0: 
            go_butt = table.add_cell('<input type="button" class="clone_titles" value="Clone"/>') 
            go_butt.add_attr('sk',sk)
            go_butt.add_attr('search_type','twog/order')
            go_butt.add_attr('user',user_name)
            behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                            try{
                              var my_sk = '%s';
                              var my_user = '%s';
                              var my_code = my_sk.split('code=')[1];
                              if(confirm("Do You Really Want To Clone These Titles?")){
                                  var server = TacticServerStub.get();
                                  current_order = server.eval("@SOBJECT(twog/order['code','" + my_code + "'])")[0];
                                  var top_el = spt.api.get_parent(bvr.src_el, '.clone_titles_selector');
                                  oname_input = top_el.getElementById('clone_order_name');
                                  oname = oname_input.value;
                                  charge_type_el = top_el.getElementById('charge_sel');
                                  charge_type = charge_type_el.value;
                                  redo = false;
                                  no_charge = false;
                                  if(charge_type.indexOf('Redo') != -1){
                                      redo = true;
                                      if(charge_type.indexOf('No Charge') != -1){
                                          no_charge = true;
                                      }
                                  }
                                  clone_order_count = top_el.getElementById('clone_order_count').value;
                                  if(isNaN(clone_order_count)){
                                      alert("'" + clone_order_count + "' is not a number. Proceeding as if you entered '1' for the number of orders to create.");
                                      clone_order_count = 1;
                                  }else{
                                      clone_order_count = Number(clone_order_count);
                                  }
                                  proceed = true;
                                  clone_type = '';
                                  that_order = null;
                                  new_order = false;
                                  new_order_codes = '';
                                  duplicate = false;
                                  if(oname == '' || oname == null){
                                      //Just an alert to remind them they have to tell us where the title clones should go
                                      alert("You must enter an existing order code or a new order name to put the cloned titles in");
                                      proceed = false;
                                  //}else if(oname.indexOf('ORDER') != -1){
                                  }else if(/^ORDER([0-9]{5,})$/.test(oname)){
                                      //If "ORDER" is in the name, assume that it is actually an order code
                                      if(clone_order_count != 1){
                                          alert("You have indicated that you want these clones to go into " + clone_order_count + " new orders. However, we can't do that if you are specifying an order as well (" + oname + "). Please fix this and then try again."); 
                                          proceed = false;
                                      }
                                      that_order = server.eval("@SOBJECT(twog/order['code','" + oname + "'])");
                                      if(that_order.length == 1 && proceed){
                                          that_order = that_order[0];
                                          new_order_codes = that_order.code;
                                          proceed = true;
                                          clone_type = that_order.name + ' (' + that_order.code + ')';
                                          alert("Cloning the selected titles to " + that_order.name + "(" + that_order.code + ")");
                                      }else{
                                          //Only proceed if we could find the order they wanted to attach the title clones to
                                          proceed = false;
                                          alert("Could not find the Order with code '" + oname + "'");
                                      }
                                  }else if(proceed){
                                      yes_no_els = top_el.getElementsByTagName('select');
                                      for(var xp = 0; xp < yes_no_els.length; xp++){
                                          if(yes_no_els[xp].getAttribute('name') == 'duplicate_order_vals'){
                                              if(yes_no_els[xp].value == 'Yes'){
                                                  duplicate = true;
                                              }
                                          }
                                      }
                                      packet = {'client_code': current_order.client_code, 'client_name': current_order.client_name, 'classification': 'Bid', 'no_charge': no_charge, 'redo': redo, 'login': my_user};
                                      if(duplicate){
                                          packet['sap_po'] = current_order.sap_po;
                                          packet['sales_rep'] = current_order.sales_rep;
                                          packet['platform'] = current_order.platform;
                                          packet['client_rep'] = current_order.client_rep;
                                          packet['sales_rep'] = current_order.sales_rep;
                                          packet['start_date'] = current_order.start_date;
                                          packet['due_date'] = current_order.due_date;
                                          packet['expected_delivery_date'] = current_order.expected_delivery_date;
                                          packet['expected_price'] = current_order.expected_price;
                                      }
                                      for(var dr = 1; dr < clone_order_count + 1; dr++){
                                          new_name = oname + ' ' + dr;
                                          clone_type = 'New Order: ' + oname;
                                          if(clone_order_count == 1){
                                              new_name = oname;
                                              clone_type = 'New Orders (' + clone_order_count + '): ' + oname;
                                          }
                                          packet['name'] = new_name;
                                          that_order = server.insert('twog/order', packet);
                                          proceed = true;
                                          new_order = true;
                                          if(new_order_codes == ''){
                                              new_order_codes = that_order.code;
                                          }else{
                                              new_order_codes = new_order_codes + ',' + that_order.code;
                                          }
                                      }
                                  }
                                  if(proceed){
                                      //Good to go...
                                      clone_titles = [];
                                      checks = top_el.getElementsByClassName('title_selector');
                                      for(var r = 0; r < checks.length; r++){
                                          //see which titles will be cloned, and which ones will not
                                          title_code = checks[r].getAttribute('value_field');
                                          if(checks[r].getAttribute('checked') == 'true'){
                                              clone_titles.push(title_code)
                                          }
                                      }
                                      //Get number of times per selected title that we want to clone each title
                                      counters = {};
                                      for(var r = 0; r < clone_titles.length; r++){
                                          this_count_el = top_el.getElementById('clone_count_' + clone_titles[r]);
                                          ccount = this_count_el.value;
                                         
                                          if(!isNaN(ccount)){
                                              //If it is a number, give it that number
                                              counters[clone_titles[r]] = this_count_el.value;
                                          }else{
                                              //If it isn't a number, just assume the user wants to clone it once
                                              counters[clone_titles[r]] = '1';
                                              alert(clone_titles[r] + "'s " + ccount + " is not a number. Will clone only once.");
                                          }
                                          
                                      }
                                      
                                      if(confirm("Are You Sure You Want To Clone These " + clone_titles.length + " Titles to " + clone_type + "?")){
                                          title_str = '';
                                          //Create string like "TITLE12345[10],TITLE23456[2]" to pass to the TitleClonerCmd
                                          //Bracketed items are the number of times to clone the title
                                          for(var r = 0; r < clone_titles.length; r++){
                                              title_code = clone_titles[r];
                                              if(title_str == ''){
                                                  title_str = title_code + '[' + counters[title_code] + ']';
                                              }else{
                                                  title_str = title_str  + ',' + title_code + '[' + counters[title_code] + ']';
                                              }
                                          }
                                          spt.app_busy.show("Creating Clones...");

                                          //Here send the order and title info to the cloner wdg
                                          copy_attributes = 'false'
                                          if(duplicate){
                                              copy_attributes = 'true';
                                          }
                                          kwargs = {'order_code': new_order_codes, 'titles': title_str, 'user_name': my_user, 'no_charge': no_charge, 'redo': redo, 'copy_attributes': copy_attributes};
                                          //now send to the cloning process
                                          thing = server.execute_cmd('manual_updaters.TitleClonerCmd', kwargs);
                                          if(clone_order_count == 1){
                                              //Here load a new tab with the order getting the clones
                                              var class_name = 'order_builder.order_builder.OrderBuilder';
                                              kwargs = {
                                                       'sk': that_order.__search_key__,
                                                       'user': my_user
                                              };
                                              spt.tab.add_new('order_builder_' + that_order.code, 'Order Builder For ' + that_order.name, class_name, kwargs);
                                          }else{
                                              alert("Please reload your list of orders in the order view. You will see your " + clone_order_count + " new cloned orders there.");
                                          }
                                          spt.popup.close(spt.popup.get_popup(bvr.src_el));
                                          spt.app_busy.hide();
                                      }else{
                                          if(new_order && clone_order_count == 1){
                                              server.retire_sobject(that_order.__search_key__);
                                          }else if(clone_order_count > 1){
                                              code_split = new_order_codes.split(',');
                                              for(var ww = 0; ww < code_split.length; ww++){
                                                 server.retire_sobject(server.build_search_key('twog/order', code_split[ww]));
                                              }
                                          }
                                      }

                                  }
                              }
                    }
                    catch(err){
                              spt.app_busy.hide();
                              spt.alert(spt.exception.handler(err));
                              //alert(err);
                    }
             ''' % (sk, user_name)}
            #Add the clone behavior
            go_butt.add_behavior(behavior)
        widget.add(table)

        return widget

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

class TitleProjStatusTriggerWdg(BaseTableElementWdg):
    #Allows the user to select which projects should have status triggers turned on, and which should not

    def init(my):
        nothing = 'true'

    def set_status_triggers(my, code):
        behavior = {'css_class': 'change', 'type': 'change', 'cbjs_action': '''
                        try{
                            code = '%s';
                            st = 'twog/title';
                            if(code.indexOf('TITLE') == -1){
                                //Then it is a project
                                st = 'twog/proj';
                            }
                            new_val = bvr.src_el.value;
                            server = TacticServerStub.get();
                            dude_sk = server.build_search_key(st, code);
                            //Update the project
                            server.update(dude_sk, {'status_triggers': new_val});
                            if(st == 'twog/title'){
                                //If the select was for the title, apply the change to all of the projects
                                top_el = document.getElementById('title_st_wdg_' + code);
                                other_sels = top_el.getElementsByTagName('select');
                                for(var r = 0; r < other_sels.length; r++){
                                    if(other_sels[r].name.indexOf(code) == -1){
                                        other_sels[r].value = new_val;
                                    }
                                }
                            }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % code}
        return behavior

    def get_display(my):
        server = TacticServerStub.get()
        title_code = my.kwargs.get('title_code')
        # Get the title
        title = server.eval("@SOBJECT(twog/title['code','%s'])" % title_code)[0]
        # Get the projects
        projs = server.eval("@SOBJECT(twog/proj['title_code','%s'])" % title_code)
        widget = DivWdg()
        table = Table()
        table.add_attr('id', 'title_st_wdg_%s' % title_code)
        table.add_row()
        tc = table.add_cell('<b><u>Status Triggers on Title:</u></b> ')
        tc.add_attr('nowrap', 'nowrap')
        # Create a selection for the whole title
        title_sel = SelectWdg("title_st_sel_%s" % title_code)
        title_sel.append_option('Yes', 'Yes')
        title_sel.append_option('No', 'No')
        title_sel.set_value(title.get('status_triggers'),title.get('status_triggers'))
        title_sel.add_behavior(my.set_status_triggers(title_code))
        table.add_cell(title_sel)
        # Create a selection for each project
        for proj in projs:
            table.add_row()
            guy = table.add_cell('&nbsp;&nbsp;&nbsp;%s (%s))' % (proj.get('process'), proj.get('code')))
            guy.add_attr('nowrap', 'nowrap')
            p_sel = SelectWdg('proj_st_sel_%s' % proj.get('code'))
            p_sel.append_option('Yes', 'Yes')
            p_sel.append_option('No', 'No')
            # Preset the value on the select
            p_sel.set_value(proj.get('status_triggers'),proj.get('status_triggers'))
            p_sel.add_behavior(my.set_status_triggers(proj.get('code')))
            table.add_cell(p_sel)

        widget.add(table)
        return widget


class OrderBuilder(BaseRefreshWdg):
    # This is the top level widget, containing the whole order builder
    def init(my):
        my.server = TacticServerStub.get()
        my.sk = ''
        my.code = ''
        my.order_code = ''
        my.sid = ''
        my.allowed_titles_str = ''
        my.allowed_titles = []
        my.user = Environment.get_user_name() 
        my.width = '1000px'
        my.height = '300px'
        my.small = False
        my.disp_mode = 'Normal'
        my.groups_str = ''
        #Get list of groups the user is in. This list will be passed along to other widgets
        #Probably want to rewrite much of the order builder, as many things are passed along as params, like the groups_str, to other classes, although it doesn't need to be this way
        #The sloppiness is due to a few years of adding to, repurposing, and tweaking various classes of the order builder
        my.is_master = False
        my.is_master_str = 'false'

        my.user_group_names = Environment.get_group_names()
        my.user_is_scheduler = False
        my.g_edit_mode = 'view'
        for mg in my.user_group_names:
            if my.groups_str == '':
                my.groups_str = mg
            else:
                my.groups_str = '%s,%s' % (my.groups_str, mg)
        if 'scheduling' in my.groups_str:
            my.user_is_scheduler = True
            my.g_edit_mode = 'edit'
    
    def get_display(my):
        my.sk = str(my.kwargs.get('sk', ''))
        if not my.sk:
            code = my.kwargs.get('code', '')
            my.sk = my.server.build_search_key('twog/order', code)
        my.code = my.sk.split('code=')[1]
        my.order_code = my.code
        sob_expr = "@SOBJECT(twog/order['code','%s'])" % my.code
        #Get the order sobject
        sob = my.server.eval(sob_expr)[0]
        if sob.get('classification') in ['master','Master']:
            my.is_master = True
            my.is_master_str = 'true'
        #I want to do away with the display mode and the QuickEditWdg
        #Need to incorporate functionality of QuickEdit into normal form
        if 'display_mode' in my.kwargs.keys():
            my.disp_mode = my.kwargs.get('display_mode')
        if my.disp_mode == 'Small':
            my.small = True
        if 'allowed_titles' in my.kwargs.keys():
            my.allowed_titles_str = my.kwargs.get('allowed_titles')
            my.allowed_titles = my.allowed_titles_str.split('|')
        else:
            #If a list of allowed_titles was not passed in, just assume all titles should be allowed
            titles = my.server.eval("@GET(twog/title['order_code','%s'].code)" % sob.get('code'))
            my.allowed_titles_str = ''
            for t in titles:
                if my.allowed_titles_str == '':
                    my.allowed_titles_str = t
                else:
                    my.allowed_titles_str = '%s|%s' % (my.allowed_titles_str, t)
            my.allowed_titles = my.allowed_titles_str.split('|')
        #Get the client and make sure we are allowed to do work for them
        client = my.server.eval("@SOBJECT(twog/client['code','%s'])" % sob.get('client_code'))
        client_color = '#e31919'
        client_str = 'DO NOT WORK ON THIS. THERE IS A POTENTIAL BILLING ISSUE WITH THE CLIENT.<br/>PLEASE CONTACT ACCOUNTING. DO NOT TELL THE CLIENT ABOUT THIS, BUT LET ACCOUNTING HANDLE IT'
        client_billing = 'On Hold - Do Not Book'
        if client:
            client = client[0]
            client_billing = client.get('billing_status')
            if 'No Billing Problems' in client_billing:
                client_color = ''
                client_str = ''
            elif 'Do Not Ship' in client_billing:
                client_color = '#ffaa00'
                client_str = "THERE IS A POTENTIAL BILLING ISSUE, WHICH WILL PREVENT DELIVERY OF THE CLIENT'S FINAL DELIVERABLES.<br/>PLEASE CONTACT ACCOUNTING. DO NOT TELL THE CLIENT ABOUT THIS, BUT LET ACCOUNTING HANDLE IT.<br/>PLEASE CONTINUE BUILDING THE ORDER AND SET THE ORDER CLASSIFICATION TO 'In Production' AFTER NOTIFYING ACCOUNTING."
        order_search_id = sob.get('id')
        my.sid = order_search_id
        #These are all of the javascript scripts, in a different class
        #Better for programming (IMHO), but may be worse for loading times???
        #Might want to test speed differences of using this, vs the alternative
        obs = OBScripts(order_sk=my.sk,user=my.user,groups_str=my.groups_str,is_master=my.is_master_str,display_mode=my.disp_mode)
        table = Table()
        table.add_attr('cellspacing', '0')
        table.add_attr('cellpadding', '0')
        table.add_attr('class', 'twog_order_builder twog_order_builder_%s' % my.sk)
        table.add_attr('classification', sob.get('classification'))
        table.add_attr('order_sk', my.sk)
        table.add_attr('pipefocus_class_type', '')
        table.add_attr('pipefocus_sob_sk', '')
        table.add_attr('pipefocus_name', '')
        table.add_attr('allowed_titles', my.allowed_titles_str)
        table.add_attr('is_master_str', my.is_master_str)
        table.add_attr('name', my.code)
        table.add_attr('client', sob.get('client_code'))
        table.add_attr('order_code', my.order_code)
        table.add_attr('groups_str', my.groups_str)
        table.add_attr('user', my.user)
        table.add_attr('is_master', my.is_master)
        table.add_attr('display_mode', my.disp_mode)
        table.add_style('width: 100%;')
        inner_table = Table()
        xrow = inner_table.add_row()
        xrow.add_attr('class', 'closer_row')
        xrow.add_style('display: none;')
        closecell = inner_table.add_cell('CLOSE')
        closecell.add_attr('align','right')
        closecell.add_style('cursor: pointer;')
        closecell.add_behavior(obs.get_close_piper_behavior())
        piperow = inner_table.add_row()
        #Hide the section that contains the pipeline editor
        piperow.add_style('display: none;')
        piperow.add_attr('class', 'pipe_row')
        pipe_editor = ''
        pipecell = inner_table.add_cell(pipe_editor)
        pipecell.add_attr('class','pipe_cell')
        pipecontainerrow = table.add_row()
        pipecontainer = table.add_cell(inner_table)
        if my.small:
            #Again, I hate the QuickEditWdg. It used to be a good idea, but now it is just a waste of time and coding
            quick_edit_wdg = QuickEditWdg(order_sk=my.sk,user=my.user,groups_str=my.groups_str,display_mode=my.disp_mode)
            qe_tbl = Table()
            qe_cell = qe_tbl.add_cell(quick_edit_wdg)
            qe_cell.add_attr('class', 'qe_cell_%s' % my.sk)
            quick_edit_row = table.add_row()
            quick_edit_row.add_attr('class','quick_edit_row_%s' % my.sk)
            quick_edit_row.add_attr('width','100%s' % '%')
            table.add_cell(qe_tbl)
        wholerow = table.add_row()
        wholerow.add_style('width: 100%s' % '%')
        tword = Table()
        show = False
        #If the client str is not empty, then there is something to warn the scheduler about
        if client_str != '':
            tword.add_style('background-color: %s;' % client_color) 
            tword.add_row()
            tcell = tword.add_cell('<b>%s</b>' % client_str)
            tcell.add_attr('nowrap','nowrap')
            if 'Do Not Ship' in client_billing:
                show = True
        else:
            show = True
        tword.add_row()
        #This is the list of buttons on the order builder row
        build_tools = BuilderTools(order_sk=my.sk,groups_str=my.groups_str,user=my.user,display_mode=my.disp_mode,is_master=my.is_master_str)
        tool_cell = tword.add_cell(build_tools)
        tool_cell.add_attr('class','buildtools_%s' % my.sk)
        tool_cell.add_attr('height','100%s' % '%')
        tool_cell.add_attr('valign','top')
        tword.add_row()
        order_obj = None
        div = DivWdg()
        #Give it a scrollbar if there is an overflow
        div.add_style('overflow-y: scroll;')
        div.add_style('height: 1000px;')
        if show:
            #If we are allowed to show the rest, grab the rest here
            order_obj = OrderTable(sk=my.sk,search_id=my.sid,allowed_titles=my.allowed_titles_str,groups_str=my.groups_str,user=my.user,display_mode=my.disp_mode,is_master=my.is_master_str) 
            div.add(order_obj)
        ord_cell = tword.add_cell(div)
        ord_cell.add_attr('i_am','ord_cell')
        ord_cell.add_attr('class', 'cell_%s' % my.sk)
        ord_cell.add_attr('id', 'cell_%s' % my.sk)
        ord_cell.add_attr('call_me', 'The Order')
        ord_cell.add_attr('sk', my.sk)
        ord_cell.add_attr('parent_sk', my.sk)
        ord_cell.add_attr('order_sk', my.sk)
        ord_cell.add_attr('valign','top')
        ord_cell.add_attr('width','100%s' % '%')
        ord_cell.add_style('width: 100%s;' % '%')
        ord_cell.add_style('padding-left: 20px;')
        usns = table.add_cell(tword)
        usns.add_attr('valign','top')
        edit_and_wiki = Table()
        edit_and_wiki.add_attr('class','edit_and_wiki_top')
        edit_and_wiki.add_attr('order_sk',my.sk)
        edit_and_wiki.add_row()
        #Add the edit widget for this sobject to the right side. This will appear for every sobject clicked on.
        edit_wdg = EditWdg(element_name='general', mode=my.g_edit_mode, search_type='twog/order', code=my.code,\
                title='Modify Order',view='edit', widget_key='edit_layout', cbjs_edit_path='builder/refresh_from_save', scroll_height='1000px')
        edit_part = edit_and_wiki.add_cell(edit_wdg)
        edit_part.add_attr('valign','top')
        edit_part.add_attr('name','edit_%s' % my.sk)
        edit_part.add_attr('class', 'edit_%s' % my.sk)
        if my.user_is_scheduler:
            edit_and_wiki.add_row()
            #This will always be called, only appearing when the sobjet has a task tied to it
            task_wdg = TaskEditWdg(task_code='',order_sk=sob.get('__search_key__'),parent_sk='')
            task_part = edit_and_wiki.add_cell(task_wdg)
            task_part.add_attr('class','task_cell')
            task_part.add_attr('valign','top')
            task_part.add_attr('width','100%s' % '%')
        combine_cell = table.add_cell(edit_and_wiki)
        combine_cell.add_attr('valign','top')
        combine_cell.add_attr('width','100%s' % '%')
        cover_table = Table()
        cover_table.add_attr('class','twog_order_builder_cover_%s' % my.sk)
        cover_table.add_row()
        cover_cell = cover_table.add_cell(table)
        cover_cell.add_attr('class','cover_cell')
        return cover_table


class AddWorkOrderWdg(BaseRefreshWdg): 

    def init(my):
        my.proj_sk = ''
        my.proj_code = ''
        my.order_sk = ''

    def get_commit(my, user_name):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        function encode_utf8( s )
                        {
                            return unescape( encodeURIComponent( s ) );
                        }
                        try{
                          var server = TacticServerStub.get();
                          var proj_sk = '%s';
                          var order_sk = '%s';
                          var user_name = '%s';
                          proj_code = proj_sk.split('code=')[1];
                          order_code = order_sk.split('code=')[1];
                          pop_el = document.getElementsByClassName('addwo_' + proj_code)[0];
                          process_el = pop_el.getElementsByClassName('add_wo_process')[0];
                          work_hours_el = pop_el.getElementsByClassName('add_wo_work_hours')[0];
                          instructions_el = pop_el.getElementsByClassName('add_wo_instructions')[0];
                          work_group_el = null;
                          selects = pop_el.getElementsByTagName('select');
                          for(var r = 0; r < selects.length; r++){
                              if(selects[r].name == 'add_wo_work_group'){
                                  work_group_el = selects[r];
                              }
                          }
                          all_filled = true;
                          process = process_el.value;
                          if(process == '' || process == null){
                              all_filled = false;
                          }
                          work_hours = work_hours_el.value;
                          if(work_hours == '' || work_hours == null || Number(work_hours) == 0){
                              all_filled = false;
                          }
                          instructions = instructions_el.value;
                          instructions = encode_utf8(instructions);
                          work_group = work_group_el.value;
                          if(work_group == '--Select--' || work_group == ''){
                              all_filled = false;
                          }  
                          if(all_filled){
                              proj = server.eval("@SOBJECT(twog/proj['code','" + proj_code + "'])")[0];
                              title = server.eval("@SOBJECT(twog/title['code','" + proj.title_code + "'])")[0];
                              order = server.eval("@SOBJECT(twog/order['code','" + order_code + "'])")[0];
                              client_code = title.client_code
                              client = server.eval("@SOBJECT(twog/client['code','" + client_code + "'])");
                              client_name = '';
                              client_hold = 'no problems';
                              if(client.length > 0){
                                  client = client[0];
                                  client_name = client.name;
                                  client_billing_status = client.billing_status;
                                  if(client_billing_status.indexOf('Do Not Book') != -1){
                                      client_hold = 'nobook';
                                  }else if(client_billing_status.indexOf('Do Not Ship') != -1){
                                      client_hold = 'noship';
                                  }
                              }
                              new_wo = server.insert('twog/work_order', {'process': process, 'work_group': work_group, 'instructions': instructions, 'estimated_work_hours': work_hours, 'proj_code': proj_code, 'parent_pipe': 'Manually Inserted into ' + proj.pipeline_code, 'login': user_name, 'creation_type': 'hackup', 'title_code': title.code, 'order_code': order_code, 'client_code': client_code})
                              new_task_data = {'process': process, 'context': process, 'assigned_login_group': work_group, 'active': false, 'client_name': client_name, 'title': title.title, 'episode': title.episode, 'territory': title.territory, 'creator_login': user_name, 'lookup_code': new_wo.code, 'search_type': 'twog/proj?project=twog', 'search_id': proj.id, 'pipeline_code': 'Manually Inserted into ' + proj.pipeline_code, 'po_number': title.po_number, 'status': 'Pending', 'title_code': title.code, 'order_code': order_code, 'client_code': client_code, 'client_hold': client_hold};
                              if(order.classification == 'in_production' || order.classification == 'In Production'){
                                  new_task_data['active'] = true;
                              }
                              new_task = server.insert('sthpw/task', new_task_data);
                              server.update(new_wo.__search_key__, {'task_code': new_task.code}); 
                              
                              kwargs = {'parent_sk': proj_sk, 'order_sk': order_sk, 'user_name': user_name, 'task_sk': new_task.__search_key__, 'new_item_sk': new_wo.__search_key__};
                              spt.panel.load_popup('Connect Work Order To Pipeline', 'order_builder.HackPipeConnectWdg', kwargs); 
                              spt.popup.close(spt.popup.get_popup(bvr.src_el));
                          }else{
                              alert('Please fill in each field correctly.');
                          }
                          
                          
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (my.proj_sk, my.order_sk, user_name)}
        return behavior

    def get_display(my):
        user_name = Environment.get_user_name() 
        my.proj_sk = str(my.kwargs.get('proj_sk'))
        my.proj_code = my.proj_sk.split('code=')[1]
        my.order_sk = str(my.kwargs.get('order_sk'))

        table = Table()
        table.add_attr('class', 'addwo_%s' % my.proj_code)
        group_search = Search("sthpw/login_in_group")
        group_search.add_filter('login', my.user)
        groups = group_search.get_sobjects()
        group_sel = SelectWdg('add_wo_work_group')
        group_sel.append_option('--Select--', '--Select--')
        for group in groups:
            group_sel.append_option(group.get_value('login_group'), group.get_value*('login_group'))
        table.add_row()
        table.add_cell('Process: ')
        table.add_cell('<input type="text" class="add_wo_process"/>')
        table.add_row()
        table.add_cell('Work Group: ')
        table.add_cell(group_sel)
        table.add_row()
        nw = table.add_cell('Estimated Work Hours: ')
        nw.add_attr('nowrap','nowrap')
        table.add_cell('<input type="text" class="add_wo_work_hours"/>')
        table.add_row()
        table.add_cell('Instructions: ')
        table.add_cell('<textarea cols="50" rows="10" class="add_wo_instructions"></textarea>')
        table.add_row()
        table2 = Table()
        table2.add_row()
        t1 = table2.add_cell(' ')
        t1.add_attr('width', '100%')
        button = table2.add_cell('<input type="button" value="Create"/>')
        button.add_behavior(my.get_commit(user_name))
        t2 = table2.add_cell(' ')
        t2.add_attr('width', '100%')
        table.add_cell(' ')
        table.add_cell(table2)

        return table


class AddProjWdg(BaseRefreshWdg):

    def init(my):
        my.title_sk = ''
        my.title_code = ''
        my.order_sk = ''

    @staticmethod
    def get_commit(tsk, osk, user_name):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        function encode_utf8( s )
                        {
                            return unescape( encodeURIComponent( s ) );
                        }
                        try{
                          var server = TacticServerStub.get();
                          var title_sk = '%s';
                          var order_sk = '%s';
                          var user_name = '%s';
                          order_code = order_sk.split('code=')[1];
                          title_code = title_sk.split('code=')[1];
                          pop_el = document.getElementsByClassName('addproj_' + title_code)[0];
                          process_el = pop_el.getElementsByClassName('add_proj_process')[0];
                          specs_el = pop_el.getElementsByClassName('add_proj_specs')[0];
                          process = process_el.value;
                          specs = specs_el.value;
                          all_filled = true;
                          if(all_filled){
                              title = server.eval("@SOBJECT(twog/title['code','" + title_code + "'])")[0];
                              order = server.eval("@SOBJECT(twog/order['code','" + order_code + "'])")[0];
                              client_code = title.client_code
                              client = server.eval("@SOBJECT(twog/client['code','" + client_code + "'])");
                              client_name = '';
                              if(client.length > 0){
                                  client = client[0];
                                  client_name = client.name
                              }
                              new_proj = server.insert('twog/proj', {'process': process, 'specs': specs, 'title_code': title_code, 'parent_pipe': 'Manually Inserted into ' + title.pipeline_code, 'login': user_name, 'creation_type': 'hackup', 'status': 'Pending', 'order_code': order_code, 'client_code': client_code})
                              new_task_data = {'process': process, 'context': process, 'active': false, 'client_name': client_name, 'title': title.title, 'episode': title.episode, 'territory': title.territory, 'creator_login': user_name, 'lookup_code': new_proj.code, 'search_type': 'twog/title?project=twog', 'search_id': title.id, 'pipeline_code': 'Manually Inserted into ' + title.pipeline_code, 'po_number': title.po_number, 'status': 'Pending', 'title_code': title_code, 'order_code': order_code, 'client_code': client_code};
                              if(order.classification == 'in_production' || order.classification == 'In Production'){
                                  new_task_data['active'] = true;
                              }
                              new_task = server.insert('sthpw/task',new_task_data);
                              server.update(new_proj.__search_key__, {'task_code': new_task.code}); 
                              kwargs = {'parent_sk': title_sk, 'order_sk': order_sk, 'user_name': user_name, 'task_sk': new_task.__search_key__, 'new_item_sk': new_proj.__search_key__} 
                              spt.panel.load_popup('Connect Project To Pipeline', 'order_builder.HackPipeConnectWdg', kwargs); 
                              spt.popup.close(spt.popup.get_popup(bvr.src_el));
                          }else{
                              alert('Please fill in each field correctly.');
                          }
                          
                          
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (tsk, osk, user_name)}
        return behavior
    
    def get_display(my):
        user_name = Environment.get_user_name() 
        my.title_sk = str(my.kwargs.get('title_sk'))
        my.title_code = my.title_sk.split('code=')[1]
        my.order_sk = str(my.kwargs.get('order_sk'))
        table = Table()
        table.add_attr('class','addproj_%s' % my.title_code)
        table.add_row()
        table.add_cell('Process: ')
        table.add_cell('<input type="text" class="add_proj_process"/>')
        table.add_row()
        table.add_cell('Specs: ')
        table.add_cell('<input type="text" class="add_proj_specs"/>')
        table.add_row()
        table2 = Table()
        table2.add_row()
        t1 = table2.add_cell(' ')
        t1.add_attr('width', '100%s' % '%')
        button = table2.add_cell('<input type="button" value="Create"/>')
        button.add_behavior(my.get_commit(my.title_sk, my.order_sk, user_name))
        t2 = table2.add_cell(' ')
        t2.add_attr('width', '100%s' % '%')
        table.add_cell(' ')
        table.add_cell(table2)

        return table


class EditHackPipe(BaseRefreshWdg): 

    def init(my):
        my.server = TacticServerStub.get()
        my.sob = None

    @staticmethod
    def get_connect(nsk, psk):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                          var server = TacticServerStub.get();
                          item_sk = '%s';
                          parent_sk = '%s'
                          item_code = item_sk.split('code=')[1];
                          parent_code = parent_sk.split('code=')[1];
                          pop_el = document.getElementsByClassName('hackpipeedit_' + parent_sk)[0];
                          all_inputs = pop_el.getElementsByClassName('hack_in_selector');
                          all_in_checks = [];
                          all_out_checks = [];
                          in_deletions = [];
                          out_deletions = [];
                          in_adds = [];
                          out_adds = [];
                          alert("INPUT LEN = " + all_inputs.length);
                          for(var r = 0; r < all_inputs.length; r++){
                              if(all_inputs[r].getAttribute('name').indexOf('choice') != -1){
                                  c_code = all_inputs[r].getAttribute('code');
                                  c_ino = all_inputs[r].getAttribute('in_or_out');
                                  c_linked = all_inputs[r].getAttribute('linked');
                                  if(c_ino == 'in'){
                                      if(all_inputs[r].getAttribute('checked') == 'true'){
                                          if(c_linked == 'NOPE'){
                                              in_adds.push(c_code);
                                          }
                                      }else{
                                          if(c_linked == 'in'){
                                              in_deletions.push(c_code);
                                          }
                                      }
                                  }
                                  if(c_ino == 'out'){
                                      if(all_inputs[r].getAttribute('checked') == 'true'){
                                          if(c_linked == 'NOPE'){
                                              out_adds.push(c_code);
                                          }
                                      }else{
                                          if(c_linked == 'out'){
                                              out_deletions.push(c_code);
                                          }
                                      }
                                  }
                              } 
                          }
                          spt.app_busy.show('Making the connections...')
                          for(var r = 0; r < in_adds.length; r++){
                              server.insert('twog/hackpipe_out', {'lookup_code': in_adds[r], 'out_to': item_code})
                          } 
                          for(var r = 0; r < out_adds.length; r++){
                              server.insert('twog/hackpipe_out', {'out_to': out_adds[r], 'lookup_code': item_code})
                          } 
                          for(var r = 0; r < in_deletions.length; r++){
                              entry_expr = "@SOBJECT(twog/hackpipe_out['lookup_code','" + in_deletions[r] + "']['out_to','" + item_code + "'])";
                              entry = server.eval(entry_expr);
                              for(var x = 0; x < entry.length; x++){
                                  server.delete_sobject(entry[x].__search_key__);
                              }
                          } 
                          for(var r = 0; r < out_deletions.length; r++){
                              entry_expr = "@SOBJECT(twog/hackpipe_out['out_to','" + out_deletions[r] + "']['lookup_code','" + item_code + "'])";
                              entry = server.eval(entry_expr);
                              for(var x = 0; x < entry.length; x++){ 
                                  server.delete_sobject(entry[x].__search_key__);
                              }
                          } 
                          if(item_code.indexOf('PROJ') != -1){
                              server.insert('twog/simplify_pipe', {'proj_code': item_code});
                          }else{
                              server.insert('twog/simplify_pipe', {'work_order_code': item_code});
                          }
                          spt.popup.close(spt.popup.get_popup(bvr.src_el));
                          spt.app_busy.hide();
                          
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (nsk, psk)}
        return behavior

    @staticmethod
    def get_selector_side(parent_sk, item_code, in_or_out):
        choices = []
        parent_code = parent_sk.split('code=')[1]
        parent_st = parent_sk.split('?')[0]
        parent_search = Search(parent_st)
        parent_search.add_filter('code',parent_code)
        parent_obj = parent_search.get_sobject()
        parent_name = ''
        if 'twog/proj' in parent_sk:
            parent_name = parent_obj.get_value('process')
            wo_search = Search("twog/work_order")
            wo_search.add_filter('proj_code',parent_code)
            wo_search.add_order_by("order_in_pipe")
            wos = wo_search.get_sobjects()

            for wo in wos:
                if wo.get_value('code') != item_code:
                    choices.append([wo.get_value('code'), wo.get_value('process')])
        elif 'twog/title' in parent_sk:
            parent_name = '%s: %s' % (parent_obj.get_value('title'), parent_obj.get_value('episode'))
            proj_search = Search("twog/proj")
            proj_search.add_filter('title_code', parent_code)
            proj_search.add_order_by('order_in_pipe')
            projs = proj_search.get_sobjects()

            for proj in projs:
                if proj.get_value('code') != item_code:
                    choices.append([proj.get_value('code'), proj.get_value('process')])
        entries = []
        hack_search = Search("twog/hackpipe_out")
        if in_or_out == 'in':
            hack_search.add_filter('out_to', item_code)
            hacks = hack_search.get_sobjects()
            for hack in hacks:
                entries.append(hack.get_value('lookup_code'))

        else:
            hack_search.add_filter('lookup_code', item_code)
            hacks = hack_search.get_sobjects()
            for hack in hacks:
                entries.append(hack.get_value('out_to'))

        table = Table()
        table.add_attr('class', 'selector_%s' % in_or_out)
        table.add_row()
        t1 = table.add_cell(in_or_out.upper())
        t1.add_attr('align', 'center')
        if in_or_out == 'in':

            check_val = 'false'
            linked_val = 'NOPE'
            if parent_code in entries:
                linked_val = 'in'
                check_val = 'false'
            else:
                linked_val = 'NOPE'
                check_val = 'true'
            checkbox = CustomCheckboxWdg(name='parent_choice_%s_%s' % (in_or_out, parent_code), value_field=parent_code,
                                         checked=check_val, dom_class='hack_in_selector',
                                         code=parent_code, in_or_out=in_or_out, linked=linked_val)

            table2 = Table()
            table2.add_row()
            table2.add_cell(checkbox)
            nw0 = table2.add_cell('%s [%s]' % (parent_name, parent_code))
            nw0.add_attr('nowrap','nowrap')
            table.add_row()
            table.add_cell(table2)

        table3 = Table()
        for choice in choices:
            table3.add_row()

            linked_val = ''
            check_val = ''
            if choice[0] in entries:
                linked_val = in_or_out
                check_val = 'true'
            else:
                check_val = 'false'
                linked_val = 'NOPE'
            chk = CustomCheckboxWdg(name='child_choice_%s_%s' % (in_or_out, choice[0]),value_field=choice[0],checked=check_val,dom_class='hack_in_selector',code=choice[0],in_or_out=in_or_out,linked=linked_val) 
            table3.add_cell(chk)
            nw = table3.add_cell('%s [%s]' % (choice[1], choice[0]))
            nw.add_attr('nowrap','nowrap')
        table.add_row()
        marge = table.add_cell(table3)
        marge.add_style('padding-left: 20px;')
        contain_tbl = Table()
        contain_tbl.add_row()
        c1 = contain_tbl.add_cell(table)
        c1.add_attr('align','center')
        return contain_tbl
         
    def get_display(my):
        my.code = str(my.kwargs.get('code'))
        parent_sk = ''
        child_st = ''
        child_type = ''
        if 'PROJ' in my.code:
            sob_search = Search("twog/proj")
            sob_search.add_filter('code',my.code)
            my.sob = sob_search.get_sobject()
            parent_sk = my.server.build_search_key('twog/title', my.sob.get_value('title_code'))
            child_st = 'twog/proj'
            child_type = 'Project'
        elif 'WORK_ORDER' in my.code:
            sob_search = Search("twog/work_order")
            sob_search.add_filter('code',my.code)
            my.sob = sob_search.get_sobject()
            parent_sk = my.server.build_search_key('twog/proj', my.sob.get_value('proj_code'))
            child_st = 'twog/work_order'
            child_type = 'Work Order'
        table = Table()
        table.add_attr('class','hackpipeedit_%s' % parent_sk)
        table.add_row()
        left = my.get_selector_side(parent_sk, my.code, 'in')
        right = my.get_selector_side(parent_sk, my.code, 'out')
        table.add_cell(left)
        mtable = Table()
        mtable.add_style('background-color: #e4e4e4;')
        mtable.add_row()
        m1 = mtable.add_cell('%s:' % child_type) 
        m1.add_attr('align','center')
        mtable.add_row()
        m2 = mtable.add_cell('%s [%s]' % (my.sob.get_value('process'), my.sob.get_value('code'))) 
        m2.add_attr('align','center')
        mid = table.add_cell(mtable)
        mid.add_attr('align','right')
        table.add_cell(right)
        table.add_row()
        table.add_cell(' ')
        inner_tbl = Table()
        inner_tbl.add_row()
        i1 = inner_tbl.add_cell(' ')
        i1.add_attr('width','100%s' % '%')
        i2 = inner_tbl.add_cell('<input type="button" value="Connect" />')
        i2.add_behavior(my.get_connect(my.sob.get_search_key(), parent_sk))
        i3 = inner_tbl.add_cell(' ')
        i3.add_attr('width','100%s' % '%')
        c2 = table.add_cell(inner_tbl)
        c2.add_attr('align','center')
        table.add_cell(' ')
        return table

class HackPipeConnectWdg(BaseRefreshWdg): 

    def init(my):
        my.order_sk = ''
        my.parent_sk = ''
        my.new_item_sk = ''
        my.task_sk = ''
        my.user_name = ''

    @staticmethod
    def get_connect(nsk, psk, osk, user_name):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                          var server = TacticServerStub.get();
                          new_item_sk = '%s';
                          parent_sk = '%s'
                          order_sk = '%s';
                          user_name = '%s';
                          item_code = new_item_sk.split('code=')[1];
                          pop_el = document.getElementsByClassName('hackpipeconnect_' + parent_sk)[0];
                          all_inputs = pop_el.getElementsByClassName('hack_in_selector');
                          all_in_checks = [];
                          all_out_checks = [];
                          for(var r = 0; r < all_inputs.length; r++){
                              if(all_inputs[r].getAttribute('name').indexOf('choice') != -1){
                                  if(all_inputs[r].getAttribute('checked') == 'true'){
                                      if(all_inputs[r].getAttribute('in_or_out') == 'in'){
                                          all_in_checks.push(all_inputs[r].getAttribute('code'));
                                      }else if(all_inputs[r].getAttribute('in_or_out') == 'out'){
                                          all_out_checks.push(all_inputs[r].getAttribute('code'));
                                      }
                                  }
                              } 
                          }   
                          spt.app_busy.show('Making the connections...')
                          for(var r = 0; r < all_in_checks.length; r++){
                              server.insert('twog/hackpipe_out', {'lookup_code': all_in_checks[r], 'out_to': item_code})
                          } 
                          for(var r = 0; r < all_out_checks.length; r++){
                              server.insert('twog/hackpipe_out', {'out_to': all_out_checks[r], 'lookup_code': item_code})
                          } 
                          if(item_code.indexOf('PROJ') != -1){
                              server.insert('twog/simplify_pipe', {'proj_code': item_code});
                          }else{
                              server.insert('twog/simplify_pipe', {'work_order_code': item_code});
                          }
                          
                          var top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                          display_mode = top_el.getAttribute('display_mode');
                          user = top_el.getAttribute('user');
                          groups_str = top_el.get('groups_str');
                          allowed_titles = top_el.getAttribute('allowed_titles');
                          parent_el = top_el.getElementsByClassName('cell_' + parent_sk)[0];
                          found_parent_sk = parent_el.get('parent_sk');
                          found_parent_sid = parent_el.get('parent_sid');
                          send_data = {sk: parent_sk, parent_sid: found_parent_sid, parent_sk: found_parent_sk, order_sk: order_sk, user: user, groups_str: groups_str, allowed_titles: allowed_titles, display_mode: display_mode};
                          parent_pyclass = '';
                          if(parent_sk.indexOf('twog/proj') != -1){
                              parent_pyclass = 'ProjRow'
                          }else if(parent_sk.indexOf('twog/title') != -1){
                              parent_pyclass = 'TitleRow'
                          }
                          spt.api.load_panel(parent_el, 'order_builder.' + parent_pyclass, send_data); 
                          spt.popup.close(spt.popup.get_popup(bvr.src_el));
                          spt.app_busy.hide();
                          
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (nsk, psk, osk, user_name)}
        return behavior

    @staticmethod
    def get_selector_side(parent_sk, item_code, in_or_out):
        choices = []
        parent_code = parent_sk.split('code=')[1]
        parent_st = parent_sk.split('?')[0]
        parent_search = Search(parent_st)
        parent_search.add_filter('code', parent_code)
        parent_obj = parent_search.get_sobject()
        parent_name = ''
        if 'twog/proj' in parent_sk:
            parent_name = parent_obj.get_value('process')
            wo_search = Search("twog/work_order")
            wo_search.add_filter('proj_code', parent_code)
            wo_search.add_order_by("order_in_pipe")
            wos = wo_search.get_sobjects()
            for wo in wos:
                if wo.get_value('code') != item_code:
                    choices.append([wo.get_value('code'), wo.get_value('process')])
        elif 'twog/title' in parent_sk:
            parent_name = '%s: %s' % (parent_obj.get_value('title'), parent_obj.get_value('episode'))
            proj_search = Search("twog/proj")
            proj_search.add_filter('title_code', parent_code)
            proj_search.add_order_by('order_in_pipe')
            projs = proj_search.get_sobjects()
            for proj in projs:
                if proj.get_value('code') != item_code:
                    choices.append([proj.get_value('code'), proj.get_value('process')])
             
        table = Table()
        table.add_attr('class','selector_%s' % in_or_out)
        table.add_row()
        t1 = table.add_cell(in_or_out.upper())
        t1.add_attr('align','center')
        if in_or_out == 'in':
            checkbox = CustomCheckboxWdg(name='parent_choice_%s_%s' % (in_or_out, parent_code), value_field=parent_code,
                                         checked='false', dom_class='hack_in_selector', code=parent_code,
                                         in_or_out=in_or_out)
            table2 = Table()
            table2.add_row()
            table2.add_cell(checkbox)
            nw0 = table2.add_cell('%s [%s]' % (parent_name, parent_code))
            nw0.add_attr('nowrap', 'nowrap')
            table.add_row()
            table.add_cell(table2)

        table3 = Table()
        for choice in choices:
            table3.add_row()

            chk = CustomCheckboxWdg(name='child_choice_%s_%s' % (in_or_out, choice[0]), value_field=choice[0],
                                    checked='false', dom_class='hack_in_selector', code=choice[0], in_or_out=in_or_out)
            table3.add_cell(chk)
            nw = table3.add_cell('%s [%s]' % (choice[1], choice[0]))
            nw.add_attr('nowrap','nowrap')
        table.add_row()
        marge = table.add_cell(table3)
        marge.add_style('padding-left: 20px;')
        contain_tbl = Table()
        contain_tbl.add_row()
        c1 = contain_tbl.add_cell(table)
        c1.add_attr('align','center')
        return contain_tbl

    def get_display(my):
        my.order_sk = str(my.kwargs.get('order_sk'))
        my.parent_sk = str(my.kwargs.get('parent_sk'))
        my.new_item_sk = str(my.kwargs.get('new_item_sk'))
        my.task_sk = str(my.kwargs.get('task_sk'))
        my.user_name = str(my.kwargs.get('user_name'))
        child_st = my.new_item_sk.split('?')[0]
        new_item_code = my.new_item_sk.split('code=')[1]
        child_type = ''
        if child_st == 'twog/proj': 
            child_type = "Project"
        elif child_st == 'twog/work_order':
            child_type = "Work Order"
        child_search = Search(child_st)
        child_search.add_filter('code',new_item_code)
        child = child_search.get_sobject()
        table = Table()
        table.add_attr('class','hackpipeconnect_%s' % my.parent_sk)
        table.add_row()
        parent_search_type = my.parent_sk.split('?')[0]
        left = my.get_selector_side(my.parent_sk, new_item_code, 'in')
        right = my.get_selector_side(my.parent_sk, new_item_code, 'out')
        table.add_cell(left)
        mtable = Table()
        mtable.add_style('background-color: #e4e4e4;')
        mtable.add_row()
        m1 = mtable.add_cell('New %s:' % child_type) 
        m1.add_attr('align', 'center')
        mtable.add_row()
        m2 = mtable.add_cell('%s [%s]' % (child.get_value('process'), child.get_value('code'))) 
        m2.add_attr('align', 'center')
        mid = table.add_cell(mtable)
        mid.add_attr('align', 'right')
        table.add_cell(right)
        table.add_row()
        table.add_cell(' ')
        inner_tbl = Table()
        inner_tbl.add_row()
        i1 = inner_tbl.add_cell(' ')
        i1.add_attr('width','100%s' % '%')
        i2 = inner_tbl.add_cell('<input type="button" value="Connect" />')
        i2.add_behavior(my.get_connect(my.new_item_sk, my.parent_sk, my.order_sk, my.user_name))
        i3 = inner_tbl.add_cell(' ')
        i3.add_attr('width','100%s' % '%')
        c2 = table.add_cell(inner_tbl)
        c2.add_attr('align','center')
        table.add_cell(' ')
        return table


class DeliverableWdg(BaseRefreshWdg): 

    def init(my):
        my.title_code = ''
        my.order_sk = ''

    def get_display(my):
        my.title_code = str(my.kwargs.get('title_code'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        
        obs = OBScripts(order_sk=my.order_sk)
        delivs_search = Search("twog/work_order_deliverables")
        delivs_search.add_filter('title_code',my.title_code)
        deliverables = delivs_search.get_sobjects()
        overhead = Table()
        overhead.add_attr('class','overhead_%s' % my.title_code)
        table = Table()
        table.add_attr('class','deliverable_lister')
        table.add_attr('title_code',my.title_code)
        table.add_attr('order_sk',my.order_sk)
        table.add_row()
        table.add_cell(' ')
        table.add_cell(' ')
        table.add_cell(' ')
        table.add_cell(' ')
        created = 'Created?'
        if len(deliverables) < 1:
            created = 'No Deliverables'
        sat = table.add_cell(created)
        sat.add_attr('align','center')
        table.add_cell(' ')
        for p in deliverables:
            source_code = p.get_value('deliverable_source_code')
            dvbl_search = Search("twog/source")
            dvbl_search.add_filter('code',source_code)
            dvbl = dvbl_search.get_sobject()
            table.add_row()
            table.add_cell(p.get_value('work_order_code'))
            alabel = table.add_cell('Permanent Element: ')
            alabel.add_attr('align','center')
            see_deets = table.add_cell('<u>%s, %s To: %s</u>' % (p.get_value('name'), dvbl.get_value('source_type'), p.get_value('deliver_to')))
            see_deets.add_attr('nowrap','nowrap')
            see_deets.add_style('cursor: pointer;')
            see_deets.add_behavior(obs.get_open_deliverable_behavior(dvbl.get_value('code'),p.get_value('work_order_code'),my.title_code,'edit'))
            table.add_cell(' ')
            ck = None
            if p.get_value('satisfied') == True:
                ck = table.add_cell('Yes')
            else:
                ck = table.add_cell('No')
            ck.add_attr('align','center')
        overhead.add_row()
        oh_cell = overhead.add_cell(table)
        oh_cell.add_attr('class','deliverable_list_cell')

        return overhead

class IntermediateEditWdg(BaseRefreshWdg): 

    def init(my):
        my.server = TacticServerStub.get()
        my.order_sk = ''
        my.intermediate_code = ''
        my.work_order_code = ''
        my.client_code = ''

    def get_display(my):   
        from tactic.ui.widget import SObjectCheckinHistoryWdg

        my.order_sk = str(my.kwargs.get('order_sk'))
        my.client_code = str(my.kwargs.get('client_code'))
        my.intermediate_code = str(my.kwargs.get('intermediate_code'))
        intermediate_sk = my.server.build_search_key('twog/intermediate_file', my.intermediate_code)
        my.work_order_code = str(my.kwargs.get('work_order_code'))

        edit_wdg = EditWdg(element_name='general', mode='edit', search_type='twog/intermediate_file', code=my.intermediate_code, title='Modify Permanent Element', view='edit', widget_key='edit_layout', cbjs_edit_path='builder/reload_from_inter_save')
        table = Table()
        table.add_attr('class','intermediate_edit_top')
        table.add_attr('order_sk', my.order_sk)
        table.add_attr('work_order_code', my.work_order_code)
        table.add_attr('client_code', my.client_code)
        table.add_row()
        edit_source_cell = table.add_cell(edit_wdg)
        edit_source_cell.add_attr('class','edit_intermediate_cell')
        edit_source_cell.add_attr('valign','top')
        table.add_row()
        
        history = SObjectCheckinHistoryWdg(search_key=intermediate_sk)
        history_cell = table.add_cell(history)
        history_cell.add_attr('class','history_intermediate_cell')
        table.add_row()

        checkin = TwogEasyCheckinWdg(sk=intermediate_sk,code=my.intermediate_code,order_sk=my.order_sk)
        checkin_cell = table.add_cell(checkin)
        checkin_cell.add_attr('class','checkin_intermediate_cell')
        checkin_cell.add_attr('width','100%s' % '%')
        checkin_cell.add_attr('align','center')

        return table

class DeliverableEditWdg(BaseRefreshWdg): 

    def init(my):
        my.server = TacticServerStub.get()
        my.title_code = ''
        my.order_sk = ''
        my.deliverable_source_code = ''

    def get_display(my):
        from tactic.ui.widget import SObjectCheckinHistoryWdg
        from source_security_wdg import SourceSecurityEditWdg

        my.title_code = str(my.kwargs.get('title_code'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        my.deliverable_source_code = str(my.kwargs.get('deliverable_source_code'))
        deliverable_sk = my.server.build_search_key('twog/source', my.deliverable_source_code)

        main_search = Search("twog/source")
        main_search.add_filter('code',my.deliverable_source_code)
        main_sob = main_search.get_sobject()

        if main_sob.get_value('high_security'):
            edit_wdg = SourceSecurityEditWdg(source_code=my.deliverable_source_code)
        else:
            edit_wdg = EditWdg(element_name='general', mode='edit', search_type='twog/source', code=my.deliverable_source_code, title='Modify Permanent Element', view='edit', widget_key='edit_layout')
        table = Table()
        table.add_attr('class','deliverable_edit_top')
        table.add_row()
        edit_source_cell = table.add_cell(edit_wdg)
        edit_source_cell.add_attr('class','edit_deliverable_cell')
        edit_source_cell.add_attr('valign','top')
        table.add_row()
        
        history = SObjectCheckinHistoryWdg(search_key=deliverable_sk)
        history_cell = table.add_cell(history)
        history_cell.add_attr('class','history_deliverable_cell')
        table.add_row()

        checkin = TwogEasyCheckinWdg(sk=deliverable_sk,code=my.deliverable_source_code,order_sk=my.order_sk)
        checkin_cell = table.add_cell(checkin)
        checkin_cell.add_attr('class','checkin_deliverable_cell')
        checkin_cell.add_attr('width','100%s' % '%')
        checkin_cell.add_attr('align','center')

        return table


class WorkOrderSourceAddWdg(BaseRefreshWdg): 

    def init(my):
        my.server = TacticServerStub.get()
        my.work_order_sk = ''
        my.work_order_code = '' 
        my.title_code = ''
        my.order_sk = ''

    def get_snapshot_file(my, snapshot_code):
        what_to_ret = ''
        base = '/volumes'
        rel_paths = my.server.get_all_paths_from_snapshot(snapshot_code, mode='relative')
        file_only = ''
        if len(rel_paths) > 0:
            rel_path = rel_paths[0]
            splits = rel_path.split('/')
            if len(splits) < 2:
                splits = rel_path.split('\\')
            file_only = splits[len(splits) - 1]
        return file_only 

    def get_display(my):
        my.work_order_code = str(my.kwargs.get('work_order_code'))
        my.work_order_sk = str(my.kwargs.get('work_order_sk'))
        my.title_code = str(my.kwargs.get('title_code'))
        my.call_me = str(my.kwargs.get('call_me'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        obs = OBScripts(order_sk=my.order_sk)
        src_search = Search("twog/title_origin")
        src_search.add_filter('title_code',my.title_code)
        title_sources = src_search.get_sobjects()
        table = Table()
        table.add_attr('class','wo_src_attacher')
        wsrc_search = Search("twog/work_order_sources")
        wsrc_search.add_filter('work_order_code',my.work_order_code)
        wo_sources = wsrc_search.get_sobjects()
        existing = {}
        wos_lookup = {}
        for wos in wo_sources:
            wosoc = wos.get_value('source_code')
            wosnc = wos.get_value('snapshot_code')
            if wosoc not in existing.keys():
                existing[wosoc] = []
            existing[wosoc].append(wosnc)
            wos_lookup['%s%s%s' % (my.work_order_code,wosoc,wosnc)] = wos.get_search_key()
        for src in title_sources:
            src_code = src.get_value('source_code')
            rsrc_search = Search("twog/source")
            rsrc_search.add_filter('code',src_code)
            real_src = rsrc_search.get_sobject()
            real_id = real_src.get_value('id')
            table.add_row()
            is_checked = ''
            preselected = 'false'
            if src_code in existing.keys():
                is_checked = 'checked="true"' 
                preselected = 'true'
            wos_sk = ''
            if '%s%s' % (my.work_order_code,src_code) in wos_lookup.keys():
                wos_sk = wos_lookup['%s%s' % (my.work_order_code,src_code)] 
            table.add_cell('<input type="checkbox" class="src_add_checks" code="%s" src_code="%s" st="twog/source" preselected="%s" wos_sk="%s" %s/>' % (src_code,src_code,preselected,wos_sk,is_checked))
            table.add_cell('<u>%s</u>' % real_src.get_value('title'))
            snap_search = Search("sthpw/snapshot")
            snap_search.add_filter('search_type','twog/source?project=twog')
            snap_search.add_filter('search_id',real_id)
            snaps = snap_search.get_sobjects()
            
            inner_table = Table()
            for snap in snaps:
                file_only = my.get_snapshot_file(snap.get_value('code'))
                inner_table.add_row()
                checked = ''
                presel = 'false'
                if src_code in existing.keys():
                    if snap.get_value('code') in existing[src_code]:
                        checked = 'checked="true"'
                        presel = 'true'
                wos2_sk = ''
                if '%s%s%s' % (my.work_order_code,src_code,snap.get_value('code')) in wos_lookup.keys():
                    wos2_sk = wos_lookup['%s%s%s' % (my.work_order_code,src_code,snap.get_value('code'))] 
                inner_table.add_cell('<input type="checkbox" class="src_add_checks" code="%s" src_code="%s" st="sthpw/snapshot" preselected="%s" wos_sk="%s" %s/>' % (snap.get_value('code'),src_code,presel,wos2_sk,checked))       
                fo = inner_table.add_cell(file_only)
                fo.add_attr('nowrap','nowrap')
            table.add_row()
            table.add_cell(' ')
            table.add_cell(inner_table) 
            table.add_row()
        save_tbl = Table()
        noth_1 = save_tbl.add_cell(' ')
        noth_1.add_attr('width', '100%')
        save_line = save_tbl.add_cell('<input type="button" value="Commit Changes"/>')
        save_line.add_attr('align', 'center')
        save_line.add_style('cursor: pointer;')
        save_line.add_behavior(obs.get_attach_sources_to_wo_behavior(my.work_order_code, my.work_order_sk, my.call_me))
        noth_2 = save_tbl.add_cell(' ')
        noth_2.add_attr('width', '100%')
        dbl = table.add_cell(save_tbl)
        dbl.add_attr('colspan', '2')

        return table


class TwogEasyCheckinWdg(BaseRefreshWdg):
    def init(my):
        my.code = ''
        my.sk = ''
        my.source_contexts = []
        my.order_sk = ''

    def get_display(my):
        from pyasm.prod.biz import ProdSetting
        my.code = str(my.kwargs.get('code'))
        my.sk = str(my.kwargs.get('sk'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        my.source_contexts = ProdSetting.get_value_by_key('source_contexts').split('|')
        obs = OBScripts(order_sk=my.order_sk)
        table = Table()
        table.add_attr('class','twog_easy_checkin')
        table.add_attr('width','100%s' % '%')
        table.add_row()
        title_bar = table.add_cell('<b><u>Checkin New File</u></b>')
        title_bar.add_attr('align','center')
        title_bar.add_attr('colspan','4')
        title_bar.add_style('font-size: 110%ss' % '%')
        processes_sel = SelectWdg('source_process_select')
        for ctx in my.source_contexts:
            processes_sel.append_option(ctx,ctx)
        table.add_row()
        mini0 = Table()
        mini0.add_row()
        mini0.add_cell('Checkin Context: ')
        mini0.add_cell(processes_sel)
        table.add_cell(mini0)
        mini1 = Table()
        mini1.add_row()
        file_holder = mini1.add_cell(' ')
        file_holder.add_attr('width','100%s' % '%')
        file_holder.add_attr('align','center')
        file_holder.add_attr('class','file_holder')
        button = mini1.add_cell('<input type="button" value="Browse"/>')
        button.add_attr('align','right')
        button.add_style('cursor: pointer;')
        button.add_behavior(obs.get_easy_checkin_browse_behavior())
        big_button = mini1.add_cell('<input type="button" value="Check In" class="easy_checkin_commit" disabled/>')
        big_button.add_style('cursor: pointer;')
        big_button.add_behavior(obs.get_easy_checkin_commit_behavior(my.sk))
        table.add_cell(mini1)

        return table
    
class OutsideBarcodesListWdg(BaseRefreshWdg):
    def init(my):
        my.source_code = ''
        my.order_sk = ''

    def get_display(my):
        if 'order_sk' in my.kwargs.keys():
            my.order_sk = str(my.kwargs.get('order_sk'))
        if 'source_code' in my.kwargs.keys():
            my.source_code = str(my.kwargs.get('source_code'))
        table = Table()
        obc_row = table.add_row()
        obc_row.add_attr('class','obc_row')
        if my.source_code not in [None,'']:
            obc_row.add_style('display: table-row;')
        else:
            obc_row.add_style('display: none;') # Change to none
         
        obs = OBScripts(order_sk=my.order_sk)
        obc = Table()
        obc.add_attr('class','outside_barcodes_list')
        obc.add_row()
        ob1 = obc.add_cell('<b><u>Outside Barcodes</u></b>')
        ob1.add_attr('align','center')
        client_search = Search("twog/client")
        client_search.add_order_by('name desc')
        clients = client_search.get_sobjects()
        client_sel = '<select class="REPLACE_ME" out_code="OUT_CODE"><option value="">--Select--</option>'
        for client in clients:
            client_sel = '%s<option value="%s">%s</option>' % (client_sel, client.get_value('code'), client.get_value('name'))
        client_sel = '%s</select>' % client_sel
        out_count = -1
        if my.source_code not in [None,'']:
            out_search = Search("twog/outside_barcode")
            out_search.add_filter('source_code',my.source_code)
            outsiders = out_search.get_sobjects()
            out_count = len(outsiders)
            if out_count == 0:
                out_count = -1
            this_count = 0
            for out in outsiders:
                obc.add_row()
                barcode_text_wdg = TextWdg('outside_barcode_insert_%s' % this_count)
                barcode_text_wdg.set_value(out.get_value('barcode'))
                obc.add_cell(barcode_text_wdg)
                new_sel = client_sel
                new_sel = new_sel.replace('REPLACE_ME','outside_client_%s' % this_count)
                new_sel = new_sel.replace('OUT_CODE',out.get_value('code'))
                new_sel = new_sel.replace('value="%s"' % out.get_value('client_code'), 'value="%s" selected="selected"' % out.get_value('client_code'))
                obc.add_cell(new_sel)
                this_count += 1
                
        additional_count = [0, 1, 2, 3, 4, 5]
        for n in additional_count:
            if n > out_count:
                obc.add_row()
                barcode_text_wdg = TextWdg('outside_barcode_insert_%s' % n)
                obc.add_cell(barcode_text_wdg)
                new_sel = client_sel
                new_sel = new_sel.replace('REPLACE_ME','outside_client_%s' % n)
                new_sel = new_sel.replace('OUT_CODE','')
                obc.add_cell(new_sel)
        obc.add_row()
        widhun = obc.add_cell()
        widhun.add_style('width: 100%;')
        create_butt = obc.add_cell('<input type="button" value="Assign"/>')
        create_butt.add_behavior(obs.get_save_outside_barcodes_behavior(my.source_code))
        widhun = obc.add_cell()
        widhun.add_style('width: 100%;')
        table.add_cell(obc)

        return table

class NewSourceWdg(BaseRefreshWdg):
    def init(my):
        my.server = TacticServerStub.get()
        my.source_code = ''
        my.order_sk = ''

    def get_display(my):
        default = {}
        if 'order_sk' in my.kwargs.keys():
            my.order_sk = str(my.kwargs.get('order_sk'))
        if 'clone' in my.kwargs.keys():
            if str(my.kwargs.get('clone')) in [True,'true','True',1]:
                source_code = str(my.kwargs.get('source_code')) 
                parent_source = my.server.eval("@SOBJECT(twog/source['code','%s'])" % source_code)[0]
                default['parent_source_code'] = parent_source.get('code')
                user_name = str(my.kwargs.get('user_name'))
                default['login'] = user_name
                for el in parent_source.keys():
                    if el not in ['id','code','barcode','client_asset_id','inhouse_location','location','login','timestamp','parent_source_code']:
                        if el.find('strat2g') == -1:
                            default[el] = parent_source.get(el)
        barcoder = Barcoder()
        default['barcode'] = barcoder.get_new_barcode('false') 
        if my.source_code == None:
            my.source_code = ''
        tables = Table()
        tables.add_attr('class','yo_daddy_source_add')
        tables.add_row()
        table = Table()
        table.add_attr('class','ob_source_add')
        table.add_attr('source_code',my.source_code)
        mode = 'insert'
        insert_path = 'builder/source_add'
        if my.source_code != '':
            mode = 'edit'
            insert_path = ''
        insert_wdg = EditWdg(element_name='general', mode=mode, search_type='twog/source',\
                title='Create Source',view=mode, widget_key='edit_layout', default=default, cbjs_insert_path=insert_path)
        table.add_row()
        edit_part = table.add_cell(insert_wdg)
        edit_part.add_attr('class','edit_part_sadd')
        obc = OutsideBarcodesListWdg(order_sk=my.order_sk, source_code=my.source_code)
        table.add_row()
        obc_cell = table.add_cell(obc) 
        obc_cell.add_attr('class','obc_cell')
        tables.add_cell(table)

        return tables
 
class SourceEditWdg(BaseRefreshWdg): 

    def init(my):
        my.server = TacticServerStub.get()
        my.title_sk = ''
        my.title_code = '' 
        my.code = ''
        my.sk = ''
        my.order_sk = ''

    def get_display(my):
        from tactic.ui.widget import SObjectCheckinHistoryWdg
        from source_cloner import SourceCloneLauncherWdg
        from source_security_wdg import SourceSecurityEditWdg

        my.code = str(my.kwargs.get('code'))
        my.sk = my.server.build_search_key('twog/source', my.code)
        my.order_sk = str(my.kwargs.get('order_sk'))
        main_obj = my.server.eval("@SOBJECT(twog/source['code','%s'])" % my.code)[0]

        if not main_obj.get('high_security'):
            edit_wdg = EditWdg(element_name='general', mode='edit', search_type='twog/source', code=my.code, title='Modify Source',view='edit', widget_key='edit_layout')
        else:
            edit_wdg = SourceSecurityEditWdg(source_code=my.code)
        table = Table()
        table.add_attr('class','source_edit_top')
        table.add_row()
        cloner = SourceCloneLauncherWdg(source_code=my.code)
        table.add_cell(cloner)
        table.add_row()
        edit_source_cell = table.add_cell(edit_wdg)
        edit_source_cell.add_attr('class','edit_source_cell')
        edit_source_cell.add_attr('valign','top')
        table.add_row()
        obc = OutsideBarcodesListWdg(order_sk=my.order_sk, source_code=my.code)
        table.add_cell(obc)
        table.add_row()
        
        history = SObjectCheckinHistoryWdg(search_key=my.sk)
        history_cell = table.add_cell(history)
        history_cell.add_attr('class','history_source_cell')
        table.add_row()

        checkin = TwogEasyCheckinWdg(sk=my.sk,code=my.code,order_sk=my.order_sk)
        checkin_cell = table.add_cell(checkin)
        checkin_cell.add_attr('class', 'checkin_source_cell')
        checkin_cell.add_attr('width', '100%')
        checkin_cell.add_attr('align', 'center')

        return table


class ProjDueDateChanger(BaseRefreshWdg): 

    def init(my):
        nothing = True

    @staticmethod
    def get_change_dates_behavior(proj_code, proj_name, order_sk, send_wdg):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                           var server = TacticServerStub.get();
                           proj_code = '%s';
                           proj_name = '%s';
                           order_sk = '%s';
                           send_wdg = '%s';
                           proj_sk = server.build_search_key('twog/proj', proj_code);
                           pop_top = document.getElementsByClassName('due_date_change_proj_' + proj_code)[0];
                           inputs = pop_top.getElementsByTagName('input');
                           new_due_el = '';
                           for(var r = 0; r < inputs.length; r++){
                               if(inputs[r].getAttribute('name') == 'due_date_calendar'){
                                   new_due_el = inputs[r];
                               }
                           }
                           reload_wos = []
                           if(new_due_el != ''){
                               new_due = new_due_el.value;
                               server.update(proj_sk, {'due_date': new_due});
                           }
                           if(send_wdg == 'OrderBuilder'){
                               wos = server.eval("@SOBJECT(twog/work_order['proj_code','" + proj_code + "'])");
                               for(var x = 0; x < wos.length; x++){
                                   reload_wos.push(wos[x].__search_key__);
                               }
                               top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                               display_mode = top_el.getAttribute('display_mode');
                               user = top_el.getAttribute('user');
                               groups_str = top_el.get('groups_str');
                               allowed_titles = top_el.getAttribute('allowed_titles');
                               for(var r = 0; r < reload_wos.length; r++){
                                   wo_el = top_el.getElementsByClassName('cell_' + reload_wos[r])[0];
                                   sk = wo_el.get('sk');
                                   parent_sk = wo_el.get('parent_sk');
                                   parent_sid = wo_el.get('parent_sid');
                                   spt.api.load_panel(wo_el, 'order_builder.WorkOrderRow', {'sk': sk, 'parent_sk': parent_sk, 'order_sk': order_sk, 'parent_sid': parent_sid, display_mode: display_mode, user: user, groups_str: groups_str, allowed_titles: allowed_titles}); 
                                } 
                           }else if(send_wdg == 'OperatorView'){
                               alert('Done Setting Due Date(s)');     
                           }
                          spt.popup.close(spt.popup.get_popup(bvr.src_el));
                           
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (proj_code, proj_name, order_sk, send_wdg)}
        return behavior

    def get_display(my):
        proj_code = str(my.kwargs.get('proj_code'))
        proj_name = str(my.kwargs.get('proj_name'))
        order_sk = str(my.kwargs.get('order_sk'))
        send_wdg = str(my.kwargs.get('send_wdg'))

        calendar = CalendarInputWdg('due_date_calendar')
        calendar.set_option('show_time', 'true')
        calendar.set_option('show_activator', 'true')
        calendar.set_option('display_format', 'MM/DD/YYYY HH:MM')
        calendar.set_option('time_input_default', '5:00 PM')
        proj_search = Search("twog/proj")
        proj_search.add_filter('code',proj_code)
        proj = proj_search.get_sobject()
        if proj.get_value('due_date') not in [None,'']:
            calendar.set_option('default', fix_date(proj.get_value('due_date')))
        table = Table()
        table.add_attr('class', 'due_date_change_proj_%s' % proj_code)
        table.add_row()
        table.add_cell(calendar)
         
        inner_table = Table()
        inner_table.add_row()
        t1 = inner_table.add_cell(' ')
        t1.add_attr('width', '100%')
        action = inner_table.add_cell('<input type="button" value="Update Due Dates" />')
        action.add_behavior(my.get_change_dates_behavior(proj_code, proj_name, order_sk, send_wdg))
        t2 = inner_table.add_cell(' ')
        t2.add_attr('width', '100%')
        table.add_row()
        table.add_cell(inner_table)

        return table


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
        obs = OBScripts(order_sk=my.order_sk)
        table = Table()
        table.add_attr('class','intermediate_passin_add_wdg')
        wos_search = Search("twog/work_order")
        wos_search.add_filter('proj_code',my.proj_code)
        wos_search.add_filter('code',my.work_order_code, op="!=")
        wos_search.add_order_by('order_in_pipe')
        all_wos = wos_search.get_sobjects()
        all_wo_is = []
        for a in all_wos:
            wi_search = Search("twog/work_order_intermediate")
            wi_search.add_filter('work_order_code',a.get_value('code'))
            wo_inters = wi_search.get_sobjects()
            for woi in wo_inters:
                int_search = Search("twog/intermediate_file")
                int_search.add_filter('code',woi.get_value('intermediate_file_code'))
                inter = int_search.get_sobject()
                all_wo_is.append([a.get_value('code'), woi.get_value('code'), woi.get_value('title'), '%s: %s' % (inter.get_value('title'), inter.get_value('episode')), inter.get_value('code')])
        for b in all_wo_is:
            table.add_row()

            checkbox = CustomCheckboxWdg(name='selecta_perm_%s' % b[1],value_field=b[1],checked='false',dom_class='inter_passin_selector',code=b[1],woi_code=b[1],inter_code=b[4])

            ck = table.add_cell(checkbox)
            ck.add_attr('align','center')
            nw1 = table.add_cell('From Work Order: %s' % b[0])
            nw1.add_attr('nowrap','nowrap')
            table.add_cell(' &nbsp;&nbsp; ')
            nw2 = table.add_cell('Intermediate: %s (%s)' % (b[3], b[2]))
            nw2.add_attr('nowrap','nowrap')
        table.add_row()
        passin_butt = table.add_cell('<input type="button" value="Add As Pass-in(s) to Work Order"/>')
        passin_butt.add_behavior(obs.get_assign_intermediate_passins_behavior(my.work_order_code))

        return table

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
        obs = OBScripts(order_sk=my.order_sk)
        table = Table()
        table.add_attr('class', 'deliverable_passin_add_wdg')
        wo_search = Search("twog/work_order")
        wo_search.add_filter('proj_code',my.proj_code)
        wo_search.add_filter('code',my.work_order_code,op="!=")
        wo_search.add_order_by('order_in_pipe')
        all_wos = wo_search.get_sobjects()
        all_wo_ds = []
        for a in all_wos:
            deliv_search = Search("twog/work_order_deliverables")
            deliv_search.add_filter("work_order_code",a.get_value('code'))
            wo_delivs = deliv_search.get_sobjects()
            for wod in wo_delivs:
                src_search = Search("twog/source")
                src_search.add_filter('code',wod.get_value('deliverable_source_code'))
                src = src_search.get_sobject()
                all_wo_ds.append([a.get_value('code'), wod.get_value('code'), wod.get_value('name'), '%s: %s' % (src.get_value('title'), src.get_value('episode')), src.get_value('code')])
        for b in all_wo_ds:
            table.add_row()

            checkbox = CustomCheckboxWdg(name='selecta_perm_%s' % b[1],value_field=b[1],checked='false',dom_class='deliverable_passin_selector',code=b[1],wod_code=b[1],src_code=b[4])

            ck = table.add_cell(checkbox)
            ck.add_attr('align','center')
            nw1 = table.add_cell('From Work Order: %s' % b[0])
            nw1.add_attr('nowrap','nowrap')
            table.add_cell(' &nbsp;&nbsp; ')
            nw2 = table.add_cell('Permanent: %s (%s)' % (b[3], b[2]))
            nw2.add_attr('nowrap','nowrap')
        table.add_row()
        passin_butt = table.add_cell('<input type="button" value="Add As Pass-in(s) to Work Order"/>')
        passin_butt.add_behavior(obs.get_assign_deliverable_passins_behavior(my.work_order_code))

        return table

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
        obs = OBScripts(order_sk=my.order_sk)
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
        barcode_wdg.add_behavior(obs.get_switch_by_barcode_behavior(my.work_order_code, my.order_sk, my.client_code))
        switch_table.add_cell(barcode_wdg)
        table.add_row()
        table.add_cell(switch_table)

        clone_table = Table()
        clone_table.add_row()
        nw = clone_table.add_cell('Clone Existing Asset By Barcode: ')
        nw.add_attr('nowrap','nowrap')
        barcode_wdg = TextWdg('barcode_cloner')
        barcode_wdg.add_behavior(obs.get_clone_by_barcode_behavior(my.work_order_code, my.order_sk, my.client_code))
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

class IntermediateFileAddWdg(BaseRefreshWdg): 

    def init(my):
        my.work_order_code = ''
        my.order_sk = ''
        my.client_code = ''
        my.is_master = ''

    def get_display(my):
        my.work_order_code = str(my.kwargs.get('work_order_code'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        my.client_code = str(my.kwargs.get('client_code'))
        my.is_master = str(my.kwargs.get('is_master'))
        table = Table()
        table.add_attr('class','intermediate_file_add_wdg')
        table.add_attr('work_order_code',my.work_order_code)
        table.add_attr('order_sk',my.order_sk)
        table.add_attr('client_code',my.client_code)
        table.add_attr('is_master',my.is_master)
        table.add_row()

        insert_wdg = EditWdg(element_name='general', mode='insert', search_type='twog/intermediate_file', title='Create Intermediate File', view='insert', widget_key='edit_layout', cbjs_insert_path='builder/new_inter_file')
        table.add_cell(insert_wdg)

        return table


class EquipmentUsedAdderWdg(BaseRefreshWdg):
    def init(my):
        my.work_order_sk = ''
        my.work_order_code = ''
        my.client_code = ''
        my.parent_pyclass = 'ProjRow'
        my.parent_sk = ''
        my.order_sk = ''
        my.user = Environment.get_user_name() 
        my.width = '1000px'
        my.height = '300px'
        my.submit_eu = "<input type='button' value='Submit'/>"
    
    def get_display(my):
        my.work_order_sk = str(my.kwargs.get('work_order_sk'))
        my.work_order_code = str(my.kwargs.get('work_order_code'))
        my.client_code = str(my.kwargs.get('client_code'))
        my.parent_sk = str(my.kwargs.get('parent_sk'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        obs = OBScripts(order_sk=my.order_sk)
        eq_search = Search("twog/equipment")
        eq_search.add_order_by('name desc')
        all_equip = eq_search.get_sobjects()
        client_eq_search = Search("twog/equipment_used_templ")
        client_eq_search.add_filter('client_code',my.client_code)
        client_eq_search.add_order_by('name desc')
        all_client_equip = client_eq_search.get_sobjects()
        table = Table()
        table.add_attr('class', 'equipment_used_adder_top_%s' % my.work_order_code)
        table.add_row()
        table.add_cell('Equipment: ')
        puller = SelectWdg('equipment_changer')
        if len(all_equip) > 0:
            puller.append_option('--Select--', 'NOTHINGXsXNOTHING')
            for equip in all_equip:
                puller.append_option(equip.get_value('name'), '%sXsX%s' % (equip.get_value('code'), equip.get_value('name')))
        puller.add_behavior(obs.get_eq_change_behavior(my.work_order_code))
        table.add_cell(puller)

        table.add_row()
        table.add_cell("Client's Template-Used Equipment: ")
        puller2 = SelectWdg('client_eu_changer')
        if len(all_client_equip) > 0:
            puller2.append_option('--Select--', 'NOTHINGXsXNOTHING')
            for equip in all_client_equip:
                puller2.append_option('%s: Quant: %s, Units: %s, Dur: %s' % (equip.get_value('name'), equip.get_value('expected_quantity'), equip.get_value('units'), equip.get_value('expected_duration')), '%sXsX%s' % (equip.get_value('code'), equip.get_value('name')))
        puller2.add_behavior(obs.get_client_eq_change_behavior(my.work_order_code))
        table.add_cell(puller2)

        table.add_row()
        hr = table.add_cell('<hr/>')
        hr.add_attr('colspan','2')
        table.add_row()
        table.add_cell('Name: ')# if name here does not match name in pulldown when submitted, create a new 'equipment' entry out of info in panel
        table.add_cell('<input type="text" class="eu_add_name" style="width: 200px;"/>')
        table.add_row()
        eqt = table.add_cell('Estimated Quantity: ')
        eqt.add_attr('nowrap','nowrap')
        table.add_cell('<input type="text" class="eu_add_quantity" style="width: 200px;"/>')
        table.add_row()
        edt = table.add_cell('Estimated Duration: ')
        edt.add_attr('nowrap','nowrap')
        table.add_cell('<input type="text" class="eu_add_duration" style="width: 200px;"/>')
        units = ['items','mb','gb','tb']
        unit_pull = SelectWdg('eu_add_units')
        unit_pull.append_option('--Select--','NOTHING')
        for unit in units:
            unit_pull.append_option(unit, unit)
        table.add_row()
        table.add_cell('Units: ')
        table.add_cell(unit_pull)
        table.add_row()
        table.add_cell('Description')
        table.add_row()
        desc = table.add_cell('<textarea rows="5" cols="50" class="eu_add_description"></textarea>')
        desc.add_attr('colspan','2')
        table.add_row()
        saver = table.add_cell(my.submit_eu)
        saver.add_attr('colspan','2')
        saver.add_attr('align','right')
        saver.add_behavior(obs.get_eu_submit_behavior(my.work_order_code, my.parent_pyclass))

        return table


class EquipmentUsedMultiAdderWdg(BaseRefreshWdg):
    def init(my):
        my.server = TacticServerStub.get()
        my.work_order_sk = ''
        my.work_order_code = ''
        my.client_code = ''
        my.order_sk = ''
        my.user = Environment.get_user_name() 
        my.width = '1000px'
        my.height = '300px'
        my.submit_eu = "<input type='button' value='Submit'/>"
        my.x_butt = "<img src='/context/icons/common/BtnKill_Black.gif' title='Delete' name='Delete'/>" 
        my.is_master = False
        my.sks = []

    def get_eq(my, sks):
        #THIS NEEDS TO USE TACTIC SERVER STUB, NOT SEARCH, BECAUSE OF KEYS
        qstr = ''
        qq_str = ''
        bunch = {}
        for sk in sks:
            code = sk.split('code=')[1]
            if qstr == '':
                qstr = code
            else:
                qstr = '%s|%s' % (qstr, code)
            if qq_str == '':
                qq_str = "('%s'" % code
            else:
                qq_str = "%s,'%s'" % (qq_str, code)
            qq_str = '%s)' % qq_str
                
        query = "@SOBJECT(twog/equipment_used['work_order_code','in','%s'])" % qstr
        eqs = my.server.eval(query)

        for eq in eqs:
            eq_code = eq.get('equipment_code')
            expected_quan = eq.get('expected_quantity')
            if expected_quan in [None,'']:
                expected_quan = 'MT'
            expected_duration = eq.get('expected_duration')
            if expected_duration in [None,'']:
                expected_duration = 'MT'
            units = eq.get('units')
            if units in [None,'']:
                units = 'MT'
            length = eq.get('length')
            if length in [None,'']:
                length = 'MT'
            delim = '*D3L1M#'
            ident_str = '%s%s%s%s%s%s%s%s%s' % (eq_code, delim, expected_quan, delim, expected_duration, delim, units, delim, length)
            if ident_str not in bunch.keys():
                eq['wo_codes'] = eq.get('work_order_code')
                eq['eq_codes'] = eq.get('code')
                bunch[ident_str] = eq
            else:
                bunch[ident_str]['wo_codes'] = '%s|%s' % (bunch[ident_str]['wo_codes'], eq.get('work_order_code'))
                bunch[ident_str]['eq_codes'] = '%s|%s' % (bunch[ident_str]['eq_codes'], eq.get('code'))
        equipment = []
        for key, val in bunch.iteritems():
            equipment.append(val)   
        return equipment
        
    def get_display(my):   
        mk = my.kwargs
        mkk = mk.keys()
        my.order_sk = str(mk.get('order_sk'))
        order_code = my.order_sk.split('code=')[1]
        if 'work_order_sk' in mkk:
            my.work_order_sk = str(mk.get('work_order_sk'))
            my.work_order_code = my.work_order_sk.split('code=')[1]
        if my.work_order_code == '':
            my.work_order_code = 'MULTIPLE'
            
        order_search = Search("twog/order")
        order_search.add_filter('code',order_code)
        order = order_search.get_sobject()
        order_classification = order.get_value('classification')
        if order_classification in ['master','Master']:
            my.is_master = True
        my.client_code = order.get_value('client_code')
        if 'sks' in mkk:
            sks_str = mk.get('sks')
            my.sks = sks_str.split('|')
        else:
            my.sks = [my.work_order_sk]

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

        obs = OBScripts(order_sk=my.order_sk)
        eq_search = Search("twog/equipment")
        eq_search.add_order_by('name desc')
        all_equip = eq_search.get_sobjects()
        wo_eqs = None
        if len(my.sks) > 0:
            wo_eqs = my.get_eq(my.sks) 
        table = Table()
        table.add_attr('class', 'equipment_used_multi_adder_top_%s' % my.work_order_code)
        table.add_attr('work_order_sk', my.work_order_sk)
        table.add_attr('sks', '|'.join(my.sks))
        table.add_attr('client_code', my.client_code)
        table.add_attr('order_sk', my.order_sk)
        list_table = Table()
        list_table.add_style('cellpadding: 10px;')
        for woeq in wo_eqs:
            list_table.add_row()
            if user_is_scheduler:
                killer = list_table.add_cell(my.x_butt)
                killer.add_attr('wo_codes', woeq.get('wo_codes'))
                killer.add_attr('eq_codes', woeq.get('eq_codes'))
                killer.add_attr('sks', '|'.join(my.sks))
                killer.add_style('cursor: pointer;')
                killer.add_behavior(obs.get_eq_multi_kill_behavior(woeq.get('__search_key__'), woeq.get('name'), my.work_order_code))
            type_eq = ''
            eparent_search = Search("twog/equipment")
            eparent_search.add_filter('code',woeq.get('equipment_code'))
            eq_parent = eparent_search.get_sobjects()
            if eq_parent:
                eq_parent = eq_parent[0]
                type_eq = eq_parent.get_value('type')
                if type_eq == 'Equipment':
                    type_eq = 'EQUIP'
                elif type_eq == 'Storage':
                    type_eq = 'STOR'
                elif type_eq == 'Media':
                    type_eq = 'MEDIA'

            list_table.add_cell('%s:' %  type_eq) #MTM NEED TO PUT EQUIPMENT TYPE IN HERE (MEDIA, STORAGE, ETC)
            name_to_use = woeq.get('name')
            if woeq.get('length') not in [None,'']:
                name_to_use = '%s: %s' % (name_to_use, woeq.get('length'))
            solid1 = list_table.add_cell('<input type="text" value="%s" disabled="disabled" size="40"/>' % name_to_use)
            solid1.add_style('width: 100px;')
            solid2 = list_table.add_cell('<input type="text" value="UNITS: %s" disabled="disabled" style="width: 100px;"/>' % woeq.get('units'))
            solid2.add_style('width: 50px;')
            solid4 = None
            if woeq.get('length') not in [None,'']:
                solid4 = list_table.add_cell('<input type="text" value="LENGTH: %s" disabled="disabled" style="width: 120px;"/>' % woeq.get('length'))
            else:
                if woeq.get('units') in ['mb','gb','tb']:
                    solid4 = list_table.add_cell('<input type="text" value="EST AMT: %s" disabled="disabled" style="width: 120px;"/>' % woeq.get('expected_duration'))
                else:    
                    solid4 = list_table.add_cell('<input type="text" value="EST DUR: %s" disabled="disabled" style="width: 120px;"/>' % woeq.get('expected_duration'))
            solid3 = list_table.add_cell('<input type="text" value="EST QUANT: %s" disabled="disabled" style="width: 120;"/>' % woeq.get('expected_quantity'))
            solid3.add_style('width: 80px;')
        units = ['items','mb','gb','tb']
        table.add_row()
        table.add_cell(list_table)
        ctable = Table()
        ctable.add_row()
        ctable.add_cell(' ')
        ctable.add_cell('Name')
        ctable.add_cell('Length')
        ctable.add_cell('Quantity')
        ctable.add_cell(' ')

        ctable.add_row()
        ctable.add_cell('Media: ')
        media_sel = SelectWdg('media_select')
        media_sel.add_style('width: 370px;')
        media_sel.add_behavior(obs.get_change_length_pull_behavior(my.work_order_code))
        media_sel.append_option('--Select--','NOTHINGXsXNOTHING')
        for eq in all_equip:
            if eq.get_value('type') == 'Media':
                media_sel.append_option(eq.get_value('name'),eq.get_value('code'))
        ctable.add_cell(media_sel)
        len_sel = SelectWdg('media_length')
        len_sel.add_style('width: 77px;')
        len_sel.append_option('Name 1st','NOTHINGXsXNOTHING')
        ctable.add_cell(len_sel)
        ctable.add_cell('<input type="text" class="media_quant" value="1" style="width: 42px;"/>')
        create_media = ctable.add_cell('<input type="button" value="Create"/>')
        create_media.add_behavior(obs.get_add_eq_from_multi_behavior('media',my.work_order_code))

        ctable.add_row()
        ctable.add_cell(' ')
        ctable.add_cell('Name')
        ctable.add_cell('Duration (hrs)')
        ctable.add_cell('Quantity')
        ctable.add_cell(' ')

        ctable.add_row()
        ctable.add_cell('Equip: ')
        equip_sel = SelectWdg('equip_select')
        equip_sel.add_style('width: 370px;')
        equip_sel.append_option('--Select--','NOTHINGXsXNOTHING')
        for eq in all_equip:
            if eq.get_value('type') == 'Equipment':
                equip_sel.append_option(eq.get_value('name'),eq.get_value('code'))
        ctable.add_cell(equip_sel)
        ctable.add_cell('<input type="text" class="equip_duration" style="width: 77px;"/>')
        ctable.add_cell('<input type="text" class="equip_quant" value="1" style="width: 42px;"/>')
        create_equip = ctable.add_cell('<input type="button" value="Create"/>')
        create_equip.add_behavior(obs.get_add_eq_from_multi_behavior('equip',my.work_order_code))

        ctable.add_row()
        ctable.add_cell(' ')
        ctable.add_cell('Name')
        ctable.add_cell('Units')
        ctable.add_cell('Size')
        ctable.add_cell(' ')

        ctable.add_row()
        ctable.add_cell('Storage: ')
        stor_sel = SelectWdg('stor_select')
        stor_sel.add_style('width: 370px;')
        stor_sel.append_option('--Select--','NOTHINGXsXNOTHING')
        for eq in all_equip:
            if eq.get_value('type') == 'Storage':
                stor_sel.append_option(eq.get_value('name'),eq.get_value('code'))
        ctable.add_cell(stor_sel)
        stor_units_sel = SelectWdg('stor_units_select')
        stor_units_sel.add_style('width: 77px;')
        stor_units_sel.append_option('gb','gb')
        stor_units_sel.append_option('tb','tb')
        ctable.add_cell(stor_units_sel)
        ctable.add_cell('<input type="text" class="stor_duration"  style="width: 42px;"/>')
        create_media = ctable.add_cell('<input type="button" value="Create"/>')
        create_media.add_behavior(obs.get_add_eq_from_multi_behavior('stor',my.work_order_code))
        table.add_row()
        table.add_cell(ctable)
        table.add_row()
        tbl2 = Table()
        tbl2.add_row()
        save_changes = tbl2.add_cell('<input type="button" value="Save Changes"/>')
        save_changes.add_behavior(obs.get_save_multi_eq_changes_behavior(my.work_order_code, my.order_sk))
        t22 = tbl2.add_cell(' ')
        t22.add_attr('width','100%s' % '%')
        table.add_cell(tbl2)
        return table


class OperatorErrorDescriptPopupWdg(BaseRefreshWdg): 
    def init(my):
        my.production_error_code = ''

    def get_submit_description_behavior(my, production_error_code): 
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                           var server = TacticServerStub.get();
                           production_error_code = '%s';
                           prod_e_sk = server.build_search_key('twog/production_error', production_error_code);
                           var top_el = document.getElementsByClassName('prod_error_' + production_error_code)[0]; 
                           descript_el = top_el.getElementsByClassName('error_description')[0];
                           description = descript_el.value;
                           if(description != '' && description != null){
                               server.update(prod_e_sk, {'operator_description': description});
                               spt.popup.close(spt.popup.get_popup(bvr.src_el));
                           }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (production_error_code)}
        return behavior

    def get_display(my):   
        my.production_error_code = str(my.kwargs.get('production_error_code'))
        table = Table()
        table.add_attr('class', 'prod_error_%s' % my.production_error_code)
        table.add_row()
        table.add_cell('Please explain what created the error and whatever you think may have contributed to it so we can resolve this issue. Thanks')
        table.add_row()
        table.add_cell('<textarea cols="50" rows="10" class="error_description"></textarea>')
        table.add_row()
        little_table = Table()
        little_table.add_row()
        w1 = little_table.add_cell(' ')
        w1.add_attr('width', '50%')
        action_button = little_table.add_cell('<input type="button" value="Submit"/>')
        action_button.add_behavior(my.get_submit_description_behavior(my.production_error_code))
        w2 = little_table.add_cell(' ')
        w2.add_attr('width', '50%')
        table.add_cell(little_table)
        return table

class ExternalRejectionReasonWdg(BaseRefreshWdg): 
    def init(my):
        my.title_sk = ''
        my.order_k = ''

    def get_submit_description_behavior(my, title_sk, order_sk): 
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                           var server = TacticServerStub.get();
                           title_sk = '%s';
                           order_sk = '%s';
                           var top_el = document.getElementsByClassName('external_reject_' + title_sk)[0]; 
                           //var top_el2 = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                           var top_el2 = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                           descript_el = top_el.getElementsByClassName('rejection_description')[0];
                           description = descript_el.value;
                           if(description != '' && description != null){
                               spt.app_busy.show('Sending Description...');
                               server.update(title_sk, {'is_external_rejection': 'true', 'external_rejection_reason': description});
                               spt.popup.close(spt.popup.get_popup(bvr.src_el));

                               order_sk = top_el2.getAttribute('order_sk');
                               display_mode = top_el2.getAttribute('display_mode');
                               user = top_el2.getAttribute('user');
                               groups_str = top_el2.get('groups_str');
                               is_master_str = top_el2.getAttribute('is_master_str');
                               allowed_titles = top_el2.getAttribute('allowed_titles');
                               title_el = top_el2.getElementsByClassName('cell_' + title_sk)[0];
                               found_parent_sk = title_el.get('parent_sk');
                               found_parent_sid = title_el.get('parent_sid');
                               send_data =  {sk: title_sk, parent_sid: found_parent_sid, parent_sk: found_parent_sk, order_sk: order_sk, display_mode: display_mode, user: user, groups_str: groups_str, allowed_titles: allowed_titles, is_master: is_master_str}; 
                               spt.api.load_panel(title_el, 'order_builder.TitleRow', send_data); 
                               spt.app_busy.hide();
                               
                               title_code = title_sk.split('code=')[1];
                               newest_exter = server.eval("@SOBJECT(twog/external_rejection['title_code','" + title_code + "']['@ORDER_BY','timestamp desc'])")[0];
                               class_name = 'order_builder.ErrorDetailEditWdg';
                               kwargs = {
                                           'code': newest_exter.code
                               };
                               spt.panel.load_popup('Edit Error Information', class_name, kwargs);
                                
                           }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (title_sk, order_sk)}
        return behavior

    def get_display(my):   
        my.title_sk = str(my.kwargs.get('title_sk'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        table = Table()
        table.add_attr('class', 'external_reject_%s' % my.title_sk)
        table.add_row()
        table.add_cell('Please tell us what created the external rejection. Thank you.')
        table.add_row()
        table.add_cell('<textarea cols="50" rows="10" class="rejection_description"></textarea>')
        table.add_row()
        little_table = Table()
        little_table.add_row()
        w1 = little_table.add_cell(' ')
        w1.add_attr('width', '50%')
        action_button = little_table.add_cell('<input type="button" value="Submit"/>')
        action_button.add_behavior(my.get_submit_description_behavior(my.title_sk, my.order_sk))
        w2 = little_table.add_cell(' ')
        w2.add_attr('width', '50%')
        table.add_cell(little_table)
        return table


class TitleRedoWdg(BaseRefreshWdg): 
    def init(my):
        my.title_sk = ''
        my.order_k = ''

    @staticmethod
    def get_submit(title_sk, order_sk):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                           var server = TacticServerStub.get();
                           title_sk = '%s';
                           order_sk = '%s';
                           title_code = title_sk.split('code=')[1];
                           order_code = order_sk.split('code=')[1];
                           var top_el = document.getElementsByClassName('redo_' + title_sk)[0]; 
                           var top_el2 = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                           redo_title_code = top_el.getElementById('redo_title_code');
                           no_charge = top_el.getElementById('no_charge').value;
                           redo_title_code = redo_title_code.value;
                           if(redo_title_code != '' && redo_title_code != null){
                               spt.app_busy.show('Sending Information...');
                               up_dict = {'redo_of_title_code': redo_title_code, 'redo': 'true', 'no_charge': no_charge, 'bigboard': 'true', 'priority': .00000001}
                               tit = server.eval("@SOBJECT(twog/title['code','" + title_code + "'])")[0];
                               if(tit.status == ''){
                                   up_dict['status'] = 'Fixes';
                               }
                               server.update(title_sk, up_dict); 
                               tasks =server.eval("@SOBJECT(sthpw/task['title_code','" + title_code + "'])");
                               for(var r = 0; r < tasks.length; r++){
                                   server.update(tasks[r].__search_key__, {'bigboard': 'true'});
                               }
                               ext_r = server.eval("@SOBJECT(twog/external_rejection['title_code','" + redo_title_code + "']['@ORDER_BY','timestamp desc'])");
                               if(ext_r.length > 0){
                                   server.update(ext_r[0].__search_key__, {'replacement_order_code': order_code, 'replacement_title_code': title_code, 'status': 'Closed'}); 
                               }else{
                                   alert("No External Rejection found with that title code.");
                               }
                               spt.popup.close(spt.popup.get_popup(bvr.src_el));

                               order_sk = top_el2.getAttribute('order_sk');
                               display_mode = top_el2.getAttribute('display_mode');
                               user = top_el2.getAttribute('user');
                               groups_str = top_el2.get('groups_str');
                               is_master_str = top_el2.getAttribute('is_master_str');
                               allowed_titles = top_el2.getAttribute('allowed_titles');
                               title_el = top_el2.getElementsByClassName('cell_' + title_sk)[0];
                               found_parent_sk = title_el.get('parent_sk');
                               found_parent_sid = title_el.get('parent_sid');
                               send_data =  {sk: title_sk, parent_sid: found_parent_sid, parent_sk: found_parent_sk, order_sk: order_sk, display_mode: display_mode, user: user, groups_str: groups_str, allowed_titles: allowed_titles, is_master: is_master_str}; 
                               spt.api.load_panel(title_el, 'order_builder.TitleRow', send_data); 
                               spt.app_busy.hide();
                           }else{
                               alert("Please tell us what code of the previous Title is.");
                           } 
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (title_sk, order_sk)}
        return behavior

    def get_display(my):
        server = TacticServerStub.get()
        my.title_sk = str(my.kwargs.get('title_sk'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        title_obj = server.get_by_search_key(my.title_sk)
        table = Table()
        table.add_attr('class','redo_%s' % my.title_sk)
        table.add_row()
        t1 = table.add_cell('Please enter the Title Code of the Title this is a redo of.')
        t1.add_attr('nowrap','nowrap')
        redo_title_code = TextWdg("redo_title_code")
        redo_title_code.add_attr('id','redo_title_code')
        if title_obj.get('redo_of_title_code') not in [None,'']:
            redo_title_code.set_value(title_obj.get('redo_of_title_code'))
        table.add_cell(redo_title_code)
        table.add_row()
        t2 = table.add_cell("Is this a No-Charge Redo?")
        t2.add_attr('nowrap','nowrap')
        yeah_nah = SelectWdg("no_charge")
        yeah_nah.add_attr('id','no_charge')
        no_charge = 'true'
        if title_obj.get('no_charge') in ['False','false','0',0,False,None]: 
            no_charge = 'false'
        yeah_nah.append_option('No','false')
        yeah_nah.append_option('Yes','true')
        yeah_nah.set_value(no_charge)
        table.add_cell(yeah_nah)
        table.add_row()
        little_table = Table()
        little_table.add_row()
        w1 = little_table.add_cell(' ')
        w1.add_attr('width','50%s' % '%')
        action_button = little_table.add_cell('<input type="button" value="Submit"/>')
        action_button.add_behavior(my.get_submit(my.title_sk, my.order_sk))
        w2 = little_table.add_cell(' ')
        w2.add_attr('width','50%s' % '%')
        table.add_cell(little_table)
        return table

class Barcoder(BaseRefreshWdg):
    def init(my):
        my.server = TacticServerStub.get()
        my.order_sk = ''
        if 'order_sk' in my.kwargs.keys():
            my.order_sk = str(my.kwargs.get('order_sk'))

    def get_new_barcode(my, deliverable):
        new_bc = 'XsXsXsXsX'
        repeat = True
        while repeat:
            last_search = Search("twog/barcode")
            last_search.add_filter('name','The only entry')
            last_bc = last_search.get_sobject()
            last_num = int(last_bc.get_value('number'))
            new_num = last_num + 1
            my.server.update(last_bc.get_search_key(), {'number': new_num})
            new_bc = "2GV%s" % new_num        
            if deliverable == 'true':
                new_bc = "2GV%s" % new_num
            bc_search = Search("twog/source")
            bc_search.add_filter('barcode',new_bc)
            bc_sources = bc_search.get_sobjects()
            if len(bc_sources) < 2:
               repeat = False

        return new_bc  
