__all__ = ["OrderBuilderLauncherWdg", "TitleSelectorWdg", "TitleDuePrioBBWdg", "TitleCloneSelectorWdg",
           "TitleDeletorWdg", "TitleProjStatusTriggerWdg", "OrderBuilder", "QuickEditWdg", "ErrorEntryWdg",
           "OrderTable", "TitleRow", "AddWorkOrderWdg", "AddProjWdg", "EditHackPipe", "HackPipeConnectWdg",
           "TitleSourceInspectorWdg", "DeliverableWdg", "IntermediateEditWdg", "DeliverableEditWdg", "PreReqWdg",
           "WorkOrderSourceAddWdg", "TwogEasyCheckinWdg", "OutsideBarcodesListWdg", "NewSourceWdg", "SourceEditWdg",
           "ProjDueDateChanger", "OutFilesWdg", "SourcePortalWdg", "IntermediatePassinAddWdg",
           "DeliverablePassinAddWdg", "DeliverableAddWdg", "IntermediateFileAddWdg", "TitleAdderWdg",
           "EquipmentUsedAdderWdg", "EquipmentUsedMultiAdderWdg", "OperatorErrorDescriptPopupWdg",
           "ExternalRejectionReasonWdg", "Barcoder", "TitleRedoWdg", "MultiManualAdderWdg"]

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
from order_builder_utils import OBScripts, get_upload_behavior


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

class QuickEditWdg(BaseRefreshWdg):
    #This widget is used to reduce the number of elements loaded in order builder, so loading is faster.
    #It's good for making a lot of changes, especially global changes to selected elements
    #I hate this widget now, and it really doesn't seem to do much for us. Would like to take it out and modify the regular order builder to keep it's good elements
    def init(my):
        my.server = TacticServerStub.get()
        my.order_sk = ''
        my.user = ''
        my.groups_str = ''
        my.disp_mode = ''
        my.is_master = False
        my.is_master_str = 'false'
        my.small = False
        #There is no territory table in Tactic rigt now. We may want to do that in the future
        my.territory_str = 'Afghanistan|Aland Islands|Albania|Algeria|American Samoa|Andorra|Angola|Anguilla|Antigua and Barbuda|Argentina|Armenia|Aruba|Australia|Austria|Azerbaijan|Bahamas|Bahrain|Bangladesh|Barbados|Belarus|Belgium|Belize|Benin|Bermuda|Bhutan|Bolivia|Bonaire|Bosnia and Herzegovina|Botswana|Bouvet Island|Brazil|Brunei Darussalam|Bulgaria|Burkina Faso|Burundi|Cambodia|Cameroon|Canada|Cantonese|Cape Verde|Cayman Islands|Central African Republic|Chad|Chile|China|Christmas Island|Cocos Islands|Colombia|Comoros|Congo|Dem. Rep. of Congo|Cook Islands|Costa Rica|Croatia|Cuba|Curacao|Cyprus|Czech|Denmark|Djibouti|Dominica|Dominican Republic|Ecuador|Egypt|El Salvador|English|Equatorial Guinea|Eritrea|Estonia|Ethiopia|Falkland Islands|Faroe Islands|Fiji|Finland|France|French Guiana|French Polynesia|Gabon|Gambia|Georgia|Germany|Ghana|Gibraltar|Greece|Greek|Greenland|Grenada|Guadeloupe|Guam|Guatemala|Guernsey|Guinea|Guinea-Bissau|Guyana|Haiti|Honduras|Hong Kong|Hungary|Iceland|India|Indonesia|Iran|Iraq|Ireland|Isle of Man|Israel|Italy|Ivory Coast|Jamaica|Japan|Jersey|Jordan|Kazakhstan|Kenya|Kiribati|Kuwait|Kyrgyztan|Laos|Latin America|Latin Spanish|Latvia|Lebanon|Lesotho|Liberia|Libya|Liechtenstein|Lithuania|Luzembourg|Macao|Macedonia|Madagascar|Malawi|Malaysia|Maldives|Mali|Malta|Marshall Islands|Martinique|Mauritania|Mauritius|Mayotte|Mexico|Micronesia|Moldova|Monaco|Mongolia|Montenegro|Montserrat|Morocco|Mozambique|Multi-language|Myanmar|Namibia|Nauru|Nepal|Netherlands|New Caledonia|New Zealand|Nicaragua|Niger|Nigeria|Niue|Norfolk Island|North Korea|Northern Mariana Islands|Norway|Oman|Pakistan|Palau|Palestine|Panama|Papua New Guinea|Pan-Asia|Paraguay|Peru|Philippines|Pitcairn|Poland|Portugal|Puerto Rico|Qatar|Reunion|Romania|Russia|Russian|Rwanda|St Barthelemy|St Helena|St Kitts and Nevis|St Lucia|St Martin|St Pierre and Miquelo|St Vincent and Grenadines|Samoa|San Marino|Sao Tome and Principe|Saudi Arabia|Senegal|Serbia|Seychelles|Sierra Leone|Signapore|Sint Maarten|Slovakia|Slovenia|Solomon Islands|Somalia|South Africa|South Georgia and Swch Islands|South Korea|South Sudan|Spain|Sri Lanka|Sudan|Suriname|Svalbard|Swaziland|Sweden|Switzerland|Syria|Taiwan|Tajikistan|Tanzania|Thai|Thailand|Timor-Leste|Togo|Tokelau|Tonga|Trinidad and Tobago|Tunisia|Turkey|Turkmenistan|Turks and Caicos Islands|Tuvalu|Uganda|Ukraine|UAE|United Kingdom|United States|Uruguay|Uzbekistan|Vanuatu|Various|Vatican|Venezuela|Vietnam|Virgin Islands|Wallis and Futuna|West Indies|Western Sahara|Yemen|Zambia|Zimbabwe'
        #There is no language table in Tactic rigt now. We may want to do that in the future
        my.language_str = 'Abkhazian|Afar|Afrikaans|Akan|Albanian|All Languages|Amharic|Arabic|Arabic - Egypt|Arabic - UAE and Lebanon|Aragonese|Aramaic|Armenian|Assamese|Avaric|Avestan|Aymara|Azerbaijani|Bahasa (Not Specified)|Bashkir|Basque|Belarusian|Bengali|Bihari languages|Bislama|Bosnian|Breton|Bulgarian|Burmese|Catalan|Catalan (Valencian)|Central Khmer|Chamorro|Chechen|Chichewa (Chewa, Nyanja)|Chinese (Cantonese)|Chinese (Mandarin - Not Specified)|Chinese (Mandarin - PRC)|Chinese (Mandarin - Taiwan)|Chinese Simplified Characters|Chinese Simplified Characters - Malaysia|Chinese Simplified Characters - PRC|Chinese Simplified Characters - Singapore|Chinese Traditional Characters|Chinese Traditional Characters - Hong Kong|Chinese Traditional Characters - Taiwan|Chuvash|Cornish|Corsican|Cree|Croatian|Czech|Danish|Dari|Divehi (Dhivehi, Maldivian)|Dutch|Dzongkha|English|English - Australian|English - British|Esperanto|Estonian|Ewe|Faroese|Farsi (Persian)|Fijian|Finnish|Flemish|French (Not Specified)|French - Canadian (Quebecois)|French - France|Fulah|Gaelic (Scottish Gaelic)|Galician|Georgian|German|German - Austrian|German - Swiss/Alsatian|Greek - Modern|Guarani|Gujarati|Haitian (Haitian Creole)|Hausa|Hawaiian|Hebrew|Herero|Hindi|Hiri Motu|Hungarian|Icelandic|Ido|Indonesian Bahasa|Interlingua (International Auxiliary Language Association)|Interlingue (Occidental)|Inuktitut|Inupiaq|Italian|Japanese|Javanese|Kalaallisut (Greenlandic)|Kannada|Kanuri|Kashmiri|Kazakh|Kikuyu (Gikuyu)|Kinyarwanda|Kirghiz (Kyrgyz)|Komi|Kongo|Korean|Kuanyama (Kwanyama)|Kurdish|Lao|Latin|Latvian|Limburgan (Limburger, Limburgish)|Lingala|Lithuanian|Luba-Katanga|Luxembourgish (Letzeburgesch)|MOS (no audio)|Macedonian|Malagasy|Malay Bahasa|Malayalam|Maltese|Maori|Marathi|Marshallese|Mauritian Creole|Mayan|Moldavian|Mongolian|Nauru|Navajo (Navaho)|Ndebele - North|Ndebele - South|Ndonga|Nepali|No Audio|Northern Sami|Norwegian|Occitan|Ojibwa|Oriya|Oromo|Ossetian (Ossetic)|Palauan|Pali|Panjabi (Punjabi)|Polish|Polynesian|Portuguese (Not Specified)|Portuguese - Brazilian|Portuguese - European|Pushto (Pashto)|Quechua|Romanian|Romanian (Moldavian)|Romansh|Rundi|Russian|Samoan|Sango|Sanskrit|Sardinian|Sepedi|Serbian|Serbo-Croatian|Setswana|Shona|Sichuan Yi (Nuosu)|Sicilian|Silent|Sindhi|Sinhala (Sinhalese)|Slavic|Slovak|Slovenian|Somali|Sotho, Sesotho|Spanish (Not Specified)|Spanish - Argentinian|Spanish - Castilian|Spanish - Latin American|Spanish - Mexican|Sudanese|Swahili|Swati|Swedish|Tagalog|Tahitian|Taiwanese (Min Nah)|Tajik|Tamil|Tatar|Telugu|Tetum|Textless|Thai|Tibetan|Tigrinya|Tok Pisin|Tongan|Tsonga|Turkish|Turkmen|Tuvaluan|Twi|Uighur (Uyghur)|Ukrainian|Unavailable|Unknown|Unknown|Urdu|Uzbek|Valencian|Venda|Vietnamese|Volapuk|Walloon|Welsh|Western Frisian|Wolof|Xhosa|Yiddish|Yoruba|Zhuang (Chuang)|Zulu'

    def get_toggle_select_check_behavior(my):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                           var checked_img = '<img src="/context/icons/custom/custom_checked.png"/>'
                           var not_checked_img = '<img src="/context/icons/custom/custom_unchecked.png"/>'
                           order_sk = '%s';
                           top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                           var curr_val = bvr.src_el.getAttribute('checked');
                           image = '';
                           if(curr_val == 'false'){
                               curr_val = false;
                               image = not_checked_img;
                           }else if(curr_val == 'true'){
                               curr_val = true;
                               image = checked_img;
                           }
                           checks = top_el.getElementsByClassName('ob_selector');
                           for(var r = 0; r < checks.length; r++){
                               check_code = checks[r].getAttribute('value_field');
                               parent_table_class = checks[r].getAttribute('parent_table');
                               parent_table = top_el.getElementsByClassName(parent_table_class)[0];
                               new_color = '';
                               if(curr_val){
                                   new_color = checks[r].getAttribute('selected_color');
                               }else{
                                   new_color = checks[r].getAttribute('normal_color');
                               }
                               parent_table.style.backgroundColor = new_color;
                               checks[r].setAttribute('checked',curr_val);
                               checks[r].innerHTML = image;
                           }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (my.order_sk)}
        return behavior

    def get_assigned_group_select(my, assigned, name):
        #Make the select element for groups
        groups_expr = "@GET(sthpw/login_group['login_group','not in','user|client|compression supervisor|edit supervisor|machine room supervisor|media vault supervisor|qc supervisor|sales supervisor|scheduling supervisor|streamz|executives|admin|management|office employees|it'].login_group)"
        groups = my.server.eval(groups_expr)
        group_sel = SelectWdg(name)
        if len(groups) > 0:
            group_sel.append_option('--Select--','')
            if assigned:
                group_sel.set_value(assigned)
            else:
                group_sel.set_value('')
            for group in groups:
                group_sel.append_option(group,group)
        return group_sel

    def get_assigned_select(my, assigned):
        #Make the select element for workers
        workers_expr = "@GET(sthpw/login['location','internal']['license_type','user'].login)"
        workers = my.server.eval(workers_expr)
        work_sel = SelectWdg('task_assigned_select')
        if len(workers) > 0:
            work_sel.append_option('--Select--','')
            if assigned:
                work_sel.set_value(assigned)
            else:
                work_sel.set_value('')
            for worker in workers:
                work_sel.append_option(worker,worker)
        return work_sel

    def get_display(my):
        my.order_sk = my.kwargs.get('order_sk')
        order_code = my.order_sk.split('code=')[1]
        my.groups_str = None 
        if 'display_mode' in my.kwargs.keys():
            my.disp_mode = my.kwargs.get('display_mode') 
            if my.disp_mode == 'Small':
                my.small = True
        if 'user' in my.kwargs.keys():
            my.user = my.kwargs.get('user')
        else:
            my.user = Environment.get_user_name()
        if 'groups_str' in my.kwargs.keys():
            my.groups_str = my.kwargs.get('groups_str')
        if my.groups_str in [None,'']:
            user_group_names = Environment.get_group_names()
            for mg in user_group_names:
                if my.groups_str == '':
                    my.groups_str = mg
                else:
                    my.groups_str = '%s,%s' % (my.groups_str, mg)
        if 'is_master' in my.kwargs.keys():
            my.is_master_str = my.kwargs.get('is_master')
            if my.is_master_str == 'true':
                my.is_master = True 
        else:
            server = TacticServerStub.get()
            main_obj = server.eval("@SOBJECT(twog/order['code','%s'])" % order_code)[0]
            if main_obj.get('classification') in ['master','Master']:
                my.is_master = True
                my.is_master_str = 'true'
        # Get the javascript functions
        obs = OBScripts(order_sk=my.order_sk,user=my.user,groups_str=my.groups_str,display_mode=my.disp_mode)
        table = Table()
        table.add_attr('class','qe_top_%s' % my.order_sk)
        table.add_attr('width','100%s' % '%')
        table.add_row()
        type_checks_tbl = Table()
        long_row = type_checks_tbl.add_row() 
        long_row.add_attr('width','100%s' % '%')
        title_check = CustomCheckboxWdg(name='qe_titles_%s' % my.order_sk,value_field='title',checked='false',dom_class='quick_edit_selector') 

        type_checks_tbl.add_cell(title_check)
        type_checks_tbl.add_cell('Titles')

        proj_check = CustomCheckboxWdg(name='qe_projects_%s' % my.order_sk,value_field='projects',checked='false',dom_class='quick_edit_selector') 

        type_checks_tbl.add_cell(proj_check)
        type_checks_tbl.add_cell('Projects')

        wo_check = CustomCheckboxWdg(name='qe_work_orders_%s' % my.order_sk,value_field='work orders',checked='false',dom_class='quick_edit_selector')
        type_checks_tbl.add_cell(wo_check)
        wo = type_checks_tbl.add_cell('Work Orders')
        wo.add_attr('nowrap','nowrap')

        eq_check = CustomCheckboxWdg(name='qe_equipment_%s' % my.order_sk,value_field='equipment',checked='false',dom_class='quick_edit_selector') 

        type_checks_tbl.add_cell(eq_check)
        type_checks_tbl.add_cell('Equipment')

        group_selector = my.get_assigned_group_select(None,'group_selector')
        group_selector.add_behavior(obs.get_select_checks_by_group_behavior())
        sbd0 = type_checks_tbl.add_cell('&nbsp;&nbsp;&nbsp;')
        sbd = type_checks_tbl.add_cell('Select by Dept:')
        sbd.add_attr('nowrap','nowrap')
        type_checks_tbl.add_cell(group_selector)

        tog_check = CustomCheckboxWdg(name='qe_toggler',additional_js=my.get_toggle_select_check_behavior(),value_field='toggler',id='selection_toggler',checked='false')

        last_cell = type_checks_tbl.add_cell(tog_check)
        last_cell.add_attr('width', '100%s' % '%')
        last_cell.add_attr('align','right')
        lc1 = type_checks_tbl.add_cell('Select/Deselect All In Table')
        lc1.add_attr('width', '100%s' % '%')
        lc1.add_attr('align','right')
        lc1.add_attr('nowrap','nowrap')
       
        long_cell = table.add_cell(type_checks_tbl)
        long_cell.add_attr('colspan','8')

        table.add_row()
        table.add_cell('Platform: ')
        # Get the list of platforms from the db
        # Create the platform select wdg
        platforms = my.server.eval("@GET(twog/platform['@ORDER_BY','name'].name)")
        platform_sel = SelectWdg('platform_sel_%s' % my.order_sk)
        platform_sel.append_option('--Select--','--Select--')
        for platform in platforms:
            platform_sel.append_option(platform, platform)
        table.add_cell(platform_sel)

        # Create the territory select wdg
        territories = my.territory_str.split('|')
        territory_sel = SelectWdg('territory_sel_%s' % my.order_sk)
        territory_sel.append_option('--Select--','--Select--')
        for territory in territories:
            territory_sel.append_option(territory, territory)
        table.add_cell('Territory: ')
        table.add_cell(territory_sel)

        # Create the languages select wdg
        languages = my.language_str.split('|')
        language_sel = SelectWdg('language_sel_%s' % my.order_sk)
        language_sel.append_option('--Select--','--Select--')
        for language in languages:
            language_sel.append_option(language, language)
        table.add_cell('Language: ')
        table.add_cell(language_sel)
        
        # Create calendar input for start date
        sd = table.add_cell('Start Date: ')
        sd.add_attr('nowrap','nowrap')
        start = CalendarInputWdg("qe_start_date_%s" % my.order_sk)
        start.set_option('show_activator', True)
        start.set_option('show_confirm', False)
        start.set_option('show_text', True)
        start.set_option('show_today', False)
        start.set_option('read_only', False)    
        start.get_top().add_style('width: 150px')
        start.set_persist_on_submit()
        start_date = table.add_cell(start)
        start_date.add_attr('nowrap', 'nowrap')

        # Create calendar input for due date
        dd = table.add_cell('Due Date: ')
        dd.add_attr('nowrap', 'nowrap')
        due = CalendarInputWdg("qe_due_date_%s" % my.order_sk)
        due.set_option('show_activator', True)
        due.set_option('show_confirm', False)
        due.set_option('show_text', True)
        due.set_option('show_today', False)
        due.set_option('read_only', False)    
        due.get_top().add_style('width: 150px')
        due.set_persist_on_submit()
        due_date = table.add_cell(due)
        due_date.add_attr('nowrap', 'nowrap')

        table.add_cell('Priority: ')
        table.add_cell('<input type="text" name="qe_priority_%s"/>' % my.order_sk)

        table.add_row()

        # Statuses should pull from the database soon, so I won't have to adjust this list every time a new status is added or removed
        statuses = ['Pending', 'Ready', 'On Hold', 'Client Response', 'Fix Needed', 'Rejected', 'In Progress',
                    'DR In Progress', 'Amberfin01 In Progress', 'Amberfin02 In Progress', 'BATON In Progress',
                    'Export In Progress', 'Need Buddy Check', 'Buddy Check In Progress', 'Completed']
        status_sel = SelectWdg('eq_status_%s' % my.order_sk)
        status_sel.append_option('--Select--','--Select--')
        for status in statuses:
            status_sel.append_option(status, status)
        table.add_cell('Status: ')
        table.add_cell(status_sel)

        assigned_group_select = my.get_assigned_group_select(None, 'assigned_group_select')
        ag = table.add_cell('Assigned Group: ')
        ag.add_attr('nowrap', 'nowrap')
        table.add_cell(assigned_group_select)

        assigned_select = my.get_assigned_select(None)
        ad = table.add_cell('Assigned: ')
        ad.add_attr('nowrap', 'nowrap')
        table.add_cell(assigned_select)

        ewh = table.add_cell('Estimated Work Hours: ')
        ewh.add_attr('nowrap', 'nowrap')
        table.add_cell('<input type="text" name="qe_ewh_%s"/>' % my.order_sk)
      
        table.add_row()

        ed = table.add_cell('Expected Duration: ')
        ed.add_attr('nowrap', 'nowrap')
        table.add_cell('<input type="text" name="qe_ex_dur_%s"/>' % my.order_sk)

        exq = table.add_cell('Expected Quantity: ')
        exq.add_attr('nowrap', 'nowrap')
        table.add_cell('<input type="text" name="qe_ex_quan_%s"/>' % my.order_sk)

        #Submit button applies changes to everything in the order builder that is selected
        submit_button = table.add_cell('<input type="button" name="submit_button" value="Apply Changes"/>')
        submit_button.add_behavior(obs.get_submit_quick_changes())
        #Add equipment to all work orders that are selected
        add_eq_button = table.add_cell('<input type="button" name="add_eq_button" value="Edit Equipment"/>')
        add_eq_button.add_behavior(obs.get_eq_edit_behavior())
        last_chunk = table.add_cell(' ')
        last_chunk.add_attr('width', '100%')
        open_errors = table.add_cell('<u>Document Errors</u>')
        open_errors.add_attr('name','qe_error_opener_%s' % my.order_sk)
        open_errors.add_style('cursor: pointer;')
        open_errors.add_behavior(obs.get_open_errors_behavior())
        # Button to delete selected objects
        delete_button = table.add_cell('<input type="button" name="delete_button" value="Delete Selected"/>')
        delete_button.add_behavior(obs.get_qe_delete())

        # This is where the scheduler can enter production errors. It is hidden until "Document Errors" is clicked
        errors_row = table.add_row()
        errors_row.add_attr('class','qe_errors_row_%s' % my.order_sk)
        errors_row.add_style('display: none;')
        errors_wdg = ErrorEntryWdg(order_sk=my.order_sk,code='NOCODE',user=my.user,groups_str=my.groups_str,display_mode=my.disp_mode)
        errors_cell = table.add_cell(errors_wdg)
        errors_cell.add_attr('colspan','10')
        return table

