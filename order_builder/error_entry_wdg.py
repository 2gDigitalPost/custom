from tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Environment
from pyasm.web import Table
from pyasm.widget import SelectWdg

from alternative_elements.customcheckbox import CustomCheckboxWdg


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
