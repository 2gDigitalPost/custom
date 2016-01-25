import datetime

from tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseTableElementWdg

from pyasm.common import Environment
from pyasm.web import Table, DivWdg
from pyasm.widget import SelectWdg, TextWdg, CheckboxWdg

from qc_reports import ElementEvalLinesWdg, ElementEvalAudioWdg


class ElementEvalWdg(BaseTableElementWdg):

    def init(my):
        nothing = 'true'
        my.formats = ['Electronic/File', 'File - ProRes', 'File - MXF', 'File - MPEG', 'File - WAV','DBC', 'D5',
                      'HDCAM SR', 'NTSC', 'PAL']
        my.frame_rates = ['23.98fps', '59.94i', '50i', '29.97fps', '59.94p', 'DFTC', 'NDFTC', 'PAL/EBU', '-']
        my.machines = ['VTR221', 'VTR222', 'VTR223', 'VTR224', 'VTR225', 'VTR231', 'VTR232', 'VTR233', 'VTR234',
                       'VTR235', 'VTR251', 'VTR252', 'VTR253', 'VTR254', 'VTR255', 'VTR261', 'VTR262', 'VTR263',
                       'VTR264', 'VTR265', 'VTR281', 'VTR282', 'VTR283', 'VTR284', 'VTR285', 'FCP01', 'FCP02', 'FCP03',
                       'FCP04', 'FCP05', 'FCP06', 'FCP07', 'FCP08', 'FCP09', 'FCP10', 'FCP11', 'FCP12', 'Amberfin',
                       'Clipster', 'Stradis']
        my.styles = ['Technical', 'Spot QC','Mastering']
        my.aspect_ratios = ['16x9 1.33',
                            '16x9 1.33 Pan & Scan',
                            '16x9 1.78 Anamorphic',
                            '16x9 1.78 Full Frame',
                            '16x9 1.85 Letterbox',
                            '16x9 1.85 Matted',
                            '16x9 1.85 Matted Anamorphic',
                            '16x9 2.00 Letterbox',
                            '16x9 2.10 Letterbox',
                            '16x9 2.20 Letterbox',
                            '16x9 2.35 Anamorphic',
                            '16x9 2.35 Letterbox',
                            '16x9 2.40 Letterbox',
                            '16x9 2.55 Letterbox',
                            '4x3 1.33 Full Frame',
                            '4x3 1.78 Letterbox',
                            '4x3 1.85 Letterbox',
                            '4x3 2.35 Letterbox',
                            '4x3 2.40 Letterbox']
        my.standards = ['625', '525', '720', '1080 (4:4:4)', '1080', 'PAL', 'NTSC', '-']
        my.element = None
        my.element_lines = None
        my.key_tbl = Table()
        my.key_tbl.add_attr('border', '1')
        my.key_tbl.add_row()
        long = my.key_tbl.add_cell('SECTOR KEY')
        long.add_attr('colspan', '3')
        long.add_attr('align', 'center')
        my.key_tbl.add_row()
        my.key_tbl.add_cell('&nbsp;U-L&nbsp;')
        my.key_tbl.add_cell('&nbsp;U-C&nbsp;')
        my.key_tbl.add_cell('&nbsp;U-R&nbsp;')
        my.key_tbl.add_row()
        my.key_tbl.add_cell('&nbsp;M-L&nbsp;')
        my.key_tbl.add_cell('&nbsp;M-C&nbsp;')
        my.key_tbl.add_cell('&nbsp;M-R&nbsp;')
        my.key_tbl.add_row()
        my.key_tbl.add_cell('&nbsp;L-L&nbsp;')
        my.key_tbl.add_cell('&nbsp;L-C&nbsp;')
        my.key_tbl.add_cell('&nbsp;L-R&nbsp;')

    def get_save_bvr(my, wo_code, ell_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        function loop_dict(dictionary){
                            //var keys = [];
                            for (var key in dictionary) {
                              if (dictionary.hasOwnProperty(key)) {
                                //keys.push(key);
                                alert(key + ': ' + dictionary[key]);
                              }
                            }
                        }
                        try{
                          wo_code = '%s';
                          ell_code = '%s';
                          top_els = document.getElementsByClassName('printable_element_form_' + wo_code);
                          top_el = null;
                          for(var r = 0; r < top_els.length; r++){
                              if(top_els[r].getAttribute('element_code') == ell_code){
                                  top_el = top_els[r];
                              }
                          }
                          big_els = document.getElementsByClassName('big_ol_element_wdg_' + wo_code);
                          big_el = null;
                          for(var r = 0; r < big_els.length; r++){
                              if(big_els[r].getAttribute('element_code') == ell_code){
                                  big_el = big_els[r];
                              }
                          }
                          element_code_old = top_el.getAttribute('element_code');
                          var server = TacticServerStub.get();
                          whole_status = '';
                          stat_els = top_el.getElementsByClassName('spt_input');
                          for(var r = 0; r < stat_els.length; r++){
                              name = stat_els[r].getAttribute('name');
                              if(name.indexOf('marked_') != -1 && stat_els[r].getAttribute('type') == 'checkbox'){
                                  if(stat_els[r].checked){
                                      if(whole_status == ''){
                                          whole_status = name.replace('marked_','');
                                      }else{
                                          whole_status = whole_status + ',' + name.replace('marked_','');
                                      }
                                  }
                              }
                          }
                          if(whole_status == ''){
                              spt.alert('You must first tell us if it was Approved, Rejected, or if there is a Special Condition. Do This by using the checkboxes in the upper-right');
                          }else{
                              spt.app_busy.show('Saving this report...');
                              work_order = server.eval("@SOBJECT(twog/work_order['code','" + wo_code + "'])")[0];
                              sources = server.eval("@SOBJECT(twog/title_origin['title_code','" + work_order.title_code + "'])");
                              source_codes = '';
                              for(var r = 0; r < sources.length; r++){
                                  if(source_codes == ''){
                                      source_codes = sources[r].source_code;
                                  }else{
                                      source_codes = source_codes + ',' + sources[r].source_code;
                                  }
                              }
                              new_data_fields = ['description','timestamp','operator','bay','machine_number','client_name','title','season','episode','version','style','format','standard','po_number','style','aspect_ratio','frame_rate','roll_up','bars_tone','black_silence_1','slate_silence','black_silence_2','start_of_program','end_of_program','roll_up_f','bars_tone_f','black_silence_1_f','slate_silence_f','black_silence_2_f','start_of_program_f','end_of_program_f','active_video_begins','active_video_ends','horizontal_blanking','video_peak','chroma_peak','total_runtime','tv_feature_trailer','textless_at_tail','cc_subtitles','vitc','record_date','language','label','head_logo','tail_logo','notices','record_vendor','vendor_id','file_name'];
                              new_data = {};
                              for(var r = 0; r < new_data_fields.length; r++){
                                  the_field = new_data_fields[r];
                                  the_element = top_el.getElementById(the_field);
                                  if(the_element != null){
                                    new_data[the_field] = the_element.value;
                                  }
                              }
                              decs = ['dec_a1','dec_a2','dec_a3','dec_a4','dec_b1','dec_b2','dec_b3','dec_b4','dec_c1','dec_c2','dec_c3','dec_c4','dec_d1','dec_d2','dec_d3','dec_d4'];
                              for(var r = 0; r < decs.length; r++){
                                  new_data[decs[r]] = '';
                              }
                              date_els = top_el.getElementsByClassName('spt_calendar_input');
                              record_date_el = null;
                              for(var w = 0; w < date_els.length; w++){
                                  if(date_els[w].name == 'record_date'){
                                      record_date_el = date_els[w];
                                  }
                              }
                              record_date = record_date_el.value;
                              new_data['record_date'] = record_date;
                              new_data['login'] = new_data['operator'];
                              new_data['client_code'] = work_order.client_code;
                              new_data['title_code'] = work_order.title_code;
                              new_data['order_code'] = work_order.order_code;
                              new_data['work_order_code'] = wo_code;
                              new_data['conclusion'] = whole_status;
                              new_data['source_code'] = source_codes;
                              new_data['wo_name'] = work_order.process;
                              new_data['type'] = '';
                              new_data['title_type'] = '';
                              new_data['setup'] = '';
                              new_data['vertical_blanking'] = '';
                              new_data['timecodes'] = '';
                              new_data['comp_mne_sync'] = '';
                              new_data['comp_mne_phase'] = '';
                              new_data['missing_mne'] = '';
                              new_data['average_dialogue'] = '';
                              new_data['ltc'] = '';
                              new_data['control_track'] = '';
                              new_element_eval = null;
                              if(element_code_old == ''){
                                  new_element_eval = server.insert('twog/element_eval', new_data);
                              }else{
                                  new_element_eval = server.update(server.build_search_key('twog/element_eval', element_code_old), new_data);
                              }
                              if(new_element_eval.code != ''){
                                  lines = big_el.getElementsByClassName('element_lines');
                                  for(var r = 0; r < lines.length; r++){
                                      if(lines[r].style.display != 'none'){
                                          rowct = lines[r].getAttribute('line');
                                          old_code = lines[r].getAttribute('code');
                                          timecode_in = big_el.getElementById('timecode_in-' + rowct).value;
                                          field_in = big_el.getElementById('field_in-' + rowct).value;
                                          timecode_out = big_el.getElementById('timecode_out-' + rowct).value;
                                          field_out = big_el.getElementById('field_out-' + rowct).value;
                                          //media_type = big_el.getElementById('media_type-' + rowct).value;
                                          description_ele = big_el.getElementById('description-' + rowct);
                                          description_style = '';
                                          if(description_ele.style.fontWeight == 'bold'){
                                              description_style = 'b';
                                          }
                                          if(description_ele.style.fontStyle == 'italic'){
                                              description_style = description_style + 'i';
                                          }
                                          description = description_ele.value;
                                          type_code = big_el.getElementById('type_code-' + rowct).value;
                                          scale = big_el.getElementById('scale-' + rowct).value;
                                          in_source = big_el.getElementById('in_source-' + rowct).value;
                                          in_safe = big_el.getElementById('in_safe-' + rowct).value;
                                          sector_or_channel = big_el.getElementById('sector_or_channel-' + rowct).value;
                                          ordering = big_el.getElementById('ordering-' + rowct);
                                          element_line = {'description': description, 'login': new_data['operator'], 'element_eval_code': new_element_eval.code, 'order_code': work_order.order_code, 'title_code': work_order.title_code, 'work_order_code': wo_code, 'timecode_in': timecode_in, 'field_in': field_in, 'timecode_out': timecode_out, 'field_out': field_out, 'type_code': type_code, 'scale': scale, 'sector_or_channel': sector_or_channel, 'in_source': in_source, 'in_safe': in_safe, 'source_code': source_codes, 'description_style': description_style}
                                          if(ordering){
                                              oval = ordering.value;
                                              if(oval == null){
                                                  oval = '';
                                              }
                                              element_line['ordering'] = oval;
                                          }
                                          //loop_dict(element_line);
                                          if(description != '' && timecode_in != ''){
                                              if(old_code == ''){
                                                  server.insert('twog/element_eval_lines', element_line);
                                              }else{
                                                  server.update(server.build_search_key('twog/element_eval_lines', old_code), element_line);
                                              }
                                          }
                                      }
                                  }
                                  //This needs to be for the barcode lines
                                  bcs = big_el.getElementsByClassName('element_barcodes');
                                  for(var r = 0; r < bcs.length; r++){
                                      if(bcs[r].style.display != 'none'){
                                          rowct = bcs[r].getAttribute('line');
                                          old_code = bcs[r].getAttribute('code');
                                          barcode = big_el.getElementById('barcode-' + rowct).value;
                                          program_start = big_el.getElementById('program_start-' + rowct).value;
                                          f1 = big_el.getElementById('f1-' + rowct).value;
                                          program_end = big_el.getElementById('program_end-' + rowct).value;
                                          f2 = big_el.getElementById('f2-' + rowct).value;
                                          length = big_el.getElementById('length-' + rowct).value;
                                          label_info = big_el.getElementById('label_info-' + rowct).value;
                                          slate_info = big_el.getElementById('slate_info-' + rowct).value;
                                          element_line = {'barcode': barcode, 'program_start': program_start, 'f1': f1, 'program_end': program_end, 'f2': f2, 'length': length, 'label_info': label_info, 'slate_info': slate_info, 'element_eval_code': new_element_eval.code}
                                          if(barcode != '' && program_start != ''){
                                              if(old_code == ''){
                                                  server.insert('twog/element_eval_barcodes', element_line);
                                              }else{
                                                  server.update(server.build_search_key('twog/element_eval_barcodes', old_code), element_line);
                                              }
                                          }
                                      }
                                  }
                                  //barcode lines end
                                  audio_information_el = big_el.getElementById('audio_information');
                                  num_o_channels = Number(audio_information_el.getAttribute('channels'));
                                  for(var r = 0; r < num_o_channels; r++){
                                      rowct = r;
                                      channel_el = big_el.getElementById('channel-' + rowct);
                                      old_code = channel_el.getAttribute('code');
                                      channel = channel_el.value;
                                      content = big_el.getElementById('content-' + rowct).value;
                                      tone = big_el.getElementById('tone-' + rowct).value;
                                      peak = big_el.getElementById('peak-' + rowct).value;
                                      audio_line = {'channel': channel, 'content': content, 'tone': tone, 'peak': peak, 'element_eval_code': new_element_eval.code};
                                      if(channel != '' && content != ''){
                                          if(old_code == ''){
                                              server.insert('twog/element_eval_audio', audio_line);
                                          }else{
                                              server.update(server.build_search_key('twog/element_eval_audio', old_code), audio_line);
                                          }
                                      }
                                  }
                                  var class_name = 'qc_reports.qc_reports.ElementEvalWdg';
                                  kwargs = {'code': wo_code, 'element_code': new_element_eval.code, 'channels': num_o_channels}
                                  //spt.popup.close(spt.popup.get_popup(bvr.src_el));
                                  //spt.panel.load_popup('Element Evaluation for ' + wo_code, class_name, kwargs);
                                  spt.tab.add_new('ElementEvalWdg_qc_report_for_' + wo_code,'Element Evaluation for ' + wo_code, class_name, kwargs);
                              }
                              spt.app_busy.hide();
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, ell_code)}
        return behavior

    def get_clone_report(my, wo_code, el_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          var work_order_code = '%s';
                          var report_code = '%s';
                          var class_name = 'qc_reports.qc_reports.QCReportClonerWdg';
                          kwargs = {'wo_code': work_order_code, 'report_code': report_code, 'type': 'element'}
                          //spt.popup.close(spt.popup.get_popup(bvr.src_el));
                          spt.app_busy.show("Collecting related qc work orders...");
                          spt.panel.load_popup('Clone Report To ... ', class_name, kwargs);
                          spt.app_busy.hide();
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, el_code)}
        return behavior

    def get_print_bvr(my, wo_code, el_code, type):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        function replaceAll(find, replace, str) {
                          find = find.replace('[','\\\[').replace(']','\\\]').replace('+','\\\+');
                          return str.replace(new RegExp(find, 'g'), replace);
                        }
                        function printExternal(url) {
                            var printWindow = window.open( url, 'Print', 'toolbar=1,location=1,directories=1,status=1,menubar=1,scrollbars=0,resizable=0');
                            printWindow.addEventListener('load', function(){
                                printWindow.print();
                                //printWindow.close();
                            }, true);
                        }
                        try{
                          wo_code = '%s';
                          element_code = '%s';
                          type = '%s';
                          top_els = document.getElementsByClassName('printable_element_form_' + wo_code);
                          top_el = null;
                          for(var r = 0; r < top_els.length; r++){
                              if(top_els[r].getAttribute('element_code') == element_code){
                                  top_el = top_els[r];
                              }
                          }
                          title = top_el.getElementById('title').value;
                          episode = top_el.getElementById('episode').value;
                          language = top_el.getElementById('language').value;
                          file_name_str = replaceAll(' ','_',title);
                          if(episode != '' && episode != null){
                              file_name_str = file_name_str + '__' + replaceAll(' ','_',episode);
                          }
                          if(language == '' || language == null){
                              language = 'None_Set';
                          }
                          whole_status = '';
                          stat_els = top_el.getElementsByClassName('spt_input');
                          for(var r = 0; r < stat_els.length; r++){
                              name = stat_els[r].getAttribute('name');
                              if(name.indexOf('marked_') != -1 && stat_els[r].getAttribute('type') == 'checkbox'){
                                  if(stat_els[r].checked){
                                      if(whole_status == ''){
                                          whole_status = name.replace('marked_','');
                                      }else{
                                          whole_status = whole_status + '_' + name.replace('marked_','');
                                      }
                                  }
                              }
                          }
                          file_name_str = file_name_str + '__' + replaceAll(' ','_',language) + '__' + whole_status;
                          file_name_str = replaceAll("\\\'",'',file_name_str);
                          file_name_str = replaceAll("\\\-",'_',file_name_str);
                          file_name_str = replaceAll("\\\.",'',file_name_str);
                          file_name_str = replaceAll("\\\,",'',file_name_str);
                          file_name_str = replaceAll("\\\!",'',file_name_str);
                          file_name_str = replaceAll("\\\?",'',file_name_str);
                          file_name_str = replaceAll("\\\^",'',file_name_str);
                          file_name_str = replaceAll("\\\#",'',file_name_str);
                          file_name_str = replaceAll("\\\&",'_and_',file_name_str);
                          file_name_str = replaceAll("\\\(",'',file_name_str);
                          file_name_str = replaceAll("\\\)",'',file_name_str);
                          file_name_str = replaceAll("\\\*",'',file_name_str);
                          file_name_str = replaceAll("\\\%s",'',file_name_str);
                          file_name_str = replaceAll("\\\$",'',file_name_str);
                          file_name_str = replaceAll("\\\@",'',file_name_str);
                          file_name_str = replaceAll("\\\~",'',file_name_str);
                          file_name_str = replaceAll("\\\`",'',file_name_str);
                          file_name_str = replaceAll("\\\:",'',file_name_str);
                          file_name_str = replaceAll("\\\;",'',file_name_str);
                          file_name_str = replaceAll('\\\"','',file_name_str);
                          file_name_str = replaceAll('\\\<','',file_name_str);
                          file_name_str = replaceAll('\\\>','',file_name_str);
                          file_name_str = replaceAll('\\\/','',file_name_str);
                          file_name_str = replaceAll('\\\|','',file_name_str);
                          file_name_str = replaceAll('\\\}','',file_name_str);
                          file_name_str = replaceAll('\\\{','',file_name_str);
                          file_name_str = replaceAll('\\\=','',file_name_str);
                          var server = TacticServerStub.get();
                          lines = top_el.getElementsByClassName('element_lines');
                          for(var r = 0; r < lines.length; r++){
                              linect = lines[r].getAttribute('line');
                              tc = top_el.getElementById('timecode_in-' + linect);
                              if(tc.value == '' || tc.value == null){
                                  lines[r].style.display = 'none';
                              }
                              ord = top_el.getElementById('ordering-' + linect);
                              if(ord){
                                  ord.style.display = 'none';
                              }
                              killer = top_el.getElementById('killer-' + linect);
                              if(killer){
                                  killer.style.display = 'none';
                              }
                              descriptioner = top_el.getElementById('description-' + linect);
                              if(descriptioner){
                                  descriptioner.setAttribute('width', '520px');
                                  descriptioner.style.width = '520px';
                              }
                          }
                          bcs = top_el.getElementsByClassName('element_barcodes');
                          for(var r = 0; r < bcs.length; r++){
                              linect = bcs[r].getAttribute('line');
                              tc = top_el.getElementById('barcode-' + linect);
                              if(tc.value == '' || tc.value == null){
                                  bcs[r].style.display = 'none';
                              }else{
                                  cells = bcs[r].getElementsByTagName('td');
                                  for(var w = 0; w < cells.length; w++){
                                      if(cells[w].innerHTML == '<b>X</b>'){
                                          cells[w].style.display = 'none';
                                      }
                                  }
                              }
                          }
                          sels = top_el.getElementsByClassName('select_cell');
                          for(var r = 0; r < sels.length; r++){
                              select_el = sels[r].getElementsByTagName('select')[0];
                              offset_width = select_el.offsetWidth;
                              value = select_el.value;
                              sels[r].innerHTML = '<input type="text" value="' + value + '" style="width: ' + offset_width + ';"/>';
                          }
                          tc_shifter = top_el.getElementById('tc_shifter');
                          tc_shifter.style.display = 'none';
                          description_el = top_el.getElementById('description');
                          description_el.setAttribute('cols','110');
                          darkrow = top_el.getElementById('darkrow');
                          darkrow.setAttribute('width','110px');
                          audio_row = top_el.getElementById('audio_row');
                          audio_row.innerHTML = audio_row.innerHTML.replace('- click to change number of channels','');
                          top_els = document.getElementsByClassName('printable_element_form_' + wo_code);
                          top_el = null;
                          for(var r = 0; r < top_els.length; r++){
                              if(top_els[r].getAttribute('element_code') == element_code){
                                  top_el = top_els[r];
                              }
                          }
                          new_html = top_el.innerHTML;
                          //thing = server.execute_cmd('qc_reports.qc_reports.PrintQCReportWdg', {'html': '<table>' + top_el.innerHTML + '</table>','wo_code': wo_code, 'type': type});
                          thing = server.execute_cmd('qc_reports.qc_reports.PrintQCReportWdg', {'html': '<table>' + new_html + '</table>','preppend_file_name': file_name_str, 'type': ''});
                          var url = 'http://tactic01/qc_reports/work_orders/' + file_name_str + '.html';
                          printExternal(url);
                          if(element_code != '' && element_code != null){
                              //close, then reload page
                              var class_name = 'qc_reports.qc_reports.ElementEvalWdg';
                              kwargs = {'code': wo_code, 'element_code': element_code}
                              spt.tab.add_new('ElementEvalWdg_qc_report_for_' + wo_code,'Element Evaluation for ' + wo_code, class_name, kwargs);
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, el_code, type, '%')}
        return behavior

    def get_click_row(my, wo_code, el_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          var work_order_code = '%s';
                          var element_code = '%s';
                          var class_name = 'qc_reports.qc_reports.ElementEvalWdg';
                          kwargs = {'code': work_order_code, 'element_code': element_code}
                          //spt.popup.close(spt.popup.get_popup(bvr.src_el));
                          //spt.panel.load_popup('Element Evaluation for ' + work_order_code, class_name, kwargs);
                          spt.tab.add_new('ElementEvalWdg_qc_report_for_' + work_order_code,'Element Evaluation for ' + work_order_code, class_name, kwargs);
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, el_code)}
        return behavior

    def get_add_dots(my):
        behavior = {'css_class': 'clickme', 'type': 'keyup', 'cbjs_action': '''
                try{
                    var entered = bvr.src_el.value;
                    var new_str = '';
                    entered = entered.replace(/:/g,'');
                    for(var r = 0; r < entered.length; r++){
                        if(r % 2 == 0 && r != 0){
                            new_str = new_str + ':';
                        }
                        new_str = new_str + entered[r];
                    }
                    bvr.src_el.value = new_str;
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         '''}
        return behavior

    def get_delete_report(my, wo_code, el_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          var work_order_code = '%s';
                          var element_code = '%s';
                          if(confirm("Are you sure you want to delete this report?")){
                              if(confirm("Checking again. You really want to delete this report?")){
                                  var server = TacticServerStub.get();
                                  server.retire_sobject(server.build_search_key('twog/element_eval', element_code));
                                  var class_name = 'qc_reports.qc_reports.ElementEvalWdg';
                                  kwargs = {'code': work_order_code}
                                  //spt.popup.close(spt.popup.get_popup(bvr.src_el));
                                  //spt.panel.load_popup('Element Evaluation for ' + work_order_code, class_name, kwargs);
                                  spt.tab.add_new('ElementEvalWdg_qc_report_for_' + work_order_code,'Element Evaluation for ' + work_order_code, class_name, kwargs);
                              }
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, el_code)}
        return behavior

    def get_change_channels(my, wo_code, ell_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          entered = prompt("How many audio channels do you want in this report?");
                          if(isNaN(entered)){
                              alert(entered + " is not a number. Please only enter numbers here.")
                          }else{
                              wo_code = '%s';
                              ell_code = '%s';
                              big_els = document.getElementsByClassName('big_ol_element_wdg_' + wo_code);
                              big_el = null;
                              for(var r = 0; r < big_els.length; r++){
                                  if(big_els[r].getAttribute('element_code') == ell_code){
                                      big_el = big_els[r];
                                  }
                              }
                              audio_table = big_el.getElementById('audio_table');
                              element_eval_code = audio_table.getAttribute('code');
                              send_data = {'code': element_eval_code, 'wo_code': wo_code, 'channels': entered, 'force_it': 'true'};
                              spt.api.load_panel(audio_table, 'qc_reports.qc_reports.ElementEvalAudioWdg', send_data);
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, ell_code)}
        return behavior

    def launch_tc_shifter(my, wo_code, ell_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          wo_code = '%s';
                          ell_code = '%s';
                          var class_name = 'qc_reports.qc_reports.ReportTimecodeShifterWdg';
                          kwargs = {
                                           'wo_code': wo_code,
                                           'ell_code': ell_code
                                   };
                          spt.panel.load_popup('Timecode Shifter', class_name, kwargs);
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code,ell_code)}
        return behavior

    def kill_nothing(my, val):
        if val == 'NOTHINGXsXNOTHING':
            val = ''
        return val

    def txtbox(my, name, width='200px', js='no'):
        txt = TextWdg(name)
        txt.add_attr('id', name)
        txt.add_style('width: {0};'.format(width))
        txt.set_value(my.element.get(name))

        if js in ['Yes', 'yes']:
            txt.add_behavior(my.get_add_dots())

        return txt

    def get_display(my):
        login = Environment.get_login()
        this_user = login.get_login()
        groups = Environment.get_group_names()

        show_save = False
        for g in groups:
            if 'qc' in g or 'edeliveries' in g or 'admin' in g:
                show_save = True

        this_timestamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        code = my.kwargs.get('code')

        channels = 21
        if 'channels' in my.kwargs.keys():
            channels = my.kwargs.get('channels')

        original_code = code
        server = TacticServerStub.get()
        widget = DivWdg()

        if 'TITLE' in code:
            wos = server.eval("@GET(twog/work_order['title_code','%s'].code)" % code)
            if len(wos) > 0:
                code = wos[0]
            else:
                none_msg = 'THERE ARE NO WORK ORDERS IN THIS TITLE'
                none_tbl = Table()
                none_tbl.add_row()
                none_tbl.add_cell(none_msg)
                widget.add(none_tbl)
                return widget

        work_order = server.eval("@SOBJECT(twog/work_order['code','%s'])" % code)[0]
        title = server.eval("@SOBJECT(twog/title['code','%s'])" % work_order.get('title_code'))[0]
        element_code = ''

        my.element = {
            'code': '',
            'description': '',
            'timestamp': this_timestamp,
            'login': this_user,
            'operator': this_user,
            'type': '',
            'bay': '',
            'machine_number': '',
            'client_code': title.get('client_code'),
            'client_name': title.get('client_name'),
            'title': title.get('title'),
            'episode': title.get('episode'),
            'version': '',
            'title_type': '',
            'timecode': '',
            'po_number': title.get('po_number'),
            'style': '',
            'title_code': work_order.get('title_code'),
            'order_code': work_order.get('order_code'),
            'work_order_code': code,
            'conclusion': '',
            'source_code': '',
            'standard': my.kill_nothing(title.get('deliverable_standard')),
            'aspect_ratio': my.kill_nothing(title.get('deliverable_aspect_ratio')),
            'frame_rate': my.kill_nothing(title.get('deliverable_frame_rate')),
            'format': my.kill_nothing(title.get('deliverable_format')),
            'wo_name': work_order.get('process'),
            'roll_up': '',
            'bars_tone': '',
            'black_silence_1': '',
            'slate_silence': '',
            'black_silence_2': '',
            'video_mod_disclaimer': '',
            'start_of_program': '',
            'end_of_program': '',
            'roll_up_f': '',
            'bars_tone_f': '',
            'black_silence_1_f': '',
            'slate_silence_f': '',
            'black_silence_2_f': '',
            'video_mod_disclaimer_f': '',
            'start_of_program_f': '',
            'end_of_program_f': '',
            'active_video_begins': '',
            'active_video_ends': '',
            'horizontal_blanking': '',
            'vertical_blanking': '',
            'video_average': '',
            'video_peak': '',
            'chroma_average': '',
            'chroma_peak': '',
            'video_sync': '',
            'chroma_burst': '',
            'setup': '',
            'control_track': '',
            'video_rf': '',
            'front_porch': '',
            'sync_duration': '',
            'burst_duration': '',
            'total_runtime': '',
            'tv_feature_trailer': '',
            'textless_at_tail': '',
            'cc_subtitles': '',
            'timecodes': '',
            'vitc': '',
            'ltc': '',
            'record_vendor': '',
            'record_date': '',
            'language': '',
            'comp_mne_sync': '',
            'comp_mne_phase': '',
            'missing_mne': '',
            'average_dialogue': '',
            'dec_a1': '',
            'dec_a2': '',
            'dec_a3': '',
            'dec_a4': '',
            'dec_b1': '',
            'dec_b2': '',
            'dec_b3': '',
            'dec_b4': '',
            'dec_c1': '',
            'dec_c2': '',
            'dec_c3': '',
            'dec_c4': '',
            'dec_d1': '',
            'dec_d2': '',
            'dec_d3': '',
            'dec_d4': '',
            'tape_pack': '',
            'label': '',
            'head_logo': '',
            'tail_logo': '',
            'notices': '',
            'vendor_id': '',
            'file_name': ''
        }
        my.element_lines = [
            {
                'code': '',
                'description': '',
                'timestamp': this_timestamp,
                's_status': '',
                'keywords': '',
                'login': this_user,
                'id': '',
                'name': '',
                'element_eval_code': '',
                'order_code': work_order.get('order_code'),
                'title_code': work_order.get('title_code'),
                'work_order_code': code,
                'timecode_in': '',
                'field_in': '',
                'timecode_out': '',
                'field_out': '',
                'media_type': '',
                'type_code': '',
                'scale': '',
                'sector_or_channel': '',
                'in_safe': '',
                'in_source': '',
                'source_code': ''
            }
        ]
        if 'element_code' in my.kwargs.keys():
            element_code = str(my.kwargs.get('element_code'))
            my.element = server.eval("@SOBJECT(twog/element_eval['code','%s'])" % element_code)[0]
            my.element_lines = server.eval("@SOBJECT(twog/element_eval_lines['element_eval_code','%s'])" % element_code)

        wo_pevals = server.eval("@SOBJECT(twog/element_eval['work_order_code','%s']['code','!=','%s'])" % (code, element_code))
        title_pevals = server.eval("@SOBJECT(twog/element_eval['title_code','%s']['work_order_code','!=','%s']['code','!=','%s'])" % (work_order.get('title_code'), work_order.get('code'), element_code))
        others = Table()
        others.add_style('background-color: #528B8B; width: 100%;')
        cols = ['#537072', '#518A1A']
        colsct = 0
        if len(title_pevals) > 0:
            trrr = others.add_row()
            trrr.add_style('background-color: #50EDA1;')
            others.add_cell('<b>Other Element Evals for Title</b>')
            for t in title_pevals:
                click_row = others.add_row()
                click_row.add_attr('element_code', t.get('code'))
                click_row.add_attr('work_order_code', t.get('work_order_code'))
                click_row.set_style('cursor: pointer; background-color: %s;' % cols[colsct % 2])
                click_row.add_behavior(my.get_click_row(t.get('work_order_code'), t.get('code')))
                others.add_cell('<b>WO:</b> %s, <b>CODE:</b> %s' % (t.get('wo_name'), t.get('work_order_code')))
                others.add_cell('<b>LANGUAGE:</b> %s' % (t.get('language')))
                others.add_cell('<b>OPERATOR:</b> %s' % t.get('operator'))
                others.add_cell('<b>STYLE:</b> %s' % t.get('style'))
                others.add_cell('<b>CONCLUSION:</b> %s' % t.get('conclusion'))
                others.add_cell('<b>DATETIME:</b> %s' % t.get('timestamp'))
                colsct += 1
        if len(wo_pevals) > 0:
            wrrr = others.add_row()
            wrrr.add_style('background-color: #50EDA1;')
            others.add_cell('<b>Other Element Evals for Work Order</b>')
            for w in wo_pevals:
                click_row = others.add_row()
                click_row.add_attr('element_code', w.get('code'))
                click_row.add_attr('work_order_code', w.get('work_order_code'))
                click_row.set_style('cursor: pointer; background-color: %s;' % cols[colsct % 2])
                click_row.add_behavior(my.get_click_row(w.get('work_order_code'), w.get('code')))
                others.add_cell('<b>WO:</b> %s, <b>CODE:</b> %s' % (w.get('wo_name'), w.get('work_order_code')))
                others.add_cell('<b>LANGUAGE:</b> %s' % (w.get('language')))
                others.add_cell('<b>OPERATOR:</b> %s' % w.get('operator'))
                others.add_cell('<b>STYLE:</b> %s' % w.get('style'))
                others.add_cell('<b>CONCLUSION:</b> %s' % w.get('conclusion'))
                others.add_cell('<b>DATETIME:</b> %s' % w.get('timestamp'))
                colsct += 1

        widget.add_attr('class', 'big_ol_element_wdg_%s' % code)
        widget.add_attr('element_code', my.element.get('code'))
        widget.add_attr('id', 'big_ol_element_wdg_%s' % code)
        table = Table()
        table.add_attr('class', 'printable_element_form_%s' % code)
        table.add_attr('element_code', my.element.get('code'))
        table.add_attr('work_order_code', my.element.get('work_order_code'))
        img_tbl = Table()
        img_tbl.add_row()
        i2 = Table()
        i2.add_row()
        i2.add_cell('<img src="/source_labels/2GLogo_small4.png"/>')
        img_tbl.add_cell(i2)
        ad = Table()
        ad.add_row()
        address = ad.add_cell('<b>2G Digital Post, Inc.</b><br/>280 E. Magnolia Blvd.<br/>Burbank, CA 91502<br/>310-840-0600<br/>www.2gdigitalpost.com')
        address.add_attr('nowrap', 'nowrap')
        address.add_style('font-size: 9px;')
        img_tbl.add_cell(ad)
        acr_s = ['APPROVED', 'REJECTED']
        acr = Table()
        for mark in acr_s:
            acr.add_row()
            acr1 = CheckboxWdg('marked_%s' % mark)

            if mark in my.element.get('conclusion'):
                acr1.set_value(True)
            else:
                acr1.set_value(False)

            acr.add_cell(acr1)
            acr.add_cell('<b>{0}</b>'.format(mark))
        rtbl = Table()
        rtbl.add_row()
        rtbl.add_cell('&nbsp;&nbsp;&nbsp;&nbsp;')
        client_name = my.element.get('client_name').upper()

        if not client_name:
            client_name = "ELEMENT EVALUATION"

        big = rtbl.add_cell("<b>{0}</b>".format(client_name))
        big.add_attr('nowrap', 'nowrap')
        big.add_attr('align', 'center')
        big.add_attr('valign', 'center')
        big.add_style('font-size: 40px;')
        rtbl.add_cell('&nbsp;&nbsp;&nbsp;&nbsp;')
        rtbl.add_cell(acr)
        toptbl = Table()
        toptbl.add_row()
        toptbl.add_cell(img_tbl)
        toptbl.add_cell(rtbl)
        bay_sel = SelectWdg('bay_select')
        bay_sel.add_attr('id', 'bay')
        bay_sel.add_style('width: 135px;')
        bay_sel.append_option('--Select--', '')
        for i in range(1, 13):
            bay_sel.append_option('Bay %s' % i, 'Bay %s' % i)
        if my.element.get('bay') not in [None, '']:
            bay_sel.set_value(my.element.get('bay'))

        style_sel = SelectWdg('style_select')
        style_sel.add_attr('id', 'style')
        style_sel.add_style('width: 135px;')
        style_sel.append_option('--Select--', '')
        for s in my.styles:
            style_sel.append_option(s, s)
        if my.element.get('style') not in [None, '']:
            style_sel.set_value(my.element.get('style'))

        machine_sel = SelectWdg('machine_select')
        machine_sel.add_attr('id', 'machine_number')
        machine_sel.add_style('width: 135px;')
        machine_sel.append_option('--Select--', '')
        for m in my.machines:
            machine_sel.append_option(m, m)
        if my.element.get('machine_number') not in [None, '']:
            machine_sel.set_value(my.element.get('machine_number'))

        format_sel = SelectWdg('format_select')
        format_sel.add_attr('id', 'format')
        format_sel.add_style('width: 153px;')
        format_sel.append_option('--Select--', '')
        for f in my.formats:
            format_sel.append_option(f, f)
        if my.element.get('format') not in [None, '']:
            format_sel.set_value(my.element.get('format'))

        frame_rate_sel = SelectWdg('frame_rate_select')
        frame_rate_sel.add_attr('id', 'frame_rate')
        frame_rate_sel.add_style('width: 153px;')
        frame_rate_sel.append_option('--Select--', '')
        for f in my.frame_rates:
            frame_rate_sel.append_option(f, f)
        if my.element.get('frame_rate') not in [None, '']:
            frame_rate_sel.set_value(my.element.get('frame_rate'))

        standard_sel = SelectWdg('standard_select')
        standard_sel.add_attr('id', 'standard')
        standard_sel.add_style('width: 153px;')
        standard_sel.append_option('--Select--', '')
        for s in my.standards:
            standard_sel.append_option(s, s)
        if my.element.get('standard') not in [None, '']:
            standard_sel.set_value(my.element.get('standard'))

        majtbl = Table()
        majtbl.add_attr('class', 'majtbl')
        majtbl.add_row()
        majtbl.add_cell('DATE')
        majtbl.add_cell('OPERATOR')
        majtbl.add_cell('STYLE')
        majtbl.add_cell('BAY')
        majtbl.add_cell('MACHINE #')
        majtbl.add_row()

        # Add the input box for 'DATE' with the current timestamp
        majtbl.add_cell(my.txtbox('timestamp', width='137px'))

        if my.element.get('operator') not in [None, '']:
            that_login = server.eval("@SOBJECT(sthpw/login['login','%s'])" % my.element.get('operator'))
            if that_login:
                that_login = that_login[0]
                that_login_name = '%s %s' % (that_login.get('first_name'), that_login.get('last_name'))
                my.element['operator'] = that_login_name
        majtbl.add_cell(my.txtbox('operator', width='150px'))
        mm1 = majtbl.add_cell(style_sel)
        mm1.add_attr('class', 'select_cell')

        mm2 = majtbl.add_cell(bay_sel)
        mm2.add_attr('class', 'select_cell')

        mm3 = majtbl.add_cell(machine_sel)
        mm3.add_attr('class', 'select_cell')

        title_table = Table()
        title_table.add_row()
        title_table.add_cell('TITLE:')
        title_table.add_cell(my.txtbox('title', width='400px'))
        title_table.add_cell('&nbsp;&nbsp;&nbsp;FORMAT:')

        format_select_cell = title_table.add_cell(format_sel)
        format_select_cell.add_attr('class', 'select_cell')

        title_table.add_row()
        title_table.add_cell('SEASON:')
        title_table.add_cell(my.txtbox('season', width='400px'))
        title_table.add_cell('&nbsp;&nbsp;&nbsp;STANDARD:')

        standard_select_cell = title_table.add_cell(standard_sel)
        standard_select_cell.add_attr('class', 'select_cell')

        title_table.add_row()
        title_table.add_cell('EPISODE:')
        title_table.add_cell(my.txtbox('episode', width='400px'))

        ffr = title_table.add_cell('&nbsp;&nbsp;&nbsp;FRAME RATE:')
        ffr.add_attr('nowrap', 'nowrap')

        framerate_select_cell = title_table.add_cell(frame_rate_sel)
        framerate_select_cell.add_attr('class', 'select_cell')

        title_table.add_row()
        title_table.add_cell('VERSION:')
        title_table.add_cell(my.txtbox('version', width='400px'))
        title_table.add_cell('&nbsp;&nbsp;&nbsp;PO #:')
        title_table.add_cell(my.txtbox('po_number', width='151px'))
        title_table.add_row()

        file_name_label = title_table.add_cell('FILE NAME:')
        file_name_label.add_attr('nowrap', 'nowrap')

        file_name_input = title_table.add_cell(my.txtbox('file_name', width='635px'))
        file_name_input.add_attr('colspan', '3')

        tt2 = Table()
        tt2.add_attr('width', '85%')
        tt2.add_row()
        tt2.add_cell(title_table)

        pgf = Table()
        pgf.add_attr('class', 'pgf')

        head = Table()
        head.set_style('background-color: #4a4a4a; width: 100%; color: #FFFFFF')
        head.add_row()

        pgc = head.add_cell('<b>PROGRAM FORMAT</b>')
        pgc.add_attr('width', '500px')
        pgc.add_attr('align', 'left')

        spcs0 = head.add_cell('<b>F</b>')
        spcs0.add_attr('align', 'left')
        spcs0.add_attr('width', '25px')

        pgc2 = head.add_cell('<b>VIDEO MEASUREMENTS</b>')
        pgc2.add_attr('align', 'left')

        pg1 = pgf.add_cell(head)
        pg1.add_attr('width', '100%')
        pg1.add_attr('colspan', '3')

        pgf.add_row()

        pf = Table()
        pf.add_attr('border', '1')
        pf.add_attr('nowrap', 'nowrap')
        pf.add_row()

        pf1 = pf.add_cell('Roll-up (blank)')
        pf1.add_attr('nowrap', 'nowrap')

        pf.add_cell(my.txtbox('roll_up', width='399px', js='yes'))
        pf.add_cell(my.txtbox('roll_up_f', width='20px'))

        pf.add_row()
        pf2 = pf.add_cell('Bars/Tone')
        pf2.add_attr('nowrap', 'nowrap')
        pf.add_cell(my.txtbox('bars_tone', width='399px', js='yes'))
        pf.add_cell(my.txtbox('bars_tone_f', width='20px'))
        pf.add_row()

        pf3 = pf.add_cell('Black/Silence')
        pf3.add_attr('nowrap', 'nowrap')

        pf.add_cell(my.txtbox('black_silence_1', width='399px', js='yes'))
        pf.add_cell(my.txtbox('black_silence_1_f', width='20px'))
        pf.add_row()

        pf4 = pf.add_cell('Slate/Silence')
        pf4.add_attr('nowrap', 'nowrap')
        pf.add_cell(my.txtbox('slate_silence', width='399px', js='yes'))
        pf.add_cell(my.txtbox('slate_silence_f', width='20px'))
        pf.add_row()
        pf5 = pf.add_cell('Black/Silence')
        pf5.add_attr('nowrap', 'nowrap')
        pf.add_cell(my.txtbox('black_silence_2', width='399px', js='yes'))
        pf.add_cell(my.txtbox('black_silence_2_f', width='20px'))
        pf.add_row()
        pf7 = pf.add_cell('Start of Program')
        pf7.add_attr('nowrap', 'nowrap')
        pf.add_cell(my.txtbox('start_of_program', width='399px', js='yes'))
        pf.add_cell(my.txtbox('start_of_program_f', width='20px'))
        pf.add_row()
        pf8 = pf.add_cell('End of Program')
        pf8.add_attr('nowrap', 'nowrap')
        pf.add_cell(my.txtbox('end_of_program', width='399px', js='yes'))
        pf.add_cell(my.txtbox('end_of_program_f', width='20px'))

        vm = Table()
        vm.add_attr('border', '1')
        vm.add_attr('nowrap', 'nowrap')
        vm.add_row()
        vm1 = vm.add_cell('Active Video Begins')
        vm1.add_attr('nowrap', 'nowrap')
        vm.add_cell(my.txtbox('active_video_begins', width="400px"))

        vm.add_row()
        vm3 = vm.add_cell('Active Video Ends')
        vm3.add_attr('nowrap', 'nowrap')
        vm.add_cell(my.txtbox('active_video_ends', width="400px"))

        vm.add_row()
        vm5 = vm.add_cell('Horizontal Blanking')
        vm5.add_attr('nowrap', 'nowrap')
        vm.add_cell(my.txtbox('horizontal_blanking', width="400px"))
        vm.add_row()

        vm.add_row()
        vm11 = vm.add_cell('Luminance Peak')
        vm11.add_attr('nowrap', 'nowrap')
        vm.add_cell(my.txtbox('video_peak', width="400px"))
        vm.add_row()
        vm.add_row()
        vm15 = vm.add_cell('Chroma Peak')
        vm15.add_attr('nowrap', 'nowrap')
        vm.add_cell(my.txtbox('chroma_peak', width="400px"))
        vm.add_row()

        tm4 = vm.add_cell('Head Logo')
        tm4.add_attr('nowrap', 'nowrap')
        vm.add_cell(my.txtbox('head_logo', width="400px"))

        vm.add_row()
        tm55 = vm.add_cell('Tail Logo')
        tm55.add_attr('nowrap', 'nowrap')
        vm.add_cell(my.txtbox('tail_logo', width="400px"))

        pfc1 = pgf.add_cell(pf)
        pfc1.add_attr('valign', 'top')
        pgf.add_cell('&nbsp;')
        pgf.add_cell(vm)

        epro = Table()
        epro.add_attr('class', 'epro')

        head2 = Table()
        head2.set_style('background-color: #4a4a4a; width: 100%; color: #FFFFFF')
        head2.add_row()

        pgc2 = head2.add_cell('<b>ELEMENT PROFILE</b>')
        pgc2.add_attr('align', 'left')
        pg1 = epro.add_cell(head2)
        pg1.add_attr('width', '100%')
        pg1.add_attr('colspan', '3')
        epro.add_row()
        ef = Table()
        ef.add_attr('border', '1')
        ef.add_row()
        ef1 = ef.add_cell('Total Runtime')
        ef1.add_attr('nowrap', 'nowrap')
        ef.add_cell(my.txtbox('total_runtime', width="400px", js='yes'))
        ef.add_row()
        ef2 = ef.add_cell('TV/Feature/Trailer')
        ef2.add_attr('nowrap', 'nowrap')
        ef.add_cell(my.txtbox('tv_feature_trailer', width="400px"))
        ef.add_row()
        ef2 = ef.add_cell('Video Aspect Ratio')
        ef2.add_attr('nowrap', 'nowrap')
        ar_select = SelectWdg('aspect_ratio_select')
        ar_select.add_attr('id', 'aspect_ratio')
        ar_select.add_style('width: 380px;')
        ar_select.append_option('--Select--', '')
        for a in my.aspect_ratios:
            ar_select.append_option(a, a)
        if my.element.get('aspect_ratio') not in [None, '']:
            ar_select.set_value(my.element.get('aspect_ratio'))
        mm10 = ef.add_cell(ar_select)
        mm10.add_attr('class', 'select_cell')
        ef.add_row()
        ef2 = ef.add_cell('Textless @ Tail')
        ef2.add_attr('nowrap', 'nowrap')
        ef.add_cell(my.txtbox('textless_at_tail', width="400px"))
        ef.add_row()
        ef2 = ef.add_cell('Notices')
        ef2.add_attr('nowrap', 'nowrap')
        ef.add_cell(my.txtbox('notices', width="400px"))
        ef.add_row()
        ef.add_cell('Label')

        gng2 = ['Good', 'Fair', 'Poor', '-']
        lab_sel = SelectWdg('label')
        lab_sel.add_attr('id', 'label')
        lab_sel.add_style('width: 380px;')
        lab_sel.append_option('--Select--', '')

        for la in gng2:
            lab_sel.append_option(la, la)
        if my.element.get('label') not in [None, '']:
            lab_sel.set_value(my.element.get('label'))

        in1 = ef.add_cell(lab_sel)
        in1.add_attr('class', 'select_cell')

        tm = Table()
        tm.add_attr('border', '1')
        tm.add_attr('nowrap', 'nowrap')
        tm.add_row()
        tm2 = tm.add_cell('Language')
        tm2.add_attr('nowrap', 'nowrap')
        tm.add_cell(my.txtbox('language', width="424px"))
        tm.add_row()
        ef2 = tm.add_cell('(CC)/Subtitles')
        ef2.add_attr('nowrap', 'nowrap')
        tm.add_cell(my.txtbox('cc_subtitles', width="424px"))
        tm.add_row()
        tm3 = tm.add_cell('VITC')
        tm3.add_attr('nowrap', 'nowrap')
        tm.add_cell(my.txtbox('vitc', width="424px"))

        tm.add_row()
        tm3 = tm.add_cell('Source Barcode')
        tm3.add_attr('nowrap', 'nowrap')
        tm.add_cell(my.txtbox('record_vendor', width="424px"))
        tm.add_row()
        tm33 = tm.add_cell('Element QC Barcode')
        tm33.add_attr('nowrap', 'nowrap')
        tm.add_cell(my.txtbox('vendor_id', width="424px"))
        tm.add_row()
        tm3 = tm.add_cell('Record Date')
        tm3.add_attr('nowrap', 'nowrap')

        from tactic.ui.widget import CalendarInputWdg
        rcrd = CalendarInputWdg("record_date")
        rcrd.set_option('show_activator', 'true')
        rcrd.set_option('show_time', 'false')
        rcrd.set_option('width', '380px')
        rcrd.set_option('id', 'record_date')
        rcrd.set_option('display_format', 'MM/DD/YYYY HH:MM')
        if my.element.get('record_date') not in [None, '']:
            rcrd.set_option('default', my.element.get('record_date'))
        else:
            rcrd.set_option('default', this_timestamp.split(' ')[0])
        rcrd.get_top().add_attr('id', 'record_date')
        rcrd.set_persist_on_submit()
        rcrd_date = tm.add_cell(rcrd)
        rcrd_date.add_attr('nowrap', 'nowrap')

        epro.add_cell(ef)
        epro.add_cell('&nbsp;')
        epro.add_cell(tm)

        ktbl = Table()
        ktbl.add_row()
        k1 = ktbl.add_cell('<i>Code Definitions: F=Film V=Video T=Telecine A=Audio</i>')
        k1.add_attr('align', 'left')
        k = ktbl.add_cell('&nbsp;&nbsp;&nbsp;')
        k.add_attr('align', 'right')
        k2 = ktbl.add_cell('<i>Severity Scale: 1=Minor 2=Marginal 3=Severe</i>')
        k2.add_attr('align', 'right')
        ktbl.add_cell('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
        k3 = ktbl.add_cell('<u>TC Shift</u>')
        k3.add_attr('id', 'tc_shifter')
        k3.add_attr('align', 'right')
        k3.add_style('cursor: pointer;')
        k3.add_behavior(my.launch_tc_shifter(code, my.element.get('code')))

        linestbl = ElementEvalLinesWdg(code=my.element.get('code'), wo_code=code,
                                       client_code=my.element.get('client_code'))
        audtbl = ElementEvalAudioWdg(code=my.element.get('code'), wo_code=code, channels=channels)

        fulllines = Table()
        fulllines.add_attr('border', '2')
        fulllines.add_row()
        fulllines.add_cell(ktbl)
        fulllines.add_row()
        fulllines.add_cell(linestbl)

        table.add_row()
        table.add_cell(toptbl)
        table.add_row()
        table.add_cell(majtbl)
        table.add_row()
        table.add_cell(tt2)
        table.add_row()
        table.add_cell(pgf)
        table.add_row()
        table.add_cell(epro)
        table.add_row()

        aud2 = table.add_cell('<b>AUDIO CONFIGURATION - click to change number of channels</b>')
        aud2.add_attr('align', 'left')
        aud2.add_attr('id', 'audio_row')
        aud2.add_style('background-color: #4a4a4a;')
        aud2.add_style('color', '#FFFFFF')
        aud2.add_style('cursor: pointer;')
        aud2.add_style('width: 100%;')
        aud2.add_behavior(my.get_change_channels(code, my.element.get('code')))

        table.add_row()

        audio_table = table.add_cell(audtbl)
        audio_table.add_attr('id', 'audio_table')
        audio_table.add_attr('code', my.element.get('code'))
        audio_table.add_attr('wo_code', code)

        darkrow = table.add_row()
        darkrow.add_attr('id', 'darkrow')
        darkrow.set_style('background-color: #4a4a4a; width: 55%;')
        table.add_cell('<b><font color="#FFFFFF">GENERAL COMMENTS</font></b>')
        table.add_row()
        table.add_cell('<textarea cols="194" rows="10" class="description" id="description">%s</textarea>' % my.element.get('description'))

        printtbl = Table()
        printtbl.add_style('background-color: #528B8B; width: 100%;')
        printtbl.add_row()
        p1 = printtbl.add_cell(' ')
        p1.add_style('width: 40%;')
        p2 = printtbl.add_cell('<u><b>Print This Report</b></u>')
        p2.add_attr('nowrap','nowrap')
        p2.add_style('cursor: pointer;')
        p2.add_behavior(my.get_print_bvr(code, my.element.get('code'), 'element'))
        p3 = printtbl.add_cell(' ')
        p3.add_style('width: 40%;')

        table.add_row()
        table.add_cell(fulllines)

        stbl = Table()
        stbl.add_row()
        s1 = stbl.add_cell(' ')
        s1.add_style('width: 40%;')
        s2 = stbl.add_cell('<input type="button" value="Save"/>')
        s2.add_behavior(my.get_save_bvr(code, my.element.get('code')))
        s3 = stbl.add_cell(' ')
        s3.add_style('width: 40%;')
        if my.element.get('code') not in [None, '']:
            cloner = stbl.add_cell('<input type="button" value="Clone"/>')
            cloner.add_attr('align','center')
            cloner.add_behavior(my.get_clone_report(code, my.element.get('code')))

            s4 = stbl.add_cell('<input type="button" value="Delete This Report"/>')
            s4.add_behavior(my.get_delete_report(code, my.element.get('code')))

        ttbl = Table()
        ttbl.add_style('background-color: #528B8B; width: 100%;')
        ttbl.add_row()

        tt1 = ttbl.add_cell(others)
        tt1.add_attr('width', '100%')
        ttbl.add_row()

        tt2 = ttbl.add_cell(printtbl)
        tt2.add_attr('width', '100%')

        widget.add(ttbl)
        widget.add(table)
        if show_save and 'TITLE' not in original_code:
            widget.add(stbl)

        return widget
