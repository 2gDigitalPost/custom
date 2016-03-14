from tactic.ui.common import BaseRefreshWdg
from pyasm.common import Environment


# Lines 229, 1063
# Lines 2627, 5021, 5460 also fit under this, they used a smaller subset of this dictionary

# 'Not Set' key was written twice, once as '#d7d7d7' and again as '#FFFFCC'
# I've removed the second one for now. Not sure which one is correct


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
    'Not Set': '#d7d7d7',
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
    'Buddy Check In_Progress': '#1AADE3',
    'Buddy Check In Progress': '#1AADE3',
}

# Lines 1723, 7339
statuses = ['Pending', 'Ready', 'On Hold', 'Client Response', 'Fix Needed', 'Rejected', 'In Progress', 'DR In Progress',
            'Amberfin01 In Progress', 'Amberfin02 In Progress', 'BATON In Progress', 'Export In Progress',
            'Need Buddy Check', 'Buddy Check In Progress', 'Completed']


def get_save_task_info_behavior(task_sk, parent_sk, parent_pyclass, order_sk, is_master_str, user):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    function oc(a){
                        var o = {};
                        for(var i=0;i<a.length;i++){
                            o[a[i]]='';
                        }
                        return o;
                    }
                    try{
                      var server = TacticServerStub.get();
                      var task_sk = '%s';
                      var sk = '%s';
                      var parent_pyclass = '%s';
                      var order_sk = '%s';
                      var is_master_str = '%s';
                      var this_user = '%s';
                      var st = sk.split('?')[0];
                      task_code = task_sk.split('code=')[1];
                      var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                      var allowed_titles = top_el.getAttribute('allowed_titles');
                      if(allowed_titles == 'NOTHING|NOTHING'){
                          allowed_titles = '';
                      }
                      var task_panel = top_el.getElementsByClassName('task_table')[0];
                      priority_el = top_el.getElementsByClassName('priority_setter')[0];
                      priority = priority_el.value;
                      send_priority = ''
                      if(isNaN(priority)){
                          send_priority = -1;
                      }else{
                          send_priority = Number(priority);
                      }
                      sels = task_panel.getElementsByTagName('select');
                      assigned = '';
                      assigned_group = '';
                      new_status = '';
                      old_status = '';
                      status_sel = null;
                      for(var r = 0; r < sels.length; r++){
                          if(sels[r].name == 'task_assigned_select'){
                              assigned = sels[r].value;
                          }else if(sels[r].name == 'task_stat_select'){
                              new_status = sels[r].value;
                              old_status = sels[r].getAttribute('old_status');
                              status_sel = sels[r];
                          }else if(sels[r].name == 'task_assigned_group_select'){
                              assigned_group = sels[r].value;
                          }
                      }
                      dates = task_panel.getElementsByTagName('input');
                      start_date = '';
                      end_date = '';
                      for(var r = 0; r < dates.length; r++){
                          if(dates[r].name == 'task_bid_start'){
                              start_date = dates[r].value;
                          }else if(dates[r].name == 'task_bid_end'){
                              end_date = dates[r].value;
                          }
                      }
                      var data = {};
                      if(st != 'twog/title'){
                          data = {'assigned': assigned, 'assigned_login_group': assigned_group, 'status': new_status};
                      }else{
                          data = {'assigned_login_group': assigned_group, 'status': new_status, 'assigned': assigned};
                      }
                      if(send_priority != -1){
                          data['priority'] = send_priority;
                      }
                      if(!(start_date == '' || start_date == null)){
                          data['bid_start_date'] = start_date
                      }
                      if(!(end_date == '' || end_date == null)){
                          data['bid_end_date'] = end_date
                      }
                      hours_el = top_el.getElementsByClassName('hour_adder')[0];
                      hours = hours_el.value;
                      if(hours == '' || hours == null){
                          hours = 0;
                      }
                      hours_dict = null;
                      order_sk = top_el.getAttribute('order_sk');
                      if(!(isNaN(hours))){
                          if(hours > 0){
                              order_code = order_sk.split('code=')[1];
                              the_order = server.eval("@SOBJECT(twog/order['code','" + order_code + "'])")[0];
                              task = server.eval("@SOBJECT(sthpw/task['code','" + task_code + "'])")[0];
                              the_title = server.eval("@SOBJECT(twog/title['code','" + task.title_code + "'])")[0];
                              var today = new Date();
                              var dd = today.getDate();
                              var mm = today.getMonth() + 1;
                              var yyyy = today.getFullYear();
                              var day = yyyy + '-' + mm + '-' + dd + ' ' + today.getHours() + ':' + today.getMinutes() + ':' + today.getSeconds();
                              is_billable = true;
                              if(the_title.no_charge){
                                  is_billable = false;
                              }
                              hours_dict = {'task_code': task_code, 'client_code': the_order.client_code, 'client_name': the_order.client_name, 'title_code': task.title_code, 'category': task.process, 'process': task.process, 'scheduler': this_user, 'straight_time': hours, 'order_code': order_code, 'login': assigned, 'description': 'Added by scheduler in Order Builder', 'day': day, 'search_type': 'sthpw/task', 'search_id': task.id, 'is_billable': is_billable};
                              server.insert('sthpw/work_hour', hours_dict);
                              hours_el.value = '';
                          }
                      }else{
                          spt.alert("Please only add real numbers in the 'Add Hours' box");
                      }
                      server.update(task_sk, data);
                      display_mode = top_el.getAttribute('display_mode');
                      user = top_el.getAttribute('user');
                      groups_str = top_el.get('groups_str');
                      allowed_titles = top_el.getAttribute('allowed_titles');
                      parent_el = top_el.getElementsByClassName('cell_' + sk)[0];
                      found_parent_sk = parent_el.get('parent_sk');
                      found_parent_sid = parent_el.get('parent_sid');
                      send_data = {sk: sk, parent_sid: found_parent_sid, parent_sk: found_parent_sk, order_sk: order_sk, display_mode: display_mode, user: user, groups_str: groups_str, allowed_titles: allowed_titles, is_master: is_master_str, open_bottom: 'true'};
                      if(parent_pyclass == 'OrderTable'){
                          send_data['allowed_titles'] = allowed_titles;
                      }
                      spt.api.load_panel(parent_el, 'order_builder.' + parent_pyclass, send_data);
                      status_sel.setAttribute('old_status',new_status);
                      if('twog/order' != sk.split('?')[0]){
                          bot = top_el.getElementsByClassName('bot_' + sk)[0];
                          if(bot.style.display != 'none'){
                              bot.style.display = 'none';
                              bot.style.display = 'table-row';
                          }
                      }
                      if(st != 'twog/title'){
                          task = server.eval("@SOBJECT(sthpw/task['code','" + task_code + "'])")[0];
                          some_special_statuses = false;
                          some_path_prompts = false;
                          force_response_strings = '';
                          if(new_status in oc(['Rejected','Fix Needed','On Hold','Client Response'])){
                              //Get a forced response as to why
                              //Get production error generated prior to this, if applicable and send production error code to ForceResponseWdg
                              some_special_statuses = true;
                              production_error_code = '';
                              if(new_status in oc(['Rejected','Fix Needed'])){
                                  error_entries = server.eval("@SOBJECT(twog/production_error['work_order_code','" + task.lookup_code + "'])")
                                  if((error_entries.length > 0)){
                                      error_entry = error_entries[error_entries.length - 1];
                                      production_error_code = error_entry.code;
                                  }
                              }
                              this_row_str = 'MTMX-Prompt:Please tell us why the new status for ' + task.process + ' is going to ' + new_status + 'MTMX-production_error_code:' + production_error_code + 'MTMX-work_order_code:' + task.lookup_code + 'MTMX-process:' + task.process + 'MTMX-new_status:' + new_status + 'MTMX-old_status:' + old_status;
                              if(force_response_strings == ''){
                                  force_response_strings = this_row_str;
                              }else{
                                  force_response_strings = force_response_strings + 'MTM_NEXT_MTM' + this_row_str;
                              }
                          }else if(old_status in oc(['Rejected','Fix Needed','On Hold','Client Response'])){
                              //Get a forced response as to why
                              //Probably no production error here, so no need to send production error code
                              production_error_code = '';
                              some_special_statuses = true;
                              this_row_str = 'MTMX-Prompt:Please tell us why the new status for ' + task.process + ' is going to ' + new_status + ' from ' + old_status + 'MTMX-production_error_code:' + production_error_code + 'MTMX-work_order_code:' + task.lookup_code + 'MTMX-process:' + task.process + 'MTMX-new_status:' + new_status + 'MTMX-old_status:' + old_status;
                              if(force_response_strings == ''){
                                  force_response_strings = this_row_str;
                              }else{
                                  force_response_strings = force_response_strings + 'MTM_NEXT_MTM' + this_row_str;
                              }
                          }
                          if(new_status != old_status && new_status == 'Completed' && task.assigned_login_group in oc(['compression','compression supervisor','machine room','machine room supervisor','audio','edit','edit supervisor'])){
                              this_row_str = 'MTMX-Prompt:Please Enter the Path to the File(s) for ' + task.process + '.\\nStatus went to ' + new_status + ' from ' + old_status + 'MTMX-work_order_code:' + task.lookup_code + 'MTMX-process:' + task.process + 'MTMX-new_status:' + new_status + 'MTMX-old_status:' + old_status;
                              if(force_response_strings == ''){
                                  force_response_strings = this_row_str;
                              }else{
                                  force_response_strings = force_response_strings + 'MTM_NEXT_MTM' + this_row_str;
                              }
                              some_path_prompts = true;
                          }
                          if(some_special_statuses || some_path_prompts){
                              //Send to ForceResponseWdg
                              add_str = '';
                              if(some_path_prompts){
                                  add_str = ' or enter a file path where prompted';
                              }
                              spt.panel.load_popup('Please tell us why this work order is getting a special status' + add_str, 'operator_view.resetter.ForceResponseWdg', {'string_to_parse': force_response_strings});
                          }
                      }
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (task_sk, parent_sk, parent_pyclass, order_sk, is_master_str, user)}
    return behavior


def get_selected_color_behavior(code, row_type, on_color, off_color):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    code = '%s';
    row_type = '%s';
    on_color = '%s';
    off_color = '%s';
    var row_el = document.getElementsByClassName(row_type + '_' + code)[0];
    check_val = bvr.src_el.getAttribute('checked');
    if(check_val == 'true') {
        row_el.style.backgroundColor = on_color;
    } else {
        row_el.style.backgroundColor = off_color;
    }
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (code, row_type, on_color, off_color)}
    return behavior


def get_upload_behavior(sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    var my_sk = '%s';
    var class_name = 'uploader.CustomHTML5UploadWdg';

    kwargs = {
        'sk': my_sk
    };

    spt.panel.load_popup('Upload', class_name, kwargs);
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % sk}
    return behavior


def get_launch_wo_source_behavior(work_order_code, work_order_sk, wo_source, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      //alert('m42');
                      var server = TacticServerStub.get();
                      var work_order_code = '%s';
                      var work_order_sk = '%s';
                      var wo_source = '%s';
                      var order_sk = '%s';
                      spt.panel.load_popup('Source Portal', 'order_builder.SourceEditWdg', {'code': wo_source, 'order_sk': order_sk});
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (work_order_code, work_order_sk, wo_source, order_sk)}
    return behavior