class ErrorEntryWdg(BaseRefreshWdg):
    #This is the widget with which people can report production errrors
    def init(my):
        my.server = TacticServerStub.get()
        my.order_sk = ''
        my.user = ''
        my.groups_str = ''
        my.disp_mode = ''
        my.is_master = False
        my.is_master_str = 'false'
        my.small = False
        #Data for dropdowns
        my.video_reasons = {'Cropping': 'video_cropping_reason','Digital Hits / Macroblocking': 'video_digihits_reason', 'Dropped Frames': 'video_dropped_frames_reason', 'Dropout': 'video_dropout_reason', 'Duplicate Frames': 'video_duplicate_frames_reason', 'Interlacing on a progressive file': 'video_interlacing_progressive_reason', 'Motion/Image Lag': 'video_motion_lag_reason', 'Missing elements': 'video_missing_elements_reason', 'Corrupt file': 'video_corrupt_file_reason', 'Incorrect aspect ratio': 'video_bad_aspect_ratio_reason', 'Incorrect resolution': 'video_bad_resolution_reason', 'Incorrect pixel aspect ratio': 'video_bad_pixel_aspect_ratio_reason', 'Incorrect specifications': 'video_bad_specifications_reason', ' Incorrect head/tail format': 'video_bad_head_tail_reason', 'Other issue': 'video_other_reason'}
        my.video_reasons_arr = ['Cropping','Digital Hits / Macroblocking', 'Dropped Frames', 'Dropout', 'Duplicate Frames', 'Interlacing on a progressive file', 'Motion/Image Lag', 'Missing elements', 'Corrupt file', 'Incorrect aspect ratio', 'Incorrect resolution', 'Incorrect pixel aspect ratio', 'Incorrect specifications', ' Incorrect head/tail format', 'Other issue']
        my.audio_reasons = {'Incorrect Audio Mapping': 'audio_bad_mapping_reason', 'Missing Audio Channel': 'audio_missing_audio_channel_reason', 'Crackle/Hiss/Pop/Static/Ticks': 'audio_crackle_reason', 'Distortion': 'audio_distortion_reason', 'Dropouts': 'audio_dropouts_reason', 'Sync issue': 'audio_sync_reason', 'Missing elements': 'audio_missing_elements_reason', 'Corrupt file / missing file': 'audio_corrupt_missing_file_reason', 'Incorrect specifications': 'audio_bad_specifications_reason', 'Other Issue': 'audio_other_reason'}
        my.audio_reasons_arr = ['Incorrect Audio Mapping', 'Missing Audio Channel', 'Crackle/Hiss/Pop/Static/Ticks', 'Distortion', 'Dropouts', 'Sync issue', 'Missing elements', 'Corrupt file / missing file', 'Incorrect specifications', 'Other Issue']
        my.metadata_reasons = {'Missing information': 'metadata_missing_info_reason', 'Incorrect information': 'metadata_bad_info_reason', 'Incorrect formatting': 'metadata_bad_formatting_reason', 'Other Issue': 'metadata_other_reason'}
        my.metadata_reasons_arr = ['Missing information', 'Incorrect information', 'Incorrect formatting', 'Other Issue']
        my.subtitle_reasons = {'Interlacing on subtitles': 'subtitle_interlacing_reason', 'Incorrect subtitles': 'subtitle_bad_subtitles_reason', 'Sync issue': 'subtitle_sync_issue_reason', 'Overlapping other text': 'subtitle_overlapping_reason', 'Other issue': 'subtitle_other_reason'}
        my.subtitle_reasons_arr = ['Interlacing on subtitles', 'Incorrect subtitles', 'Sync issue', 'Overlapping other text', 'Other issue']
        my.cc_reasons = {'Sync issue': 'cc_sync_issue_reason','Incorrect CC': 'cc_bad_cc_reason', 'Overlapping other text': 'cc_overlapping_reason','Other issue': 'cc_other_reason'}
        my.cc_reasons_arr = ['Sync issue','Incorrect CC', 'Overlapping other text','Other issue']
        my.rejection_causes = ['Client Error','Machine Error','Manager Error','Operator Error','Process Error','Scheduler Error']

    def get_submit_errors_behavior(my, wo_code, in_ob):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        function encode_utf8( s )
                        {
                            return unescape( encodeURIComponent( s ) );
                        }
                        try{
                               order_sk = '%s';
                               user_name = '%s';
                               wo_code = '%s';
                               in_ob = '%s';
                               var ee_top = document.getElementsByClassName('error_entry_' + order_sk)[0];
                               var top_el = document.getElementsByClassName('twog_order_builder_' + order_sk);
                               if(top_el.length > 0){
                                   top_el = top_el[0];
                               }
                               //Get all of the select elements this way, since we can't do it by class (custom class will kill SelectWdg's javascript)
                               selects = ee_top.getElementsByTagName('select');
                               type_sel = null;
                               cause_sel = null;
                               for(var r = 0; r < selects.length; r++){
                                   name = selects[r].getAttribute('name');
                                   if(name == 'err_type_sel_' + order_sk){
                                       type_sel = selects[r];
                                   }
                                   if(name == 'rejection_cause_' + order_sk){
                                       cause_sel = selects[r];
                                   }
                               }
                               type = type_sel.value;
                               cause = cause_sel.value;
                               //--Select-- and NOTHINGXsXNOTHING are the same - they just mean nothing has been selected
                               //The NOTHINGXsXNOTHING selection was created just because I didn't want to be confused as to the origin of nulls or blank fields - it helped me track them
                               if(cause == '--Select--' || cause == 'NOTHINGXsXNOTHING'){
                                   cause = '';
                               }
                               time_spent_text = ee_top.getElementsByClassName('err_time_spent_' + order_sk)[0];
                               time_spent = time_spent_text.value;
                               err_des = ee_top.getElementsByClassName('err_operator_description_' + order_sk)[0];
                               act_des = ee_top.getElementsByClassName('err_action_taken_' + order_sk)[0];
                               error_description = err_des.value;
                               //Problem characters sometimes arise from descriptions, so we;'' have to encode to utf8
                               error_description = encode_utf8(error_description);
                               action_taken = act_des.value;
                               action_taken = encode_utf8(action_taken);
                               checks2= ee_top.getElementsByClassName('check_table_selector');
                               responsible = '';
                               errchecks = [];
                               //Run through the checks and sort them into normal error selections and responsible person selections
                               for(var r = 0; r < checks2.length; r++){
                                   if(checks2[r].getAttribute('checked') == 'true'){
                                      name = checks2[r].getAttribute('name');
                                      if(name != '' && name != null){
                                          if(name.indexOf('responsible_') != -1){
                                              login = checks2[r].getAttribute('login');
                                              if(responsible == ''){
                                                  responsible = login;
                                              }else{
                                                  responsible = responsible + ',' + login;
                                              }
                                          }
                                          if(name.indexOf('errcheck_') != -1){
                                              field = checks2[r].getAttribute('field');
                                              errchecks.push(field);
                                          }
                                      }
                                   }
                               }
                               if(wo_code == 'NOCODE'){
                                   //If there was no real code passed in, you'll have to grab that info from the selected work orders
                                   //Get all the checkboxes
                                   checks = null;
                                   if(in_ob == 'true'){
                                       //checks = top_el.getElementsByClassName('SPT_BVR');
                                       checks = top_el.getElementsByClassName('ob_selector');
                                   }else{
                                       checks = document.getElementsByClassName('ob_selector');
                                   }
                                   spt.app_busy.show("Sending Error Information...");
                                   //Sort through the checks and insert a production error for each selected work order
                                   for(var r = 0; r < checks.length; r++){
                                       if(checks[r].getAttribute('checked') == 'true'){
                                           if(checks[r].getAttribute('name') != null){
                                               name = checks[r].getAttribute('name');
                                               if(name.indexOf('select_') != -1){
                                                   if(name.indexOf('WORK_ORDER') != -1){
                                                       code = checks[r].getAttribute('code');
                                                       proj_code = checks[r].getAttribute('proj_code');
                                                       title_code = checks[r].getAttribute('title_code');
                                                       order_code = checks[r].getAttribute('order_code');
                                                       task_code = checks[r].getAttribute('task_code');
                                                       process = checks[r].getAttribute('process');
                                                       if(task_code != '' && task_code != null){
                                                           spt.app_busy.show("Sending Error Information for " + code + "..." );
                                                           //Get the objects so you'll have all the info you need for the production_error insert
                                                           var server = TacticServerStub.get();
                                                           title = server.eval("@SOBJECT(twog/title['code','" + title_code + "'])")[0];
                                                           order = server.eval("@SOBJECT(twog/order['code','" + order_code + "'])")[0];
                                                           task = server.eval("@SOBJECT(sthpw/task['code','" + task_code + "'])")[0];
                                                           insert_data = {'error_type': type, 'process': process, 'work_order_code': code, 'proj_code': proj_code, 'title_code': title_code, 'order_code': order_code, 'title': title.title, 'episode': title.episode, 'order_name': order.name, 'po_number': order.po_number, 'scheduler_login': task.creator_login, 'login': user_name, 'responsible_users': responsible, 'time_spent': time_spent, 'action_taken': action_taken, 'scheduler_description': error_description, 'rejection_cause': cause, 'operator_login': user_name}
                                                           //Loop through the errors selected and add them to the dictionary for insert
                                                           for(var p = 0; p < errchecks.length; p++){
                                                               insert_data[errchecks[p]] = true;
                                                           }
                                                           server.insert('twog/production_error',insert_data);
                                                       }
                                                   }
                                               }
                                           }
                                       }
                                   }
                               }else{
                                   //Here we know what the work order code is, so we get all of the remaining info from the associated objects for the error insert
                                   var server = TacticServerStub.get();
                                   code = wo_code;
                                   wo = server.eval("@SOBJECT(twog/work_order['code','" + code + "'])")[0];
                                   proj = server.eval("@SOBJECT(twog/proj['code','" + wo.proj_code + "'])")[0];
                                   title = server.eval("@SOBJECT(twog/title['code','" + proj.title_code + "'])")[0];
                                   order = server.eval("@SOBJECT(twog/order['code','" + title.order_code + "'])")[0];
                                   task = server.eval("@SOBJECT(sthpw/task['code','" + wo.task_code + "'])")[0];
                                   process = wo.process
                                   insert_data = {'error_type': type, 'process': process, 'work_order_code': code, 'proj_code': proj.code, 'title_code': title.code, 'order_code': order.code, 'title': title.title, 'episode': title.episode, 'order_name': order.name, 'po_number': order.po_number, 'scheduler_login': task.creator_login, 'login': user_name, 'responsible_users': responsible, 'time_spent': time_spent, 'action_taken': action_taken, 'scheduler_description': error_description, 'rejection_cause': cause, 'operator_login': user_name}
                                   //Loop through the errors selected and add them to the dictionary for insert
                                   for(var p = 0; p < errchecks.length; p++){
                                       insert_data[errchecks[p]] = true;
                                   }
                                   server.insert('twog/production_error', insert_data);
                                   alert('Done Adding Error');
                               }
                               if(in_ob == 'true'){
                                   //If we are working with this widget inside order builder, then hide the widget after saving
                                   var qe_top = document.getElementsByClassName('qe_top_' + order_sk)[0];
                                   err_row = top_el.getElementsByClassName('qe_errors_row_' + order_sk);
                                   if(err_row.length > 0){
                                       err_row = err_row[0];
                                       err_row.style.display = 'none';
                                       var tds = qe_top.getElementsByTagName('td');
                                       cell_el = null;
                                       for(var r = 0; r < tds.length; r++){
                                           if(tds[r].getAttribute('name') == 'qe_error_opener_' + order_sk){
                                               cell_el = tds[r];
                                           }
                                       }
                                       cell_el.innerHTML = '<u>Document Errors</u>'
                                   }else{
                                       spt.popup.close(spt.popup.get_popup(bvr.src_el));
                                   }
                               }else{
                                   //If not in order builder, then it is a popup. So close it after saving.
                                   spt.popup.close(spt.popup.get_popup(bvr.src_el));
                               }
                               spt.app_busy.hide();

                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (my.order_sk, my.user, wo_code, in_ob)}
        return behavior

    def get_sel_change_behavior(my, code):
        behavior = {'css_class': 'sel_change', 'type': 'change', 'cbjs_action': '''        
                        try{
                          //Apply the change of rejection cause for the production_error immediately upon change
                          var server = TacticServerStub.get();
                          var code = '%s';
                          sk = server.build_search_key('twog/production_error', code)
                          value = bvr.src_el.value;
                          if(value == '--Select--'){
                              value = '';
                          }
                          server.update(sk, {'rejection_cause': value});
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (code)}
        return behavior

    def make_login_table(my):
        #Makes a list of workers to select from
        table = Table()
        table.add_style('background-color: #fffff1;')
        max_width = 4
        table.add_row()
        top_cell = table.add_cell('<b><u>Responsible</u></b>')
        top_cell.add_attr('colspan',max_width)
        top_cell.add_attr('align','center')
        count = 0
        users = my.server.eval("@SOBJECT(sthpw/login['location','internal']['license_type','user']['@ORDER_BY','login'])")
        for u in users:
            if count % max_width == 0:
                table.add_row()

            checker = CustomCheckboxWdg(name='responsible_%s' % u.get('login'),value_field=u.get('login'),checked='false',dom_class='check_table_selector') 

            table.add_cell(checker)
            label = table.add_cell(u.get('login'))
            label.add_attr('nowrap','nowrap')
            label.add_attr('width','137px')
            count = count + 1
        return table

    def make_check_table(my, dictoid, arr, sob, sk, my_name, color):
        #Makes a table of checklisted items
        table = Table()
        table.add_style('background-color: %s;' % color)
        #The maximum width across (max number of columns of checkboxes)
        max_width = 3
        table.add_row()
        top_cell = table.add_cell('<b><u>%s</u></b>' % my_name)
        top_cell.add_attr('colspan',max_width)
        top_cell.add_attr('align','center')
        count = 0
        for entry in arr:
            #If it has hit the max width for the row, create a new row
            if count % max_width == 0:
                table.add_row()
            #Create textbox
            check_bool = 'false'
            if sob:
                if sob.get(dictoid[entry]):
                    check_bool = 'true'
                else:
                    check_bool = 'false'
            else:
                check_bool = 'false'
            checker = CustomCheckboxWdg(name='errcheck_%s_%s' % (dictoid[entry], sk),value_field=dictoid[entry],checked=check_bool,dom_class='check_table_selector',field=dictoid[entry]) 
            check_hold = table.add_cell(checker)
            check_hold.add_attr('field', dictoid[entry])
            label = table.add_cell(entry)
            label.add_attr('nowrap','nowrap')
            label.add_attr('width','190px')
            count = count + 1 
        return table

    def get_display(my):
        in_ob = 'true'
        if 'order_sk' in my.kwargs.keys():
            my.order_sk = my.kwargs.get('order_sk')
        else:
            work_order_code = my.kwargs.get('work_order_code')
            my.code = work_order_code
            top_order = my.server.eval("@SOBJECT(twog/work_order['code','%s'].twog/proj.twog/title.twog/order)" % work_order_code)[0]
            my.order_sk = top_order.get('__search_key__')
        if 'code' in my.kwargs.keys():
            my.code = my.kwargs.get('code')
        order_code = my.order_sk.split('code=')[1]
        if 'display_mode' in my.kwargs.keys():
            my.disp_mode = my.kwargs.get('display_mode') 
            if my.disp_mode == 'Small':
                my.small = True
        if 'user' in my.kwargs.keys():
            my.user = my.kwargs.get('user')
        else:
            my.user = Environment.get_user_name() 
        if 'groups_str' in my.kwargs.keys():
            my.groups_str = my.kwargs.get('groups_str')
        user_group_names = Environment.get_group_names()
        if my.groups_str in [None,'']:
            for mg in user_group_names:
                if my.groups_str == '':
                    my.groups_str = mg
                else:
                    my.groups_str = '%s,%s' % (my.groups_str, mg)
        if 'is_master' in my.kwargs.keys():
            my.is_master_str = my.kwargs.get('is_master')
            if my.is_master_str == 'true':
                my.is_master = True 
        else:
            main_obj = my.server.eval("@SOBJECT(twog/order['code','%s'])" % order_code)[0]
            if main_obj.get('classification') in ['Master','master']:
                my.is_master = True
                my.is_master_str = 'true'
        if 'in_ob' in my.kwargs.keys():
            in_ob = my.kwargs.get('in_ob')
        table = Table() 
        table.add_attr('class','error_entry_%s' % my.order_sk)
        table.add_style('background-color: #797676;')
        table.add_row()
        top_tbl = Table()

        #Create checkbox tables of common reasons for errors
        video_tbl = my.make_check_table(my.video_reasons, my.video_reasons_arr, None, my.order_sk, 'Video', '#ffef91')
        audio_tbl =  my.make_check_table(my.audio_reasons, my.audio_reasons_arr, None, my.order_sk, 'Audio', '#ffefa1')
        metadata_tbl =  my.make_check_table(my.metadata_reasons, my.metadata_reasons_arr, None, my.order_sk, 'MetaData', '#ffefb1')
        subtitle_tbl =  my.make_check_table(my.subtitle_reasons, my.subtitle_reasons_arr, None, my.order_sk, 'Subtitle', '#ffefc1')
        cc_tbl =  my.make_check_table(my.cc_reasons, my.cc_reasons_arr, None, my.order_sk, 'CC', '#ffefd1')

        cause_sel = SelectWdg('rejection_cause_%s' % my.order_sk)
        cause_sel.append_option('--Select--', '--Select--')
        for cause in my.rejection_causes:
            cause_sel.append_option(cause, cause)

        error_types = ['Internal Error', 'External Error']
        type_sel = SelectWdg('err_type_sel_%s' % my.order_sk)
        for error_type in error_types:
            type_sel.append_option(error_type, error_type)

        top_tbl.add_cell('Error Type: ')
        top_tbl.add_cell(type_sel)

        top_tbl.add_cell(' Cause: ')
        top_tbl.add_cell(cause_sel)

        time_spent = top_tbl.add_cell('Time Spent (on Each): ')
        time_spent_text = top_tbl.add_cell('<input type="text" class="err_time_spent_%s"/>' % my.order_sk)

        table.add_cell(top_tbl)
        table.add_row()
        op_dt = Table()
        op_dt.add_row()
        op1 = op_dt.add_cell('Description of Error')
        op1.add_attr('align','left')
        op_dt.add_row()
        #Create textarea for operator decription
        op_dt.add_cell('<textarea cols="45" rows="10" class="err_operator_description_%s"></textarea>' % my.order_sk)
        table.add_cell(op_dt)
        act_t = Table()
        act_t.add_row()
        act_t.add_cell('Action Taken')
        act_t.add_row()
        #Create textarea for operator decription
        act_t.add_cell('<textarea cols="45" rows="10" class="err_action_taken_%s"></textarea>' % my.order_sk)
        #Add the reason checkbox tables
        table.add_cell(act_t)
        table.add_row()
        table.add_cell(video_tbl)
        table.add_row()
        table.add_cell(audio_tbl)
        table.add_row()
        table.add_cell(metadata_tbl)
        table.add_row()
        table.add_cell(subtitle_tbl)
        table.add_row()
        table.add_cell(cc_tbl)
        
        #Only show the responsible people list if the user is in the technical_services or senior staff depts
        show_responsible = False
        for gl in user_group_names:
            if gl in ['technical services','senior_staff']:
                show_responsible = True
        if show_responsible:
            #Display the table containing workers to assign blame
            table.add_row()
            table.add_cell(my.make_login_table())
        table.add_row()
        table.add_cell(' ')
        butt = table.add_cell('<input type="button" value="Apply To Selected Work Orders"/>')
        butt.add_attr('align','right')
        butt.add_behavior(my.get_submit_errors_behavior(my.code, in_ob))

        return table


class OrderTable(BaseRefreshWdg): 
    ''' This is the top level view of the dynamic order builder part ''' 

    def init(my):
        my.search_type = 'twog/order'
        my.title = "Order"
        my.sk = ''
        my.sid = ''
        my.code = ''
        my.allowed_titles_str = ''
        my.allowed_titles = []
        my.user = '' 
        my.width = '1000px'
        my.height = '300px'
        my.disp_mode = 'Normal'
        my.small = False
        my.groups_str = ''
        my.is_master = False
        my.is_master_str = 'false'
    
    def get_display(my):
        import common_tools.utils as ctu
        from common_tools.copy_url_button import CopyUrlButton

        my.sk = str(my.kwargs.get('sk'))
        my.sid = str(my.kwargs.get('search_id'))
        allowed_search_titles = ''
        if 'user' in my.kwargs.keys():
            my.user = my.kwargs.get('user')
        else:
            my.user = Environment.get_user_name() 
        if 'groups_str' in my.kwargs.keys():
            my.groups_str = my.kwargs.get('groups_str')
        if my.groups_str in [None,'']:
            user_group_names = Environment.get_group_names()
            for mg in user_group_names:
                if my.groups_str == '':
                    my.groups_str = mg
                else:
                    my.groups_str = '%s,%s' % (my.groups_str, mg)
        user_is_scheduler = False
        if 'scheduling' in my.groups_str:
            user_is_scheduler = True
        if 'display_mode' in my.kwargs.keys():
            my.disp_mode = my.kwargs.get('display_mode')
        if my.disp_mode == 'Small':
            my.small = True
        my.code = my.sk.split('code=')[1]
        if 'allowed_titles' in my.kwargs.keys():
            my.allowed_titles_str = str(my.kwargs.get('allowed_titles'))
            split_allow = my.allowed_titles_str.split('|')
            for sa in split_allow:
                if allowed_search_titles == '':
                    allowed_search_titles = "('%s'" % sa
                else:
                    allowed_search_titles = "%s,'%s'" % (allowed_search_titles, sa)
            if allowed_search_titles != '':
                allowed_search_titles = '%s)' % allowed_search_titles
        if my.allowed_titles_str == '':
            my.allowed_titles_str = 'NOTHING|NOTHING'
        main_search = Search("twog/order")
        main_search.add_filter('code',my.code)
        main_obj = main_search.get_sobject()
        if 'is_master' in my.kwargs.keys():
            my.is_master_str = my.kwargs.get('is_master')
            if my.is_master_str == 'true':
                my.is_master = True 
        else:
            if main_obj.get_value('classification') in ['master','Master']:
                my.is_master = True
                my.is_master_str = 'true'
        sched_full_name = ''
        if main_obj.get_value('login') not in [None,'']:
            sched_s = Search('sthpw/login')
            sched_s.add_filter('location','internal')
            sched_s.add_filter('login',main_obj.get_value('login'))
            sched = sched_s.get_sobject()
            if sched:
                sched_full_name = '%s %s' % (sched.get_value('first_name'), sched.get_value('last_name'))

        sales_full_name = ''
        if main_obj.get_value('sales_rep') not in [None,'']:
            sales_s = Search('sthpw/login')
            sales_s.add_filter('location','internal')
            sales_s.add_filter('login',main_obj.get_value('sales_rep'))
            sales = sales_s.get_sobject()
            if sales:
                sales_full_name = '%s %s' % (sales.get_value('first_name'), sales.get_value('last_name'))
        
        obs = OBScripts(order_sk=my.sk,user=my.user,groups_str=my.groups_str,display_mode=my.disp_mode,is_master=my.is_master_str)
        title_search = Search("twog/title")
        title_search.add_filter('order_code',main_obj.get_value('code'))
        if allowed_search_titles != '':
            title_search.add_where("\"code\" in %s" % allowed_search_titles)
        titles = title_search.get_sobjects()
        table = Table()
        table.add_attr('I_AM','ORDER TABLE')
        if user_is_scheduler:
            table.add_attr('SOY','ORDER-O TABLE-O')
            print "\n\n\nIMA ORDER\n\n\n"
        table.add_attr('cellpadding','0')
        table.add_attr('cellspacing','0')
        table.add_style('border-collapse', 'separate')
        table.add_style('border-spacing', '25px 0px')
        table.add_style('color: #00033a;')
        table.add_style('background-color: #d9edf7;')
        table.add_style('width: 100%s;' % '%')
        table.add_style('border-bottom-right-radius', '10px')
        table.add_style('border-bottom-left-radius', '10px')
        table.add_style('border-top-right-radius', '10px')
        table.add_style('border-top-left-radius', '10px')
        order_name_row = table.add_row()
        full_o_name = main_obj.get('name')
        if main_obj.get('details') not in [None,'']:
            full_o_name = '%s - %s' % (full_o_name, main_obj.get('details'))
        order_name_cell = table.add_cell('<b><u>Order: %s</u><b>' % full_o_name)
        order_name_cell.add_attr('nowrap','nowrap')
        order_name_cell.add_style('cursor: pointer;')
        order_name_cell.add_behavior(obs.get_panel_change_behavior(my.search_type, my.code, my.sk, my.sk, my.title, '', 'builder/refresh_from_save', '',my.sk,main_obj.get_value('name'), user_is_scheduler))
        order_due_cell = table.add_cell("Due: %s" % fix_date(main_obj.get_value('due_date')).split(' ')[0])
        order_due_cell.add_attr('nowrap','nowrap')
        long_cell1 = table.add_cell('Scheduler: %s' % sched_full_name)
        long_cell1.add_style('width: 100%s' % '%')
        order_sales_row = table.add_row()
        order_po_cell = table.add_cell("Code: %s &nbsp; &nbsp; PO Number: %s" % (my.code, main_obj.get_value('po_number')))
        order_po_cell.add_attr('nowrap','nowrap')
        order_sales_cell = table.add_cell('Sales Rep: %s' % sales_full_name)
        order_sales_cell.add_attr('nowrap','nowrap')
        bottom_buttons = Table()
        bottom_buttons.add_row()

        order_builder_url = ctu.get_order_builder_url(my.code)
        copy_url_button = CopyUrlButton(title='Copy URL to Clipboard', url=order_builder_url)
        copy_url_cell = bottom_buttons.add_cell(copy_url_button)
        copy_url_cell.add_attr('align', 'right')

        instructions_button = FullInstructionsLauncherWdg(title='View Instructions', search_key=my.sk)
        instructions_cell = bottom_buttons.add_cell(instructions_button)
        instructions_cell.add_attr('align', 'right')

        if user_is_scheduler:
            tcloner = ButtonSmallNewWdg(title="Title Cloner", icon=CustomIconWdg.icons.get('STAR'))
            tcloner.add_behavior(obs.get_launch_title_cloner_behavior(my.sk, main_obj.get_value('name'), my.user))
            dcl = bottom_buttons.add_cell(tcloner)
            dcl.add_attr('align', 'right')
    
            tchanger = ButtonSmallNewWdg(title="Title Changer", icon=CustomIconWdg.icons.get('CALENDAR'))
            tchanger.add_behavior(obs.get_launch_title_changer_behavior(my.sk, main_obj.get_value('name'), my.user))
            dcal = bottom_buttons.add_cell(tchanger)
            dcal.add_attr('align', 'right')
    
            tdeletor = ButtonSmallNewWdg(title="Title Deletor", icon=CustomIconWdg.icons.get('TABLE_ROW_DELETE'))
            tdeletor.add_behavior(obs.get_launch_title_deletor_behavior(my.sk, main_obj.get_value('name'), my.user))
            dfilt = bottom_buttons.add_cell(tdeletor)
            dfilt.add_attr('align', 'right')

        tfilter = ButtonSmallNewWdg(title="Filter Titles", icon=CustomIconWdg.icons.get('CONTENTS'))
        tfilter.add_behavior(obs.get_launch_title_filter_behavior(my.sk, main_obj.get_value('name'), my.user))
        filt = bottom_buttons.add_cell(tfilter)
        filt.add_attr('align', 'right')

        upload = ButtonSmallNewWdg(title="Upload", icon=CustomIconWdg.icons.get('PUBLISH'))
        upload.add_behavior(get_upload_behavior(my.sk))
        up = bottom_buttons.add_cell(upload)
        up.add_attr('align', 'right')

        note_adder = ButtonSmallNewWdg(title="Add Note", icon=CustomIconWdg.icons.get('NOTE_ADD'))
        note_adder.add_behavior(obs.get_launch_note_behavior(my.sk, main_obj.get_value('name')))
        nadd = bottom_buttons.add_cell(note_adder)
        nadd.add_attr('align', 'right')
        nadd.add_style('cursor: pointer;')
        
        if user_is_scheduler:
            title_adder = ButtonSmallNewWdg(title="Add Titles", icon=CustomIconWdg.icons.get('INSERT_MULTI'))
            title_adder.add_behavior(obs.get_title_add_behavior(my.sk, my.sid, main_obj.get_value('client_code'), main_obj.get_value('name')))
            tadd = bottom_buttons.add_cell(title_adder)
            tadd.add_attr('align', 'right')
            tadd.add_style('cursor: pointer;')


        long_cell2 = table.add_cell(bottom_buttons)
        long_cell2.add_attr('align', 'right')
        long_cell2.add_attr('valign', 'bottom')
        long_cell2.add_style('width: 100%')
        bottom = Table()
        bottom.add_attr('width', '100%')
        bottom.add_attr('cellpadding', '0')
        bottom.add_attr('cellspacing', '0')
        for title in titles:
            title_sk = title.get_search_key()
            title_row  = bottom.add_row()
            title_row.add_attr('width', '100%')
            title_row.add_attr('class','row_%s' % title_sk)
            title_obj = TitleRow(sk=title_sk, parent_sk=my.sk, parent_sid=my.sid, groups_str=my.groups_str,
                                 user=my.user, display_mode=my.disp_mode, is_master=my.is_master_str, main_obj=title)
            content_cell = bottom.add_cell(title_obj)
            content_cell.add_attr('width', '100%')
            content_cell.add_attr('sk', title_sk)
            content_cell.add_attr('order_sk', my.sk)
            content_cell.add_attr('parent_sk', my.sk)
            content_cell.add_attr('parent_sid', my.sid)
            content_cell.add_attr('call_me', title.get_value('title'))
            content_cell.add_attr('episode', title.get_value('episode'))
            content_cell.add_attr('my_class','TitleRow')
            content_cell.add_attr('client_code', title.get_value('client_code'))
            content_cell.add_attr('class', 'cell_%s' % title_sk)
        tab2ret = Table()
        tab2ret.add_attr('width', '100%')
        tab2ret.add_row()
        tab2ret.add_cell(table)
        tab2ret.add_row()
        bot = tab2ret.add_cell(bottom)
        bot.add_style('padding-left: 40px;')

        return tab2ret


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

class TitleSourceInspectorWdg(BaseRefreshWdg): 

    def init(my):
        my.search_type = 'twog/title'
        my.title = 'Title'
        my.sk = ''
        my.code = ''
        my.x_butt = "<img src='/context/icons/common/BtnKill_Black.gif' title='Delete' name='Delete'/>" 

    def get_display(my):
        my.sk = str(my.kwargs.get('search_key'))
        my.code = my.sk.split('code=')[1]
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
        sources_search = Search("twog/title_origin")
        sources_search.add_filter('title_code',my.code)
        sources_searched = sources_search.get_sobjects()
        sources = []
        for ss in sources_searched:
            sources.append(ss.get_value('source_code'))
        obs = OBScripts()
        table = Table()
        table.add_attr('class', 'titlesourceinspector_%s' % my.sk)
        if sources in [None,[]]:
            table.add_row()
            table.add_cell('There are no sources attached to this Title')
        else:
            for source_link in sources:
                source_search = Search("twog/source")
                source_search.add_filter('code',source_link)
                source = source_search.get_sobject()
                row = table.add_row()
                row.add_attr('class', 'titlesourceinspector_source_%s' % source.get_value('code'))
                if user_is_scheduler:
                    killer = table.add_cell(my.x_butt)
                    killer.add_style('cursor: pointer;')
                    killer.add_behavior(obs.get_kill_title_source_behavior(source.get_value('code'), '%s: %s' % (source.get_value('title'), source.get_value('episode')), my.sk))
                name = table.add_cell('<b><u>Barcode: %s  Title: %s: %s, Code : %s</u></b>' % (source.get_value('barcode'), source.get_value('title'), source.get_value('episode'), source.get_value('code'))) 
                name.add_attr('nowrap','nowrap')
                name.add_style('cursor: pointer;')
                name.add_behavior(obs.get_launch_source_behavior(my.code,my.sk,source.get_value('code'),source.get_search_key()))

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


class PreReqWdg(BaseRefreshWdg): 

    def init(my):
        my.sob_sk = ''
        my.sob_code = '' 
        my.sob_name = ''
        my.sob_st = ''
        my.prereq_st = ''
        my.prereq_field = ''
        my.pipeline = '' 
        my.order_sk = ''
        my.x_butt = "<img src='/context/icons/common/BtnKill_Black.gif' title='Delete' name='Delete'/>" 
        my.is_master = False

    def get_display(my):
        my.sob_code = str(my.kwargs.get('sob_code'))
        my.sob_sk = str(my.kwargs.get('sob_sk'))
        my.sob_st = str(my.kwargs.get('sob_st'))
        my.sob_name = str(my.kwargs.get('sob_name'))
        my.pipeline = str(my.kwargs.get('pipeline'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        order_code = my.order_sk.split('code=')[1]
        if 'is_master' in my.kwargs.keys():
            my.is_master = my.kwargs.get('is_master')
        else:
            order_search = Search("twog/order")
            order_search.add_filter('code',order_code)
            order = order_search.get_sobject()
            order_classification = order.get_value('classification')
            if order_classification in ['master','Master']:
                my.is_master = True
        obs = OBScripts(order_sk=my.order_sk)
        if my.sob_st == 'twog/title':
            my.prereq_st = 'twog/title_prereq'
            my.prereq_field = 'title_code'
        elif my.sob_st == 'twog/work_order':
            my.prereq_st = 'twog/work_order_prereq'
            my.prereq_field = 'work_order_code'

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

        prereq_search = Search(my.prereq_st)
        prereq_search.add_filter(my.prereq_field,my.sob_code)
        prereqs = prereq_search.get_sobjects()
        overhead = Table()
        overhead.add_attr('class','overhead_%s' % my.sob_code)
        table = Table()
        table.add_attr('class','prereq_adder_%s' % my.sob_code)
        table.add_row()
        if my.sob_st == 'twog/work_order' and user_is_scheduler:
            kill_title_pqs_btn = table.add_cell('<input type="button" value="Remove\nTitle PreReqs"/>')
            kill_title_pqs_btn.add_attr('colspan','2')
            kill_title_pqs_btn.add_behavior(obs.get_kill_wos_title_prereqs_behavior(my.sob_sk, my.order_sk, my.sob_name, my.pipeline)) 
        else:
            table.add_cell(' ')
            table.add_cell(' ')
        table.add_cell(' ')
        table.add_cell(' ')
        sat = table.add_cell('Satisfied?')
        sat.add_attr('align','center')
        table.add_cell(' ')
        for p in prereqs:
            table.add_row()
            if user_is_scheduler:
                killer = table.add_cell(my.x_butt)
                killer.add_style('cursor: pointer;')
                killer.add_behavior(obs.get_prereq_killer_behavior(p.get_value('code'), my.prereq_st, my.sob_code, my.sob_sk, my.sob_st, my.sob_name, my.pipeline))
            prereq_text = 'PreReq: '
            if my.sob_st == 'twog/work_order':
                if p.get_value('from_title') == True:
                    prereq_text = 'Title PreReq: '
            alabel = table.add_cell(prereq_text)
            alabel.add_attr('align','center')
            table.add_cell('<input type="text" class="prereq_%s" value="%s" style="width: 500px;"/>' % (p.get_value('code'), p.get_value('prereq')))
            save_butt = table.add_cell('<input type="button" class="save_%s" value="Save"/>' % (p.get_value('code')))
            save_butt.add_behavior(obs.get_save_prereq_behavior(p.get_value('code'), my.prereq_st, my.sob_code, my.pipeline))

            check_val = ''
            if p.get_value('satisfied') == True:
                check_val = 'true'
            else:
                check_val = 'false'
            checkbox = CustomCheckboxWdg(name='satisfied_%s' % p.get_value('code'),value_field=p.get_value('code'),checked=check_val,dom_class='prereq_selector',code=p.get_value('code'),additional_js=obs.get_change_satisfied_behavior(p.get_value('code'), my.prereq_st, my.sob_code, p.get_value('satisfied'), my.sob_sk, my.sob_st, my.sob_name, my.pipeline)) 

            ck = table.add_cell(checkbox)
            ck.add_attr('align','center')
            if my.is_master:
                if my.sob_st == 'twog/title':
                    table.add_cell(' &nbsp; ')
                    templ_search = Search("twog/pipeline_prereq")
                    templ_search.add_filter('pipeline_code',my.pipeline)
                    templ_search.add_filter('prereq',p.get_value('prereq'))
                    templ_rez = templ_search.get_sobjects()
                    templ_count = len(templ_rez)
                    if templ_count == 0:
                        template_button = ButtonSmallNewWdg(title="Template This PreReq", icon=CustomIconWdg.icons.get('TEMPLATE'))
                        if my.is_master and user_is_scheduler:
                            template_button.add_behavior(obs.get_template_prereq_behavior(my.sob_code, my.pipeline, my.prereq_st, p.get_value('code')))
                    else:
                        template_button = '<img border="0" style="vertical-align: middle" title="Templated" name="Templated" src="/context/icons/silk/tick.png">'
                    tb = table.add_cell(template_button)
                    tb.add_class('prereq_templ_%s' % p.get_value('code'))
                elif my.sob_st == 'twog/work_order':
                    table.add_cell(' &nbsp; ')
                    wot_search = Search("twog/work_order")
                    wot_search.add_filter('code',my.sob_code)
                    wot = wot_search.get_sobject()
                    work_order_templ_code = wot.get_value('work_order_templ_code')
                    templ_search = Search("twog/work_order_prereq_templ")
                    templ_search.add_filter('work_order_templ_code',work_order_templ_code)
                    templ_search.add_filter('prereq',p.get_value('prereq'))
                    templ_rez = templ_search.get_sobjects()
                    templ_count = len(templ_rez)
                    if templ_count == 0:
                        template_button = ButtonSmallNewWdg(title="Template This PreReq", icon=CustomIconWdg.icons.get('TEMPLATE'))
                        if my.is_master:
                            template_button.add_behavior(obs.get_template_wo_prereq_behavior(my.sob_code, my.prereq_st, p.get_value('code'), work_order_templ_code))
                    else:
                        template_button = '<img border="0" style="vertical-align: middle" title="Templated" name="Templated" src="/context/icons/silk/tick.png">'
                    tb = table.add_cell(template_button)
                    tb.add_class('prereq_templ_%s' % p.get_value('code'))
        table.add_row()
        table.add_cell('<hr/>')
        table.add_row()
        table.add_cell(' &nbsp; ')
        if user_is_scheduler:
            label = table.add_cell('New PreReq: ')
            label.add_attr('nowrap','nowrap')
            prereq_text_wdg = TextWdg('new_prereq')
            prereq_text_wdg.add_behavior(obs.get_create_prereq_change_behavior(my.sob_code, my.prereq_st, my.sob_sk, my.sob_st, my.sob_name, my.pipeline))
            table.add_cell(prereq_text_wdg)
            create_butt = table.add_cell('<input type="button" class="create_prereq" value="Create"/>')
            create_butt.add_behavior(obs.get_create_prereq_behavior(my.sob_code, my.prereq_st, my.sob_sk, my.sob_st, my.sob_name, my.pipeline))
        overhead.add_row()
        oh_cell = overhead.add_cell(table)
        oh_cell.add_attr('class','prereq_adder_cell')

        return overhead


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
        overhead.add_attr('class','out_overhead_%s' % my.work_order_code)
        overhead.add_attr('client_code',my.client_code)
        obs = OBScripts(order_sk=my.order_sk)
        wo_search = Search("twog/work_order")
        wo_search.add_filter('code',my.work_order_code)
        work_order = wo_search.get_sobject()
        delivs_search = Search("twog/work_order_deliverables")
        delivs_search.add_filter('work_order_code',my.work_order_code)
        delivs = delivs_search.get_sobjects()
        inter_search = Search("twog/work_order_intermediate")
        inter_search.add_filter('work_order_code',my.work_order_code)
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
        add_inter.add_behavior(obs.get_add_inter_behavior(my.work_order_code, my.client_code, my.is_master_str))
        inters_tbl = Table()
        for inter1 in inters:
            i_search = Search("twog/intermediate_file")
            i_search.add_filter('code',inter1.get_value('intermediate_file_code'))
            inter = i_search.get_sobject()
            inters_tbl.add_row()
            if user_is_scheduler:
                killer = inters_tbl.add_cell(my.x_butt)
                killer.add_style('cursor: pointer;')
                killer.add_behavior(obs.get_intermediate_killer_behavior(inter1.get_value('code'), inter.get_value('title'), my.work_order_code, my.is_master_str))
            alabel = inters_tbl.add_cell('Intermediate: ')
            alabel.add_attr('align','center')
            popper = inters_tbl.add_cell('<u>%s</u>' % inter.get_value('title'))
            popper.add_attr('nowrap','nowrap')
            popper.add_style('cursor: pointer;')
            popper.add_behavior(obs.get_open_intermediate_behavior(inter.get_value('code'),my.work_order_code, my.client_code))

            if str(inter1.get_value('satisfied')) == 'True':
                check_val = 'true'
            else:
                check_val = 'false'
            checkbox = CustomCheckboxWdg(name='satisfied_%s' % inter.get_value('code'),value_field=inter.get_value('code'),checked=check_val,dom_class='inter_selector',code=inter.get_value('code'),additional_js=obs.get_change_inter_satisfied_behavior(inter1.get_value('code'), my.work_order_code, my.client_code, str(inter1.get_value('satisfied'))))

            ck = inters_tbl.add_cell(checkbox)
            ck.add_attr('align','center')
            inters_tbl.add_cell(' &nbsp; ')
            if my.is_master:
                if inter.get_value('intermediate_file_templ_code') in [None,'']:
                    template_button = ButtonSmallNewWdg(title="Template This Intermediate File", icon=CustomIconWdg.icons.get('TEMPLATE'))
                    template_button.add_behavior(obs.get_template_intermediate_behavior(inter.get_value('code'), my.work_order_code))
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
        add_delv.add_behavior(obs.get_add_deliverable_behavior(my.work_order_code, my.client_code))
        delv_tbl = Table()
        client_search = Search("twog/client")
        client_search.add_order_by('name desc')
        clients = client_search.get_sobjects()
        client_sel = '<select class="deliver_to_DELIV_CODE"><option value="">--Select--</option>'
        for client in clients:
            client_sel = '%s<option value="%s">%s</option>' % (client_sel, client.get_value('name'), client.get_value('name'))
        client_sel = '%s</select>' % client_sel
        for deliv1 in delivs:
            d_search = Search("twog/source")
            d_search.add_filter('code',deliv1.get_value('deliverable_source_code'))
            deliv = d_search.get_sobject()
            deliv_name = '%s, Episode: %s, Type: %s' % (deliv.get_value('title'),deliv.get_value('episode'), deliv.get_value('source_type')) 
            delv_tbl.add_row()
            if user_is_scheduler:
                killer = delv_tbl.add_cell(my.x_butt)
                killer.add_style('cursor: pointer;')
                killer.add_behavior(obs.get_deliverable_killer_behavior(deliv1.get_value('code'), my.work_order_code, deliv1.get_value('title_code'), deliv.get_value('code'), '%s (%s: %s)' % (deliv1.get_value('name'), deliv.get_value('title'), deliv.get_value('episode')), my.is_master_str))
            alabel = delv_tbl.add_cell('Permanent: ')
            alabel.add_attr('align','center')
            popper = delv_tbl.add_cell('<u>%s</u>' % deliv.get_value('title'))
            popper.add_attr('nowrap','nowrap')
            popper.add_style('cursor: pointer;')
            popper.add_behavior(obs.get_open_deliverable_behavior(deliv.get_value('code'), my.work_order_code, deliv1.get_value('title_code'), my.client_code))

            if str(deliv1.get_value('satisfied')) == 'True':
                check_val = 'true'
            else:
                check_val = 'false'
            checkbox = CustomCheckboxWdg(name='satisfied_%s' % deliv.get_value('code'),value_field=deliv.get_value('code'),checked=check_val,dom_class='deliv_selector',code=deliv.get_value('code'),additional_js=obs.get_change_deliverable_satisfied_behavior(deliv1.get_value('code'), my.work_order_code, deliv1.get_value('title_code'), str(deliv1.get_value('satisfied')), my.client_code))

            ck = delv_tbl.add_cell(checkbox)
            ck.add_attr('align','center')
            delv_tbl.add_cell(' &nbsp; ')
            if my.is_master:
                if deliv.get_value('templ_code') in [None,'']:
                    template_button = ButtonSmallNewWdg(title="Template This Intermediate File", icon=CustomIconWdg.icons.get('TEMPLATE'))
                    template_button.add_behavior(obs.get_template_deliverable_behavior(deliv1.get_value('code'), work_order.get_value('work_order_templ_code'), deliv1.get_value('deliverable_source_code'), my.work_order_code))
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
            save_cell.add_behavior(obs.get_save_deliv_info_behavior(deliv1.get_value('code'), my.work_order_code, deliv1.get_value('title_code'), my.client_code, my.is_master_str))
            
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
        wo_search.add_filter('code',my.work_order_code)
        work_order = wo_search.get_sobject()
        wo_sk = work_order.get_search_key()
        proj_code = work_order.get_value('proj_code')
        wo_templ_code = work_order.get_value('work_order_templ_code')
        ws_search = Search("twog/work_order_sources")
        ws_search.add_filter("work_order_code",my.work_order_code)
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
        other_search.add_filter('proj_code',work_order.get_value('proj_code'))
        other_search.add_filter('process',ignore_processes, op="!=")
        all_other_wos = other_search.get_sobjects()
        
        all_other_interms = {}
        for other in all_other_wos:
            or_search = Search("twog/work_order_intermediate")
            or_search.add_filter('work_order_code',other.get_value('code'))
            other_reals = or_search.get_sobjects()
            for otr in other_reals:
                intermediate_file_code = otr.get_value('intermediate_file_code')
                inter_search = Search("twog/intermediate_file")
                inter_search.add_filter('code',intermediate_file_code)
                intermediate_file = inter_search.get_sobject()
                inter_title = intermediate_file.get_value('inter_file') 
                if other.get_value('code') not in all_other_interms.keys():
                    all_other_interms[other.get_value('code')] = []
                all_other_interms[other.get_value('code')].append([inter_title, intermediate_file.get_value('code')])
         
        order_code = my.order_sk.split('code=')[1]
        overhead = Table()
        overhead.add_attr('class','sp_overhead_%s' % my.work_order_code)
        overhead.add_attr('client_code',my.client_code)
        overhead.add_attr('is_master',my.is_master)
        overhead.add_attr('parent_pipe',my.parent_pipe)
        obs = OBScripts(order_sk=my.order_sk)
        table = Table()
        src_tbl = Table()
        for sc in work_order_sources:
            src_search = Search("twog/source")
            src_search.add_filter('code',sc.get_value('source_code'))
            src = src_search.get_sobjects()
            if len(src) > 0:
                src = src[0]
                src_tbl.add_row()
                if user_is_scheduler:
                    killer = src_tbl.add_cell(my.x_butt)
                    killer.add_style('cursor: pointer;')
                    killer.add_behavior(obs.get_source_killer_behavior(sc.get_value('code'), my.work_order_code, my.parent_pipe, my.client_code, my.is_master, '%s: %s' % (src.get_value('title'), src.get_value('episode'))))
                alabel = src_tbl.add_cell('Source: ')
                alabel.add_attr('align','center')
                popper = src_tbl.add_cell('<u>%s: %s</u>' % (src.get_value('title'), src.get_value('episode')))
                popper.add_attr('nowrap','nowrap')
                popper.add_style('cursor: pointer;')
                popper.add_behavior(obs.get_launch_wo_source_behavior(my.work_order_code, wo_sk, src.get_value('code')))
        table.add_row()
        table.add_cell(src_tbl)

        pass_search = Search("twog/work_order_passin")
        pass_search.add_filter('work_order_code',my.work_order_code)
        passins = pass_search.get_sobjects()

        table.add_row()
        table.add_cell(' ')
        table.add_cell(' ')
        add_deliv_passin_butt= table.add_cell('<input type="button" value="Add Permanent Element Pass-in"/>')
        add_deliv_passin_butt.add_attr('colspan','2')
        add_deliv_passin_butt.add_behavior(obs.get_add_deliverable_passin_behavior(my.work_order_code, wo_templ_code, proj_code))
        # Now do passed in permanent sources, which can be templated
        dsrc_tbl = Table()
        for p in passins:
            if p.get_value('deliverable_source_code') not in [None,'']:
                ds_search = Search("twog/source")
                ds_search.add_filter('code',p.get_value('deliverable_source_code'))
                d_source = ds_search.get_sobjects()
                if len(d_source) > 0: 
                    d_source = d_source[0]
                    dsrc_tbl.add_row()
                    if user_is_scheduler:
                        killer = dsrc_tbl.add_cell(my.x_butt)
                        killer.add_style('cursor: pointer;')
                        killer.add_behavior(obs.get_deliverable_passin_killer_behavior(p.get_value('code'), my.work_order_code, wo_templ_code, my.parent_pipe, my.client_code, my.is_master, '%s: %s' % (d_source.get_value('title'), d_source.get_value('episode'))))
                    alabel = dsrc_tbl.add_cell('Source: ')
                    alabel.add_attr('align','center')
                    popper = dsrc_tbl.add_cell('<u>%s: %s</u>' % (d_source.get_value('title'), d_source.get_value('episode')))
                    popper.add_attr('nowrap','nowrap')
                    popper.add_style('cursor: pointer;')
                    popper.add_behavior(obs.get_launch_wo_source_behavior(my.work_order_code, wo_sk, d_source.get_value('code')))
                    if my.is_master in [True,'true','True',1,'t']:
                        if p.get_value('passin_templ_code') in [None,'']:
                            template_button = ButtonSmallNewWdg(title="Template This Passed-in Source", icon=CustomIconWdg.icons.get('TEMPLATE'))
                            if my.is_master == 'true':
                                template_button.add_behavior(obs.get_template_deliverable_passin_behavior(my.work_order_code, wo_templ_code, p.get_value('code')))
                        else:
                            template_button = '<img border="0" style="vertical-align: middle" title="Templated" name="Templated" src="/context/icons/silk/tick.png">'
                        tb = dsrc_tbl.add_cell(template_button)
                        tb.add_attr('class', 'sp_templ_%s' % p.get_value('code'))
        if my.is_master in [True,'true','True',1,'t']:              
            table.add_row()
            table.add_cell(dsrc_tbl)

        table.add_row()
        divider = table.add_cell('<hr/>') 
        divider.add_attr('colspan','4')
        table.add_row()
        table.add_cell(' ')
        table.add_cell(' ')
        adinter_fm_butt = table.add_cell('<input type="button" value="Add Intermediate Pass-in"/>')
        adinter_fm_butt.add_attr('colspan','2')
        adinter_fm_butt.add_behavior(obs.get_add_intermediate_passin_behavior(my.work_order_code, wo_templ_code, proj_code))
        inter_tbl = Table()
        for p in passins:
            if p.get_value('intermediate_file_code') not in [None,'']:
                in_search = Search("twog/intermediate_file")
                in_search.add_filter('code',p.get_value('intermediate_file_code'))
                inter_f = in_search.get_sobjects()
                if len(inter_f) > 0: 
                    inter_f = inter_f[0]
                    inter_tbl.add_row()
                    if user_is_scheduler:
                        killer = inter_tbl.add_cell(my.x_butt)
                        killer.add_style('cursor: pointer;')
                        killer.add_behavior(obs.get_intermediate_passin_killer_behavior(p.get_value('code'), my.work_order_code, wo_templ_code, my.parent_pipe, my.client_code, my.is_master, inter_f.get_value('title')))
                    alabel = inter_tbl.add_cell('Intermediate: ')
                    alabel.add_attr('align','center')
                    popper = inter_tbl.add_cell('<u>%s</u>' % (inter_f.get_value('title')))
                    popper.add_attr('nowrap','nowrap')
                    popper.add_style('cursor: pointer;')
                    popper.add_behavior(obs.get_open_intermediate_behavior(inter_f.get_value('code'),my.work_order_code, my.client_code))
                    if my.is_master in [True,'true','True',1,'t']:
                        if p.get_value('passin_templ_code') in [None,'']:
                            template_button = ButtonSmallNewWdg(title="Template This Passed-in Intermediate File", icon=CustomIconWdg.icons.get('TEMPLATE'))
                        if my.is_master == 'true':
                            template_button.add_behavior(obs.get_template_intermediate_passin_behavior(my.work_order_code, wo_templ_code, p.get_value('code')))
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


class TitleAdderWdg(BaseRefreshWdg): 

    def init(my):
        my.search_type = 'twog/equipment_used'
        my.title = 'Equipment Used'
        my.sk = ''
        my.code = ''
        my.user = Environment.get_user_name() 
        my.parent_sk = ''
        my.order_sk = ''
        my.order_sid = ''
        my.client_code = ''
        my.formats = ['Electronic/File', 'HDCAM SR', 'NTSC', 'PAL']
        my.frame_rates = ProdSetting.get_seq_by_key('frame_rates')
        my.aspect_ratios = ['16x9 1.33', '16x9 1.33 Pan & Scan', '16x9 1.78 Anamorphic', '16x9 1.78 Full Frame',
                            '16x9 1.85 Letterbox', '16x9 1.85 Matted', '16x9 1.85 Matted Anamorphic', '16x9 2.20',
                            '16x9 2.20 Letterbox', '16x9 2.35 Anamorphic', '16x9 2.35 Letterbox', '16x9 2.40 Letterbox',
                            '16x9 2.55 Letterbox', '4x3 1.33 Full Frame', '4x3 1.78 Letterbox', '4x3 1.85 Letterbox',
                            '4x3 2.35 Letterbox', '4x3 2.40 Letterbox']
        my.standards = ['625', '525', '720', '1080 (4:4:4)', '1080', 'PAL', 'NTSC']

    def get_display(my):
        my.client_code = str(my.kwargs.get('client_code'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        my.order_sid = str(my.kwargs.get('order_sid'))
        order_code = my.order_sk.split('code=')[1]
        order_search = Search("twog/order")
        order_search.add_filter('code',order_code)
        the_order = order_search.get_sobject()
        obs = OBScripts(order_sk=my.order_sk)
        table = Table()
        table.add_attr('class', 'title_adder_top_%s' % my.order_sk)
        table.add_row()
        table.add_cell('Title: ')
        cell1 = table.add_cell('<input class="tadd_title" type="text"/>')
        cell1.add_attr('colspan','5')
        cell1.add_attr('align','left')

        table.add_row()
        empt = table.add_cell(' ')
        beg = table.add_cell('Range Begin')
        empt = table.add_cell(' ')
        end = table.add_cell('Range End')
        formatter = table.add_cell('# Formatter')
        empt = table.add_cell(' ')
        beg.add_attr('nowrap', 'nowrap')
        beg.add_attr('valign', 'bottom')
        end.add_attr('nowrap', 'nowrap')
        end.add_attr('valign', 'bottom')
        formatter.add_attr('nowrap', 'nowrap')
        formatter.add_attr('valign', 'bottom')
        beg.add_style('font-size: 50%;')
        end.add_style('font-size: 50%;')
        formatter.add_style('font-size: 50%;')
        singl = table.add_cell('Single Episode Name, or Comma Seperated Episode Names')
        singl.add_attr('valign','bottom')
        singl.add_style('font-size: 50%;')
        table.add_row()
        table.add_cell('Episode: ')
        table.add_cell('<input class="tadd_epi_range_1" type="text" style="width: 35px;"/>')
        ctr = table.add_cell(' - ')
        ctr.add_attr('align','center')
        table.add_cell('<input class="tadd_epi_range_2" type="text" style="width: 35px;"/>')
        table.add_cell('<input class="tadd_episode_format" type="text" style="width: 70px;"/>')
        table.add_cell(' OR ')
        table.add_cell('<input class="tadd_epi_name" type="text" style="width: 200px;"/>')
        #There is no territory table in Tactic rigt now. We may want to do that in the future
        territories_str = 'Afghanistan|Aland Islands|Albania|Algeria|American Samoa|Andorra|Angola|Anguilla|Antigua and Barbuda|Argentina|Armenia|Aruba|Australia|Austria|Azerbaijan|Bahamas|Bahrain|Bangladesh|Barbados|Belarus|Belgium|Belize|Benin|Bermuda|Bhutan|Bolivia|Bonaire|Bosnia and Herzegovina|Botswana|Bouvet Island|Brazil|Brunei Darussalam|Bulgaria|Burkina Faso|Burundi|Cambodia|Cameroon|Canada|Cantonese|Cape Verde|Cayman Islands|Central African Republic|Chad|Chile|China|Christmas Island|Cocos Islands|Colombia|Comoros|Congo|Dem. Rep. of Congo|Cook Islands|Costa Rica|Croatia|Cuba|Curacao|Cyprus|Czech|Denmark|Djibouti|Dominica|Dominican Republic|Ecuador|Egypt|El Salvador|English|Equatorial Guinea|Eritrea|Estonia|Ethiopia|Falkland Islands|Faroe Islands|Fiji|Finland|France|French Guiana|French Polynesia|Gabon|Gambia|Georgia|Germany|Ghana|Gibraltar|Greece|Greek|Greenland|Grenada|Guadeloupe|Guam|Guatemala|Guernsey|Guinea|Guinea-Bissau|Guyana|Haiti|Honduras|Hong Kong|Hungary|Iceland|India|Indonesia|Iran|Iraq|Ireland|Isle of Man|Israel|Italy|Ivory Coast|Jamaica|Japan|Jersey|Jordan|Kazakhstan|Kenya|Kiribati|Kuwait|Kyrgyztan|Laos|Latin America|Latin Spanish|Latvia|Lebanon|Lesotho|Liberia|Libya|Liechtenstein|Lithuania|Luzembourg|Macao|Macedonia|Madagascar|Malawi|Malaysia|Maldives|Mali|Malta|Marshall Islands|Martinique|Mauritania|Mauritius|Mayotte|Mexico|Micronesia|Moldova|Monaco|Mongolia|Montenegro|Montserrat|Morocco|Mozambique|Multi-language|Myanmar|Namibia|Nauru|Nepal|Netherlands|New Caledonia|New Zealand|Nicaragua|Niger|Nigeria|Niue|Norfolk Island|North Korea|Northern Mariana Islands|Norway|Oman|Pakistan|Palau|Palestine|Panama|Papua New Guinea|Pan-Asia|Paraguay|Peru|Philippines|Pitcairn|Poland|Portugal|Puerto Rico|Qatar|Reunion|Romania|Russia|Russian|Rwanda|St Barthelemy|St Helena|St Kitts and Nevis|St Lucia|St Martin|St Pierre and Miquelo|St Vincent and Grenadines|Samoa|San Marino|Sao Tome and Principe|Saudi Arabia|Senegal|Serbia|Seychelles|Sierra Leone|Signapore|Sint Maarten|Slovakia|Slovenia|Solomon Islands|Somalia|South Africa|South Georgia and Swch Islands|South Korea|South Sudan|Spain|Sri Lanka|Sudan|Suriname|Svalbard|Swaziland|Sweden|Switzerland|Syria|Taiwan|Tajikistan|Tanzania|Thai|Thailand|Timor-Leste|Togo|Tokelau|Tonga|Trinidad and Tobago|Tunisia|Turkey|Turkmenistan|Turks and Caicos Islands|Tuvalu|Uganda|Ukraine|UAE|United Kingdom|United States|Uruguay|Uzbekistan|Vanuatu|Various|Vatican|Venezuela|Vietnam|Virgin Islands|Wallis and Futuna|West Indies|Western Sahara|Yemen|Zambia|Zimbabwe'
        territories = territories_str.split('|')
        territory_sel = SelectWdg('tadd_territory')
        territory_sel.append_option('--Select--','--Select--')
        for terr in territories:
            territory_sel.append_option(terr, terr)
        #There is no language table in Tactic. We may want to change that in the future.
        language_str = 'Abkhazian|Afar|Afrikaans|Akan|Albanian|All Languages|Amharic|Arabic|Arabic - Egypt|Arabic - UAE and Lebanon|Aragonese|Aramaic|Armenian|Assamese|Avaric|Avestan|Aymara|Azerbaijani|Bahasa (Not Specified)|Bashkir|Basque|Belarusian|Bengali|Bihari languages|Bislama|Bosnian|Breton|Bulgarian|Burmese|Catalan|Catalan (Valencian)|Central Khmer|Chamorro|Chechen|Chichewa (Chewa, Nyanja)|Chinese (Cantonese)|Chinese (Mandarin - Not Specified)|Chinese (Mandarin - PRC)|Chinese (Mandarin - Taiwan)|Chinese Simplified Characters|Chinese Simplified Characters - Malaysia|Chinese Simplified Characters - PRC|Chinese Simplified Characters - Singapore|Chinese Traditional Characters|Chinese Traditional Characters - Hong Kong|Chinese Traditional Characters - Taiwan|Chuvash|Cornish|Corsican|Cree|Croatian|Czech|Danish|Dari|Divehi (Dhivehi, Maldivian)|Dutch|Dzongkha|English|English - Australian|English - British|Esperanto|Estonian|Ewe|Faroese|Farsi (Persian)|Fijian|Finnish|Flemish|French (Not Specified)|French - Canadian (Quebecois)|French - France|Fulah|Gaelic (Scottish Gaelic)|Galician|Georgian|German|German - Austrian|German - Swiss/Alsatian|Greek - Modern|Guarani|Gujarati|Haitian (Haitian Creole)|Hausa|Hawaiian|Hebrew|Herero|Hindi|Hiri Motu|Hungarian|Icelandic|Ido|Indonesian Bahasa|Interlingua (International Auxiliary Language Association)|Interlingue (Occidental)|Inuktitut|Inupiaq|Italian|Japanese|Javanese|Kalaallisut (Greenlandic)|Kannada|Kanuri|Kashmiri|Kazakh|Kikuyu (Gikuyu)|Kinyarwanda|Kirghiz (Kyrgyz)|Komi|Kongo|Korean|Kuanyama (Kwanyama)|Kurdish|Lao|Latin|Latvian|Limburgan (Limburger, Limburgish)|Lingala|Lithuanian|Luba-Katanga|Luxembourgish (Letzeburgesch)|MOS (no audio)|Macedonian|Malagasy|Malay Bahasa|Malayalam|Maltese|Maori|Marathi|Marshallese|Mauritian Creole|Mayan|Moldavian|Mongolian|Nauru|Navajo (Navaho)|Ndebele - North|Ndebele - South|Ndonga|Nepali|No Audio|Northern Sami|Norwegian|Occitan|Ojibwa|Oriya|Oromo|Ossetian (Ossetic)|Palauan|Pali|Panjabi (Punjabi)|Polish|Polynesian|Portuguese (Not Specified)|Portuguese - Brazilian|Portuguese - European|Pushto (Pashto)|Quechua|Romanian|Romanian (Moldavian)|Romansh|Rundi|Russian|Samoan|Sango|Sanskrit|Sardinian|Sepedi|Serbian|Serbo-Croatian|Setswana|Shona|Sichuan Yi (Nuosu)|Sicilian|Silent|Sindhi|Sinhala (Sinhalese)|Slavic|Slovak|Slovenian|Somali|Sotho, Sesotho|Spanish (Not Specified)|Spanish - Argentinian|Spanish - Castilian|Spanish - Latin American|Spanish - Mexican|Sudanese|Swahili|Swati|Swedish|Tagalog|Tahitian|Taiwanese (Min Nah)|Tajik|Tamil|Tatar|Telugu|Tetum|Textless|Thai|Tibetan|Tigrinya|Tok Pisin|Tongan|Tsonga|Turkish|Turkmen|Tuvaluan|Twi|Uighur (Uyghur)|Ukrainian|Unavailable|Unknown|Unknown|Urdu|Uzbek|Valencian|Venda|Vietnamese|Volapuk|Walloon|Welsh|Western Frisian|Wolof|Xhosa|Yiddish|Yoruba|Zhuang (Chuang)|Zulu'

        languages = language_str.split('|')
        language_sel = SelectWdg('tadd_language')
        language_sel.append_option('--Select--', '--Select--')
        for language in languages:
            language_sel.append_option(language, language)

        client_search = Search("twog/client")
        client_search.add_order_by('name desc')
        clients = client_search.get_sobjects()

        pipe_search = Search("sthpw/pipeline")
        pipe_search.add_filter('search_type', 'twog/title')
        pipelines = pipe_search.get_sobjects()
        client_pull = SelectWdg('tadd_client_pull')
        client_name = ''
        if len(clients) > 0:
            client_pull.append_option('--Select--', 'NOTHINGXsXNOTHING')
            for client in clients:
                client_pull.append_option(client.get_value('name'), '%sXsX%s' % (client.get_value('code'),client.get_value('name'))) 
                if client.get_value('code') == my.client_code:
                    client_name = client.get_value('name')
                    client_name_pull = '%sXsX%s' % (client.get_value('code'),client.get_value('name'))
                    client_pull.set_value(client_name_pull)
        client_pull.add_behavior(obs.get_client_change_behavior(my.order_sk))
        platform_search = Search("twog/platform")
        platform_search.add_order_by('name desc')
        outlet_list = platform_search.get_sobjects()
        outlet_pull = SelectWdg('tadd_outlet_pull')
        outlet_pull.append_option('--Select--', 'NOTHINGXsXNOTHING')
        for outlet in outlet_list:
            outlet_pull.append_option(outlet.get_value('name'), outlet.get_value('name'))
        pipe_pull = SelectWdg('tadd_pipe_pull')
        if len(pipelines) > 0:
            pipe_pull.append_option('--Select--', 'NOTHINGXsXNOTHING')
            for pipe in pipelines:
                if not pipe.get_value('hide'):
                    if pipe.get_value('code').split('_')[0] == client_name:
                        pipe_pull.append_option(pipe.get_value('code'), pipe.get_value('code'))
            for pipe in pipelines:
                if not pipe.get_value('hide'):
                    if pipe.get_value('code').split('_')[0] != client_name:
                        pipe_pull.append_option(pipe.get_value('code'), pipe.get_value('code'))
        pipe_pull.add_behavior(obs.get_pipeline_change_behavior(my.order_sk))


        dlv_standard_pull = SelectWdg('tadd_deliverable_standard')
        dlv_standard_pull.append_option('--Select--', 'NOTHINGXsXNOTHING')
        for s in my.standards:
            dlv_standard_pull.append_option(s, s)
        dlv_format_pull = SelectWdg('tadd_deliverable_format')
        dlv_format_pull.append_option('--Select--', 'NOTHINGXsXNOTHING')
        for f in my.formats:
            dlv_format_pull.append_option(f, f)
        dlv_aspect_ratio_pull = SelectWdg('tadd_deliverable_aspect_ratio')
        dlv_aspect_ratio_pull.append_option('--Select--', 'NOTHINGXsXNOTHING')
        for a in my.aspect_ratios:
            dlv_aspect_ratio_pull.append_option(a, a)
        dlv_frame_rate_pull = SelectWdg('tadd_deliverable_frame_rate')
        dlv_frame_rate_pull.append_option('--Select--', 'NOTHINGXsXNOTHING')
        for f in my.frame_rates:
            dlv_frame_rate_pull.append_option(f, f)

        status_triggers_pull = SelectWdg('tadd_status_triggers')
        for f in ['Yes', 'No']:
            status_triggers_pull.append_option(f, f)

        priority_triggers_pull = SelectWdg('tadd_priority_triggers')
        for f in ['Yes', 'No']:
            priority_triggers_pull.append_option(f, f)

        table.add_row()
        t1 = table.add_cell('Territory: ')
        t2 = table.add_cell(territory_sel)
        t1.add_attr('align', 'left')
        t2.add_attr('colspan', '6')
        t2.add_attr('align', 'left')

        table.add_row()
        t1 = table.add_cell('Language: ')
        t2 = table.add_cell(language_sel)
        t1.add_attr('align', 'left')
        t2.add_attr('colspan', '6')
        t2.add_attr('align', 'left')
        
        table.add_row()
        c1 = table.add_cell('Client: ')
        c2 = table.add_cell(client_pull)
        c1.add_attr('align', 'left')
        c2.add_attr('colspan', '6')
        c2.add_attr('align', 'left')

        table.add_row()
        o1 = table.add_cell('Platform: ')
        o2 = table.add_cell(outlet_pull)
        o1.add_attr('align', 'left')
        o2.add_attr('colspan', '6')
        o2.add_attr('align', 'left')

        table.add_row()
        r1 = table.add_cell('Title Id Num: ')
        r2 = table.add_cell('<input type="text" class="tadd_title_id_number"/>')
        r1.add_attr('align', 'left')
        r2.add_attr('colspan', '6')
        r2.add_attr('align', 'left')

        table.add_row()
        w1 = table.add_cell('Total Program Run Time: ')
        w2 = table.add_cell('<input type="text" class="tadd_total_program_run_time"/>')
        w1.add_attr('align', 'left')
        w2.add_attr('colspan', '6')
        w2.add_attr('align', 'left')

        table.add_row()
        z1 = table.add_cell('Total Run Time w/ Textless: ')
        z2 = table.add_cell('<input type="text" class="tadd_total_run_time_with_textless"/>')
        z1.add_attr('align', 'left')
        z2.add_attr('colspan', '6')
        z2.add_attr('align', 'left')

        table.add_row()
        p1 = table.add_cell('Pipeline: ')
        p2 = table.add_cell(pipe_pull)
        p1.add_attr('align', 'left')
        p2.add_attr('colspan', '6')
        p2.add_attr('align', 'left')

        table.add_row()
        sd = table.add_cell('Start Date: ')
        sd.add_attr('nowrap', 'nowrap')
        start = CalendarInputWdg("tadd_start_date")
        if the_order.get_value('start_date') not in [None,'']:
            start.set_option('default', fix_date(the_order.get_value('start_date')))
        start.set_option('show_activator', True)
        start.set_option('show_confirm', False)
        start.set_option('show_text', True)
        start.set_option('show_today', False)
        start.set_option('read_only', False)    
        start.get_top().add_style('width: 150px')
        start.set_persist_on_submit()
        start_date = table.add_cell(start)
        start_date.add_attr('colspan','7')
        start_date.add_attr('nowrap','nowrap')

        table.add_row()
        ed = table.add_cell('Due Date: ')
        ed.add_attr('nowrap','nowrap')
        end = CalendarInputWdg("tadd_due_date")
        if the_order.get_value('due_date') not in [None,'']:
            end.set_option('default', fix_date(the_order.get_value('due_date')))
        end.set_option('show_activator', True)
        end.set_option('show_confirm', False)
        end.set_option('show_text', True)
        end.set_option('show_today', False)
        end.set_option('read_only', False)    
        end.get_top().add_style('width: 150px')
        end.set_persist_on_submit()
        end_date = table.add_cell(end)
        end_date.add_attr('colspan', '7')
        end_date.add_attr('nowrap', 'nowrap')

        table.add_row()
        rm = table.add_cell('Revenue Month: ')
        rm.add_attr('nowrap','nowrap')
        rem = CalendarInputWdg("tadd_rm_date")
        if the_order.get_value('expected_delivery_date') not in [None,'']:
            rem.set_option('default', fix_date(the_order.get_value('expected_delivery_date')))
        rem.set_option('show_activator', True)
        rem.set_option('show_confirm', False)
        rem.set_option('show_text', True)
        rem.set_option('show_today', False)
        rem.set_option('read_only', False)    
        rem.get_top().add_style('width: 150px')
        rem.set_persist_on_submit()
        rem_date = table.add_cell(rem)
        rem_date.add_attr('colspan', '7')
        rem_date.add_attr('nowrap', 'nowrap')

        table.add_row()
        r8 = table.add_cell('Expected Price: ')
        r9 = table.add_cell('<input type="text" class="tadd_expected_price"/>')
        r8.add_attr('align', 'left')
        r9.add_attr('colspan', '6')
        r9.add_attr('align', 'left')

        table.add_row()
        taa = table.add_cell('Description')
        taa.add_attr('valign', 'top')
        ta1 = table.add_cell('<textarea cols="50" rows="10" class="tadd_description"></textarea>')
        ta1.add_attr('colspan', '6')
        
        table.add_row()
        s1 = table.add_cell('Deliverable Standard: ')
        s2 = table.add_cell(dlv_standard_pull)
        s1.add_attr('align', 'left')
        s2.add_attr('colspan', '6')
        s2.add_attr('align', 'left')

        table.add_row()
        s1 = table.add_cell('Deliverable Aspect Ratio: ')
        s2 = table.add_cell(dlv_aspect_ratio_pull)
        s1.add_attr('align', 'left')
        s2.add_attr('colspan', '6')
        s2.add_attr('align', 'left')

        table.add_row()
        s1 = table.add_cell('Deliverable Frame Rate: ')
        s2 = table.add_cell(dlv_frame_rate_pull)
        s1.add_attr('align', 'left')
        s2.add_attr('colspan', '6')
        s2.add_attr('align', 'left')

        table.add_row()
        s1 = table.add_cell('Deliverable Format: ')
        s2 = table.add_cell(dlv_format_pull)
        s1.add_attr('align', 'left')
        s2.add_attr('colspan', '6')
        s2.add_attr('align', 'left')

        table.add_row()
        s1 = table.add_cell('Status Triggers?: ')
        s2 = table.add_cell(status_triggers_pull)
        s1.add_attr('align', 'left')
        s2.add_attr('colspan', '6')
        s2.add_attr('align', 'left')

        table.add_row()
        s1 = table.add_cell('Priority Triggers?: ')
        s2 = table.add_cell(priority_triggers_pull)
        s1.add_attr('align', 'left')
        s2.add_attr('colspan', '6')
        s2.add_attr('align', 'left')

        table.add_row()
        tca = table.add_cell('Deliverable Specs')
        tca.add_attr('valign', 'top')
        ta8 = table.add_cell('<textarea cols="50" rows="10" class="tadd_delivery_specs"></textarea>')
        ta8.add_attr('colspan', '6')

        table.add_row()
        table.add_cell('Keywords')
        ta2 = table.add_cell('<textarea cols="50" class="tadd_keywords"></textarea>')
        ta2.add_attr('colspan', '6')

        go_butt = ActionButtonWdg(tip='Create', title='Create')
        go_butt.add_behavior(obs.get_create_titles_behavior(my.order_sk,my.order_sid,my.user))
        table.add_row()
        bottom_butt = table.add_cell(go_butt)
        bottom_butt.add_attr('colspan', '7')
        bottom_butt.add_attr('align', 'center')

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

class MultiManualAdderWdg(BaseRefreshWdg):
    def init(my):
        my.server = TacticServerStub.get()
        my.order_sk = ''
        if 'order_sk' in my.kwargs.keys():
            my.order_sk = str(my.kwargs.get('order_sk'))
        my.search_type = my.kwargs.get('search_type')
        my.name_type = 'Work Order'
        if my.search_type == 'twog/proj':
            my.name_type = 'Proj'
        my.parent_sk = my.kwargs.get('parent_sk')
        my.parent_code = my.parent_sk.split('code=')[1]
        my.title_code = ''
        if 'TITLE' in my.parent_code:
            my.title_code = my.parent_code
        else:
            my.title_code = my.server.eval("@GET(twog/proj['code','%s'].title_code)" % my.parent_code)[0]
        my.user_name = Environment.get_user_name() 

    def get_save(my):
        behavior = None
        if my.search_type == 'twog/proj':
            behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                            try{
                                   var server = TacticServerStub.get();
                                   order_sk = '%s';
                                   order_code = order_sk.split('code=')[1];
                                   top_el = document.getElementById('manual_proj_adder_top_' + order_sk);
                                   title_code = top_el.getAttribute('title_code');
                                   parent_sk = top_el.getAttribute('parent_sk');
                                   user_name = top_el.getAttribute('user_name');
                                   make_em = [];
                                   comma_names = top_el.getElementById('comma_names').value;
                                   if(comma_names != '' && comma_names != ' ' && comma_names != null){
                                       make_em = comma_names.split(',');
                                   }else{
                                       primary_name = top_el.getElementById('primary_name').value;
                                       from_number = top_el.getElementById('from_number').value;
                                       to_number = top_el.getElementById('to_number').value;
                                       if(isNaN(from_number)){
                                           from_number = -1;
                                       }else{
                                           from_number = Number(from_number);
                                           if(isNaN(to_number)){
                                               to_number = -1;
                                           }else{
                                               to_number = Number(to_number);
                                           }
                                       }
                                       if(from_number == -1){
                                           make_em.push(primary_name);
                                       }else{
                                           if(to_number == -1){
                                               make_em.push(primary_name + ' ' + from_number);
                                           }else{
                                               for(var r = from_number; r < to_number + 1; r++){
                                                   make_em.push(primary_name + ' ' + r);
                                               } 
                                           }     
                                       }
                                   }
                                   dates = top_el.getElementsByClassName('spt_calendar_input');
                                   start_date = ''
                                   due_date = '';
                                   for(var r = 0; r < dates.length; r++){
                                       dname = dates[r].getAttribute('name');
                                       val = dates[r].value;
                                       if(dname == 'start_date'){
                                           start_date = val;
                                       }else if(dname = 'due_date'){
                                           due_date = val;
                                       }
                                   }
                                   priority = top_el.getElementById('priority').value;
                                   platform = top_el.getElementById('platform').value;
                                   //
                                   title = server.eval("@SOBJECT(twog/title['code','" + title_code + "'])")[0];
                                   order = server.eval("@SOBJECT(twog/order['code','" + order_code + "'])")[0];
                                   client_code = title.client_code
                                   client = server.eval("@SOBJECT(twog/client['code','" + client_code + "'])");
                                   client_name = '';
                                   if(client.length > 0){
                                       client = client[0];
                                       client_name = client.name
                                   }
                                   codes_inorder = [title_code];
                                   //HERE INSERT TASKS AND PROJS
                                   spt.app_busy.show('CREATING PROJECTS');

                                   nada_before = true;
                                   from_els = top_el.getElementsByClassName('from_check');
                                   for(var r = 0; r < from_els.length; r++){
                                       if(from_els[r].getAttribute('checked') == 'true'){
                                           nada_before = false;
                                       }
                                   }
                                   for(var r = 0; r < make_em.length; r++){ 
                                       filler = 'NEEDS_TO_BE_FILLED'
                                       if(r == 0 && nada_before){
                                           filler = ''
                                       }
                                       new_proj = server.insert('twog/proj', {'process': make_em[r].trim(), 'title_code': title_code, 'parent_pipe': 'Manually Inserted into ' + title.pipeline_code, 'login': user_name, 'creation_type': 'hackup', 'status': 'Pending', 'order_code': order_code, 'client_code': client_code, 'priority': priority, 'platform': platform, 'client_name': client_name, 'title': title.title, 'episode': title.episode, 'territory': title.territory, 'po_number': order.po_number, 'order_name': order.name, 'start_date': start_date, 'due_date': due_date, 'comes_from': filler, 'goes_to': 'NEEDS_TO_BE_FILLED'})
                                       codes_inorder.push(new_proj.code);
                                       spt.app_busy.show('CREATING ' + new_proj.process);
                                       new_task_data = {'process': new_proj.process, 'context': new_proj.process, 'active': false, 'client_name': client_name, 'title': title.title, 'episode': title.episode, 'territory': title.territory, 'creator_login': user_name, 'lookup_code': new_proj.code, 'search_type': 'twog/title?project=twog', 'search_id': title.id, 'pipeline_code': 'Manually Inserted into ' + title.pipeline_code, 'po_number': order.po_number, 'status': 'Pending', 'title_code': title_code, 'order_code': order_code, 'order_name': order.name, 'client_code': client_code, 'platform': new_proj.platform, 'priority': priority, 'territory': title.territory, 'project_code': 'twog', 'bid_end_date': due_date, 'bid_start_date': start_date};
                                       if(order.classification == 'in_production' || order.classification == 'In Production'){
                                           new_task_data['active'] = true;
                                       }
                                       new_task = server.insert('sthpw/task',new_task_data);
                                       server.update(new_proj.__search_key__, {'task_code': new_task.code}); 
                                   }
                                   spt.app_busy.show('CREATING CONNECTIONS');
                                   //CONNECT EACH TO THE NEXT AS A HACKUP
                                   for(var r = 0; r < codes_inorder.length - 1; r++){
                                       server.insert('twog/hackpipe_out', {'lookup_code': codes_inorder[r], 'out_to': codes_inorder[r + 1]})
                                   }
                                   //DO FINAL HACKUP CONNECTIONS HERE WITH THE FIRST PROJ INSERTED CONNECTING TO FROMS, LAST PROJ CONNECTING TO TOS
                                   from_els = top_el.getElementsByClassName('from_check');
                                   for(var r = 0; r < from_els.length; r++){
                                       if(from_els[r].getAttribute('checked') == 'true'){
                                           server.insert('twog/hackpipe_out', {'lookup_code': from_els[r].getAttribute('id'), 'out_to': codes_inorder[1]})
                                       }
                                   }
                                   to_els = top_el.getElementsByClassName('to_check');
                                   for(var r = 0; r < to_els.length; r++){
                                       if(to_els[r].getAttribute('checked') == 'true'){
                                           server.insert('twog/hackpipe_out', {'out_to': to_els[r].getAttribute('id'), 'lookup_code': codes_inorder[codes_inorder.length - 1]})
                                       }
                                   }
                                   last_inserted = codes_inorder[codes_inorder.length - 1];
                                   if(last_inserted.indexOf('PROJ') != -1){
                                       server.insert('twog/simplify_pipe', {'proj_code': last_inserted});
                                   }else{
                                       server.insert('twog/simplify_pipe', {'work_order_code': last_inserted});
                                   }

                                   var big_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                                   display_mode = big_el.getAttribute('display_mode');
                                   user = big_el.getAttribute('user');
                                   groups_str = big_el.get('groups_str');
                                   allowed_titles = big_el.getAttribute('allowed_titles');
                                   parent_el = big_el.getElementsByClassName('cell_' + parent_sk)[0];
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
             ''' % (my.order_sk)}
        elif my.search_type == 'twog/work_order':
            behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        function encode_utf8( s )
                        {
                            return unescape( encodeURIComponent( s ) );
                        }
                            try{
                                   var server = TacticServerStub.get();
                                   order_sk = '%s';
                                   order_code = order_sk.split('code=')[1];
                                   top_el = document.getElementById('manual_wo_adder_top_' + order_sk);
                                   title_code = top_el.getAttribute('title_code');
                                   parent_sk = top_el.getAttribute('parent_sk');
                                   proj_code = parent_sk.split('code=')[1];
                                   user_name = top_el.getAttribute('user_name');
                                   make_em = [];
                                   comma_names = top_el.getElementById('comma_names').value;
                                   if(comma_names != '' && comma_names != ' ' && comma_names != null){
                                       make_em = comma_names.split(',');
                                   }else{
                                       primary_name = top_el.getElementById('primary_name').value;
                                       from_number = top_el.getElementById('from_number').value;
                                       to_number = top_el.getElementById('to_number').value;
                                       if(isNaN(from_number)){
                                           from_number = -1;
                                       }else{
                                           from_number = Number(from_number);
                                           if(isNaN(to_number)){
                                               to_number = -1;
                                           }else{
                                               to_number = Number(to_number);
                                           }
                                       }
                                       if(from_number == -1){
                                           make_em.push(primary_name);
                                       }else{
                                           if(to_number == -1){
                                               make_em.push(primary_name + ' ' + from_number);
                                           }else{
                                               for(var r = from_number; r < to_number + 1; r++){
                                                   make_em.push(primary_name + ' ' + r);
                                               } 
                                           }     
                                       }
                                   }
                                   dates = top_el.getElementsByClassName('spt_calendar_input');
                                   start_date = ''
                                   due_date = '';
                                   for(var r = 0; r < dates.length; r++){
                                       dname = dates[r].getAttribute('name');
                                       val = dates[r].value;
                                       if(dname == 'start_date'){
                                           start_date = val;
                                       }else if(dname = 'due_date'){
                                           due_date = val;
                                       }
                                   }
                                   instructions = top_el.getElementById('instructions').value;
                                   instructions = encode_utf8(instructions);
                                   assigned_login_group = top_el.getElementById('assigned_login_group').value;
                                   assigned = top_el.getElementById('assigned').value;
                                   title_id_num = top_el.getElementById('title_id_num').value;
                                   estimated_work_hours = top_el.getElementById('estimated_work_hours').value;
                                   proj = server.eval("@SOBJECT(twog/proj['code','" + proj_code + "'])")[0];
                                   title = server.eval("@SOBJECT(twog/title['code','" + title_code + "'])")[0];
                                   order = server.eval("@SOBJECT(twog/order['code','" + order_code + "'])")[0];
                                   client_code = title.client_code
                                   client = server.eval("@SOBJECT(twog/client['code','" + client_code + "'])");
                                   client_name = '';
                                   client_hold = 'no problems';
                                   if(client.length > 0){
                                       client = client[0];
                                       client_name = client.name
                                       client_billing_status = client.billing_status;
                                       if(client_billing_status.indexOf('Do Not Book') != -1){
                                           client_hold = 'nobook';
                                       }else if(client_billing_status.indexOf('Do Not Ship') != -1){
                                           client_hold = 'noship';
                                       }
                                   }
                                   codes_inorder = [proj_code];
                                   //HERE INSERT TASKS AND WOS
                                   spt.app_busy.show('CREATING WORK ORDERS');
                                   nada_before = true;
                                   from_els = top_el.getElementsByClassName('from_check');
                                   for(var r = 0; r < from_els.length; r++){
                                       if(from_els[r].getAttribute('checked') == 'true'){
                                           nada_before = false;
                                       }
                                   }
                                   for(var r = 0; r < make_em.length; r++){ 
                                       filler = 'NEEDS_TO_BE_FILLED'
                                       if(r == 0 && nada_before){
                                           filler = ''
                                       }
                                       new_wo = server.insert('twog/work_order', {'process': make_em[r].trim(), 'work_group': assigned_login_group, 'instructions': instructions, 'estimated_work_hours': estimated_work_hours, 'proj_code': proj_code, 'parent_pipe': 'Manually Inserted into ' + proj.pipeline_code, 'login': user_name, 'creation_type': 'hackup', 'title_code': title.code, 'order_code': order_code, 'client_code': client_code, 'client_name': client_name, 'assigned': assigned, 'platform': proj.platform, 'title_id_number': title_id_num, 'territory': title.territory, 'priority': proj.priority, 'title': title.title, 'episode': title.episode, 'due_date': due_date, 'po_number': order.po_number, 'order_name': order.name, 'comes_from': filler, 'goes_to': 'NEEDS_TO_BE_FILLED'});
                                       spt.app_busy.show('CREATING ' + new_wo.process);
                                       codes_inorder.push(new_wo.code);
                                       new_task_data = {'process': new_wo.process, 'context': new_wo.process, 'assigned_login_group': assigned_login_group, 'assigned': assigned, 'active': false, 'client_name': client_name, 'title': title.title, 'episode': title.episode, 'territory': title.territory, 'creator_login': user_name, 'lookup_code': new_wo.code, 'search_type': 'twog/proj?project=twog', 'search_id': proj.id, 'pipeline_code': 'Manually Inserted into ' + proj.pipeline_code, 'po_number': order.po_number, 'status': 'Pending', 'title_code': title.code, 'order_code': order_code, 'order_name': order.name, 'client_code': client_code, 'client_hold': client_hold, 'platform': proj.platform, 'priority': proj.priority, 'project_code': 'twog', 'bid_end_date': due_date, 'bid_start_date': start_date};
                                       if(order.classification == 'in_production' || order.classification == 'In Production'){
                                           new_task_data['active'] = true;
                                       }
                                       new_task = server.insert('sthpw/task',new_task_data);
                                       server.update(new_wo.__search_key__, {'task_code': new_task.code}); 
                                   }
                                   //CONNECT EACH TO THE NEXT AS A HACKUP
                                   spt.app_busy.show('CREATING CONNECTIONS');
                                   for(var r = 0; r < codes_inorder.length - 1; r++){
                                       server.insert('twog/hackpipe_out', {'lookup_code': codes_inorder[r], 'out_to': codes_inorder[r + 1]})
                                   }
                                   //DO FINAL HACKUP CONNECTIONS HERE WITH THE FIRST PROJ INSERTED CONNECTING TO FROMS, LAST PROJ CONNECTING TO TOS
                                   from_els = top_el.getElementsByClassName('from_check');
                                   for(var r = 0; r < from_els.length; r++){
                                       if(from_els[r].getAttribute('checked') == 'true'){
                                           server.insert('twog/hackpipe_out', {'lookup_code': from_els[r].getAttribute('id'), 'out_to': codes_inorder[1]})
                                       }
                                   }
                                   to_els = top_el.getElementsByClassName('to_check');
                                   for(var r = 0; r < to_els.length; r++){
                                       if(to_els[r].getAttribute('checked') == 'true'){
                                           server.insert('twog/hackpipe_out', {'out_to': to_els[r].getAttribute('id'), 'lookup_code': codes_inorder[codes_inorder.length - 1]})
                                       }
                                   }
                                   last_inserted = codes_inorder[codes_inorder.length - 1];
                                   if(last_inserted.indexOf('PROJ') != -1){
                                       server.insert('twog/simplify_pipe', {'proj_code': last_inserted});
                                   }else{
                                       server.insert('twog/simplify_pipe', {'work_order_code': last_inserted});
                                   }
                                  
                                   //AT THE END HERE, WE WANT TO ADD EQUIPMENT TO ALL INSERTED WOS

                                   var big_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                                   display_mode = big_el.getAttribute('display_mode');
                                   user = big_el.getAttribute('user');
                                   groups_str = big_el.get('groups_str');
                                   allowed_titles = big_el.getAttribute('allowed_titles');
                                   parent_el = big_el.getElementsByClassName('cell_' + parent_sk)[0];
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
             ''' % (my.order_sk)}
        return behavior

    def get_display(my):
        table = Table()
        tbl_id = 'manual_wo_adder_top_%s' % my.order_sk
        if 'proj' in my.search_type:
            tbl_id = 'manual_proj_adder_top_%s' % my.order_sk
        table.add_attr("id",tbl_id)
        table.add_attr('search_type',my.search_type)
        table.add_attr('order_sk',my.order_sk)
        table.add_attr('parent_sk',my.parent_sk)
        table.add_attr('title_code',my.title_code)
        table.add_attr('user_name',my.user_name)

        ctbl = Table()
        ctbl.add_row()
        c1 = ctbl.add_cell('%s Names (Comma Delimited)' % my.name_type)
        c1.add_attr('nowrap','nowrap')
        ctbl.add_row()
        ctbl.add_cell('<textarea cols="100" rows="5" id="comma_names" order_sk="%s"></textarea>' % my.order_sk)

        table.add_row()
        table.add_cell(ctbl)
        table.add_row()
        mid = table.add_cell('-- OR --')
        mid.add_attr('align','center')

        ntbl = Table()
        ntbl.add_row()
        ntbl.add_cell('Name: ')
        ntbl.add_cell('<input type="text" id="primary_name" style="width: 200px;"/>')
        n1 = ntbl.add_cell(' &nbsp;From Number: ')
        n1.add_attr('nowrap','nowrap')
        ntbl.add_cell('<input type="text" id="from_number" style="width: 50px;"/>')
        n2 = ntbl.add_cell(' &nbsp;To Number: ')
        n2.add_attr('nowrap','nowrap')
        ntbl.add_cell('<input type="text" id="to_number" style="width: 50px;"/>')
 
        table.add_row()
        table.add_cell(ntbl)

        ptbl = Table()

        start_date = CalendarInputWdg('start_date')
        start_date.set_option('show_time','true')
        start_date.set_option('show_activator','true')
        start_date.set_option('display_format','MM/DD/YYYY HH:MM')
        start_date.set_option('time_input_default','5:00 PM')
        ptbl.add_row()
        ptbl.add_cell("Start Date: ")
        ptbl.add_cell(start_date)

        due_date = CalendarInputWdg('due_date')
        due_date.set_option('show_time','true')
        due_date.set_option('show_activator','true')
        due_date.set_option('display_format','MM/DD/YYYY HH:MM')
        due_date.set_option('time_input_default','5:00 PM')
        ptbl.add_row()
        ptbl.add_cell("Due Date: ")
        ptbl.add_cell(due_date)
       
        btbl = Table()
        etbl = Table()
        if my.search_type == 'twog/proj':
            platform_search = Search("twog/platform")
            platform_search.add_order_by('name desc')
            platforms = platform_search.get_sobjects()
            plat_sel = SelectWdg("platform")
            plat_sel.add_attr('id','platform')
            plat_sel.append_option('--Select--','')
            for p in platforms:
                plat_sel.append_option(p.get_value('name'),p.get_value('name'))
            ptbl.add_row()
            ptbl.add_cell("Priority: ")
            ptbl.add_cell('<input type="text" id="priority" style="width: 50px;"/>')
            ptbl.add_row()
            ptbl.add_cell('Platform: ')
            ptbl.add_cell(plat_sel)
            proj_search = Search("twog/proj")
            proj_search.add_filter('title_code',my.parent_code)
            proj_search.add_order_by('order_in_pipe')
            projs = proj_search.get_sobjects()
            btbl.add_row()
            p1 = btbl.add_cell('<u>First Proj Comes After</u>')
            p1.add_attr('nowrap','nowrap')
            p2 = btbl.add_cell('<u>Last Proj Leads To</u>')
            p2.add_attr('nowrap','nowrap')
            fromtbl = Table()
            for p in projs:
                fromtbl.add_row()

                checker = CustomCheckboxWdg(name='from_check',value_field=p.get_value('code'),id=p.get_value('code'),checked='false',dom_class='from_check',code=p.get_value('code'))

                fromtbl.add_cell(checker)
                fromtbl.add_cell("%s (%s)" % (p.get_value('process'), p.get_value('code')))
            totbl = Table()
            for p in projs:
                totbl.add_row()

                checker = CustomCheckboxWdg(name='to_check',value_field=p.get_value('code'),checked='false',id=p.get_value('code'),dom_class='to_check',code=p.get_value('code'))

                totbl.add_cell(checker)
                totbl.add_cell("%s (%s)" % (p.get_value('process'), p.get_value('code')))
            btbl.add_row()
            btbl.add_cell(fromtbl)
            btbl.add_cell(totbl)
                
        elif my.search_type == 'twog/work_order':
            g_search = Search("sthpw/login_group")
            g_search.add_where("\"login_group\" not in ('user','client')")
            g_search.add_order_by('login_group')   
            groups = g_search.get_sobjects()
            group_sel = SelectWdg('assigned_login_group')
            group_sel.add_attr('id','assigned_login_group')
            group_sel.append_option('--Select--','')
            for group in groups:
                group_sel.append_option(group.get_value('login_group'),group.get_value('login_group'))
            user_search = Search("sthpw/login")
            user_search.add_filter('location','internal')
            user_search.add_filter('license_type','user')
            user_search.add_order_by('login')
            users = user_search.get_sobjects()
            user_sel = SelectWdg("assigned")
            user_sel.add_attr('id','assigned')
            user_sel.append_option('--Select--','')
            for u in users:
                user_sel.append_option(u.get_value('login'), u.get_value('login'))
            ptbl.add_row()
            p1 = ptbl.add_cell('Work Group: ')
            p1.add_attr('nowrap', 'nowrap')
            ptbl.add_cell(group_sel)
            ptbl.add_row()
            ptbl.add_cell('Assigned: ')
            ptbl.add_cell(user_sel)
            ptbl.add_row()
            p2 = ptbl.add_cell('Title Id Number: ')
            p2.add_attr('nowrap', 'nowrap')
            ptbl.add_cell('<input type="text" id="title_id_num" style="width: 200px;"/>')
            ptbl.add_row()
            p3 = ptbl.add_cell('Estimated Work Hours: ')
            p3.add_attr('nowrap', 'nowrap')
            ptbl.add_cell('<input type="text" id="estimated_work_hours" style="width: 50px;"/>')
            ptbl.add_row()
            p4 = ptbl.add_cell('Instructions: ')
            p4.add_attr('valign', 'top')
            ptbl.add_cell('<textarea cols="100" rows="20" id="instructions"></textarea>')
            wo_search = Search("twog/work_order")
            wo_search.add_filter('proj_code', my.parent_code)
            wo_search.add_order_by('order_in_pipe')
            wos = wo_search.get_sobjects()

            btbl.add_row()
            p5 = btbl.add_cell('<u>First WO Comes After</u>')
            p5.add_attr('nowrap', 'nowrap')
            p6 = btbl.add_cell('<u>Last WO Leads To</u>')
            p6.add_attr('nowrap', 'nowrap')
            fromtbl = Table()
            for p in wos:
                fromtbl.add_row()

                checker = CustomCheckboxWdg(name='from_check',value_field=p.get_value('code'),id=p.get_value('code'),checked='false',dom_class='from_check',code=p.get_value('code'))

                fromtbl.add_cell(checker)
                f1 = fromtbl.add_cell("%s (%s)" % (p.get_value('process'), p.get_value('code')))
                f1.add_attr('nowrap', 'nowrap')
            totbl = Table()
            for p in wos:
                totbl.add_row()

                checker = CustomCheckboxWdg(name='to_check',value_field=p.get_value('code'),checked='false',id=p.get_value('code'),dom_class='to_check',code=p.get_value('code'))

                totbl.add_cell(checker)
                t1 = totbl.add_cell("%s (%s)" % (p.get_value('process'), p.get_value('code')))
                t1.add_attr('nowrap', 'nowrap')
            btbl.add_row()
            btbl.add_cell(fromtbl)
            btbl.add_cell(totbl)

        table.add_row()
        table.add_cell(ptbl)
        table.add_row()
        table.add_cell(btbl)
        table.add_row()
        table.add_cell(etbl)
        table.add_row()
      
        stbl = Table()
        stbl.add_row()
        s1 = stbl.add_cell('&nbsp;')
        s1.add_attr('width', '40%')
        saction = stbl.add_cell('<input type="button" value="Create %ss"/>' % my.name_type)
        saction.add_behavior(my.get_save())
        s2 = stbl.add_cell('&nbsp;')
        s2.add_attr('width', '40%')

        ss = table.add_cell(stbl)
        ss.add_attr('colspan','2')
        ss.add_attr('align','center')

        widget = DivWdg()
        widget.add(table)
        return widget

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
