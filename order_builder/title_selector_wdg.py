from tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseTableElementWdg

from pyasm.common import Environment
from pyasm.web import Table, DivWdg
from pyasm.widget import SelectWdg

from alternative_elements.customcheckbox import *


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
        order = None

        #Depending on the code of the object passed in (could be a work order, project, title, order, etc), get the order object
        if 'ORDER' in code and 'WORK_ORDER' not in code:
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
        client_str = client_str.replace('CLIENT_NAME', client_name)
        #Get the titles
        titles_expr = "@SOBJECT(twog/title['order_code','%s'])" % order_code
        if not user_is_scheduler and operator_titles not in [None, '']:
            titles_expr = "@SOBJECT(twog/title['code','%s'])" % operator_titles
        titles = server.eval(titles_expr)
        widget = DivWdg()
        table = Table()
        table.add_attr('class', 'allowed_titles_selector')
        table.add_row()
        table.add_cell('<b><u>ORDER NAME: %s</u></b>' % order_name)
        #If a color is set, then there is an issue with the client
        if client_color != '':
            table.add_style('background-color: %s;' % client_color)
            table.add_row()
            topcell = table.add_cell('<b>%s</b>' % client_str)
            topcell.add_attr('nowrap', 'nowrap')
            topcell.add_attr('colspan', '6')
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
            client_status_colors = {
                'Assignment': '#fcaf88',
                'Pending': '#d7d7d7',
                'In Progress': '#f5f3a4',
                'In_Progress': '#f5f3a4',
                'In Production': '#f5f3a4',
                'In_Production': '#f5f3a4',
                'In production': '#f5f3a4',
                'In_production': '#f5f3a4',
                'Waiting': '#ffd97f',
                'Need Assistance': '#fc88fb',
                'Need_Assistance': '#fc88fb',
                'Review': '#888bfc',
                'Approved': '#d4b5e7',
                'On Hold': '#e8b2b8',
                'On_Hold': '#e8b2b8',
                'Client Response': '#ddd5b8',
                'Completed': '#b7e0a5',
                'Ready': '#b2cee8',
                'Internal Rejection': '#ff0000',
                'External Rejection': '#ff0000',
                'Rejected': '#ff0000',
                'Failed QC': '#ff0000',
                'Waiting on client materials': '#ffd97f',
                'Materials received': '#b2cee8',
                'QC Rejected': '#ff0000',
                'QC Passed': '#d4b5e7',
                'QC rejected': '#ff0000',
                'QC passed': '#d4b5e7',
                'Fix Needed': '#c466a1',
                'Need Buddy Check': '#e3701a',
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
                'Buddy Check In Progress': '#1aade3',
                'Not Set': '#FFFFCC'
            }

            # No need for the toggler if there's only 1 title or less
            if len(titles) > 1:
                toggler = CustomCheckboxWdg(name='chk_toggler', additional_js=toggle_behavior, value_field='toggler',
                                            id='selection_toggler', checked='true',
                                            text='<b><- Select/Deselect ALL</b>', text_spot='right', text_align='left',
                                            nowrap='nowrap')

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
                if title.get('episode') not in [None, '']:
                    tname = '%s: %s' % (tname, title.get('episode'))

                if title.get('code') in current_titles or current_titles == '':
                    check_val = 'true'
                else:
                    check_val = 'false'
                checkbox = CustomCheckboxWdg(name='allowed_titles_%s' % title.get('code'),
                                             value_field=title.get('code'), checked=check_val, text=tname,
                                             text_spot='right', text_align='left', nowrap='nowrap',
                                             dom_class='title_selector')

                ck = table.add_cell(checkbox)

                table.add_cell('&nbsp;&nbsp;&nbsp;')
                tstatus = title.get('status')
                if tstatus in [None, '']:
                    tstatus = 'Not Set'
                status = table.add_cell(tstatus)
                status.add_attr('nowrap','nowrap')
                table.add_cell('&nbsp;&nbsp;&nbsp;')
                tclient_status = title.get('client_status')
                if tclient_status in [None, '']:
                    tclient_status = 'Not Set'
                client_status = table.add_cell(tclient_status)
                client_status.add_attr('nowrap', 'nowrap')
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