def get_open_intermediate_behavior(intermediate_code, work_order_code, client_code, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      //alert('m32');
                      var server = TacticServerStub.get();
                      intermediate_code = '%s';
                      work_order_code = '%s';
                      client_code = '%s';
                      order_sk = '%s';
                      spt.panel.load_popup('Intermediate File Portal', 'order_builder.IntermediateEditWdg', {'order_sk': order_sk, 'work_order_code': work_order_code, 'intermediate_code': intermediate_code, 'client_code': client_code});
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (intermediate_code, work_order_code, client_code, order_sk)}
    return behavior


def get_scratch_pipe_behavior(search_type, search_id, parent_sid, width, height, pipeline_code, sk, class_type, name,
                              order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      //alert('m59');
                      spt.app_busy.show('Opening Pipeline Editor...');
                      var search_type = '%s';
                      var search_id = '%s';
                      var parent_sid = '%s';
                      var width = '%s';
                      var height = '%s';
                      var pipeline_code = '%s';
                      var sob_sk = '%s';
                      var class_type = '%s';
                      var name = '%s';
                      var order_sk = '%s';
                      //var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder_' + order_sk);
                      var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                      top_el.setAttribute('pipefocus_class_type',class_type);
                      top_el.setAttribute('pipefocus_sob_sk',sob_sk)
                      top_el.setAttribute('pipefocus_name',name)
                      var sob_selected = top_el.getElementsByClassName('selected_sobject')[0];
                      sob_selected.innerHTML = 'Selected: ' + name;
                      var client_code = top_el.get('client');
                      var order_code = top_el.get('order_code');
                      var pipe_cell = top_el.getElementsByClassName('pipe_cell')[0];
                      var pipe_row = top_el.getElementsByClassName('pipe_row')[0];
                      var closer_row = top_el.getElementsByClassName('closer_row')[0];
                      var pyclass = 'order_builder.CustomPipelineToolWdg';
                      spt.api.load_panel(pipe_cell, pyclass, {search_type: search_type, search_id: search_id, parent_sid: parent_sid, width: width, height: height, client_code: client_code, order_code: order_code, order_sk: order_sk, pipeline_code: pipeline_code});
                      pipe_row.style.display = 'table-row';
                      closer_row.style.display = 'table-row';
                      //spt.pipeline.import_pipeline(pipeline_code);
                      spt.app_busy.hide();
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (search_type, search_id, parent_sid, width, height, pipeline_code, sk, class_type, name, order_sk)}
    return behavior


def get_open_deliverable_behavior(deliverable_source_code, work_order_code, title_code, open_type, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      //alert('m33');
                      var server = TacticServerStub.get();
                      deliverable_source_code = '%s';
                      work_order_code = '%s';
                      title_code = '%s';
                      open_type = '%s';
                      order_sk = '%s';
                      spt.panel.load_popup('Permanent Element Portal', 'order_builder.DeliverableEditWdg', {'order_sk': order_sk, 'deliverable_source_code': deliverable_source_code, 'work_order_code': work_order_code, 'title_code': title_code});
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (deliverable_source_code, work_order_code, title_code, open_type, order_sk)}
    return behavior


