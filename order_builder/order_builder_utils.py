# Lines 229, 1063
# Lines 2627, 5021, 5460 also fit under this, they used a smaller subset of this dictionary

# 'Not Set' key was written twice, once as '#d7d7d7' and again as '#FFFFCC'
# I've removed the second one for now. Not sure which one is correct

from pyasm.web import DivWdg
from pyasm.search import Search
from pyasm.widget import SelectWdg


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


def get_label_widget(label):
    """
    Given a label string, return a DivWdg containing the label

    :param label: String
    :return: DivWdg
    """
    widget = DivWdg()
    widget.add(label)

    return widget


def get_select_widget_from_search_type(search_type, label, label_column, value_column):
    """
    Given a search_type, create a SelectWdg. Provide label, label_column, and value_column to set the SearchWdg
    attributes.

    :param search_type: s_type ('twog/title' for example)
    :param label: String, set as 'label' on the select html element
    :param label_column: String, the database column to use for the option labels
    :param value_column: String, the database column to use for the option values
    :return: SelectWdg
    """
    search = Search(search_type)

    search_wdg = SelectWdg(label)
    search_wdg.add_empty_option('----')
    search_wdg.set_search_for_options(search, label_column=label_column, value_column=value_column)

    return search_wdg


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


def get_panel_change_behavior(search_type, code, sk, order_sk, title, templ_code, edit_path, task_code, parent_sk,
                              name, is_scheduler):
    if is_scheduler:
        edit_mode = 'edit'
    else:
        edit_mode = 'view'

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


def get_edit_hackup_connections(code, work_order_name):
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


def get_launch_source_behavior(title_code, title_sk, source_code, source_sk, order_sk):
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
     ''' % (title_code, title_sk, source_code, source_sk, order_sk)}
    return behavior


def get_launch_note_behavior(sk, name):
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


def get_killer_behavior(my_sk, parent_sk, parent_pyclass, title, order_sk, is_master):
    if is_master:
        is_master_str = 'true'
    else:
        is_master_str = 'false'

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
     ''' % (parent_sk, parent_pyclass, my_sk, title, order_sk, is_master_str)}
    return behavior
