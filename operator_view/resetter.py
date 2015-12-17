__all__ = ["WOResetWdg","WOResetWdg2","ForceResponseWdg","MakeNoteWdg","MakeBasicNoteWdg"]
import tacticenv
from pyasm.common import Environment
from pyasm.biz import *
from pyasm.web import Table, DivWdg
from pyasm.widget import SelectWdg, IconWdg, TextWdg, CheckboxWdg
from pyasm.prod.biz import ProdSetting
from tactic.ui.common import BaseTableElementWdg
from tactic.ui.common import BaseRefreshWdg
from pyasm.command import *
from formatted_emailer import email_sender, EmailDirections
import common_tools.utils as ctu


class WOResetWdg(BaseRefreshWdg):

    def init(my):
        from client.tactic_client_lib import TacticServerStub
        my.server = TacticServerStub.get()
        login = Environment.get_login()
        my.user = login.get_login()
        my.stat_colors = {'Assignment': '#fcaf88', 'Pending': '#d7d7d7', 'In Progress': '#f5f3a4', 'In_Progress': '#f5f3a4', 'In Production': '#f5f3a4', 'In_Production': '#f5f3a4', 'In production': '#f5f3a4', 'In_production': '#f5f3a4', 'Waiting': '#ffd97f', 'Need Assistance': '#fc88fb', 'Need_Assistance': '#fc88fb', 'Review': '#888bfc', 'Approved': '#d4b5e7', 'On Hold': '#e8b2b8', 'On_Hold': '#e8b2b8', 'Client Response': '#ddd5b8', 'Completed': '#b7e0a5', 'Ready': '#b2cee8', 'Internal Rejection': '#ff0000', 'External Rejection': '#ff0000', 'Rejected': '#ff0000', 'Failed QC': '#ff0000', 'Fix Needed': '#c466a1', 'Need Buddy Check': '#e3701a', 'DR In_Progress': '#d6e0a4', 'DR In Progress': '#d6e0a4','Amberfin01_In_Progress':'#D8F1A8', 'Amberfin01 In Progress':'#D8F1A8', 'Amberfin02_In_Progress':'#F3D291',  'Amberfin02 In Progress':'#F3D291','BATON In_Progress': '#c6e0a4', 'BATON In Progress': '#c6e0a4','Export In_Progress': '#796999', 'Export In Progress': '#796999','Buddy Check In_Progress': '#1aade3','Buddy Check In Progress': '#1aade3'}

    def get_set_notify(my, s, title_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                try{
                    var s = '%s';
                    var title_code = '%s';
                    notify_el = document.getElementsByClassName('notify_' + title_code)[0];
                    notify_el.innerHTML = s;
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (s, title_code)}
        return behavior

    def get_change_statuses(my, title_code, wo_code, wo_name):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                try{
                    var title_code = '%s';
                    var wo_code = '%s';
                    var wo_name = '%s';
                    notify_el = document.getElementsByClassName('notify_' + title_code)[0];
                    notify = notify_el.innerHTML;
                    status = "";
                    if(notify.indexOf("Ready") != -1){
                        status = 'Ready';
                    }
                    if(notify.indexOf("Pending") != -1){
                        status = 'Pending';
                    }
                    var title_el = document.getElementsByClassName('resetter_' + title_code)[0];
                    var checkboxes = title_el.getElementsByTagName('input');
                    var server = TacticServerStub.get();
                    title_sk = server.build_search_key('twog/title', title_code);
                    info = ''
                    if(status == 'Ready'){
                        entered = false;
                        info = '';
                        while(!entered){
                            info = prompt("What needs to be fixed?");
                            if(info != '' && info != null){
                                entered = true;
                            }
                        }
                        note = 'A Fix Needed was issued for ' + wo_name + ' (' + wo_code + '). Explanation is: ' + info;
                        thing = server.execute_cmd('operator_view.MakeNoteWdg', {'obj_sk': title_sk, 'header': wo_name + " - Fix Needed", 'note': note, 'note_ccs': ''});
                        error_entries = server.eval("@SOBJECT(twog/production_error['work_order_code','" + wo_code + "'])")
                        error_entry = error_entries[error_entries.length - 1];
                        server.update(error_entry.__search_key__, {'operator_description': note});
                    }
                    group_email_lookup = {'admin': 'administrator@2gdigital.com', 'it': 'IT@2gdigital.com', 'qc': 'QC@2gdigital.com', 'qc_supervisor': 'QC@2gdigital.com', 'compression': 'Compression@2gdigital.com', 'billing_and_accounts_receivable': '2GSales@2gdigital.com', 'audio': 'Audio@2gdigital.com', 'compression_supervisor': 'Compression@2gdigital.com', 'edeliveries': 'Edeliveries@2gdigital.com', 'machine_room': 'MR@2gdigital.com', 'media_vault': 'Mediavault@2gdigital.com', 'media_vault_supervisor': 'Mediavault@2gdigital.com', 'edit_supervisor': 'Editors@2gdigital.com', 'machine_room_supervisor': 'MR@2gdigital.com', 'office_employees': 'jaime.torres@2gdigital.com;adriana.amador@2gdigital.com', 'edit': 'Editors@2gdigital.com', 'sales': '2GSales@2gdigital.com', 'senior_staff': 'fernando.vasquez@2gdigital.com;jaime.torres@2gdigital.com;adriana.amador@2gdigital.com;stephen.buchsbaum@2gdigital.com', 'executives': 'stephen.buchsbaum@2gdigital.com', 'management': 'jaime.torres@2gdigital.com;adriana.amador@2gdigital.com', 'scheduling': 'scheduling@2gdigital.com', 'streamz': 'MR@2gdigital.com;QC@2gdigital.com;Editors@2gdigital.com', 'technical_services': 'IT@2gdigital.com', 'sales_supervisor': '2GSales@2gdigital.com', 'scheduling_supervisor': 'scheduling@2gdigital.com', 'vault': 'Mediavault@2gdigital.com'}
                    if(confirm("Change all selected work orders to " + status + "?")){
                        spt.app_busy.show("Setting selected work order statuses to " + status); 
                        for(var r = 0; r < checkboxes.length; r++){
                            if(checkboxes[r].type == 'checkbox'){
                                if(checkboxes[r].name.indexOf('selector_') != -1 && checkboxes[r].checked){
                                    group_email_str = '';
                                    code_s = checkboxes[r].name.split('_');
                                    that_code = code_s[1] + '_' + code_s[2];
                                    work_order = server.eval("@SOBJECT(twog/work_order['code','" + that_code + "'])")[0];
                                    if(status == 'Ready'){
                                        wg = work_order.work_group;
                                        if(wg != '' && wg != null){
                                            group_email_str = group_email_lookup[wg]
                                        } 
                                    }
                                    task = server.eval("@SOBJECT(sthpw/task['lookup_code','" + that_code + "'])")[0];
                                    server.update(task.__search_key__, {'status': status});
                                    if(status == "Ready"){
                                        note = 'A Fix Needed was issued for ' + wo_name + ' (' + wo_code + '). This work order (' + task.process + ') will need to be redone as a result. Explanation is: ' + info;
                                        thing = server.execute_cmd('operator_view.MakeNoteWdg', {'obj_sk': title_sk, 'header': task.process + " - Reset for Fix", 'note': note, 'note_ccs': group_email_str});
                                    }
                                    proj_task = server.eval("@SOBJECT(sthpw/task['lookup_code','" + work_order.proj_code + "'])")[0];
                                    if(status == 'Pending'){
                                        wo_tasks = server.eval("@SOBJECT(twog/work_order['proj_code','" + work_order.proj_code + "'].WT:sthpw/task)");
                                        all_pending = true;
                                        for(var g = 0; g < wo_tasks.length; g++){
                                            if(wo_tasks[g].status != "Pending"){
                                                all_pending = false; 
                                            }
                                        }
                                        if(all_pending){
                                            server.update(proj_task.__search_key__, {'status': "Pending"});
                                        }
                                    }else if(status == 'Ready'){
                                        server.update(proj_task.__search_key__, {'status': "Ready"});     
                                    }
                                }
                            }
                        }
                        spt.app_busy.hide();
                    }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (title_code, wo_code, wo_name)}
        return behavior

    def get_reset_auto_select_behavior(my, title_code):
        behavior = {'css_class': 'clickme', 'type': 'change', 'cbjs_action': '''        
                        function oc(a){
                            var o = {};
                            for(var i=0;i<a.length;i++){
                                o[a[i]]='';
                            }
                            return o;
                        }
                        function getKeys(obj){
                            keys = [];
                            for(var key in obj){
                                keys.push(key);
                            } 
                            return keys;
                        }
                        function isEmpty(obj) {
                            for(var prop in obj) {
                                if(obj.hasOwnProperty(prop))
                                    return false;
                            }
                        
                            return true;
                        }
                        function alertHash(obj, name){
                            for(var key in obj){
                                alert(name + key + '-> [' + obj[key] + ']');
                            }
                        }
                        function recurse_buffer(arr_sendback, tos, current_name, seen, connections){
                            for(var r = 0; r < tos.length; r++){
                                if(!(tos[r] in oc(arr_sendback))){
                                    new_arr = recurse_for_branch(tos[r], connections, seen, arr_sendback);
                                    for(var t = 0; t < new_arr.length; t++){
                                        if(!(new_arr[t] in oc(arr_sendback))){
                                            arr_sendback.push(new_arr[t]);
                                        }
                                    }
                                }
                            }
                            return arr_sendback;

                        }
                        function recurse_for_branch(current_name, connections, seen, arr_sendback){
                            arr_sendback.push(current_name);
                            if(current_name in oc(seen) && !(isEmpty(connections))){
                                tos = connections[current_name];
                                arr_sendback = recurse_buffer(arr_sendback, tos, current_name, seen, connections); 
                            }
                            return arr_sendback;
                        }
                        function pipe_data(pipeline_xml){
                              seen = [];
                              connections = {}
                              cut1 = pipeline_xml.split('connect from="');
                              portions = cut1.slice(1, cut1.length);
                              for(var r = 0; r < portions.length; r++){
                                   cut2 = portions[r].split('" to="');
                                   cfrom = cut2[0];
                                   cto = cut2[1].split('"')[0];
                                   if(!(cfrom in oc(seen))){
                                       seen.push(cfrom); 
                                       connections[cfrom] = [cto];
                                   }else{
                                       connections[cfrom].push(cto);
                                   }
                              }
                            return [connections, seen];
                        }
                        function fill_hackpipe_connections(st, parent_code, seen, connections){
                            disconnected = [];
                            parent_code_type = 'title_code';
                            if(st == 'twog/work_order'){
                                parent_code_type = 'proj_code';
                            }
                            hacks = server.eval("@SOBJECT(" + st + "['creation_type','hackup']['" + parent_code_type + "','" + parent_code + "'])");
                            if(hacks.length > 0){
                                for(var r = 0; r < hacks.length; r++){
                                    connected = false;
                                    as_pre_expr = "@SOBJECT(twog/hackpipe_out['lookup_code','" + hacks[r].code + "'])";
                                    as_pre = server.eval(as_pre_expr);
                                    //alertHash(connections, 'HASH ');
                                    for(var f = 0; f < as_pre.length; f++){
                                        out_to = as_pre[f].out_to;
                                        pname = server.eval("@GET(" + st + "['code','" + out_to + "'].process)");
                                        out_name = '';
                                        if(pname.length > 0){
                                            out_name = pname[0];
                                            if(!(hacks[r].process in oc(getKeys(connections)))){
                                                connections[hacks[r].process] = [out_name];
                                                seen.push(hacks[r].process);
                                            }else{
                                                connections[hacks[r].process].push(out_name);
                                            }
                                            connected = true;
                                        }
                                    }
                                    as_post_expr = "@SOBJECT(twog/hackpipe_out['out_to','" + hacks[r].code + "'])";
                                    as_post = server.eval(as_post_expr);
                                    for(var f = 0; f < as_post.length; f++){
                                        lookup_code = as_post[f].lookup_code;
                                        pname = server.eval("@GET(" + st + "['code','" + lookup_code + "'].process)");
                                        lookup_name = '';
                                        if(pname.length > 0){
                                            lookup_name = pname[0];
                                            if(!(lookup_name in oc(getKeys(connections)))){
                                                connections[lookup_name] = [hacks[r].process];
                                                seen.push(lookup_name);
                                            }else{
                                                connections[lookup_name].push(hacks[r].process);
                                            }
                                            connected = true;
                                        }
                                    }
                                    if(!connected){
                                        //Then these are being triggered straight from the parent. They need to be pushed in to the final set to do
                                        disconnected.push(hacks[r].code);
                                    }
                                } 
                            }
                            return [connections, seen, disconnected];
                        }
                        
                try{
                          title_code = '%s';
                          var notify_el = document.getElementsByClassName('notify_' + title_code)[0]; 
                          notify = notify_el.innerHTML;
                          if(bvr.src_el.checked && notify.indexOf("Ready") == -1 && notify.indexOf("Pending") == -1){
                              spt.app_busy.show("Determining Work Flow...");
                              var name = bvr.src_el.name;
                              var code = name.split('_')[1] + '_' + name.split('_')[2];
                              var server = TacticServerStub.get();
                              title = server.eval("@SOBJECT(twog/work_order['code','" + code + "'].twog/proj.twog/title)");
                              proj = server.eval("@SOBJECT(twog/work_order['code','" + code + "'].twog/proj)")[0];
                              work_order = server.eval("@SOBJECT(twog/work_order['code','" + code + "'])")[0];
                              wos_to_do = [];
                              if(title.length > 0){
                                  title = title[0];
                                  pipeline_code = title.pipeline_code;
                                  pipe = server.eval("@SOBJECT(sthpw/pipeline['code','" + pipeline_code + "'])");
                                  if(pipe.length > 0){
                                      pipe = pipe[0];
                                      pipeline_xml = pipe.pipeline;
                                      pipe_res = pipe_data(pipeline_xml);
                                      proj_connections = pipe_res[0];
                                      proj_seen = pipe_res[1];
                                      pipe_res2 = fill_hackpipe_connections('twog/proj', title.code, proj_seen, proj_connections);
                                      proj_connections = pipe_res2[0];
                                      proj_seen = pipe_res2[1];
                                      current_name = proj.process; 
                                      proj_doers = recurse_for_branch(current_name, proj_connections, proj_seen, []);
                                      for(var r = 0; r < proj_doers.length; r++){
                                          proj2_expr = "@SOBJECT(twog/proj['title_code','" + title.code + "']['process','" + proj_doers[r] + "'])";
                                          proj2 = server.eval(proj2_expr);
                                          if(proj2.length > 0){
                                              proj2 = proj2[0];
                                              proj_pipe_expr = "@SOBJECT(sthpw/pipeline['code','" + proj2.pipeline_code + "'])";
                                              proj_pipe = server.eval(proj_pipe_expr);
                                              if(proj_pipe.length > 0){
                                                  proj_pipe = proj_pipe[0];
                                                  proj_pipe_xml = proj_pipe.pipeline;
                                                  pdata = pipe_data(proj_pipe_xml);
                                                  wo_connections = pdata[0];
                                                  wo_seen = pdata[1];
                                                  if(wo_seen.length == 0){
                                                      add_wo = server.eval("@GET(twog/proj['code','" + proj2.code + "'].twog/work_order.process)");
                                                      if(add_wo.length != 0){
                                                          wo_seen.push(add_wo[0]);
                                                      }
                                                  }
                                                  wdata = fill_hackpipe_connections('twog/work_order', proj2.code, wo_seen, wo_connections);  
                                                  wo_connections = wdata[0];
                                                  wo_seen = wdata[1];
                                                  wo_disconnected = wdata[2];
                                                  wo_name = wo_seen[0];
                                                  if(proj2.code == proj.code){
                                                      wo_name = work_order.process;
                                                  }
                                                  wo_doers = recurse_for_branch(wo_name, wo_connections, wo_seen, []);
                                                  wo_doer_str = wo_doers.join('|');
                                                  wos = server.eval("@SOBJECT(twog/proj['title_code','" + title.code + "']['process','" + proj_doers[r] + "'].twog/work_order['process','in','" + wo_doer_str + "'])");
                                                  for(var d = 0; d < wos.length; d++){
                                                      wos_to_do.push(wos[d].code);
                                                  }
                                                  for(var d = 0; d < wo_disconnected.length; d++){
                                                      wos_to_do.push(wo_disconnected[d]);
                                                  }
                                              }else{
                                                  wdata = fill_hackpipe_connections('twog/work_order', proj2.code, [], {});
                                                  wo_connections = wdata[0];
                                                  wo_seen = wdata[1];
                                                  wo_disconnected = wdata[2];
                                                  wo_name = wo_seen[0];
                                                  if(proj2.code == proj.code){
                                                      wo_name = work_order.process;
                                                  }
                                                  wo_doers = recurse_for_branch(wo_name, wo_connections, wo_seen, []);
                                                  wo_doer_str = wo_doers.join('|');
                                                  wos = server.eval("@SOBJECT(twog/proj['title_code','" + title.code + "']['process','" + proj_doers[r] + "'].twog/work_order['process','in','" + wo_doer_str + "'])");
                                                  for(var d = 0; d < wos.length; d++){
                                                      wos_to_do.push(wos[d].code);
                                                  }
                                                  for(var d = 0; d < wo_disconnected.length; d++){
                                                      wos_to_do.push(wo_disconnected[d]);
                                                  }
                                                  
                                              }
                                          }
                                      }
                                  
                         
                              }
                          } 
                          //PUT RESET BUTTON ON THE TITLE. ONLY LOOK AT ELEMENTS BELONGING TO THE TITLE. SO...YOULL HAVE TO FIX THIS:
                          title_el = document.getElementsByClassName('resetter_' + title.code)[0];
                          checkboxes = title_el.getElementsByTagName('input');
                           
                          for(var r = 0; r < checkboxes.length; r++){
                              if(checkboxes[r].type == 'checkbox'){
                                  if(checkboxes[r].name.indexOf('selector_') != -1){
                                      code_s = checkboxes[r].name.split('_');
                                      that_code = code_s[1] + '_' + code_s[2];
                                      if(that_code == code){
                                          checkboxes[r].setAttribute('clicked_last','true');
                                      }else{
                                          checkboxes[r].setAttribute('clicked_last','false');
                                      }
                                      if(that_code in oc(wos_to_do)){
                                          checkboxes[r].checked = true;
                                      }
                                  }
                              }
                          }

                          spt.app_busy.hide();
                    }
                            
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % title_code}
        return behavior

    def get_reset_behavior(my, user, fix_wo_code, fix_wo_name, title_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        function oc(a){
                            var o = {};
                            for(var i=0;i<a.length;i++){
                                o[a[i]]='';
                            }
                            return o;
                        }
                        try{
                           var user = '%s';
                           var fix_wo_code = '%s';
                           var fix_wo_name = '%s';
                           var title_code = '%s';
                           group_email_lookup = {'admin': 'administrator@2gdigital.com', 'it': 'IT@2gdigital.com', 'qc': 'QC@2gdigital.com', 'qc_supervisor': 'QC@2gdigital.com', 'compression': 'Compression@2gdigital.com', 'billing_and_accounts_receivable': '2GSales@2gdigital.com', 'audio': 'Audio@2gdigital.com', 'compression_supervisor': 'Compression@2gdigital.com', 'edeliveries': 'Edeliveries@2gdigital.com', 'machine_room': 'MR@2gdigital.com', 'media_vault': 'Mediavault@2gdigital.com', 'media_vault_supervisor': 'Mediavault@2gdigital.com', 'edit_supervisor': 'Editors@2gdigital.com', 'machine_room_supervisor': 'MR@2gdigital.com', 'office_employees': 'jaime.torres@2gdigital.com;adriana.amador@2gdigital.com', 'edit': 'Editors@2gdigital.com', 'sales': '2GSales@2gdigital.com', 'senior_staff': 'fernando.vasquez@2gdigital.com;jaime.torres@2gdigital.com;adriana.amador@2gdigital.com;stephen.buchsbaum@2gdigital.com', 'executives': 'stephen.buchsbaum@2gdigital.com', 'management': 'jaime.torres@2gdigital.com;adriana.amador@2gdigital.com', 'scheduling': 'scheduling@2gdigital.com', 'streamz': 'MR@2gdigital.com;QC@2gdigital.com;Editors@2gdigital.com', 'technical_services': 'IT@2gdigital.com', 'sales_supervisor': '2GSales@2gdigital.com', 'scheduling_supervisor': 'scheduling@2gdigital.com', 'vault': 'Mediavault@2gdigital.com'}
                           rnow = new Date();
                           valof = ( new Date() ).valueOf();
                           timestamp = rnow.getFullYear() + '-' + (rnow.getMonth() + 1) + '-' + rnow.getDate() + ' ' + valof;
                           hour = Number(rnow.getHours());
                           var server = TacticServerStub.get();
                           var title_sk = server.build_search_key('twog/title', title_code);
                           entered = false;
                           info = '';
                           while(!entered){
                               info = prompt("What needs to be fixed?");
                               if(info != '' && info != null){
                                   entered = true;
                                   note = 'A Fix Needed was issued for ' + fix_wo_name + ' (' + fix_wo_code + '). Explanation is: ' + info;
                                   error_entries = server.eval("@SOBJECT(twog/production_error['work_order_code','" + fix_wo_code + "'])")
                                   error_entry = error_entries[error_entries.length - 1];
                                   server.update(error_entry.__search_key__, {'operator_description': note});
                                   thing = server.execute_cmd('operator_view.MakeNoteWdg', {'obj_sk': title_sk, 'header': fix_wo_name + " - Fix Needed", 'note': note});
                               }
                           }
                           if(info != '' && info != null && confirm('Are you sure you want to reset the statuses of selected work orders?')){
                               if(confirm("You really want to do this?")){
                                   spt.app_busy.show("Resetting selected work orders...");
                                   var tcode = bvr.src_el.getAttribute('tcode');
                                   var title = server.eval("@SOBJECT(twog/title['code','" + tcode + "'])")[0];
                                   if(title.resets in oc(['',null]) || user == 'admin' || user == 'chantal.beukman' || user == 'adriana.amador' || hour > 17){
                                       var sk = title.__search_key__; 
                                       var title_el = document.getElementsByClassName('resetter_' + title.code)[0];
                                       var checkboxes = title_el.getElementsByTagName('input');
                                       var ready_sk = '';
                                       var ready_name = '';
                                       var ready_group = '';
                                       var pending_sks = []; 
                                       var reload_sks = [];
                                       var ready_proj_task_sk = '';
                                       var pending_proj_task_sks = []; 
                                       for(var r = 0; r < checkboxes.length; r++){
                                           if(checkboxes[r].type == 'checkbox'){
                                               if(checkboxes[r].name.indexOf('selector_') != -1 && checkboxes[r].checked){
                                                   if(checkboxes[r].getAttribute('clicked_last') == 'true'){
                                                      ready_sk = checkboxes[r].getAttribute('task_sk');
                                                      ready_name = checkboxes[r].getAttribute('task_process');
                                                      ready_group = checkboxes[r].getAttribute('task_group');
                                                   }else{
                                                      pending_sks.push(checkboxes[r].getAttribute('task_sk'));
                                                   }
                                                   reload_sks.push(checkboxes[r].getAttribute('wo_sk'));
                                                   checkboxes[r].checked = false;
                                                   checkboxes[r].setAttribute('clicked_last','false');
                                               }
                                           }
                                       }
                                       server.update(ready_sk, {'status': 'Ready', 'assigned': ''});
                                       note = 'A Fix Needed was issued for ' + fix_wo_name + ' (' + fix_wo_code + '). This work order (' + ready_name + ')  will need to be redone as a result. Explanation is: ' + info;
                                       thing = server.execute_cmd('operator_view.MakeNoteWdg', {'obj_sk': title_sk, 'header': ready_name + " - Reset for Fix", 'note': note, 'note_ccs': group_email_lookup[ready_group]});
                                       var task_code = ready_sk.split('code=')[1];
                                       p = server.eval("@SOBJECT(twog/work_order['task_code','" + task_code + "'].twog/proj)");
                                       p = p[0];
                                       pt = server.eval("@SOBJECT(sthpw/task['lookup_code','" + p.code + "'])");
                                       pt = pt[0];
                                       ready_proj_task_sk = pt.__search_key__;
                                       server.update(ready_proj_task_sk, {'status': 'Ready'});
                                       p_code = p.code;
                                       for(var r = 0; r < pending_sks.length; r++){
                                           server.update(pending_sks[r], {'status': 'Pending', 'assigned': ''});
                                       }
                                       for(var r = 0; r < reload_sks.length; r++){
                                           wo_sk = reload_sks[r];
                                           wo_code = wo_sk.split('code=')[1];
                                           pj = server.eval("@SOBJECT(twog/work_order['code','" + wo_code + "'].twog/proj)")[0];
                                           proj_task = server.eval("@SOBJECT(sthpw/task['lookup_code','" + pj.code + "'])")[0];
                                           proj_task_sk = proj_task.__search_key__;
                                           if(!(proj_task_sk in oc(pending_proj_task_sks)) && proj_task_sk != ready_proj_task_sk){
                                               pending_proj_task_sks.push(proj_task_sk);
                                               server.update(proj_task_sk, {'status': 'Pending'});
                                           } 
                                       }
                                       resets = title.resets;
                                       resets = resets + '[X[' + timestamp + '[USER:' + user + '[READY:' + ready_sk + '][PENDING:' + pending_sks.join() + ']]X]';
                                       server.update(sk, {'resets': resets});
                                       spt.app_busy.hide();
                                       spt.popup.close(spt.popup.get_popup(bvr.src_el));
                                       data1 = {'wo_code': fix_wo_code};
                                       spt.panel.load_popup('Select Work Order To Go Back To', 'operator_view.resetter.WOResetWdg', data1);
                                   }else{
                                       alert('This title has already been reset at least once. Please contact the admin for assistance.');
                                   }
                               }
                           }
                           
                           
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (user, fix_wo_code, fix_wo_name, title_code)}
        return behavior

    def fix_date(my, date):
        #This is needed due to the way Tactic deals with dates (using timezone info), post v4.0
        from pyasm.common import SPTDate
        return_date = ''
        date_obj = SPTDate.convert_to_local(date)
        if date_obj not in [None,'']:
            return_date = date_obj.strftime("%Y-%m-%d  %H:%M")
        return return_date

    def title_row(my, title, wo_code, wo_name):
        table = Table()
        table.add_attr('cellpadding','0')
        table.add_attr('cellspacing','0')
        table.add_style('border-collapse', 'separate')
        table.add_style('border-spacing', '25px 0px')
        table.add_style('border-bottom-right-radius', '10px')
        table.add_style('border-bottom-left-radius', '10px')
        table.add_style('border-top-right-radius', '10px')
        table.add_style('border-top-left-radius', '10px')
        table.add_style('color: #00056a;')
        table.add_style('background-color: #d9edcf;')
        table.add_style('width: 100%s;' % '%')
        table.add_row()
        title_name = title.get('title')
        if title.get('episode') not in [None,'']:
            title_name = '%s: %s' % (title_name, title.get('episode'))
        tcell = table.add_cell('<b><u>Title: %s</u></b>' % title_name)
        tcell.add_attr('nowrap','nowrap')
        dcell = table.add_cell('Due: %s' % my.fix_date(title.get('due_date')))
        dcell.add_attr('nowrap','nowrap')
        table.add_cell('Pipeline: %s' % title.get('pipeline_code'))
        table.add_row()
        table.add_cell('Code: %s' % title.get('code'))
        table.add_cell(' ')
        atbl = Table()
        atbl.add_row()
        a1 = atbl.add_cell('<input type="button" value="Change Statuses" style="background-color: #d7d7d7;"/>')
        a1.add_style('cursor: pointer;')
        a1.add_behavior(my.get_change_statuses(title.get('code'), wo_code, wo_name))
        a11 = atbl.add_cell(' ')
        a11.add_style('width: 10px;')
        a2 = atbl.add_cell('<input type="button" value="Pending" style="background-color: #d7d7d7;"/>')
        a2.add_style('cursor: pointer;')
        a2.add_behavior(my.get_set_notify('Please Select Work Orders that should be Pending', title.get('code')))
        a21 = atbl.add_cell(' ')
        a21.add_style('width: 10px;')
        a3 = atbl.add_cell('<input type="button" value="Ready" style="background-color: #b2cee8;"/>')
        a3.add_behavior(my.get_set_notify('Please Select Work Orders that should be Ready', title.get('code')))
        a3.add_style('cursor: pointer;')
        a31 = atbl.add_cell(' ')
        a31.add_style('width: 10px;')
        reset = atbl.add_cell('<input type="button" value="Reset Selected" style="background-color: #e59400;"/>')
        reset.add_attr('tcode',title.get('code'))
        reset.add_style('cursor: pointer;')
        reset.add_behavior(my.get_reset_behavior(my.user, wo_code, wo_name, title.get('code')))
        atbl.add_row()
        notify = atbl.add_cell('Please select the work order that needs to be set to "ready". The following work orders that need to be "pending" in the work flow will be selected as well')
        notify.add_attr('colspan','7')
        notify.add_attr('class','notify_%s' % title.get('code'))
        table.add_cell(atbl)
        return table

    def proj_row(my, proj, work_group):
        task = my.server.eval("@SOBJECT(sthpw/task['lookup_code','%s'])" % proj.get('code'))[0]
        table = Table()
        table.add_attr('cellpadding','0')
        table.add_attr('cellspacing','0')
        table.add_style('border-collapse', 'separate')
        table.add_style('border-spacing', '25px 0px')
        table.add_style('border-bottom-right-radius', '10px')
        table.add_style('border-bottom-left-radius', '10px')
        table.add_style('border-top-right-radius', '10px')
        table.add_style('border-top-left-radius', '10px')
        table.add_style('color: #00056a;')
        table.add_style('background-color: #d9ed8b;')
        table.add_style('width: 100%s;' % '%')
        table.add_row()
        t1 = table.add_cell('<b><u>Project: %s</u></b>' % proj.get('process'))
        t1.add_attr('nowrap','nowrap')
        table.add_cell('Due: %s' % my.fix_date(proj.get('due_date')))
        table.add_cell('Pipeline: %s' % proj.get('pipeline_code'))
        table.add_row()
        table.add_cell('Code: %s' % proj.get('code'))
        table.add_cell('Dept: %s' % work_group)
        status = task.get('status')
        stat_cell = table.add_cell('Status: %s' % status)
        stat_cell.add_attr('nowrap','nowrap')
        if status not in [None,'']:
            stat_cell.add_style('background-color: %s;' % my.stat_colors[status])
        return table

    def wo_row(my, wo, fix_wo_code):
        bcol = '#c6eda0'
        if wo.get('code') == fix_wo_code:
            bcol = '#009acd'
        task = my.server.eval("@SOBJECT(sthpw/task['lookup_code','%s'])" % wo.get('code'))[0]
        table = Table()
        table.add_attr('cellpadding','0')
        table.add_attr('cellspacing','0')
        table.add_style('border-collapse', 'separate')
        table.add_style('border-spacing', '25px 0px')
        table.add_style('border-bottom-right-radius', '10px')
        table.add_style('border-bottom-left-radius', '10px')
        table.add_style('border-top-right-radius', '10px')
        table.add_style('border-top-left-radius', '10px')
        table.add_style('color: #00056a;')
        table.add_style('background-color: %s;' % bcol)
        table.add_style('width: 100%s;' % '%')
        table.add_row()
        reset_checkbox = CheckboxWdg('selector_%s' % wo.get('code'))
        reset_checkbox.add_attr('clicked_last','false')
        reset_checkbox.add_attr('task_sk',task.get('__search_key__'))
        reset_checkbox.add_attr('task_process',task.get('process'))
        reset_checkbox.add_attr('task_group',task.get('assigned_login_group'))
        reset_checkbox.add_attr('wo_sk',wo.get('__search_key__'))
        #reset_checkbox.set_persistence()
        reset_checkbox.set_value(False)
        reset_checkbox.add_behavior(my.get_reset_auto_select_behavior(wo.get('title_code')))
        reset_cell = table.add_cell(reset_checkbox)
        table.add_row()
        t1 = table.add_cell('<b><u>Work Order: %s</u><b>' % wo.get('process'))
        t1.add_attr('nowrap','nowrap')
        t1.add_attr('align','left')
        d1 = table.add_cell('Due: %s' % my.fix_date(wo.get('due_date')))
        d1.add_attr('nowrap','nowrap')
        status = task.get('status')
        stat_cell = table.add_cell('Status: %s' % status)
        stat_cell.add_attr('nowrap','nowrap')
        if status not in [None,'']:
            stat_cell.add_style('background-color: %s;' % my.stat_colors[status])
        table.add_row()
        c1 = table.add_cell('Code: %s' % wo.get('code'))
        c1.add_attr('nowrap','nowrap')
        dd1 = table.add_cell('Dept: %s' % wo.get('work_group'))
        dd1.add_attr('nowrap','nowrap')
        assigned = task.get('assigned')
        if assigned in [None,'']:
            assigned = ''
        a1 = table.add_cell('Assigned: %s' % assigned)
        a1.add_attr('nowrap','nowrap')
        table.add_row()
        ins = table.add_cell('<i>%s</i>' % wo.get('instructions'))
        ins.add_attr('align','left')
        ins.add_attr('colspan','3')
        ins.add_attr('width','100%s' % '%')
        return table
         
    def get_display(my):
        wo_code = str(my.kwargs.get('wo_code'))
        work_order = my.server.eval("@SOBJECT(twog/work_order['code','%s'])" % wo_code)[0]
        title = my.server.eval("@SOBJECT(twog/title['code','%s'])" % work_order.get('title_code'))[0]
        projs = my.server.eval("@SOBJECT(twog/proj['title_code','%s'])" % work_order.get('title_code'))
        widget = DivWdg()
        table = Table()
        table.add_attr('class','resetter_%s' % title.get('code'))
        table.add_row()
        table.add_cell(my.title_row(title, wo_code, work_order.get('process')))
        for proj in projs:
            alg_ct = {}
            work_orders = my.server.eval("@SOBJECT(twog/work_order['proj_code','%s'])" % proj.get('code'))
            for wo in work_orders:
                work_group = wo.get('work_group')
                if work_group not in alg_ct.keys():
                    alg_ct[work_group] = 1
                else:
                    alg_ct[work_group] = alg_ct[work_group] + 1
            work_group = ''
            high = 0
            for k in alg_ct.keys():
                num = alg_ct[k]
                if num > high:
                    work_group = k
                    high = num
            table.add_row()
            p1 = table.add_cell(my.proj_row(proj, work_group))
            p1.add_style('padding-left: 40px;')
            for wo in work_orders:
                table.add_row()
                w1 = table.add_cell(my.wo_row(wo, wo_code))
                w1.add_style('padding-left: 80px;')
        widget.add(table)
        return widget
        
        
        
class WOResetWdg2(BaseRefreshWdg):

    def init(my):
        from client.tactic_client_lib import TacticServerStub
        my.server = TacticServerStub.get()

    def get_on_load(my):
        behavior = {
                'type': 'load',
                'cbjs_action': '''
                top_kill_timer = function(timelen){
                    setTimeout('top_killer()', timelen);
                }
                top_killer = function(){
                    var top_el = spt.api.get_parent(bvr.src_el, '.spt_popup');
                    close_n_min = top_el.getElementsByClassName('hand');
                    for(var r = 0; r < close_n_min.length; r++){
                        close_n_min[r].style.display = 'none';
                    }
                    close_n_min = top_el.getElementsByClassName('glyphicon'); //this is the 4.3 way of removing the x and - buttons
                    for(var r = 0; r < close_n_min.length; r++){
                        close_n_min[r].style.display = 'none';
                    }
                }
                top_killer();
                top_kill_timer(1000);

                '''
        }
        return behavior

    def get_send_info_behavior(my, fix_wo_code, fix_wo_name, title_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                           var fix_wo_code = '%s';
                           var fix_wo_name = '%s';
                           var title_code = '%s';
                           rnow = new Date();
                           valof = ( new Date() ).valueOf();
                           timestamp = rnow.getFullYear() + '-' + (rnow.getMonth() + 1) + '-' + rnow.getDate() + ' ' + valof;
                           hour = Number(rnow.getHours());
                           var server = TacticServerStub.get();
                           var title_sk = server.build_search_key('twog/title', title_code);
                           info = '';
                           top_el = document.getElementsByClassName('resetter2_' + title_code)[0];
                           inform = top_el.getElementById('fix_needed_explanation');
                           if(inform.value != '' && inform.value != null){
                               //THIS NEEDS TO ATTACH TO THE PRODUCTION ERROR AND BE SENT IN THE NOTE EMAIL
                               info = inform.value;
                               the_wo = server.eval("@SOBJECT(twog/work_order['code','" + fix_wo_code + "'])")[0];
                               instructions = the_wo.instructions;
                               note = 'A Fix Needed was issued for ' + fix_wo_name + ' (' + fix_wo_code + '). Explanation is: ' + info + '\\nTitle: ' + title_code + '\\nWO: ' + fix_wo_code + '\\nWO Instructions: ' + instructions;
                               error_entries = server.eval("@SOBJECT(twog/production_error['work_order_code','" + fix_wo_code + "'])");
                               error_entry = error_entries[error_entries.length - 1];
                               //Had this on to kill some dupe emails, but some people were not getting emails they should get, so turning triggers back on, below -- server.update(error_entry.__search_key__, {'operator_description': note}, {'triggers': false});
                               server.update(error_entry.__search_key__, {'operator_description': note});
                               title = server.eval("@SOBJECT(twog/title['code','" + title_code + "'])")[0];
                               tname = title.title
                               if(title.episode != '' && title.episode != null){
                                   tname = tname + ": " + title.episode;
                               }
                               subject =  'Fix Needed Issued for ' + tname + '( ' + title.code + '), ' + fix_wo_name + ' (' + fix_wo_code + ')MTMSUBJECT';
                               note_ccs = 'scheduling@2gdigital.com';
                               email_list = top_el.getElementById('email_list');
                               emails = email_list.value;
                               if(emails != '' && emails != null){
                                   note_ccs = note_ccs + ';' + emails;
                               }
                               note_ccs = note_ccs.replace(',',';');
                               thing = server.execute_cmd('operator_view.MakeNoteWdg', {'obj_sk': title_sk, 'header': fix_wo_name + " - Fix Needed", 'note': subject + note, 'note_ccs': note_ccs});
                               spt.popup.close(spt.popup.get_popup(bvr.src_el));
                           }else{
                               alert("Please tell us what needs to be fixed");    
                           }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (fix_wo_code, fix_wo_name, title_code)}
        return behavior


    def get_email_select(my, title_code):
        sel_behavior = {'css_class': 'sel_change', 'type': 'change', 'cbjs_action': '''        
             try{
                   var top_el = spt.api.get_parent(bvr.src_el, '.resetter2_%s');
                   cc = top_el.getElementById('email_list');
                   selval = bvr.src_el.value;
                   if(selval != '' && selval != null){
                           cc_val = cc.value;
                           if(cc_val == '' || cc_val == null){
                               cc.value = selval;
                           }else{
                               cc.value = cc_val + ';' + selval;
                           }
                   }
                    
                }
                catch(err){
                          spt.app_busy.hide();
                          alert(err);
                }
        ''' % title_code}
        return sel_behavior 

    def get_display(my):
        wo_code = str(my.kwargs.get('wo_code'))
        work_order = my.server.eval("@SOBJECT(twog/work_order['code','%s'])" % wo_code)[0]
        widget = DivWdg()
        table = Table()
        table.add_attr('class','resetter2_%s' % work_order.get('title_code'))
        table.add_row()
        table.add_cell('<b>Please tell us what needs to be fixed</b>')
        table.add_row()
        table.add_cell('<textarea cols="50" rows="10" id="fix_needed_explanation"></textarea>')
        table.add_row()
        int_logins = my.server.eval("@SOBJECT(sthpw/login['location','internal']['license_type','user'])")
        inhousers = SelectWdg('inhousers')
        inhousers.append_option('--Select--','')

        
        group_internals = ProdSetting.get_value_by_key('internal_group_emails') # MTM
        if group_internals not in [None,'']:
            gis = group_internals.split('|')
            for gi in gis:
                gie = gi.split('->')
                slbl = gie[0]
                semail = gie[1]
                inhousers.append_option(slbl, semail)

        for logger in int_logins:
            inhousers.append_option('%s %s' % (logger.get('first_name'), logger.get('last_name')), logger.get('email'))
        inhousers.set_behavior(my.get_email_select(work_order.get('title_code')))
        t2 = Table()
        t2.add_row()
        t2.add_cell('Emails: ')
        t2.add_cell(inhousers)
        t2.add_row()
        longer = t2.add_cell('<input type="text" value="compression@2gdigital.com" id="email_list" size="70" style="font-size: 10px;"/>')
        longer.add_attr('colspan','2')
        table.add_cell(t2)
        table.add_row()
        butt = table.add_cell('<input type="button" value="Send"/>')
        butt.add_behavior(my.get_send_info_behavior(wo_code, work_order.get('process'), work_order.get('title_code')))
        widget.add(table)
        widget.add_behavior(my.get_on_load())
        return widget
        
        
class ForceResponseWdg(BaseRefreshWdg):

    def init(my):
        from client.tactic_client_lib import TacticServerStub
        my.server = TacticServerStub.get()
        my.string_to_parse = str(my.kwargs.get('string_to_parse'))
        login_obj = Environment.get_login()
        my.login = login_obj.get_login()
        my.x_butt = "<img src='/context/icons/common/BtnKill.gif' title='Clear Emails' name='Clear Emails'/>" 

    def get_on_load(my):
        behavior = {
                'type': 'load',
                'cbjs_action': '''
                top_kill_timer = function(timelen){
                    setTimeout('top_killer()', timelen);
                }
                top_killer = function(){
                    var top_el = spt.api.get_parent(bvr.src_el, '.spt_popup');
                    close_n_min = top_el.getElementsByClassName('hand');
                    for(var r = 0; r < close_n_min.length; r++){
                        close_n_min[r].style.display = 'none';
                    }
                    close_n_min = top_el.getElementsByClassName('glyphicon'); //this is the 4.3 way of removing the x and - buttons
                    for(var r = 0; r < close_n_min.length; r++){
                        close_n_min[r].style.display = 'none';
                    }
                }
                top_killer();
                top_kill_timer(1000);

                '''
        }
        return behavior

    def get_clear_behavior(my, wo_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                           var wo_code = '%s';
                           var top_el = spt.api.get_parent(bvr.src_el, '.forceresponse_wdg');
                           email_list = top_el.getElementById('email_list_' + wo_code);
                           email_list.innerHTML = '';
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % wo_code}
        return behavior

    def get_remove_path(my, wo_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                           var wo_code = '%s';
                           textarea = document.getElementById('forced_response_' + wo_code);
                           textarea_val = textarea.value;
                           remaining = '';
                           textarea_s = textarea_val.split('\\n')
                           gone = textarea_s.pop();
                           for(var r = 0; r < textarea_s.length; r++){
                               if(remaining == ''){
                                   remaining = textarea_s[r]; 
                               }else{
                                   remaining = remaining + '\\n' + textarea_s[r];
                               }
                           }
                           textarea.value = remaining;
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % wo_code}
        return behavior

    def get_reverse_status_change(my, code, old_status, new_status):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                           code= '%s';
                           old_status = '%s';
                           new_status = '%s';
                           stat_colors = {'Assignment': '#fcaf88', 'Pending': '#d7d7d7', 'In Progress': '#f5f3a4', 'In_Progress': '#f5f3a4', 'In Production': '#f5f3a4', 'In_Production': '#f5f3a4', 'In production': '#f5f3a4', 'In_production': '#f5f3a4', 'Waiting': '#ffd97f', 'Need Assistance': '#fc88fb', 'Need_Assistance': '#fc88fb', 'Review': '#888bfc', 'Approved': '#d4b5e7', 'On Hold': '#e8b2b8', 'On_Hold': '#e8b2b8', 'Client Response': '#ddd5b8', 'Completed': '#b7e0a5', 'Ready': '#b2cee8', 'Internal Rejection': '#ff0000', 'External Rejection': '#ff0000', 'Rejected': '#ff0000', 'Failed QC': '#ff0000', 'Fix Needed': '#c466a1', 'Need Buddy Check': '#e3701a', 'DR In_Progress': '#d6e0a4', 'DR In Progress': '#d6e0a4','Amberfin01_In_Progress':'#D8F1A8', 'Amberfin01 In Progress':'#D8F1A8', 'Amberfin02_In_Progress':'#F3D291',  'Amberfin02 In Progress':'#F3D291','BATON In_Progress': '#c6e0a4', 'BATON In Progress': '#c6e0a4','Export In_Progress': '#796999', 'Export In Progress': '#796999','Buddy Check In_Progress': '#1aade3','Buddy Check In Progress': '#1aade3'};
                           if(confirm("Do you really want to reverse the status of " + code + " to " + old_status + "?")){
                               server = TacticServerStub.get();
                               task = server.eval("@SOBJECT(sthpw/task['lookup_code','" + code + "'])")[0];
                               task_sk = task.__search_key__;
                               server.update(task_sk, {'status': old_status}, {'triggers': false});
                               sels = document.getElementsByTagName('select');
                               for(var r = 0; r < sels.length; r++){
                                   if(sels[r].id.indexOf("status_") != -1){
                                       sk = sels[r].id.split('tatus_')[1];
                                       disp_status = sels[r].value;
                                       if(sk == task_sk){
                                           if(disp_status != old_status){
                                               sels[r].value = old_status; 
                                               sels[r].style.backgroundColor = stat_colors[old_status];
                                               sels[r].setAttribute('old',old_status);
                                               sels[r].setAttribute('old_status',old_status);
                                           }    
                                       }
                                   }
                               }
                               wo = server.eval("@SOBJECT(twog/work_order['code','" + code + "'])")[0];
                               stats = server.eval("@SOBJECT(twog/status_log['title_code','" + wo.title_code + "']['@ORDER_BY','timestamp desc'])");
                               stop_it = false;
                               for(var r = 0; r < stats.length; r++){
                                   if(stats[r].lookup_code == code){
                                       stop_it = true;
                                   }
                                   if(!stop_it){
                                       server.update(server.build_search_key('sthpw/task', stats[r].task_code), {'status': stats[r].from_status}, {'triggers': false}); 
                                   }
                               }
                               
                               var top_el = spt.api.get_parent(bvr.src_el, '.forceresponse_wdg');
                               hide_el = top_el.getElementById(code);
                               hide_el.style.display = 'none';
                               hiders = top_el.getElementsByClassName('hid_or_showing');
                               there_count = 0;
                               for(var r = 0; r < hiders.length; r++){
                                   if(hiders[r].style.display != 'none'){
                                       there_count = there_count + 1;
                                   }
                               }
                               if(there_count == 0){
                                   spt.popup.close(spt.popup.get_popup(bvr.src_el));
                               }
                           }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (code, old_status, new_status)}
        return behavior

    def get_send_info_behavior(my):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        function encode_utf8( s )
                        {
                            return unescape( encodeURIComponent( s ) );
                        }
                        function do_bad_chars_exist(str_in){
                            ret_bool = false;
                            if(/^([a-zA-Z0-9,.'";:><\/\\\?\][}{|+=\-_)(*&^!%s\$@#`~ \\n\\t]{1,})$/.test(str_in)){
                                ret_bool = false;
                            }else{
                                ret_bool = true;
                            }
                            return ret_bool;
                        }
                        try{
                           login = '%s';
                           rnow = new Date();
                           valof = ( new Date() ).valueOf();
                           timestamp = rnow.getFullYear() + '-' + (rnow.getMonth() + 1) + '-' + rnow.getDate() + ' ' + valof;
                           hour = Number(rnow.getHours());
                           var server = TacticServerStub.get();
                           info = '';
                           var top_el = spt.api.get_parent(bvr.src_el, '.forceresponse_wdg');
                           informs = top_el.getElementsByClassName('forced_response');
                           ones_that_need_fillin = [];
                           ones_that_need_hidin = [];
                           ones_that_need_fixin = [];
                           for(var r = 0; r < informs.length; r++){
                               inform = informs[r];
                               work_order_code = inform.getAttribute('work_order_code');
                               wo_el = top_el.getElementById(work_order_code);
                               if(wo_el.style.display != 'none'){
                                   spt.app_busy.show("Sending your response(s)...");
                                   process = inform.getAttribute('process');
                                   //MTM stopped here
                                   mode = inform.getAttribute('mode');
                                   production_error_code = '';
                                   if(mode == 'special_status'){
                                       production_error_code = inform.getAttribute('production_error_code');
                                   }
                                   new_status = inform.getAttribute('new_status');
                                   old_status = inform.getAttribute('old_status');
                                   assigned_login_group = inform.getAttribute('assigned_login_group');
                                   info = inform.value;
                                   if(info != '' && info != null){
                                       entered = true;
                                       info = encode_utf8(info);
                                       contains_bad_chars = do_bad_chars_exist(info);
                                       if(!contains_bad_chars){
                                           note_ccs = 'scheduling@2gdigital.com';
                                           email_list = top_el.getElementById('email_list_' + work_order_code);
                                           //emails = email_list.value;
                                           emails = email_list.innerHTML;
                                           if(emails != '' && emails != null){
                                               note_ccs = note_ccs + ';' + emails;
                                           }
                                           if(production_error_code != '' && production_error_code != null){
                                               //Update the production_error's operator_description
                                               prod_sk = server.build_search_key('twog/production_error', production_error_code);
                                               server.update(prod_sk, {'operator_description': info}, {'triggers': false}); 
                                           }
                                           note_ccs = note_ccs.replace(',',';');
                                           ones_that_need_hidin.push([process,work_order_code]);
                                           //Now send it to MakeNoteWdg, but logic isn't all the way there yet
                                           wo = server.eval("@SOBJECT(twog/work_order['code','" + work_order_code + "'])")[0];
                                           wo_nums = work_order_code.replace('WORK_ORDER','');
                                           the_order = server.eval("@SOBJECT(twog/order['code','" + wo.order_code + "'])")[0];
                                           title = server.eval("@SOBJECT(twog/title['code','" + wo.title_code + "'])")[0];
                                           title_full_name = title.title;
                                           if(title.episode != null && title.episode != ''){
                                               title_full_name = title_full_name + ' Episode: ' + title.episode;
                                           }
                                           scheduler = the_order.login;
                                           sources = server.eval("@SOBJECT(twog/work_order_sources['work_order_code','" + work_order_code + "'])");
                                           if(sources.length == 0){
                                               sources = server.eval("@SOBJECT(twog/title_origin['title_code','" + wo.title_code + "'])");
                                           }
                                           sources_str = '';
                                           if(sources.length > 0){
                                               for(var q = 0; q < sources.length; q++){
                                                   the_barcode = server.eval("@GET(twog/source['code','" + sources[q].source_code + "'].barcode)")[0];
                                                   if(sources_str == ''){
                                                       sources_str = the_barcode;
                                                   }else{
                                                       sources_str = sources_str + ', ' + the_barcode;
                                                   }
                                               }
                                           }
                                           if(mode == 'special_status'){
                                               note = work_order_code + ' went from ' + old_status + ' to ' + new_status + '. Status Change by: ' + login + '\\n\\nReason Provided:\\n' + info + '\\n\\nOrder Code: ' + wo.order_code + '\\nTitle Code: ' + wo.title_code + '\\nWork Order Code: ' + work_order_code + '\\nSource Barcode(s): ' + sources_str;
                                               thing = server.execute_cmd('operator_view.MakeNoteWdg', {'obj_sk': wo.__search_key__, 'header': title_full_name + ': ' + assigned_login_group + ' - ' + wo.process + ' (WO#' + wo_nums + ') Scheduler: ' + scheduler + ' To ' + new_status + ' from ' + old_status + ' PO#: ' + title.po_number, 'note': note, 'note_ccs': note_ccs, 'triggers': 'false', 'notification_email': 'true', 'email_info': {'old_status': old_status, 'new_status': new_status, 'work_order_code': work_order_code, 'sources_str': sources_str, 'production_error_code': production_error_code, 'process': process, 'operator_description': info, 'login': login}});
                                           }else if(mode == 'file_path'){
                                               note = work_order_code + ' went from ' + old_status + ' to ' + new_status + '. Status Change by: ' + login + '\\n\\nFile Path Provided:\\n' + info + '\\n\\nOrder Code: ' + wo.order_code + '\\nTitle Code: ' + wo.title_code + '\\nWork Order Code: ' + work_order_code + '\\nSource Barcode(s): ' + sources_str;
                                               thing = server.execute_cmd('operator_view.MakeNoteWdg', {'obj_sk': wo.__search_key__, 'header': 'File Path - ' + title_full_name + ' - ' + wo.process + ' (WO#' + wo_nums + ') Scheduler: ' + scheduler + ' PO#: ' + title.po_number , 'note': note, 'note_ccs': note_ccs, 'triggers': 'false', 'notification_email': 'true', 'email_info': {'old_status': old_status, 'new_status': new_status, 'work_order_code': work_order_code, 'sources_str': sources_str, 'process': process, 'file_path': info, 'login': login}});
                                           }
                                       }else{
                                           ones_that_need_fixin.push([process,work_order_code]);
                                       }
                                   }else{
                                       ones_that_need_fillin.push([process,work_order_code]);
                                   }
                               }
                           }
                           spt.app_busy.hide()
                           //Need to fill in ones_that_need_fixin logic and prompt user to fix their input in those fields.
                           if(ones_that_need_fillin.length == 0 && ones_that_need_fixin.length == 0){
                               spt.popup.close(spt.popup.get_popup(bvr.src_el));
                           }else{
                               if(ones_that_need_fillin.length > 0){
                                   fix_em = '';
                                   for(var r = 0; r < ones_that_need_fillin.length; r++){
                                       entry = ones_that_need_fillin[r];
                                       if(fix_em == ''){
                                           fix_em = 'Please enter a response for:\\n' + entry[0] + ' (' + entry[1] + ')';
                                       }else{
                                           fix_em = fix_em + '\\n' + entry[0] + ' (' + entry[1] + ')';
                                       }
                                   }
                                   alert(fix_em);
                               }
                               if(ones_that_need_fixin.length > 0){
                                   fix_em = '';
                                   illegal_char_tries = Number(top_el.getAttribute('illegal_char_tries'));
                                   illegal_char_tries = illegal_char_tries + 1;
                                   top_el.setAttribute('illegal_char_tries', illegal_char_tries);
                                   if(illegal_char_tries >= 3){
                                       // Give them the close and minimize buttons 
                                       var pop_el = spt.api.get_parent(bvr.src_el, '.spt_popup');
                                       close_n_min = pop_el.getElementsByClassName('hand');
                                       for(var r = 0; r < close_n_min.length; r++){
                                           close_n_min[r].style.display = 'block';
                                       }
                                       close_n_min = pop_el.getElementsByClassName('glyphicon'); //this is the 4.3 way of removing the x and - buttons
                                       for(var r = 0; r < close_n_min.length; r++){
                                           close_n_min[r].style.display = 'block';
                                       }
                                       //prefill the alert string to let them know they can close the window.
                                       fix_em = 'You have tried to enter an illegal character 3 times so far.\\nPlease send out your message as an email if you cannot get Tactic to accept your input.\\nAlso, note that the close popup button has reappeared, so you can close this if needed.';
                                   }
                                   for(var r = 0; r < ones_that_need_fixin.length; r++){
                                       entry = ones_that_need_fixin[r];
                                       if(fix_em == ''){
                                           fix_em = 'An illegal character exists in the response you entered for the following work order(s):\\n' + entry[0] + ' (' + entry[1] + ").";
                                       }else{
                                           fix_em = fix_em + '\\n' + entry[0] + ' (' + entry[1] + ')';
                                       }
                                   }
                                   fix_em = fix_em + "\\nPlease contact IT or admin if you can't find the illegal character(s).\\n(It may be a dash or a quotation mark, or any odd-looking character. Try replacing them with something else.)";
                                   alert(fix_em);
                               }
                               for(var r = 0; r < ones_that_need_hidin.length; r++){
                                   entry = ones_that_need_hidin[r];
                                   wo_code = entry[1];
                                   hide_el = top_el.getElementById(wo_code);
                                   hide_el.style.display = 'none';
                               }
                           }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % ('%', my.login)}
        return behavior


    def get_email_select(my, wo_code):
        sel_behavior = {'css_class': 'sel_change', 'type': 'change', 'cbjs_action': '''        
             try{
                   var wo_code = '%s';
                   var top_el = spt.api.get_parent(bvr.src_el, '.forceresponse_wdg');
                   cc = top_el.getElementById('email_list_' + wo_code);
                   selval = bvr.src_el.value;
                   if(selval != '' && selval != null){
                           //cc_val = cc.value;
                           cc_val = cc.innerHTML;
                           if(cc_val == '' || cc_val == null){
                               //cc.value = selval;
                               cc.innerHTML = selval;
                           }else{
                               //cc.value = cc_val + ';' + selval;
                               cc.innerHTML = cc_val + ';' + selval;
                           }
                   }
                    
                }
                catch(err){
                          spt.app_busy.hide();
                          alert(err);
                }
        ''' % wo_code}
        return sel_behavior 

    def parse_crap(my, string):
        rows = string.split('MTM_NEXT_MTM')
        in_order = []
        dict_out = {}
        for row in rows:
            chunks = row.split('MTMX-')
            wo_code = ''
            row_dict = {}
            prompt = ''
            dict_key = ''
            for chunk in chunks:
                kv = chunk.split(':')
                k = kv[0]
                v = kv[1:]
                if k == 'work_order_code':
                    wo_code = v[0]
                if k == 'Prompt':
                    prompt = v[0]
                if wo_code != '' and prompt != '':
                    dict_key = '%s%s' % (wo_code,prompt)
                    if dict_key not in in_order:
                        in_order.append(dict_key)
                    
                row_dict[k] = v
            dict_out[dict_key] = row_dict
        dict_out['codes_in_order'] = in_order
        return dict_out

    def get_display(my):
        parsed_dict = my.parse_crap(my.string_to_parse)
        group_internals = ProdSetting.get_value_by_key('internal_group_emails')
        int_logins = my.server.eval("@SOBJECT(sthpw/login['location','internal']['license_type','user'])")
        widget = DivWdg()
        table = Table()
        table.add_attr('class','forceresponse_wdg')
        table.add_attr('illegal_char_tries','0')
        table0 = Table()
        table0.add_style('border-spacing','10em')
        table0.add_style('background-color: #FFFFFF;')
        table0.add_row()
        table0.add_cell('<font color="#000000"><b>&#8226All Large Text Boxes Are Required Fields</b>')
        table0.add_row()
        table0.add_cell('<font color="#000000"><b>&#8226Please be sure that you are writing in the correct work order box</b>')
        table0.add_row()
        table0.add_cell('<font color="#000000"><b>&#8226All Responses will be emailed to Client Services and Operations as a default.<br/>&#8226You may choose to add more email recipients for each Work Order by using the "Additional Email Addresses" pulldown.</b>')
        table.add_row()
        table.add_cell(table0)
        count = 0 
        for pair in parsed_dict['codes_in_order']:
            row_data = parsed_dict[pair]
            prompt = row_data['Prompt'][0]
            work_order_code = row_data['work_order_code'][0]
            process = row_data['process'][0]
            new_status = row_data['new_status'][0]
            old_status = row_data['old_status'][0]
            production_error_code = ''
            is_need_fp = False
            mode = ''
            if "Please Enter the Path to the File" in prompt:
                is_need_fp = True
                mode = 'file_path'
            else:
                production_error_code = row_data['production_error_code'][0]
                mode = 'special_status'
            assigned_login_group = my.server.eval("@GET(sthpw/task['lookup_code','%s'].assigned_login_group)" % work_order_code)[0]
            assigned_login_group = assigned_login_group.upper()
            table.add_row()
            table2 = Table()
            if count % 2 == 0:
                table2.add_style('background-color: #bbbbbb;')
            else:
                table2.add_style('background-color: #dddddd;')
            table3 = Table()
            table3.add_row()
            table3.add_cell('<b>For: <font color="#5C246E">%s (%s)</font></b>' % (process, work_order_code))
            table3.add_row()
            color_cell = table3.add_cell('<b>%s</b>' % prompt)
            if 'Please tell us' in prompt:
                color_cell.add_style('color: #8E0000;')
            elif 'Enter the Path' in prompt:
                color_cell.add_style('color: #0800ee;')
            table4 = Table()
            table4.add_row()
            table4.add_cell(table3)
#            if not is_need_fp:
#                revver = table4.add_cell('<input type="button" value="Reverse Status Change"/>')
#                revver.add_behavior(my.get_reverse_status_change(work_order_code, old_status, new_status))
            revver = table4.add_cell('<input type="button" value="Reverse Status Change"/>')
            revver.add_behavior(my.get_reverse_status_change(work_order_code, old_status, new_status))
            table2.add_attr('id',work_order_code)
            table2.add_attr('class','hid_or_showing')
            table2.add_row()
            table2.add_cell(table4)
            table2.add_row()
            extra_attrs = ''
            if production_error_code != '':
                extra_attrs = 'production_error_code="%s"' % production_error_code
            table2.add_cell('<textarea cols="90" rows="10" class="forced_response" id="forced_response_%s" work_order_code="%s" new_status="%s" old_status="%s" process="%s" assigned_login_group="%s" mode="%s" %s></textarea>' % (work_order_code, work_order_code, new_status, old_status, process, assigned_login_group, mode, extra_attrs))
                
            table2.add_row()
            inhousers = SelectWdg('inhousers_%s' % work_order_code)
            inhousers.append_option('--Select--','')
            
            preset_emails = ''
            if new_status in ['Rejected','Fix Needed']:
                preset_emails = 'Compression@2gdigital.com;QC@2gdigital.com;'
                if new_status == 'Rejected' and assigned_login_group == 'EDELIVERIES':
                    preset_emails = 'Compression@2gdigital.com;QC@2gdigital.com;'
                elif new_status == 'Rejected': 
                    preset_emails = 'QC@2gdigital.com;'
                    
            
            if group_internals not in [None,'']:
                gis = group_internals.split('|')
                for gi in gis:
                    gie = gi.split('->')
                    slbl = gie[0]
                    semail = gie[1]
                    inhousers.append_option(slbl, semail)
    
            for logger in int_logins:
                inhousers.append_option('%s %s' % (logger.get('first_name'), logger.get('last_name')), logger.get('email'))
            inhousers.set_behavior(my.get_email_select(work_order_code))
            t2 = Table()
            t2.add_row()
            aea = t2.add_cell('Additional Email Addresses: ')
            aea.add_attr('nowrap','nowrap')
            t2.add_cell(inhousers)
            t2.add_row()
            #longer = t2.add_cell('<input type="text" value="%s" id="email_list_%s" size="110" style="font-size: 10px;" readonly/>' % (preset_emails, work_order_code))
            longer = t2.add_cell(preset_emails)
            longer.add_attr('id','email_list_%s' % work_order_code)
            longer.add_attr('colspan','2')
            longer.add_style('font-size: 10px;')
            xb = t2.add_cell(my.x_butt)
            xb.add_attr('align','right')
            xb.add_style('cursor: pointer;')
            xb.add_behavior(my.get_clear_behavior(work_order_code))
            table2.add_cell(t2)
            table.add_cell(table2)
            count = count + 1
        table.add_row()
        butt = table.add_cell('<input type="button" value="Send"/>')
        butt.add_behavior(my.get_send_info_behavior())
        widget.add(table)
        widget.add_behavior(my.get_on_load())
        return widget

class MakeNoteWdg(Command):

    def __init__(my, **kwargs):
        from client.tactic_client_lib import TacticServerStub
        from pyasm.common import Environment
        import os, time
        super(MakeNoteWdg, my).__init__(**kwargs)
        my.obj_sk = str(my.kwargs.get('obj_sk'))
        my.header = str(my.kwargs.get('header'))
        my.note = str(my.kwargs.get('note'))
        my.note_ccs = str(my.kwargs.get('note_ccs'))
        my.triggers_str = str(my.kwargs.get('triggers')).lower()
        my.triggers = True #If the triggers are on, it might send dupe emails
        if my.triggers_str == 'false':
            my.triggers = False
        my.notification_email_str = str(my.kwargs.get('notification_email')).lower()
        my.notification_email = False
        if my.notification_email_str == 'true':
            my.notification_email = True
        my.email_info = my.kwargs.get('email_info')
        if my.email_info in [None,'']:
            my.email_info = {}
        my.email_info['error_divs'] = ''
        my.server = TacticServerStub.get()
        login_obj = Environment.get_login()
        my.login = login_obj.get_login()

    def check(my):
        return True

    def fix_date(my, date):
        #This is needed due to the way Tactic deals with dates (using timezone info), post v4.0
        from pyasm.common import SPTDate
        return_date = ''
        date_obj = SPTDate.convert_to_local(date)
        if date_obj not in [None,'']:
            return_date = date_obj.strftime("%Y-%m-%d  %H:%M")
        return return_date

    def make_email_info(my, wo_obj):
        from pyasm.search import Search
        from formatted_emailer import EmailDirections
        import common_tools.utils as ctu
        wo_sk = wo_obj.get_search_key()
        order_s = Search("twog/order")
        order_s.add_filter('code',wo_obj.get_value('order_code'))
        order = order_s.get_sobject()
        title_s = Search("twog/title")
        if 'TITLE' in wo_sk:
            title_s.add_filter('code',wo_obj.get_code())
        else:    
            title_s.add_filter('code',wo_obj.get_value('title_code'))
        title = title_s.get_sobject()
        if 'WORK_ORDER' in wo_sk:
            proj_s = Search("twog/proj")
            proj_s.add_filter('code',wo_obj.get_value('proj_code'))
            proj = proj_s.get_sobject()
            task_s = Search("sthpw/task")
            task_s.add_filter('code',wo_obj.get_value('task_code'))
            task = task_s.get_sobject()
        my.email_info['order_code'] = order.get_code()
        my.email_info['order_name'] = order.get_value('name')
        scheduler_login = order.get_value('login')
        sched_s = Search("sthpw/login")
        sched_s.add_filter('login',scheduler_login)
        scheduler_obj = sched_s.get_sobject()
        my.email_info['scheduler'] = '%s %s' % (scheduler_obj.get_value('first_name'), scheduler_obj.get('last_name'))
        my.email_info['po_number'] = order.get_value('po_number')
        my.email_info['client_name'] = order.get_value('client_name')
        title_full = title.get_value('title')
        episode = title.get_value('episode')
        if episode not in [None,'']:
            title_full = '%s Episode: %s' % (title_full, episode)
        my.email_info['title_full_name'] = title_full
        my.email_info['title_expected_delivery_date'] = title.get_value('expected_delivery_date')
        my.email_info['title_due_date'] = title.get_value('due_date')
        my.email_info['title_code'] = title.get_code()
        if 'WORK_ORDER' in wo_sk:
            my.email_info['proj_code'] = proj.get_code()
            my.email_info['proj_process'] = proj.get_value('process')
            my.email_info['group'] = task.get_value('assigned_login_group')
            my.email_info['work_order_process'] = task.get_value('process')
            my.email_info['work_order_instructions'] = wo_obj.get_value('instructions')
        else:
            my.email_info['proj_code'] = 'N/A'
            my.email_info['proj_process'] = ''
            my.email_info['group'] = 'N/A'
            my.email_info['work_order_process'] = ''
            my.email_info['work_order_instructions'] = ''
        if 'sources_str' not in my.email_info.keys():
            my.email_info['sources_str'] = ''
        login_guy_s = Search('sthpw/login')
        login_guy_s.add_filter('login',my.login)
        login_guy = login_guy_s.get_sobject()
        my.email_info['from_name'] = '%s %s' % (login_guy.get_value('first_name'), login_guy.get_value('last_name'))
        my.email_info['from_email'] = login_guy.get_value('email')
        my.email_info['to_email'] = login_guy.get_value('email')
        old_status = 'N/A'
        new_status = 'N/A'
        if 'WORK_ORDER' in wo_sk:
            old_status = my.email_info['old_status']
            new_status = my.email_info['new_status']
        my.email_info['old_status'] = old_status
        my.email_info['new_status'] = new_status
        my.email_info['status_update_str'] = 'Went to %s from %s' % (new_status.upper(), old_status.upper()) 
        if 'production_error_code' in my.email_info.keys():
            if my.email_info['production_error_code'] not in [None,'']:
                prod_s = Search('twog/production_error')
                prod_s.add_filter('code',my.email_info['production_error_code'])
                prod_e = prod_s.get_sobject()
                 
                error_divs = '''
                                    <br/><br/>
    				<div id='div_name'>Production Error Code: [PRODUCTION_ERROR_CODE] Created: [PROD_E_TIMESTAMP]</div>
    				<div id='div_name'>Error Type: [ERROR_TYPE]</div>
    				<div id='div_name'>Cause: [REJECTION_CAUSE]</div>
    				<div id='div_name'>Time Spent: [TIME_SPENT]</div>
    				<div id='div_name'>Client Description:</div>
    				<div id='div_data'>[CLIENT_DESCRIPTION]</div>
    				<div id='div_name'>Action Taken:</div>
    				<div id='div_data'>[ACTION_TAKEN]</div>
                '''
                error_divs = error_divs.replace('[PRODUCTION_ERROR_CODE]',my.email_info['production_error_code'])
                error_divs = error_divs.replace('[PROD_E_TIMESTAMP]',my.fix_date(prod_e.get_value('timestamp')))
                error_divs = error_divs.replace('[ERROR_TYPE]',prod_e.get_value('error_type'))
                error_divs = error_divs.replace('[REJECTION_CAUSE]',prod_e.get_value('rejection_cause'))
                error_divs = error_divs.replace('[TIME_SPENT]',prod_e.get_value('time_spent'))
                error_divs = error_divs.replace('[CLIENT_DESCRIPTION]',prod_e.get_value('client_description'))
                error_divs = error_divs.replace('[ACTION_TAKEN]',prod_e.get_value('action_taken'))
                my.email_info['error_divs'] = error_divs
            else:
                my.email_info['error_divs'] = ''
        subject = '%s issued for %s (%s) by %s in %s (%s) - Prev Status: %s' % (my.email_info['new_status'], my.email_info['title_full_name'], my.email_info['title_code'], my.email_info['from_name'], my.email_info['group'].upper(), my.email_info['work_order_process'],my.email_info['old_status'])
        subject = subject.replace(' ','..')
        my.email_info['subject'] = subject
        email_dirs = EmailDirections(order_code=order.get_code()) 
        ed_int = email_dirs.get_internal_data()
        new_int_ccs = ed_int['int_ccs']
        my.email_info['int_ccs'] = '%s;%s;%s;%s' % (my.note_ccs, new_int_ccs, ed_int['scheduler_email'], ed_int['to_email'])

        order_builder_url = ctu.get_order_builder_url(my.email_info['order_code'], my.server)
        href = '<a href="{0}">{1}</a>'
        order_hyperlink = href.format(order_builder_url, my.email_info['order_name'])
        my.email_info['order_hyperlink'] = order_hyperlink

        return my.email_info

    def send_internal_email(my, email_info):
        template_file = '/opt/spt/custom/formatted_emailer/status_update_email_template.html'

        if 'file_path' in email_info.keys():
            email_info['operator_description_header'] = 'File Path(s)'
        else:
            email_info['operator_description_header'] = 'Operator Description'

        if email_info['new_status'] in ['Rejected','Fix Needed','QC Rejected','Failed']:
            email_info['operator_description_color'] = '#FF0000'
        else:
            email_info['operator_description_color'] = '#0000FF'

        email_info['subject'] = my.header

        if email_info['to_email']:
            email_sender.send_email(template=template_file, email_data=email_info,
                                    email_file_name='status_change/operator_view_note_{0}.html'.format(email_info.get('work_order_code', '')),
                                    server=my.server)
    
    def execute(my):   
        from pyasm.biz import Note
        from pyasm.search import Search
        from client.tactic_client_lib import TacticServerStub
        server = TacticServerStub.get()
#        if len(my.header) > 59:
#            if 'file_path' in my.email_info.keys():
#                my.header = '%s...' % my.header[0:55]
#            else:
#                my.header = '%s - %s' % (my.email_info['work_order_code'], my.header)
#                my.header = '%s...' % my.header[0:55]
                 
        obj2 = Search.get_by_search_key(my.obj_sk)
        my.email_info = my.make_email_info(obj2)
        email_info_keys = my.email_info.keys()
        note_process = ''
        if my.kwargs.get('note_process'):
            note_process = my.kwargs.get('note_process')
        if 'work_order_process' in my.email_info.keys() and my.email_info['work_order_process'] != '':
            note_process = '%s (WO#%s) - %s - (in %s)' % (my.email_info['work_order_process'], my.email_info['work_order_code'].replace('WORK_ORDER',''), my.email_info['from_name'], my.email_info['title_code'])
        if 'File Path' in my.header:
            note_process = 'File Path - %s (WO#%s) :: %s (in %s)' % (my.email_info['work_order_process'], my.email_info['work_order_code'].replace("WORK_ORDER",""), my.email_info['group'], my.email_info['title_code']) 
        if note_process in ['',None]:
            note_process = 'Note - %s' % my.email_info['from_name']
        ties = {}
        tie = False
        if 'order_code' in my.email_info.keys():
            tie_order_code = my.email_info.get('order_code')
            if tie_order_code not in [None,'']:
                ties['order_code'] = tie_order_code
                tie = True
        if 'title_code' in my.email_info.keys():
            tie_title_code = my.email_info.get('title_code')
            if tie_title_code not in [None,'']:
                ties['title_code'] = tie_title_code
                tie = True
        if 'proj_code' in my.email_info.keys():
            tie_proj_code = my.email_info.get('proj_code')
            if tie_proj_code not in [None,'']:
                ties['proj_code'] = tie_proj_code
                tie = True
        if 'work_order_code' in my.email_info.keys():
            tie_work_order_code = my.email_info.get('work_order_code')
            if tie_work_order_code not in [None,'']:
                ties['work_order_code'] = tie_work_order_code
                tie = True
        if len(note_process) > 60:
            notep_split = note_process.split(' - ')
            note_process = ''
            count = 0
            for n in notep_split:
                if count < len(notep_split) - 1:
                    if note_process == '':
                        note_process = n
                    else:
                        note_process = '%s - %s' % (note_process, n)
        if len(note_process) > 60:
            note_process = '%s...' % note_process[0:55]
        if my.notification_email:
            if 'file_path' in email_info_keys:
                my.email_info['file_path'] = my.email_info.get('file_path')
                my.email_info['operator_description'] = my.email_info.get('file_path')
                my.email_info['error_divs'] = ''
            my.send_internal_email(my.email_info)
            title_code = obj2.get_value('title_code') 
            title_s = Search('twog/title')
            title_s.add_filter('code',title_code)
            title = title_s.get_sobject()
            title_note = Note.create(title, my.note, context=note_process, process=note_process, addressed_to=my.note_ccs, triggers=my.triggers)
            if tie: 
                server.update(title_note.get_search_key(), ties, triggers=False)
        note = Note.create(obj2, my.note, context=note_process, process=note_process, addressed_to=my.note_ccs, triggers=my.triggers)
        if tie and 'work_order_code' in ties.keys(): 
            if ties['work_order_code'] in [None,'']: 
                server.update(note.get_search_key(), ties, triggers=False)
        
        
        return ''


    def check_security(my):
        '''give the command a callback that allows it to check security'''
        return True

    def get_title(my):
        return "Make Note"


class MakeBasicNoteWdg(Command):

    def __init__(my, **kwargs):
        from client.tactic_client_lib import TacticServerStub
        from pyasm.common import Environment
        super(MakeBasicNoteWdg, my).__init__(**kwargs)
        my.obj_sk = str(kwargs.get('obj_sk'))
        my.header = str(kwargs.get('header'))
        my.note = str(kwargs.get('note'))
        my.note_ccs = str(kwargs.get('note_ccs'))
        my.server = TacticServerStub.get()

    def check(my):
        return True
    
    def execute(my):   
        from pyasm.biz import Note
        from pyasm.search import Search
        obj2 = Search.get_by_search_key(my.obj_sk)
        note = Note.create(obj2, my.note, context=my.header, process=my.header, addressed_to=my.note_ccs)
        
        return ''


    def check_security(my):
        '''give the command a callback that allows it to check security'''
        return True

    def get_title(my):
        return "Make Note"