class OBScripts(BaseRefreshWdg):
    def init(my):
        my.order_sk = ''
        my.user = ''
        my.groups_str = ''
        my.disp_mode = 'Normal'
        my.is_master = False
        my.is_master_str = 'false'
        if 'order_sk' in my.kwargs.keys():
            my.order_sk = str(my.kwargs.get('order_sk'))
        if 'is_master' in my.kwargs.keys():
            my.is_master_str = my.kwargs.get('is_master')
            if my.is_master_str == 'true':
                my.is_master = True
        if 'user' in my.kwargs.keys():
            my.user = str(my.kwargs.get('user'))
        else:
            my.user = Environment.get_user_name()
        if 'groups_str' in my.kwargs.keys():
            my.groups_str = str(my.kwargs.get('groups_str'))
        if 'disp_mode' in my.kwargs.keys():
            #print "OBS DISPLAY MODE = %s" % my.disp_mode
            my.disp_mode = str(my.kwargs.get('disp_mode'))

    def get_eq_edit_behavior(my):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                               order_sk = '%s';
                               user_name = '%s';
                               server = TacticServerStub.get();
                               top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                               //checks = top_el.getElementsByClassName('SPT_BVR');
                               checks = top_el.getElementsByClassName('ob_selector');
                               sks = ''
                               count = 0;
                               for(var r = 0; r < checks.length; r++){
                                   if(checks[r].getAttribute('checked') == 'true'){
                                       if(checks[r].getAttribute('name') != null){
                                           name = checks[r].getAttribute('name');
                                           if(name.indexOf('select_') != -1){
                                               if(name.indexOf('WORK_ORDER') != -1){
                                                   csk = checks[r].getAttribute('search_key');
                                                   if(sks == ''){
                                                       sks = csk;
                                                   }else{
                                                       sks = sks + '|' + csk;
                                                   }
                                                   count = count + 1;
                                               }
                                           }
                                       }
                                   }
                               }
                               title_str = 'Edit Equipment on Multiple Work Orders';
                               if(count == 1){
                                   code_selected = sks.split('code=')[1];
                                   title_str = 'Edit Equipment on ' + code_selected;
                               }
                               spt.panel.load_popup(title_str, 'order_builder.EquipmentUsedMultiAdderWdg', {'order_sk': order_sk, 'sks': sks});
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (my.order_sk, my.user)}
        return behavior

    def get_qe_delete(my):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                               order_sk = '%s';
                               user_name = '%s';
                               order_code = order_sk.split('code=')[1];
                               server = TacticServerStub.get();
                               top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                               //checks = top_el.getElementsByClassName('SPT_BVR');
                               checks = top_el.getElementsByClassName('ob_selector');
                               sks_by_type = {'TITLE': [], 'PROJ': [], 'WORK_ORDER': [], 'EQUIPMENT_USED': []};
                               if(confirm("Are you sure you want to DELETE all selected items?")){
                                   for(var r = 0; r < checks.length; r++){
                                       if(checks[r].getAttribute('checked') == 'true'){
                                           if(checks[r].getAttribute('name') != null){
                                               name = checks[r].getAttribute('name');
                                               if(name.indexOf('select_') != -1){
                                                   this_sk = checks[r].getAttribute('search_key');
                                                   code = this_sk.split('code=')[1];
                                                   if(code.indexOf('WORK_ORDER') != -1){
                                                       sks_by_type['WORK_ORDER'].push(this_sk);
                                                   }else if(code.indexOf('PROJ') != -1){
                                                       sks_by_type['PROJ'].push(this_sk);
                                                   }else if(code.indexOf('TITLE') != -1){
                                                       sks_by_type['TITLE'].push(this_sk);
                                                   }else if(code.indexOf('EQUIPMENT_USED') != -1){
                                                       sks_by_type['EQUIPMENT_USED'].push(this_sk);
                                                   }
                                               }
                                           }
                                       }
                                   }
                                   if(confirm("You're certain you want to delete the selected items?")){
                                         spt.app_busy.show("Deleting...");
                                       for(var r = 0; r < sks_by_type['EQUIPMENT_USED'].length; r++){
                                           server.retire_sobject(sks_by_type['EQUIPMENT_USED'][r]);
                                       }
                                       for(var r = 0; r < sks_by_type['WORK_ORDER'].length; r++){
                                           server.retire_sobject(sks_by_type['WORK_ORDER'][r]);
                                       }
                                       for(var r = 0; r < sks_by_type['PROJ'].length; r++){
                                           server.retire_sobject(sks_by_type['PROJ'][r]);
                                       }
                                       for(var r = 0; r < sks_by_type['TITLE'].length; r++){
                                           server.retire_sobject(sks_by_type['TITLE'][r]);
                                       }
                                       server.insert('twog/simplify_pipe', {'order_code': order_code, 'do_all': 'yes'});
                                       groups_str = top_el.getAttribute('groups_str');
                                       display_mode = top_el.getAttribute('display_mode');
                                       is_master_str = top_el.getAttribute('is_master_str');
                                       allowed_titles = top_el.getAttribute('allowed_titles');
                                       kwargs = {'order_sk': order_sk, 'sk': order_sk, 'groups_str': groups_str, 'user': user_name, 'display_mode': display_mode, 'is_master': is_master_str, 'allowed_titles': allowed_titles}
                                       class_name = 'order_builder.order_builder.OrderBuilder';
                                       cover = document.getElementsByClassName('twog_order_builder_cover_' + order_sk)[0];
                                       cover_cell = cover.getElementsByClassName('cover_cell')[0];
                                       spt.api.load_panel(cover_cell, class_name, kwargs);
                                       spt.app_busy.hide();
                                   }
                               }
                }catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (my.order_sk, my.user)}
        return behavior
    def get_submit_quick_changes(my):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        function encode_utf8( s )
                        {
                            return unescape( encodeURIComponent( s ) );
                        }
                        try{
                               order_sk = '%s';
                               user_name = '%s';
                               server = TacticServerStub.get();
                               top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                               //checks = top_el.getElementsByClassName('SPT_BVR');
                               checks = top_el.getElementsByClassName('ob_selector');
                               sks = []
                               sk_to_task_sk = {};
                               if(confirm("Are you sure you want to apply these changes?")){
                                   spt.app_busy.show("Applying Updates...");
                                   for(var r = 0; r < checks.length; r++){
                                       if(checks[r].getAttribute('checked') == 'true'){
                                           if(checks[r].getAttribute('name') != null){
                                               name = checks[r].getAttribute('name');
                                               if(name.indexOf('select_') != -1){
                                                   sks.push(checks[r].getAttribute('search_key'));
                                                   if(name.indexOf('WORK_ORDER') != -1 || name.indexOf('PROJ') != -1){
                                                       sk_to_task_sk[checks[r].getAttribute('search_key')] = checks[r].getAttribute('task_sk');
                                                   }
                                               }
                                           }
                                       }
                                   }
                                   qe = top_el.getElementsByClassName('qe_top_' + order_sk)[0]
                                   top_checks = qe.getElementsByClassName('quick_edit_selector');
                                   title_checked = false;
                                   proj_checked = false;
                                   wo_checked = false;
                                   eq_checked = false;
                                   title_data = {};
                                   proj_data = {};
                                   wo_data = {};
                                   eq_data = {};
                                   task_data = {};
                                   for(var r = 0; r < top_checks.length; r++){
                                       if(top_checks[r].getAttribute('checked') == 'true'){
                                           name = top_checks[r].getAttribute('name');
                                           if(name != '' && name != null){
                                               if(name == 'qe_titles_' + order_sk){
                                                   title_checked = true;
                                               }else if(name == 'qe_projects_' + order_sk){
                                                   proj_checked = true;
                                               }else if(name == 'qe_work_orders_' + order_sk){
                                                   wo_checked = true;
                                               }else if (name == 'qe_equipment_' + order_sk){
                                                   eq_checked = true;
                                               }
                                           }
                                       }
                                   }
                                   nada = 'NOTHINGATALL'
                                   platform = nada;
                                   territory = nada;
                                   language = nada;
                                   statu = nada;
                                   assigned_group = nada;
                                   assigned = nada;
                                   priority = nada;
                                   ewh = nada;
                                   ex_dur = nada;
                                   ex_quan = nada;
                                   start_date = nada;
                                   due_date = nada;
                                   selects = qe.getElementsByTagName('select');
                                   for(var r = 0; r < selects.length; r++){
                                       name = selects[r].getAttribute('name');
                                       if(selects[r].value != '--Select--'){
                                           if(name == 'platform_sel_' + order_sk){
                                               platform = selects[r].value;
                                           }else if(name == 'territory_sel_' + order_sk){
                                               territory = selects[r].value;
                                           }else if(name == 'language_sel_' + order_sk){
                                               language = selects[r].value;
                                           }else if(name == 'eq_status_' + order_sk){
                                               statu = selects[r].value;
                                           }else if(name == 'task_assigned_group_select'){
                                               assigned_group = selects[r].value;
                                           }else if(name == 'task_assigned_select'){
                                               assigned = selects[r].value;
                                           }
                                       }
                                   }
                                   inputs = qe.getElementsByTagName('input');
                                   for(var r = 0; r < inputs.length; r++){
                                       if(inputs[r].getAttribute('type') == 'text' && inputs[r].value != ''){
                                           name = inputs[r].getAttribute('name');
                                           if(name == 'qe_start_date_' + order_sk){
                                               start_date = inputs[r].value;
                                           }else if(name == 'qe_due_date_' + order_sk){
                                               due_date = inputs[r].value;
                                           }else if(name == 'qe_priority_' + order_sk){
                                               priority = inputs[r].value;
                                           }else if(name == 'qe_ewh_' + order_sk){
                                               ewh = inputs[r].value;
                                           }else if(name == 'qe_ex_dur_' + order_sk){
                                               ex_dur = inputs[r].value;
                                           }else if(name == 'qe_ex_quan_' + order_sk){
                                               ex_quan = inputs[r].value;
                                           }
                                       }
                                   }
                                   if(platform != nada){
                                       title_data['platform'] = platform;
                                       proj_data['platform'] = platform;
                                       wo_data['platform'] = platform;
                                       task_data['platform'] = platform;
                                   }
                                   if(territory != nada){
                                       title_data['territory'] = territory;
                                       proj_data['territory'] = territory;
                                       wo_data['territory'] = territory;
                                       task_data['territory'] = territory;
                                   }
                                   if(language != nada){
                                       title_data['language'] = language;
                                   }
                                   if(start_date != nada){
                                       title_data['start_date'] = start_date;
                                       proj_data['start_date'] = start_date;
                                       task_data['bid_start_date'] = start_date;
                                   }
                                   if(due_date != nada){
                                       title_data['due_date'] = due_date;
                                       proj_data['due_date'] = due_date;
                                       wo_data['due_date'] = due_date;
                                       task_data['bid_end_date'] = due_date;
                                   }
                                   if(priority != nada){
                                       proj_data['priority'] = priority;
                                       wo_data['priority'] = priority;
                                       task_data['priority'] = priority;
                                   }
                                   if(statu != nada){
                                       proj_data['status'] = statu;
                                       task_data['status'] = statu;
                                   }
                                   if(assigned_group != nada){
                                       wo_data['work_group'] = assigned_group;
                                       task_data['assigned_login_group'] = assigned_group;
                                   }
                                   if(assigned != nada){
                                       task_data['assigned'] = assigned;
                                   }
                                   if(ewh != nada){
                                       wo_data['estimated_work_hours'] = ewh;
                                       task_data['bid_duration'] = ewh;
                                   }
                                   if(ex_dur != nada){
                                       eq_data['expected_duration'] = ex_dur;
                                   }
                                   if(ex_quan != nada){
                                       eq_data['expected_quantity'] = ex_quan;
                                   }
                                   sks_len = sks.length;
                                   for(var r = 0; r < sks.length; r++){
                                       counter = r + 1;
                                       spt.app_busy.show("Applying Update " + counter + " Of " + sks_len + "...");
                                       if(sks[r].indexOf('TITLE') != -1){
                                           if(title_data != {} && title_checked){
                                               //server.update(sks[r], title_data, triggers=false);
                                               server.update(sks[r], title_data);
                                           }
                                       }
                                       if(sks[r].indexOf('PROJ') != -1){
                                           if(proj_data != {} && proj_checked){
                                               //server.update(sks[r], proj_data, triggers=false);
                                               server.update(sks[r], proj_data);
                                           }
                                           if(sk_to_task_sk[sks[r]]){
                                               if(task_data != {}){
                                                   //server.update(sk_to_task_sk[sks[r]], task_data, triggers=false);
                                                   server.update(sk_to_task_sk[sks[r]], task_data);
                                               }
                                           }
                                       }
                                       if(sks[r].indexOf('WORK_ORDER') != -1){
                                           if(wo_data != {} && wo_checked){
                                               //server.update(sks[r], wo_data, triggers=false);
                                               server.update(sks[r], wo_data);
                                           }
                                           if(sk_to_task_sk[sks[r]]){
                                               if(task_data != {}){
                                                   //server.update(sk_to_task_sk[sks[r]], task_data, triggers=false);
                                                   server.update(sk_to_task_sk[sks[r]], task_data);
                                               }
                                           }
                                       }
                                       if(sks[r].indexOf('EQUIPMENT_USED') != -1){
                                           if(eq_data != {} && eq_checked){
                                               //server.update(sks[r], eq_data, triggers=false);
                                               server.update(sks[r], eq_data);
                                           }
                                       }
                                   }
                                   spt.app_busy.hide();
                                   alert('Finished. To see the changes, reload the tab.');
                               }


                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (my.order_sk, my.user)}
        return behavior

    def get_open_errors_behavior(my):
        #This opens the section where schedulers can enter production errer records
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                               order_sk = '%s';
                               var qe_top = document.getElementsByClassName('qe_top_' + order_sk)[0];
                               var row_el = qe_top.getElementsByClassName('qe_errors_row_' + order_sk)[0];
                               var tds = qe_top.getElementsByTagName('td');
                               var cell_el = null;
                               for(var r = 0; r < tds.length; r++){
                                   if(tds[r].getAttribute('name') == 'qe_error_opener_' + order_sk){
                                       cell_el = tds[r];
                                   }
                               }
                               if(row_el.style.display == 'none'){
                                   row_el.style.display = 'table-row';
                                   cell_el.innerHTML = '<u>Hide Errors Section</u>'
                               }else{
                                   row_el.style.display = 'none';
                                   cell_el.innerHTML = '<u>Document Errors</u>'
                               }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (my.order_sk)}
        return behavior

    def get_add_wo_error_behavior(my, code): #NO SID NECC
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          order_sk = '%s';
                          user = '%s';
                          code = '%s';
                          top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                          groups_str = top_el.getAttribute('groups_str');
                          display_mode = top_el.getAttribute('display_mode');
                          spt.panel.load_popup('Report Error for ' + code, 'order_builder.ErrorEntryWdg', {'order_sk': order_sk, 'code': code, 'user': user, 'groups_str': groups_str, 'display_mode': display_mode});
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (my.order_sk, my.user, code)}
        return behavior


    def get_templ_wo_behavior(my, templ_me, wo_templ_code, sk):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                           //alert('m1');
                           var server = TacticServerStub.get();
                           var templ_me = '%s';
                           var wo_templ_code = '%s';
                           var sk = '%s';
                           var order_sk = '%s';
                           var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                           expr = "@SOBJECT(twog/work_order['work_order_templ_code','" + wo_templ_code + "']['templ_me','true'])";
                           wo_ts = server.eval(expr);
                           if(wo_ts.length == 0){
                               server.update(sk, {'templ_me': 'true'});
                               me = top_el.getElementsByClassName('templ_butt_' + sk)[0];
                               spt.api.load_panel(me, 'tactic.ui.widget.button_new_wdg.ButtonSmallNewWdg', {title: "This is the Templating Work Order", icon: '/context/icons/silk/tick.png'});
                           }else{
                               alert('This cannot become the template. Please go to the Master Order for this Template.');
                           }

                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (templ_me, wo_templ_code, sk, my.order_sk)}
        return behavior

    def get_save_multi_eq_changes_behavior(my, work_order_code, order_sk):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                           var server = TacticServerStub.get();
                           var work_order_code = '%s';
                           order_sk = '%s';
                           is_master_str = '%s';
                           top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                           display_mode = top_el.getAttribute('display_mode');
                           user = top_el.getAttribute('user');
                           groups_str = top_el.get('groups_str');
                           allowed_titles = top_el.getAttribute('allowed_titles');
                           var pop_el = document.getElementsByClassName('equipment_used_multi_adder_top_' + work_order_code)[0];
                           if(work_order_code != 'MULTIPLE'){
                               wo_sk = server.build_search_key('twog/work_order', work_order_code);
                               wo_el = top_el.getElementsByClassName('cell_' + wo_sk)[0];
                               parent_sk = wo_el.getAttribute('parent_sk');
                               parent_sid = wo_el.get('parent_sid');
                               spt.api.load_panel(wo_el, 'order_builder.WorkOrderRow', {'sk': wo_sk, 'parent_sk': parent_sk, 'order_sk': order_sk, 'parent_sid': parent_sid, display_mode: display_mode, user: user, groups_str: groups_str, allowed_titles: allowed_titles, is_master: is_master_str});
                               var wo_bot = document.getElementsByClassName('bot_' + wo_sk)[0];
                               wo_bot.style.display = 'table-row';
                           }else{
                               sks = pop_el.getAttribute('sks');
                               sks_s = sks.split('|');
                               for(var r = 0; r < sks_s.length; r++){
                                   wo_sk = sks_s[r];
                                   wo_code = wo_sk.split('code=')[1];
                                   spt.app_busy.show('Reloading ' + wo_code);
                                   wo_el = top_el.getElementsByClassName('cell_' + wo_sk)[0];
                                   parent_sk = wo_el.getAttribute('parent_sk');
                                   parent_sid = wo_el.get('parent_sid');
                                   spt.api.load_panel(wo_el, 'order_builder.WorkOrderRow', {'sk': wo_sk, 'parent_sk': parent_sk, 'order_sk': order_sk, 'parent_sid': parent_sid, display_mode: display_mode, user: user, groups_str: groups_str, allowed_titles: allowed_titles, is_master: is_master_str});
                                   var wo_bot = document.getElementsByClassName('bot_' + wo_sk)[0];
                                   wo_bot.style.display = 'table-row';
                               }
                               spt.app_busy.hide();
                           }
                           spt.popup.close(spt.popup.get_popup(bvr.src_el));
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (work_order_code, order_sk, my.is_master_str)}
        return behavior

    def get_change_length_pull_behavior(my, work_order_code):
        behavior = {'css_class': 'clickme', 'type': 'change', 'cbjs_action': '''
                        try{
                           //alert('m2');
                           var server = TacticServerStub.get();
                           var work_order_code = '%s';
                           var eq_code = bvr.src_el.value;
                           lengths = server.eval("@GET(twog/equipment['code','" + eq_code + "'].lengths)")[0].split(',');
                           new_inner = ''
                           for(var r =0; r < lengths.length; r++){
                               new_inner = new_inner + '<option value="' + lengths[r] + '">' + lengths[r] + '</option>';
                           }
                           var top_el = document.getElementsByClassName('equipment_used_multi_adder_top_' + work_order_code)[0];
                           my_selects = top_el.getElementsByTagName('select');
                           for(var r = 0; r < my_selects.length; r++){
                               if(my_selects[r].getAttribute('name') == 'media_length'){
                                   my_length_pull = my_selects[r];
                               }
                           }
                           my_length_pull.innerHTML = new_inner;
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (work_order_code)}
        return behavior

    def get_add_eq_from_multi_behavior(my, type_base, work_order_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                           var server = TacticServerStub.get();
                           var type_base = '%s';
                           var work_order_code = '%s';
                           var top_el = document.getElementsByClassName('equipment_used_multi_adder_top_' + work_order_code)[0];
                           work_order_sk = top_el.getAttribute('work_order_sk');
                           client_code = top_el.getAttribute('client_code');
                           order_sk = top_el.getAttribute('order_sk');
                           my_selects = top_el.getElementsByTagName('select');
                           my_code = '';
                           my_units = '';
                           my_name = '';
                           my_length = '';
                           for(var r = 0; r < my_selects.length; r++){
                               if(my_selects[r].getAttribute('name') == type_base + '_select'){
                                   my_code = my_selects[r].value;
                                   my_name = my_selects[r].options[my_selects[r].selectedIndex].text;
                               }
                               if(my_selects[r].getAttribute('name') == type_base + '_units_select'){
                                   my_units = my_selects[r].value;
                               }
                               if(my_selects[r].getAttribute('name') == type_base + '_length'){
                                   my_length = my_selects[r].value;
                               }
                           }
                           if(my_name.indexOf('WORKSTATION') != -1 || my_name.indexOf('MACHINEROOM') != -1){
                               my_units = 'hr';
                           }else if(my_name.indexOf('MEDIA') != -1 && my_name.indexOf('MONORAIL') == -1){
                               my_units = 'length';
                           }
                           if(my_code != 'NOTHINGXsXNOTHING'){
                               if(my_units == 'gb' || my_units == 'tb'){
                                   quantity = 1
                               }else{
                                   quant_el = top_el.getElementsByClassName(type_base + '_quant')[0];
                                   quantity = quant_el.value;
                               }
                               if(quantity == '' || quantity == null){
                                   quantity = 1;
                               }
                               data = {'expected_quantity': quantity, 'units': my_units, 'name': my_name, 'equipment_code': my_code};
                               if(my_units != 'length'){
                                   duration_el = top_el.getElementsByClassName(type_base + '_duration')[0];
                                   duration = duration_el.value;
                                   if(duration != '' && duration != null){
                                       data['expected_duration'] = duration;
                                   }
                               }else{
                                   data['length'] = my_length;
                               }
                               reload_data = {'order_sk': order_sk};
                               if(work_order_code != 'MULTIPLE'){
                                   data['work_order_code'] = work_order_code;
                                   server.insert('twog/equipment_used', data);
                                   reload_data['work_order_sk'] = work_order_sk;
                               }else{
                                   sks = top_el.getAttribute('sks');
                                   reload_data['sks'] = sks;
                                   sks_s = sks.split('|')
                                   for(var t = 0; t < sks_s.length; t++){
                                       wo_code = sks_s[t].split('code=')[1];
                                       data['work_order_code'] = wo_code
                                       spt.app_busy.show("Attaching " + my_name + " to " + wo_code);
                                       server.insert('twog/equipment_used', data);
                                   }
                                   spt.app_busy.hide();
                               }
                                   spt.api.load_panel(top_el, 'order_builder.EquipmentUsedMultiAdderWdg', reload_data);
                           }else{
                               alert('You must select the type of equipment you want to add.');
                           }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (type_base, work_order_code)}
        return behavior

    def get_eq_multi_kill_behavior(my, eqsk, eqname, work_order_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                           var server = TacticServerStub.get();
                           var eqsk = '%s';
                           var eqname = '%s';
                           var work_order_code = '%s';
                           var top_el = document.getElementsByClassName('equipment_used_multi_adder_top_' + work_order_code)[0];
                           var work_order_sk = top_el.getAttribute('work_order_sk');
                           var order_sk = top_el.getAttribute('order_sk');
                           if(work_order_code != 'MULTIPLE'){
                               if(confirm('Do you really want to delete ' + eqname + ' from this list?')){
                                   server.delete_sobject(eqsk);
                                       spt.api.load_panel(top_el, 'order_builder.EquipmentUsedMultiAdderWdg', {'work_order_sk': work_order_sk, 'order_sk': order_sk});
                               }
                           }else{
                               wo_codes_str = bvr.src_el.getAttribute('wo_codes');
                               wo_codes = wo_codes_str.split('|');
                               codes_len = wo_codes.length;
                               if(confirm('Do you really want to delete ' + eqname + ' from ' + codes_len + ' Work Orders?')){
                                   var top_el = document.getElementsByClassName('equipment_used_multi_adder_top_' + work_order_code)[0];
                                   //here delete the equipment
                                   eq_codes = bvr.src_el.getAttribute('eq_codes');
                                   eqs = eq_codes.split('|');
                                   spt.app_busy.show('Deleting Equipment. Please Wait.');
                                   for(var r = 0; r < eqs.length; r++){
                                       eqsk = server.build_search_key('twog/equipment_used', eqs[r]);
                                       server.delete_sobject(eqsk);
                                   }
                                   spt.app_busy.hide();
                                   sks = bvr.src_el.getAttribute('sks');
                                       spt.api.load_panel(top_el, 'order_builder.EquipmentUsedMultiAdderWdg', {'sks': sks, 'order_sk': order_sk});
                               }
                           }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (eqsk, eqname, work_order_code)}
        return behavior

    def get_assign_intermediate_passins_behavior(my, work_order_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                           var server = TacticServerStub.get();
                           var work_order_code = '%s';
                           var order_sk = '%s';
                           var top_el = spt.api.get_parent(bvr.src_el, '.intermediate_passin_add_wdg');
                           checks = top_el.getElementsByClassName('inter_passin_selector');
                           for(var r = 0; r < checks.length; r++){
                               if(checks[r].getAttribute('checked') == 'true'){
                                   woi_code = checks[r].getAttribute('woi_code');
                                   inter_code = checks[r].getAttribute('inter_code');
                                   server.insert('twog/work_order_passin', {'work_order_code': work_order_code, 'intermediate_file_code': inter_code, 'work_order_intermediate_code': woi_code})
                               }
                           }
                           work_order_sk = server.build_search_key('twog/work_order', work_order_code);
                           var sources_line = document.getElementsByClassName('wo_sources_' + work_order_sk)[0];
                           spt.api.load_panel(sources_line, 'order_builder.WorkOrderSourcesRow', {'work_order_code': work_order_code, 'order_sk': order_sk});
                           var sp = document.getElementsByClassName('sp_overhead_' + work_order_code)[0];
                           parent_pipe = sp.getAttribute('parent_pipe');
                           client_code = sp.getAttribute('client_code');
                           is_master = sp.getAttribute('is_master');
                           var sp_el = sp.getElementsByClassName('sp_list_cell')[0];
                           spt.api.load_panel(sp_el, 'order_builder.SourcePortalWdg', {'work_order_code': work_order_code, 'parent_pipe': parent_pipe, 'client_code': client_code, 'is_master': is_master, 'order_sk': order_sk});
                           spt.popup.close(spt.popup.get_popup(bvr.src_el));


                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (work_order_code, my.order_sk)}
        return behavior

    def get_templ_proj_behavior(my, templ_me, proj_templ_code, sk):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                           var server = TacticServerStub.get();
                           var templ_me = '%s';
                           var proj_templ_code = '%s';
                           var sk = '%s';
                           var order_sk = '%s';
                           var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                           expr = "@SOBJECT(twog/proj['proj_templ_code','" + proj_templ_code + "']['templ_me','true'])";
                           proj_ts = server.eval(expr);
                           if(proj_ts.length == 0){
                               server.update(sk, {'templ_me': 'true'});
                               me = top_el.getElementsByClassName('templ_butt_' + sk)[0];
                               spt.api.load_panel(me, 'tactic.ui.widget.button_new_wdg.ButtonSmallNewWdg', {title: "This is the Templating Project", icon: '/context/icons/silk/tick.png'});
                           }else{
                               alert('This cannot become the Template. Please go to the Master Order for this Template.');
                           }

                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (templ_me, proj_templ_code, sk, my.order_sk)}
        return behavior

    def get_easy_checkin_commit_behavior(my, source_sk):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                           var server = TacticServerStub.get();
                           var source_sk = '%s';
                           var source_top_el = document.getElementsByClassName('source_edit_top')[0];
                           var file_selected_cell = source_top_el.getElementsByClassName('file_holder')[0];
                           var file_selected = file_selected_cell.innerHTML;
                           var selects = source_top_el.getElementsByTagName('select');
                           var ctx_select = '';
                           for(var r = 0; r < selects.length; r++){
                               if(selects[r].name == 'source_process_select'){
                                   ctx_select = selects[r];
                               }
                           }
                           var ctx = ctx_select.value;
                           server.simple_checkin(source_sk, ctx, file_selected, {'mode': 'inplace'});
                           var history = source_top_el.getElementsByClassName('history_source_cell')[0];
                           spt.api.load_panel(history, 'tactic.ui.widget.SObjectCheckinHistoryWdg', {search_key: source_sk});


                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (source_sk)}
        return behavior

    def get_easy_checkin_browse_behavior(my):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                           var server = TacticServerStub.get();
                           var applet = spt.Applet.get();
                           var base_dirs = server.get_base_dirs();
                           var base_sandbox = base_dirs.win32_sandbox_dir;
                           var source_top_el = document.getElementsByClassName('twog_easy_checkin')[0];
                           var potential_files = applet.open_file_browser(base_sandbox);
                           var main_file = potential_files[0];
                           var file_selected_cell = source_top_el.getElementsByClassName('file_holder')[0];
                           file_selected_cell.innerHTML = main_file;
                           var commit_button = source_top_el.getElementsByClassName('easy_checkin_commit')[0];
                           commit_button.disabled = false;

                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         '''}
        return behavior

    def get_add_wo_sources_behavior(my, work_order_code, work_order_sk, proj_sk, sob_name):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          //alert('m18');
                          var server = TacticServerStub.get();
                          work_order_code = '%s';
                          work_order_sk = '%s';
                          proj_sk = '%s';
                          sob_name = '%s';
                          order_sk = '%s';
                          //var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder_' + order_sk);
                          var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                          parent_cell = top_el.getElementsByClassName('cell_' + proj_sk)[0];
                          title_cell = top_el.getElementsByClassName('cell_' + parent_cell.getAttribute('parent_sk'))[0];
                          proj_call_me = parent_cell.getAttribute('call_me');
                          title_call_me = title_cell.getAttribute('call_me');
                          episode = title_cell.getAttribute('episode');
                          title_code = parent_cell.getAttribute('parent_sk').split('code=')[1];
                          whole_call_me = title_call_me + ' ' + episode + ':' + proj_call_me + ':' + sob_name;
                          spt.panel.load_popup('Attach Sources to ' + sob_name + ', under ' + title_call_me + ' ' + episode + ':' + proj_call_me, 'order_builder.WorkOrderSourceAddWdg', {work_order_code: work_order_code, work_order_sk: work_order_sk, title_code: title_code, call_me: whole_call_me, order_sk: order_sk});
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (work_order_code, work_order_sk, proj_sk, sob_name, my.order_sk)}
        return behavior

    def get_create_deliverable_behavior(my, sob_code, prereq_st, sob_sk, sob_st, sob_name, pipeline):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          //alert('m29');
                          var server = TacticServerStub.get();
                          sob_code = '%s';
                          prereq_st = '%s';
                          sob_sk = '%s';
                          sob_st = '%s';
                          sob_name = '%s';
                          pipeline = '%s';
                          order_sk = '%s';
                          spt.panel.load_popup('Create New Permanent Element', 'tactic.ui.panel.EditWdg', {element_name: 'general', mode: 'insert', search_type: 'twog/deliverable', title: 'Create New Deliverable', view: 'insert', widget_key: 'edit_layout', cbjs_insert_path: 'builder/reload_deliverable_table'});
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (sob_code, prereq_st, sob_sk, sob_st, sob_name, pipeline, my.order_sk)}
        return behavior

    def get_select_checks_by_group_behavior(my):
        behavior = {'css_class': 'clickme', 'type': 'change', 'cbjs_action': '''
                        try{
                           var checked_img = '<img src="/context/icons/custom/custom_checked.png"/>'
                           var not_checked_img = '<img src="/context/icons/custom/custom_unchecked.png"/>'
                           order_sk = '%s';
                           top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                           //checks = top_el.getElementsByClassName('SPT_BVR');
                           checks = top_el.getElementsByClassName('ob_selector');
                           set_to_me = 'true';
                           if(bvr.src_el.value == ''){
                               set_to_me = 'false';
                           }
                           for(var r = 0; r < checks.length; r++){
                               if(checks[r].getAttribute('name') != null){
                                   if(checks[r].getAttribute('name').indexOf('select_') != -1 && checks[r].getAttribute('ntype') == 'work_order'){
                                       if(checks[r].getAttribute('work_group') == bvr.src_el.value){
                                           check_code = checks[r].getAttribute('code');
                                           parent_table_class = checks[r].getAttribute('parent_table');
                                           parent_table = top_el.getElementsByClassName(parent_table_class)[0];
                                           new_color = '';
                                           if(set_to_me){
                                               new_color = checks[r].getAttribute('selected_color');
                                           }else{
                                               new_color = checks[r].getAttribute('normal_color');
                                           }
                                           parent_table.style.backgroundColor = new_color;
                                           checks[r].setAttribute('checked',set_to_me);
                                           checks[r].innerHTML = checked_img;
                                       }else{
                                           check_code = checks[r].getAttribute('code');
                                           parent_table_class = checks[r].getAttribute('parent_table');
                                           parent_table = top_el.getElementsByClassName(parent_table_class)[0];
                                           checks[r].setAttribute('checked','false');
                                           new_color = checks[r].getAttribute('normal_color');
                                           parent_table.style.backgroundColor = new_color;
                                           checks[r].innerHTML = not_checked_img;
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
         ''' % (my.order_sk)}
        return behavior

    def get_barcode_insert_behavior(my, title_code, title_sk):
        behavior = {'css_class': 'clickme', 'type': 'change', 'cbjs_action': '''
                        try{
                          //alert('m39');
                          var server = TacticServerStub.get();
                          title_code = '%s';
                          title_sk = '%s';
                          order_sk = '%s';
                          var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                          //var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder_' + order_sk);
                          var source_el = top_el.getElementsByClassName('sources_' + title_sk)[0];
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
                              server.insert('twog/title_origin', {title_code: title_code, source_code: source.code});
                              spt.api.load_panel(source_el, 'order_builder.SourcesRow', {title_code: title_code, title_sk: title_sk, order_sk: order_sk});
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
         ''' % (title_code, title_sk, my.order_sk)}
        return behavior

    def get_launch_wo_source_behavior(my, work_order_code, work_order_sk, wo_source):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          //alert('m42');
                          var server = TacticServerStub.get();
                          var work_order_code = '%s';
                          var work_order_sk = '%s';
                          var wo_source = '%s';
                          var order_sk = '%s';
                          spt.panel.load_popup('Source Portal', 'order_builder.SourceEditWdg', {'code': wo_source, 'order_sk': order_sk});
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (work_order_code, work_order_sk, wo_source, my.order_sk)}
        return behavior

    def get_launch_source_behavior(my, title_code, title_sk, source_code, source_sk):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          //alert('m43');
                          var server = TacticServerStub.get();
                          var title_code = '%s';
                          var title_sk = '%s';
                          var source_code = '%s';
                          var source_sk = '%s';
                          var order_sk = '%s';
                          spt.panel.load_popup('Source Portal', 'order_builder.SourceEditWdg', {'code': source_code, 'order_sk': order_sk});
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (title_code, title_sk, source_code, source_sk, my.order_sk)}
        return behavior

    def get_save_task_info_behavior(my, task_sk, parent_sk, parent_pyclass):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        function oc(a){
                            var o = {};
                            for(var i=0;i<a.length;i++){
                                o[a[i]]='';
                            }
                            return o;
                        }
                        try{
                          var server = TacticServerStub.get();
                          var task_sk = '%s';
                          var sk = '%s';
                          var parent_pyclass = '%s';
                          var order_sk = '%s';
                          var is_master_str = '%s';
                          var this_user = '%s';
                          var st = sk.split('?')[0];
                          task_code = task_sk.split('code=')[1];
                          var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                          var allowed_titles = top_el.getAttribute('allowed_titles');
                          if(allowed_titles == 'NOTHING|NOTHING'){
                              allowed_titles = '';
                          }
                          var task_panel = top_el.getElementsByClassName('task_table')[0];
                          priority_el = top_el.getElementsByClassName('priority_setter')[0];
                          priority = priority_el.value;
                          send_priority = ''
                          if(isNaN(priority)){
                              send_priority = -1;
                          }else{
                              send_priority = Number(priority);
                          }
                          sels = task_panel.getElementsByTagName('select');
                          assigned = '';
                          assigned_group = '';
                          new_status = '';
                          old_status = '';
                          status_sel = null;
                          for(var r = 0; r < sels.length; r++){
                              if(sels[r].name == 'task_assigned_select'){
                                  assigned = sels[r].value;
                              }else if(sels[r].name == 'task_stat_select'){
                                  new_status = sels[r].value;
                                  old_status = sels[r].getAttribute('old_status');
                                  status_sel = sels[r];
                              }else if(sels[r].name == 'task_assigned_group_select'){
                                  assigned_group = sels[r].value;
                              }
                          }
                          dates = task_panel.getElementsByTagName('input');
                          start_date = '';
                          end_date = '';
                          for(var r = 0; r < dates.length; r++){
                              if(dates[r].name == 'task_bid_start'){
                                  start_date = dates[r].value;
                              }else if(dates[r].name == 'task_bid_end'){
                                  end_date = dates[r].value;
                              }
                          }
                          var data = {};
                          if(st != 'twog/title'){
                              data = {'assigned': assigned, 'assigned_login_group': assigned_group, 'status': new_status};
                          }else{
                              data = {'assigned_login_group': assigned_group, 'status': new_status, 'assigned': assigned};
                          }
                          if(send_priority != -1){
                              data['priority'] = send_priority;
                          }
                          if(!(start_date == '' || start_date == null)){
                              data['bid_start_date'] = start_date
                          }
                          if(!(end_date == '' || end_date == null)){
                              data['bid_end_date'] = end_date
                          }
                          hours_el = top_el.getElementsByClassName('hour_adder')[0];
                          hours = hours_el.value;
                          if(hours == '' || hours == null){
                              hours = 0;
                          }
                          hours_dict = null;
                          order_sk = top_el.getAttribute('order_sk');
                          if(!(isNaN(hours))){
                              if(hours > 0){
                                  order_code = order_sk.split('code=')[1];
                                  the_order = server.eval("@SOBJECT(twog/order['code','" + order_code + "'])")[0];
                                  task = server.eval("@SOBJECT(sthpw/task['code','" + task_code + "'])")[0];
                                  the_title = server.eval("@SOBJECT(twog/title['code','" + task.title_code + "'])")[0];
                                  var today = new Date();
                                  var dd = today.getDate();
                                  var mm = today.getMonth() + 1;
                                  var yyyy = today.getFullYear();
                                  var day = yyyy + '-' + mm + '-' + dd + ' ' + today.getHours() + ':' + today.getMinutes() + ':' + today.getSeconds();
                                  is_billable = true;
                                  if(the_title.no_charge){
                                      is_billable = false;
                                  }
                                  hours_dict = {'task_code': task_code, 'client_code': the_order.client_code, 'client_name': the_order.client_name, 'title_code': task.title_code, 'category': task.process, 'process': task.process, 'scheduler': this_user, 'straight_time': hours, 'order_code': order_code, 'login': assigned, 'description': 'Added by scheduler in Order Builder', 'day': day, 'search_type': 'sthpw/task', 'search_id': task.id, 'is_billable': is_billable};
                                  server.insert('sthpw/work_hour', hours_dict);
                                  hours_el.value = '';
                              }
                          }else{
                              spt.alert("Please only add real numbers in the 'Add Hours' box");
                          }
                          server.update(task_sk, data);
                          display_mode = top_el.getAttribute('display_mode');
                          user = top_el.getAttribute('user');
                          groups_str = top_el.get('groups_str');
                          allowed_titles = top_el.getAttribute('allowed_titles');
                          parent_el = top_el.getElementsByClassName('cell_' + sk)[0];
                          found_parent_sk = parent_el.get('parent_sk');
                          found_parent_sid = parent_el.get('parent_sid');
                          send_data = {sk: sk, parent_sid: found_parent_sid, parent_sk: found_parent_sk, order_sk: order_sk, display_mode: display_mode, user: user, groups_str: groups_str, allowed_titles: allowed_titles, is_master: is_master_str, open_bottom: 'true'};
                          if(parent_pyclass == 'OrderTable'){
                              send_data['allowed_titles'] = allowed_titles;
                          }
                          spt.api.load_panel(parent_el, 'order_builder.' + parent_pyclass, send_data);
                          status_sel.setAttribute('old_status',new_status);
                          if('twog/order' != sk.split('?')[0]){
                              bot = top_el.getElementsByClassName('bot_' + sk)[0];
                              if(bot.style.display != 'none'){
                                  bot.style.display = 'none';
                                  bot.style.display = 'table-row';
                              }
                          }
                          if(st != 'twog/title'){
                              task = server.eval("@SOBJECT(sthpw/task['code','" + task_code + "'])")[0];
                              some_special_statuses = false;
                              some_path_prompts = false;
                              force_response_strings = '';
                              if(new_status in oc(['Rejected','Fix Needed','On Hold','Client Response'])){
                                  //Get a forced response as to why
                                  //Get production error generated prior to this, if applicable and send production error code to ForceResponseWdg
                                  some_special_statuses = true;
                                  production_error_code = '';
                                  if(new_status in oc(['Rejected','Fix Needed'])){
                                      error_entries = server.eval("@SOBJECT(twog/production_error['work_order_code','" + task.lookup_code + "'])")
                                      if((error_entries.length > 0)){
                                          error_entry = error_entries[error_entries.length - 1];
                                          production_error_code = error_entry.code;
                                      }
                                  }
                                  this_row_str = 'MTMX-Prompt:Please tell us why the new status for ' + task.process + ' is going to ' + new_status + 'MTMX-production_error_code:' + production_error_code + 'MTMX-work_order_code:' + task.lookup_code + 'MTMX-process:' + task.process + 'MTMX-new_status:' + new_status + 'MTMX-old_status:' + old_status;
                                  if(force_response_strings == ''){
                                      force_response_strings = this_row_str;
                                  }else{
                                      force_response_strings = force_response_strings + 'MTM_NEXT_MTM' + this_row_str;
                                  }
                              }else if(old_status in oc(['Rejected','Fix Needed','On Hold','Client Response'])){
                                  //Get a forced response as to why
                                  //Probably no production error here, so no need to send production error code
                                  production_error_code = '';
                                  some_special_statuses = true;
                                  this_row_str = 'MTMX-Prompt:Please tell us why the new status for ' + task.process + ' is going to ' + new_status + ' from ' + old_status + 'MTMX-production_error_code:' + production_error_code + 'MTMX-work_order_code:' + task.lookup_code + 'MTMX-process:' + task.process + 'MTMX-new_status:' + new_status + 'MTMX-old_status:' + old_status;
                                  if(force_response_strings == ''){
                                      force_response_strings = this_row_str;
                                  }else{
                                      force_response_strings = force_response_strings + 'MTM_NEXT_MTM' + this_row_str;
                                  }
                              }
                              if(new_status != old_status && new_status == 'Completed' && task.assigned_login_group in oc(['compression','compression supervisor','machine room','machine room supervisor','audio','edit','edit supervisor'])){
                                  this_row_str = 'MTMX-Prompt:Please Enter the Path to the File(s) for ' + task.process + '.\\nStatus went to ' + new_status + ' from ' + old_status + 'MTMX-work_order_code:' + task.lookup_code + 'MTMX-process:' + task.process + 'MTMX-new_status:' + new_status + 'MTMX-old_status:' + old_status;
                                  if(force_response_strings == ''){
                                      force_response_strings = this_row_str;
                                  }else{
                                      force_response_strings = force_response_strings + 'MTM_NEXT_MTM' + this_row_str;
                                  }
                                  some_path_prompts = true;
                              }
                              if(some_special_statuses || some_path_prompts){
                                  //Send to ForceResponseWdg
                                  add_str = '';
                                  if(some_path_prompts){
                                      add_str = ' or enter a file path where prompted';
                                  }
                                  spt.panel.load_popup('Please tell us why this work order is getting a special status' + add_str, 'operator_view.resetter.ForceResponseWdg', {'string_to_parse': force_response_strings});
                              }
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (task_sk, parent_sk, parent_pyclass, my.order_sk, my.is_master_str, my.user)}
        return behavior

    def get_highlight_wo_pipe_behavior(my):
        behavior = {'type': 'hover', 'cbjs_action': '''
                        try{
                            var order_sk = '%s';
                            var top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                            var ins = bvr.src_el.getAttribute('ins');
                            var in_split = ins.split(',');
                            for(var r =0; r < in_split.length; r++){
                                el = top_el.getElementById(in_split[r]);
                                if(in_split[r].indexOf('PROJ') != -1){
                                    el.style.background-color = '#d1e088';
                                }else{
                                    el.style.background-color = '#c4e4a4';
                                }
                            }
                            var outs = bvr.src_el.getAttribute('outs');
                            var out_split = outs.split(',');
                            for(var r =0; r < out_split.length; r++){
                                el = top_el.getElementById(out_split[r]);
                                if(out_split[r].indexOf('PROJ') != -1){
                                    el.style.background-color = '#21e088';
                                }else{
                                    el.style.background-color = '#24e4a4';
                                }
                            }

                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % my.order_sk,
         'cbjs_action_out': '''
                        try{
                            var order_sk = '%s';
                            var top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                            var ins = bvr.src_el.getAttribute('ins');
                            var in_split = ins.split(',');
                            for(var r =0; r < in_split.length; r++){
                                el = top_el.getElementById(in_split[r]);
                                if(in_split[r].indexOf('PROJ') != -1){
                                    el.style.background-color = '#d9ed8b';
                                }else{
                                    el.style.background-color = '#c6eda0';
                                }
                            }
                            var outs = bvr.src_el.getAttribute('outs');
                            var out_split = outs.split(',');
                            for(var r =0; r < out_split.length; r++){
                                el = top_el.getElementById(out_split[r]);
                                if(out_split[r].indexOf('PROJ') != -1){
                                    el.style.background-color = '#d9ed8b';
                                }else{
                                    el.style.background-color = '#c6eda0';
                                }
                            }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % my.order_sk}
        return behavior

    def get_panel_change_behavior(my, search_type, code, sk, order_sk, title, templ_code, edit_path, task_code, parent_sk, name, is_scheduler): # SIDDED THROUGH 'refresh_from_save'
        edit_mode = 'view'
        if is_scheduler:
            edit_mode = 'edit'
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          //alert('m48');
                          search_type = '%s';
                          code = '%s';
                          sk = '%s';
                          order_sk = '%s';
                          title = '%s';
                          edit_path = '%s';
                          templ_code = '%s';
                          task_code = '%s';
                          parent_sk = '%s';
                          name = '%s';
                          edit_mode = '%s';
                          name_for_selected = name;
                          spt.app_busy.show('Loading ' + title);
                          //var top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                          var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                          var client_code = top_el.get('client');
                          edit_panel = top_el.getElementsByClassName('edit_' + order_sk)[0];
                          wiki_panel = top_el.getElementsByClassName('main_wiki')[0];
                          translate_panel = top_el.getElementsByClassName('translate_cell')[0];
                          spt.api.load_panel(edit_panel, 'tactic.ui.panel.EditWdg', {element_name: 'general', mode: edit_mode, search_type: search_type, code: code, title: 'Modify ' + title, view: 'edit', widget_key: 'edit_layout', cbjs_edit_path: edit_path, scroll_height: '1000px'});
                          if(edit_mode == 'edit'){
                              task_panel = top_el.getElementsByClassName('task_cell')[0];
                              spt.api.load_panel(task_panel, 'order_builder.TaskEditWdg',  {task_code: task_code, parent_sk: parent_sk});
                          }
                          var sob_selected = top_el.getElementsByClassName('selected_sobject')[0];
                          sob_selected.innerHTML = 'Selected: ' + name_for_selected;
                          if(search_type != 'twog/order' && search_type != 'twog/equipment_used'){
                              var bot = top_el.getElementsByClassName('bot_' + sk)[0];
                              if(bot.style.display == 'none'){
                                  bot.style.display = 'table-row';
                              }else{
                                  bot.style.display = 'none';
                              }
                          }
                          spt.app_busy.hide();
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (search_type, code, sk, order_sk, title, edit_path, templ_code, task_code, parent_sk, name, edit_mode)}
        return behavior

    def get_killer_behavior(my, my_sk, parent_sk, parent_pyclass, title): #SIDDED
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          //alert('m56');
                          var parent_sk = '%s';
                          var parent_pyclass = '%s';
                          var my_sk = '%s';
                          var my_title = '%s';
                          var order_sk = '%s';
                          var is_master_str = '%s';
                          //alert('parent_sk = ' + parent_sk + ' parent_pyclass = ' + parent_pyclass + ' my_sk = ' + my_sk + ' my_title = ' + my_title);
                          if(confirm('Do you really want to delete ' + my_title + '?')){
                                  spt.app_busy.show('Deleting ' + my_title + '...');
                                  var server = TacticServerStub.get();
                                  //var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder_' + order_sk);
                                  var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                                  order_sk = top_el.getAttribute('order_sk');
                                  display_mode = top_el.getAttribute('display_mode');
                                  user = top_el.getAttribute('user');
                                  groups_str = top_el.get('groups_str');
                                  allowed_titles = top_el.getAttribute('allowed_titles');
                                  parent_el = top_el.getElementsByClassName('cell_' + parent_sk)[0];
                                  found_parent_sk = parent_el.get('parent_sk');
                                  found_parent_sid = parent_el.get('parent_sid');
                                  server.retire_sobject(my_sk);
                                  parent_code = parent_sk.split('code=')[1];
                                  if(parent_code.indexOf('TITLE') != -1){
                                      server.insert('twog/simplify_pipe', {'title_code': parent_code, 'do_all': 'yes'});
                                  }else if(parent_code.indexOf('PROJ') != -1){
                                      server.insert('twog/simplify_pipe', {'proj_code': parent_code, 'do_all': 'yes'});
                                  }
                                  send_data =  {sk: parent_sk, parent_sid: found_parent_sid, parent_sk: found_parent_sk, order_sk: order_sk, display_mode: display_mode, user: user, groups_str: groups_str, allowed_titles: allowed_titles, is_master: is_master_str};
                                  spt.api.load_panel(parent_el, 'order_builder.' + parent_pyclass, send_data);
                                  if('twog/order' != parent_sk.split('?')[0]){
                                      bot = top_el.getElementsByClassName('bot_' + parent_sk)[0];
                                      bot.style.display = 'table-row';
                                  }
                          }
                          spt.app_busy.hide();
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (parent_sk, parent_pyclass, my_sk, title, my.order_sk, my.is_master_str)}
        return behavior

    def get_add_proj_behavior(my, title_sk):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                            //alert('m57');
                            title_sk = '%s';
                            order_sk = '%s';
                            kwargs = {'title_sk': title_sk, 'order_sk': order_sk};
                            spt.panel.load_popup('Add Project', 'order_builder.order_builder.AddProjWdg', kwargs);
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (title_sk, my.order_sk)}
        return behavior

    def get_add_wo_behavior(my, proj_sk):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                            proj_sk = '%s';
                            order_sk = '%s';
                            kwargs = {'proj_sk': proj_sk, 'order_sk': order_sk};
                            spt.panel.load_popup('Add Work Order', 'order_builder.order_builder.AddWorkOrderWdg', kwargs);
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (proj_sk, my.order_sk)}
        return behavior

    def get_change_due_date_behavior(my, proj_code, proj_name): #PROBABLY NEED TO SID
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                            //alert('m57');
                            proj_code = '%s';
                            proj_name = '%s';
                            order_sk = '%s';
                            kwargs = {'proj_code': proj_code, 'proj_name': proj_name, 'order_sk': order_sk, 'send_wdg': 'OrderBuilder'};
                            spt.panel.load_popup("Change Due Date for " + proj_name + "'s work orders", 'order_builder.order_builder.ProjDueDateChanger', kwargs);

                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (proj_code, proj_name, my.order_sk)}
        return behavior

    def get_change_priority_behavior(my, proj_code, proj_name): #PROBABLY NEED TO SID
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                            //alert('m57');
                            var server = TacticServerStub.get();
                            proj_code = '%s';
                            proj_name = '%s';
                            order_sk = '%s';
                            is_master_str = '%s';
                            proj_sk = server.build_search_key('twog/proj', proj_code);
                            new_priority = prompt("Please enter the desired priority number for " + proj_name + "'s work orders.");
                            reload_wos = [];
                            if(!(isNaN(new_priority))){
                               update_priority = Number(new_priority);
                               server.update(proj_sk, {'priority': update_priority});
                               wos = server.eval("@SOBJECT(twog/work_order['proj_code','" + proj_code + "'])");
                               for(var r = 0; r < wos.length; r++){
                                   reload_wos.push(wos[r].__search_key__);
                               }
                            }
                            if(reload_wos.length > 0){
                                var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                                display_mode = top_el.getAttribute('display_mode');
                                user = top_el.getAttribute('user');
                                groups_str = top_el.get('groups_str');
                                allowed_titles = top_el.getAttribute('allowed_titles');
                                for(var r = 0; r < reload_wos.length; r++){
                                    wo_el = top_el.getElementsByClassName('cell_' + reload_wos[r])[0];
                                    sk = wo_el.get('sk');
                                    parent_sk = wo_el.get('parent_sk');
                                    parent_sid = wo_el.get('parent_sid');
                                    spt.api.load_panel(wo_el, 'order_builder.WorkOrderRow', {'sk': sk, 'parent_sk': parent_sk, 'order_sk': order_sk, 'parent_sid': parent_sid, display_mode: display_mode, user: user, groups_str: groups_str, allowed_titles: allowed_titles, is_master: is_master_str});
                                }
                            }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (proj_code, proj_name, my.order_sk, my.is_master_str)}
        return behavior

    def get_edit_hackup_connections(my, code, work_order_name):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                            //alert('m57');
                            code = '%s';
                            work_order_name = '%s';
                            spt.panel.load_popup('Edit Connections for ' + work_order_name, 'order_builder.EditHackPipe', {'code': code});
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (code, work_order_name)}
        return behavior

    def old_get_upload_behavior(my, search_key, process, ctx, processes):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                            //alert('m57');
                            search_key = '%s';
                            process = '%s';
                            ctx = '%s';
                            processes = '%s';
                            var values = {};
                            var top = bvr.src_el.getParent(".spt_checkin_top");
                            //alert('top = ' + top);
                            if(top){
                                var transfer_mode = top.getElement(".spt_checkin_transfer_mode").value;
                                values['transfer_mode'] = transfer_mode;
                            }
                            var options=  {
                                title: "Check-in Widget",
                                class_name: 'tactic.ui.widget.CheckinWdg',
                                popup_id: 'checkin_widget'
                            };
                            if(search_key.indexOf('ORDER') != -1){
                                search_key = search_key.replace('?proj=','?project=');
                            }
                            var bvr2 = {};
                            bvr2.options = options;
                            bvr2.values = values;
                            bvr2.args = {'search_key': search_key, 'process': process, 'context': ctx, 'processes': processes};
                            //alert(bvr2.args);
                            spt.popup.get_widget({}, bvr2);

                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (search_key, process, ctx, processes)}
        return behavior

    def get_save_outside_barcodes_behavior(my,source_code):
        if source_code == None:
            source_code = ''
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        function oc(a){
                            var o = {};
                            for(var i=0;i<a.length;i++){
                                o[a[i]]='';
                            }
                            return o;
                        }
                        try{
                          //alert('m58');
                          var server = TacticServerStub.get();
                          var out_tbl = spt.api.get_parent(bvr.src_el, '.outside_barcodes_list');
                          var source_code = '%s';
                          var added_one = false;
                          if(source_code != ''){
                                  var inps = out_tbl.getElementsByTagName('input');
                                  var pairs = {};
                                  var seen = [];
                                  for(var r = 0; r < inps.length; r++){
                                      if(inps[r].getAttribute('type') == 'text'){
                                          if(inps[r].value != ''){
                                              var name = inps[r].getAttribute('name');
                                              var num = Number(name.split('utside_barcode_insert_')[1]);
                                              if(!(num in oc(seen))){
                                                  seen.push(num);
                                                  pairs[num] = [];
                                              }
                                              pairs[num].push(inps[r].value);
                                          }
                                      }
                                  }
                                  sels = out_tbl.getElementsByTagName('select');
                                  for(var r = 0; r < sels.length; r++){
                                      var meclass = sels[r].getAttribute('class');
                                      var num = Number(meclass.split('utside_client_')[1]);
                                      if(sels[r].value != ''){
                                          if(num in oc(seen)){
                                              pairs[num].push(sels[r].value);
                                              if(sels[r].getAttribute('out_code') != ''){
                                                  pairs[num].push(sels[r].getAttribute('out_code'));
                                              }else{
                                                  pairs[num].push('');
                                              }
                                          }
                                      }else{
                                          if(num in oc(seen)){
                                              pairs[num].push('');
                                              pairs[num].push('');
                                              alert('Make Sure Barcode ' + pairs[num][0] + ' is associated with a client.');
                                          }
                                      }
                                  }
                                  for(var r = 0; r < seen.length; r++){
                                      if(pairs[r][0] != '' && pairs[r][1] != '' && pairs[r][2] == '' && source_code != ''){
                                              check_expr = "@SOBJECT(twog/outside_barcode['client_code','" + pairs[r][1] + "']['barcode','" + pairs[r][0] + "']['source_code','" + source_code + "'])";
                                              check = server.eval(check_expr);
                                              if(check.length < 1){
                                                  added_one = true;
                                                  server.insert('twog/outside_barcode',{'client_code': pairs[r][1], 'barcode': pairs[r][0].toUpperCase(), 'source_code': source_code});
                                              }else{
                                                  alert('Barcode ' + pairs[r][0] + ' is already in the system.');
                                              }
                                      }else if(pairs[r][0] != '' && pairs[r][1] != '' && pairs[r][2] != '' && source_code != ''){
                                          added_one = true;
                                          server.update(server.build_search_key('twog/outside_barcode', pairs[r][2]),{'client_code': pairs[r][1], 'barcode': pairs[r][0].toUpperCase(), 'source_code': source_code});
                                      }
                                  }
                                  if(added_one){
                                      alert('Outside Barcodes Assigned');
                                  }
                          }else{
                              alert("You have not saved the Source element yet. Please 'Add' it, then you can save the outside barcodes to it.");
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % source_code}
        return behavior

    def get_close_piper_behavior(my): #NO SID NECC
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          //alert('m60');
                          spt.app_busy.show('Closing Pipeline Editor...');
                          var order_sk = '%s';
                          //var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder_' + order_sk);
                          var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                          var closer_row = top_el.getElementsByClassName('closer_row')[0];
                          var pipe_row = top_el.getElementsByClassName('pipe_row')[0];
                          pipe_row.style.display = 'none';
                          closer_row.style.display = 'none';
                          spt.app_busy.hide();
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % my.order_sk}
        return behavior

    def get_launch_note_behavior(my, sk, name):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          //alert('m61');
                          var sk = '%s';
                          var name = '%s';
                          //alert(sk);
                          kwargs =  {'search_key': sk, 'append_process': 'Redelivery/Rejection Request,Redelivery/Rejection Completed', 'chronological': true};
                          if(sk.indexOf('TITLE') == -1){
                              kwargs['treedown'] = 'treedown';
                          }
                          spt.panel.load_popup('Notes for ' + name, 'tactic.ui.widget.DiscussionWdg', kwargs);
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (sk, name)}
        return behavior

    def get_launch_source_portal_behavior(my, work_order_name, work_order_sk, work_order_code, parent_pipe, is_master): #NO SID NECC
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          //alert('m65');
                          var work_order_name = '%s';
                          var work_order_sk = '%s';
                          var work_order_code = '%s';
                          var parent_pipe = '%s';
                          var is_master = '%s';
                          var client_code = '';
                          var order_sk = '%s';
                          var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                          client_code = top_el.get('client');
                          spt.panel.load_popup('Source Portal for ' + work_order_name, 'order_builder.SourcePortalWdg', {'work_order_sk': work_order_sk, 'work_order_code': work_order_code, 'client_code': client_code, 'parent_pipe': parent_pipe, 'is_master': is_master, 'order_sk': order_sk});
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (work_order_name, work_order_sk, work_order_code, parent_pipe, is_master, my.order_sk)}
        return behavior

    def get_launch_out_files_behavior(my, work_order_name, work_order_sk, work_order_code): #NO SID NECC
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          //alert('m66');
                          var work_order_name = '%s';
                          var work_order_sk = '%s';
                          var work_order_code = '%s';
                          var client_code = '';
                          var order_sk = '%s';
                          var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                          client_code = top_el.get('client');
                          spt.panel.load_popup('Out Files for ' + work_order_name, 'order_builder.OutFilesWdg', {'work_order_sk': work_order_sk, 'work_order_code': work_order_code, 'client_code': client_code, 'order_sk': order_sk});
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (work_order_name, work_order_sk, work_order_code, my.order_sk)}
        return behavior

    def get_eu_add_behavior(my, work_order_name, work_order_sk, work_order_code): #NO SID NECC
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          //alert('m67');
                          var work_order_name = '%s';
                          var work_order_sk = '%s';
                          var work_order_code = '%s';
                          var client_code = '';
                          var order_sk = '%s';
                          var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                          client_code = top_el.getAttribute('client');
                          spt.panel.load_popup('Add Equipment to ' + work_order_name, 'order_builder.EquipmentUsedMultiAdderWdg', {'work_order_sk': work_order_sk, 'order_sk': order_sk});
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (work_order_name, work_order_sk, work_order_code, my.order_sk)}
        return behavior

    def get_template_single_eu_from_multi_behavior(my,eq_sk,eq_templ_code,work_order_code,wot_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        function oc(a){
                            var o = {};
                            for(var i=0;i<a.length;i++){
                                o[a[i]]='';
                            }
                            return o;
                        }
                        try{
                          var server = TacticServerStub.get();
                          var eq_sk = '%s'; //this is the equipment code
                          var eq_templ_code = '%s';
                          var work_order_code = '%s';
                          var wot_code = '%s';
                          var order_sk = '%s';
                          var eq_code = eq_sk.split('code=')[1];
                          if(wot_code != '' && wot_code != null){
                              var top_el = document.getElementsByClassName('equipment_used_multi_adder_top_' + work_order_code)[0];
                              work_order_sk = top_el.getAttribute('work_order_sk');
                              client_code = top_el.getAttribute('client_code');
                              if(eq_templ_code != '' && eq_templ_code != null){
                                  eqt_sk = server.build_search_key('twog/equipment_used_templ', eq_templ_code);
                                  server.retire_sobject(eqt_sk);
                                  server.update(eq_sk, {'equipment_used_templ_code': ''})
                              }else{
                                  me_expr = "@SOBJECT(twog/equipment_used['code','" + eq_code + "'])";
                                  eq = server.eval(me_expr)[0];
                                  templ = server.insert('twog/equipment_used_templ',{'work_order_templ_code': wot_code, 'name': eq.name, 'description': eq.description, 'client_code': client_code, 'equipment_code': eq.equipment_code, 'expected_cost': eq.expected_cost, 'expected_duration': eq.expected_duration, 'expected_quantity': eq.expected_quantity, 'units': eq.units})
                                  server.update(eq_sk, {'equipment_used_templ_code': templ.code})
                              }
                                  spt.api.load_panel(top_el, 'order_builder.EquipmentUsedMultiAdderWdg', {'work_order_sk': work_order_sk, 'order_sk': order_sk});
                          }else{
                              alert('The Work Order Must Be Templated First');
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (eq_sk, eq_templ_code, work_order_code, wot_code, my.order_sk)}
        return behavior


    def get_templ_eus_behavior(my, wo_code, wo_sk, wot_code): #NO SID NECC
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        function oc(a){
                            var o = {};
                            for(var i=0;i<a.length;i++){
                                o[a[i]]='';
                            }
                            return o;
                        }
                        try{
                          //alert('m69');
                          var wo_code = '%s';
                          var wo_sk = '%s';
                          var wot_code = '%s'; //this is the work order template code
                          var order_sk = '%s';
                          var is_master_str = '%s';
                          spt.app_busy.show('Adding Equipment Templates');
                          var server = TacticServerStub.get();
                          //var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder_' + order_sk);
                          var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                          display_mode = top_el.getAttribute('display_mode');
                          groups_str = top_el.getAttribute('groups_str');
                          user = top_el.getAttribute('user');
                          var client_code = top_el.get('client');
                          var eus_expr = "@SOBJECT(twog/equipment_used['work_order_code','" + wo_code + "'])";
                          var eus = server.eval(eus_expr);
                          var euts_expr = "@SOBJECT(twog/equipment_used_templ['work_order_templ_code','" + wot_code + "'])";
                          var euts = server.eval(euts_expr);
                          if(euts.length > eus.length){
                              for(var t = 0; t < euts.length; t++){
                                  match = false;
                                  for(var r = 0; r < eus.length; r++){
                                      if(euts[t].name == eus[r].name){
                                          match = true;
                                      }
                                  }
                                  if(!match){
                                      server.retire_sobject(euts[t].__search_key__);
                                  }
                              }
                          }
                          for(var r = 0; r < eus.length; r++){
                              eus_templ_code = eus[r].equipment_used_templ_code;
                              if(eus_templ_code != '' && eus_templ_code != null){
                                  eut_expr = "@SOBJECT(twog/equipment_used_templ['code','" + eus[r].equipment_used_templ_code + "'])";
                                  eut = server.eval(eut_expr)[0];
                                  data = {};
                                  for(var item in eut){
                                      if(eus[r][item] != eut[item] && !(item in oc(['code','timestamp','s_status','login','id']))){
                                          data[item] = eus[r][item];
                                      }
                                  }
                                  if(data != {}){
                                      server.update(eut.__search_key__, data);
                                  }
                              }else{
                                  var equipment_code = eus[r].equipment_code;
                                  var expected_cost = eus[r].expected_cost;
                                  var expected_duration = eus[r].expected_duration;
                                  var expected_quantity = eus[r].expected_quantity;
                                  var eu_name = eus[r].name;
                                  var eu_descrip = eus[r].description;
                                  var eu_sk = eus[r].__search_key__;
                                  var units = eus[r].units;
                                  templ = server.insert('twog/equipment_used_templ',{'work_order_templ_code': wot_code, 'name': eu_name, 'description': eu_descrip, 'client_code': client_code, 'equipment_code': equipment_code, 'expected_cost': expected_cost, 'expected_duration': expected_duration, 'expected_quantity': expected_quantity, 'units': units})
                                  server.update(eu_sk, {'equipment_used_templ_code': templ.code})
                              }
                              var my_cell_poss = top_el.getElementsByClassName('cell_' + eus[r].__search_key__);
                              if(my_cell_poss.length > 0){
                                  my_cell = my_cell_poss[0];
                                  spt.api.load_panel(my_cell, 'order_builder.EquipmentUsedRow', {'sk': my_cell.getAttribute('sk'), 'parent_sk': my_cell.getAttribute('parent_sk'), 'parent_sid': my_cell.getAttribute('parent_sid'), 'order_sk': my_cell.getAttribute('order_sk'), 'display_mode': display_mode, 'user': user, 'groups_str': groups_str, is_master: is_master_str});
                              }
                          }
                          spt.app_busy.hide();
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (wo_code, wo_sk, wot_code, my.order_sk, my.is_master_str)}
        return behavior

    def get_eq_change_behavior(my, work_order_code): #NO SID NECC
        behavior = {'css_class': 'sel_change', 'type': 'change', 'cbjs_action': '''
                        try{
                          //alert('m70');
                          var server = TacticServerStub.get();
                          var work_order_code = '%s';
                          var top_el = document.getElementsByClassName('equipment_used_adder_top_' + work_order_code)[0];
                          var puller1 = '';
                          var puller2 = '';
                          var unit_el = '';
                          var sels = top_el.getElementsByTagName('select');
                          for(var r= 0; r < sels.length; r++){
                              if(sels[r].name == 'equipment_changer'){
                                  puller1 = sels[r];
                              }else if(sels[r].name == 'client_eu_changer'){
                                  puller2 = sels[r];
                              }else if(sels[r].name == 'eu_add_units'){
                                  unit_el = sels[r];
                              }
                          }
                          if(puller1.value != 'NOTHINGXsXNOTHING'){
                              puller2.value = 'NOTHINGXsXNOTHING';
                              var name_el = top_el.getElementsByClassName('eu_add_name')[0];
                              var quantity_el = top_el.getElementsByClassName('eu_add_quantity')[0];
                              var duration_el = top_el.getElementsByClassName('eu_add_duration')[0];
                              var description_el = top_el.getElementsByClassName('eu_add_description')[0];
                              splits = puller1.value.split('XsX');
                              e_code = splits[0];
                              e_name = splits[1];
                              e_expr = "@SOBJECT(twog/equipment['code','" + e_code + "'])";
                              equip = server.eval(e_expr)[0];
                              name_el.value = equip.name;
                              quantity_el.value = '';
                              duration_el.value = '';
                              description_el.innerHTML = equip.description;
                              description_el.value = equip.description;
                              unit_el.value = equip.units;
                              //this needs to set the other pulldown to --Select--
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % work_order_code}
        return behavior

    def get_client_eq_change_behavior(my, work_order_code): #NO SID NECC
        behavior = {'css_class': 'sel_change', 'type': 'change', 'cbjs_action': '''
                        try{
                          //alert('m71');
                          var work_order_code = '%s';
                          var server = TacticServerStub.get();
                          var top_el = document.getElementsByClassName('equipment_used_adder_top_' + work_order_code)[0];
                          var puller1 = '';
                          var puller2 = '';
                          var unit_el = '';
                          var sels = top_el.getElementsByTagName('select');
                          for(var r= 0; r < sels.length; r++){
                              if(sels[r].name == 'equipment_changer'){
                                  puller1 = sels[r];
                              }else if(sels[r].name == 'client_eu_changer'){
                                  puller2 = sels[r];
                              }else if(sels[r].name == 'eu_add_units'){
                                  unit_el = sels[r];
                              }
                          }
                          if(puller2.value != 'NOTHINGXsXNOTHING'){
                              puller1.value = 'NOTHINGXsXNOTHING';
                              var name_el = top_el.getElementsByClassName('eu_add_name')[0];
                              var quantity_el = top_el.getElementsByClassName('eu_add_quantity')[0];
                              var duration_el = top_el.getElementsByClassName('eu_add_duration')[0];
                              var description_el = top_el.getElementsByClassName('eu_add_description')[0];
                              splits = puller2.value.split('XsX');
                              eut_code = splits[0];
                              eut_name = splits[1];
                              eut_expr = "@SOBJECT(twog/equipment_used_templ['code','" + eut_code + "'])";
                              eut = server.eval(eut_expr)[0];
                              if(eut != {}){
                                  name_el.value = eut.name;
                                  quantity_el.value = eut.expected_quantity;
                                  duration_el.value = eut.expected_duration;
                                  description_el.innerHTML = eut.description;
                                  description_el.value = eut.description;
                                  unit_el.value = eut.units;
                              }
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % work_order_code}
        return behavior

    def get_alter_prio_behavior(my, proj_sk):
        behavior = {'css_class': 'txt_change', 'type': 'change', 'cbjs_action': '''
                        function flicker(a){
                            a.style.background = '#FF0000';
                            setTimeout(function(){a.style.background = '#FFFFFF';}, 1000);
                        }
                        try{
                          var proj_sk = '%s';
                          var server = TacticServerStub.get();
                          var new_prio = bvr.src_el.value;
                          var old_val = bvr.src_el.getAttribute('old_prio');
                          new_prio = new_prio.trim();
                          if(!(isNaN(new_prio))){
                              new_val = Number(new_prio);
                              server.update(proj_sk, {'priority': new_val});
                              bvr.src_el.setAttribute('old_prio',new_val);
                              flicker(bvr.src_el);
                          }else{
                              bvr.src_el.value = old_val;
                              alert('Please only enter numbers into this box');
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % proj_sk}
        return behavior

    def get_eu_submit_behavior(my, work_order_code, parent_pyclass): #SIDDED
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          var work_order_code = '%s';
                          var parent_pyclass = '%s';
                          var is_master_str = '%s';
                          var server = TacticServerStub.get();
                          var top_el = document.getElementsByClassName('equipment_used_adder_top_' + work_order_code)[0];
                          var name_el = top_el.getElementsByClassName('eu_add_name')[0];
                          var quantity_el = top_el.getElementsByClassName('eu_add_quantity')[0];
                          var duration_el = top_el.getElementsByClassName('eu_add_duration')[0];
                          var sels = top_el.getElementsByTagName('select');
                          var unit_el = '';
                          var changer_el =  '';
                          var client_changer_el = '';
                          for(var r= 0; r < sels.length; r++){
                              if(sels[r].name == 'eu_add_units'){
                                  unit_el = sels[r];
                              }else if(sels[r].name == 'equipment_changer'){
                                  changer_el = sels[r];
                              }else if(sels[r].name == 'client_eu_changer'){
                                  client_changer_el = sels[r];
                              }
                          }
                          var description_el = top_el.getElementsByClassName('eu_add_description')[0];
                          var name = name_el.value;
                          var quantity = quantity_el.value;
                          var duration = duration_el.value;
                          var description = description_el.value;
                          var units = unit_el.value;
                          var client_changer_pair = client_changer_el.value;
                          var splits = client_changer_pair.split('XsX');
                          var client_changer_code = splits[0];
                          var client_changer_name = splits[1];
                          var equipment_used_templ_code = client_changer_code;
                          var changer_pair = changer_el.value;
                          var splits = changer_pair.split('XsX');
                          var changer_code = splits[0];
                          var changer_name = splits[1];
                          var new_equip = '';
                          var equip_code = changer_code;
                          var boolio = false;
                          if(changer_name != name && (client_changer_pair == 'NOTHINGXsXNOTHING' || client_changer_pair == '')){
                              //this is a new piece of equipment
                              if(confirm('"' + name + '" looks like new equipment to me.\\nWould you like to add it as a new equipment type?')){
                                  var count = prompt('Please enter the number of instances of this piece of equipment we have for use.');
                                  var amount_we_paid = prompt('Please enter the amount we paid - per piece - for this equipment.');
                                  var eq_desc = prompt('Please enter any other details we would like to remember about this equipment type.');
                                  new_equip = server.insert('twog/equipment', {'name': name, 'count': count, 'amount_we_paid': amount_we_paid, 'description': eq_desc});
                                  equip_code = new_equip.code;
                              }else{
                                  alert('Ok, I will not add "' + name + '" as a new equipment type. Adding equipment to work_order...');
                              }
                          }
                          if(client_changer_pair != 'NOTHINGXsXNOTHING' && client_changer_pair != ''){
                              expr = "@SOBJECT(twog/equipment_used_templ['code','" + equipment_used_templ_code + "'])";
                              eut = server.eval(expr)[0];
                              if(eut != {}){
                                  equip_code = eut.equipment_code;
                              }
                          }
                          boolio = true
                          //now create the equipment_used entry, remember to set the equipment code from new_equip if it is not ''
                          if(equipment_used_templ_code == 'NOTHING'){
                              equipment_used_templ_code = '';
                          }
                          if(units == 'NOTHING'){
                              units = '';
                          }
                          server.insert('twog/equipment_used', {'equipment_code': equip_code, 'work_order_code': work_order_code, 'description': description, 'expected_quantity': quantity, 'expected_duration': duration, 'name': name, 'equipment_used_templ_code': equipment_used_templ_code, 'units': units});
                          var wo_sk = server.build_search_key('twog/work_order', work_order_code);
                          var wo_el = document.getElementsByClassName('cell_' + wo_sk)[0];
                          var sk = wo_el.get('sk');
                          var parent_sk = wo_el.get('parent_sk');
                          var order_sk = wo_el.get('order_sk');
                          var parent_sid = wo_el.get('parent_sid');
                          display_mode = wo_el.getAttribute('display_mode');
                          user = wo_el.getAttribute('user');
                          groups_str = wo_el.get('groups_str');
                          allowed_titles = wo_el.getAttribute('allowed_titles');
                          spt.api.load_panel(wo_el, 'order_builder.WorkOrderRow', {'sk': sk, 'parent_sk': parent_sk, 'order_sk': order_sk, 'parent_sid': parent_sid, 'display_mode': display_mode, 'user': user, 'groups_str': groups_str, is_master: is_master_str});

                          var wo_bot = document.getElementsByClassName('bot_' + wo_sk)[0];
                          wo_bot.style.display = 'table-row';
                          if(boolio){
                              spt.popup.close(spt.popup.get_popup(bvr.src_el));
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
         ''' % (work_order_code, parent_pyclass, my.is_master_str)}
        return behavior
