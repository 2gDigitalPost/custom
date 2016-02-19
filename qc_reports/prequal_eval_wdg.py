import datetime

from tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseTableElementWdg

from pyasm.common import Environment
from pyasm.prod.biz import ProdSetting
from pyasm.widget import SelectWdg, TextWdg, CheckboxWdg
from pyasm.web import Table, DivWdg


class PreQualEvalWdg(BaseTableElementWdg):

    def init(my):
        nothing = 'true'
        my.formats = ['Electronic/File', 'DBC', 'D5', 'HDCAM SR', 'NTSC', 'PAL']
        my.frame_rates = ProdSetting.get_seq_by_key('frame_rates')
        my.machines = ['VTR221', 'VTR222', 'VTR223', 'VTR224', 'VTR225', 'VTR231', 'VTR232', 'VTR233', 'VTR234',
                       'VTR235', 'VTR251', 'VTR252', 'VTR253', 'VTR254', 'VTR255', 'VTR261', 'VTR262', 'VTR263',
                       'VTR264', 'VTR265', 'VTR281', 'VTR282', 'VTR283', 'VTR284', 'VTR285', 'FCP01', 'FCP02', 'FCP03',
                       'FCP04', 'FCP05', 'FCP06', 'FCP07', 'FCP08', 'FCP09', 'FCP10', 'FCP11', 'FCP12', 'Amberfin',
                       'Clipster', 'Stradis']
        my.styles = ['Technical', 'Spot QC', 'Mastering']
        my.aspect_ratios = ['16x9 1.33', '16x9 1.33 Pan & Scan', '16x9 1.78 Anamorphic', '16x9 1.78 Full Frame',
                            '16x9 1.85 Letterbox', '16x9 1.85 Matted', '16x9 1.85 Matted Anamorphic', '16x9 2.20',
                            '16x9 2.20 Letterbox', '16x9 2.35 Anamorphic', '16x9 2.35 Letterbox', '16x9 2.40 Letterbox',
                            '16x9 2.55 Letterbox', '4x3 1.33 Full Frame', '4x3 1.78 Letterbox', '4x3 1.85 Letterbox',
                            '4x3 2.35 Letterbox', '4x3 2.40 Letterbox']

        my.standards = ['625', '525', '720', '1080 (4:4:4)', '1080', 'PAL', 'NTSC']

    @staticmethod
    def kill_nothing(val):
        if val == 'NOTHINGXsXNOTHING':
            val = ''
        return val

    def get_save_bvr(my, wo_code, prequal_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          wo_code = '%s';
                          pq_code = '%s';
                          top_els = document.getElementsByClassName('printable_prequal_form_' + wo_code);
                          top_el = null;
                          for(var r = 0; r < top_els.length; r++){
                              if(top_els[r].getAttribute('prequal_code') == pq_code){
                                  top_el = top_els[r];
                              }
                          }
                          big_els = document.getElementsByClassName('big_ol_prequal_wdg_' + wo_code);
                          big_el = null;
                          for(var r = 0; r < big_els.length; r++){
                              if(big_els[r].getAttribute('prequal_code') == pq_code){
                                  big_el = big_els[r];
                              }
                          }
                          prequal_code_old = top_el.getAttribute('prequal_code');
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
                              timestamp = top_el.getElementById('timestamp').value;
                              operator = top_el.getElementById('operator').value;
                              //type = top_el.getElementById('type').value;
                              type = '';
                              bay = top_el.getElementById('bay').value;
                              machine_number = top_el.getElementById('machine_number').value;
                              client_name = top_el.getElementById('client_name').value;
                              format = top_el.getElementById('format').value;
                              aspect_ratio = top_el.getElementById('aspect_ratio').value;
                              title = top_el.getElementById('title').value;
                              standard = top_el.getElementById('standard').value;
                              frame_rate = top_el.getElementById('frame_rate').value;
                              episode = top_el.getElementById('episode').value;
                              //timecode = top_el.getElementById('timecode').value;
                              timecode = '';
                              version = top_el.getElementById('version').value;
                              po_number = top_el.getElementById('po_number').value;
                              //title_type = top_el.getElementById('title_type').value;
                              title_type = '';
                              style = top_el.getElementById('style').value;
                              description_1 = top_el.getElementById('description').value;
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
                              new_data = {'description': description_1, 'timestamp': timestamp, 'login': operator, 'operator': operator, 'type': type, 'bay': bay, 'machine_number': machine_number, 'client_code': work_order.client_code, 'client_name': client_name, 'title': title, 'episode': episode, 'version': version, 'title_type': title_type, 'format': format, 'standard': standard, 'timecode': timecode, 'po_number': po_number, 'style': style, 'title_code': work_order.title_code, 'order_code': work_order.order_code, 'work_order_code': wo_code, 'conclusion': whole_status, 'source_code': source_codes, 'wo_name': work_order.process, 'aspect_ratio': aspect_ratio, 'frame_rate': frame_rate} //I am assuming that it is new...need to fix so it will allow updates
                              new_pq = null;
                              if(prequal_code_old == ''){
                                  new_pq = server.insert('twog/prequal_eval', new_data);
                              }else{
                                  new_pq = server.update(server.build_search_key('twog/prequal_eval', prequal_code_old), new_data);
                              }
                              if(new_pq.code != ''){
                                  lines = big_el.getElementsByClassName('pq_lines');
                                  for(var r = 0; r < lines.length; r++){
                                      if(lines[r].style.display != 'none'){
                                          rowct = lines[r].getAttribute('line');
                                          old_code = lines[r].getAttribute('code');
                                          timecode = big_el.getElementById('timecode-' + rowct).value;
                                          media_type = big_el.getElementById('media_type-' + rowct).value;
                                          description = big_el.getElementById('description-' + rowct).value;
                                          type_code = big_el.getElementById('type_code-' + rowct).value;
                                          scale = big_el.getElementById('scale-' + rowct).value;
                                          in_source = big_el.getElementById('in_source-' + rowct).value;
                                          sector_or_channel = big_el.getElementById('sector_or_channel-' + rowct).value;
                                          prequal_line = {'description': description, 'timestamp': timestamp, 'login': operator, 'prequal_eval_code': new_pq.code, 'order_code': work_order.order_code, 'title_code': work_order.title_code, 'work_order_code': wo_code, 'timecode': timecode, 'media_type': media_type, 'type_code': type_code, 'scale': scale, 'sector_or_channel': sector_or_channel, 'in_source': in_source, 'source_code': source_codes}
                                          if(description != '' && timecode != ''){
                                              if(old_code == ''){
                                                  server.insert('twog/prequal_eval_lines', prequal_line);
                                              }else{
                                                  server.update(server.build_search_key('twog/prequal_eval_lines', old_code), prequal_line);
                                              }
                                          }
                                      }
                                  }
                                  var class_name = 'qc_reports.prequal_eval_wdg.PreQualEvalWdg';
                                  kwargs = {'code': wo_code, 'prequal_code': new_pq.code}
                                  //spt.popup.close(spt.popup.get_popup(bvr.src_el));
                                  //spt.tab.close(bvr.src_el);
                                  //spt.panel.load_popup('PreQual Evaluation for ' + wo_code, class_name, kwargs);
                                  spt.tab.add_new('PreQualEvalWdg_qc_report_for_' + wo_code,'PreQual Evalualtion for ' + wo_code, class_name, kwargs);
                              }
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, prequal_code)}
        return behavior

    def get_print_bvr(my, wo_code, pq_code, type):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        function printExternal(url) {
                            var printWindow = window.open( url, 'Print', 'toolbar=1,location=1,directories=1,status=1,menubar=1,scrollbars=0,resizable=0');
                            printWindow.addEventListener('load', function(){
                                printWindow.print();
                                //printWindow.close();
                            }, true);
                        }
                        try{
                          wo_code = '%s';
                          pq_code = '%s';
                          type = '%s';
                          top_els = document.getElementsByClassName('printable_prequal_form_' + wo_code);
                          top_el = null;
                          for(var r =0; r < top_els.length; r++){
                              if(top_els[r].getAttribute('prequal_code') == pq_code){
                                  top_el = top_els[r];
                              }
                          }
                          var server = TacticServerStub.get();
                          lines = top_el.getElementsByClassName('pq_lines');
                          for(var r = 0; r < lines.length; r++){
                              linect = lines[r].getAttribute('line');
                              tc = top_el.getElementById('timecode-' + linect);
                              if(tc.value == '' || tc.value == null){
                                  lines[r].style.display = 'none';
                              }
                          }
                          description_el = top_el.getElementById('description');
                          doffset = description_el.offsetWidth;
                          dwidth = description_el.style.width;
                          dlength = description_el.style.length;
                          dcols = description_el.style.cols;
                          dcols2 = description_el.getAttribute('cols');
                          dinner = description_el.innerHTML;
                          description_el.setAttribute('cols',dcols2/1.5);
                          description_el.innerHTML = dinner;
                          description_el = top_el.getElementById('description');
                          dclient = description_el.clientWidth;
                          darkcell = top_el.getElementById('darkcell');
                          darkcell.setAttribute('width',dclient);
                          sels = top_el.getElementsByClassName('select_cell');
                          for(var r = 0; r < sels.length; r++){
                              select_el = sels[r].getElementsByTagName('select')[0];
                              offset_width = select_el.offsetWidth;
                              value = select_el.value;
                              sels[r].innerHTML = '<input type="text" value="' + value + '" style="width: ' + offset_width + ';"/>';
                          }
                          top_els = document.getElementsByClassName('printable_prequal_form_' + wo_code);
                          top_el = null;
                          for(var r =0; r < top_els.length; r++){
                              if(top_els[r].getAttribute('prequal_code') == pq_code){
                                  top_el = top_els[r];
                              }
                          }
                          new_html = top_el.innerHTML;

                          thing = server.execute_cmd('qc_reports.PrintQCReportWdg', {'html': '<table>' + new_html + '</table>','preppend_file_name': wo_code, 'type': type});
                          var url = 'http://tactic01/qc_reports/work_orders/' + wo_code + '_prequal.html';
                          printExternal(url);
                          if(pq_code != '' && pq_code != null){
                              //close, then reload page
                              var class_name = 'qc_reports.prequal_eval_wdg.PreQualEvalWdg';
                              kwargs = {'code': wo_code, 'prequal_code': pq_code}
                              //if(confirm("Reload Report?")){
                                  //spt.popup.close(spt.popup.get_popup(bvr.src_el));
                                  //spt.panel.load_popup('PreQual Evaluation for ' + wo_code, class_name, kwargs);
                                  spt.tab.add_new('PreQualEvalWdg_qc_report_for_' + wo_code,'PreQual Evalualtion for ' + wo_code, class_name, kwargs);
                              //}
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, pq_code, type)}
        return behavior

    def get_click_row(my, wo_code, pq_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          var work_order_code = '%s';
                          var prequal_code = '%s';
                          var class_name = 'qc_reports.prequal_eval_wdg.PreQualEvalWdg';
                          kwargs = {'code': work_order_code, 'prequal_code': prequal_code}
                          //spt.popup.close(spt.popup.get_popup(bvr.src_el));
                          //spt.panel.load_popup('PreQual Evaluation for ' + work_order_code, class_name, kwargs);
                          spt.tab.add_new('PreQualEvalWdg_qc_report_for_' + work_order_code,'PreQual Evalualtion for ' + work_order_code, class_name, kwargs);
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, pq_code)}
        return behavior

    def get_clone_report(my, wo_code, pq_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          var work_order_code = '%s';
                          var report_code = '%s';
                          var class_name = 'qc_reports.QCReportClonerWdg';
                          kwargs = {'wo_code': work_order_code, 'report_code': report_code, 'type': 'prequal'}
                          //spt.popup.close(spt.popup.get_popup(bvr.src_el));
                          spt.app_busy.show("Collecting related qc work orders...");
                          spt.panel.load_popup('Clone Report To ... ', class_name, kwargs);
                          spt.app_busy.hide();
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, pq_code)}
        return behavior

    def get_delete_report(my, wo_code, pq_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          var work_order_code = '%s';
                          var prequal_code = '%s';
                          if(confirm("Are you sure you want to delete this report?")){
                              if(confirm("Checking again. You really want to delete this report?")){
                                  var server = TacticServerStub.get();
                                  server.retire_sobject(server.build_search_key('twog/prequal_eval', prequal_code));
                                  var class_name = 'qc_reports.prequal_eval_wdg.PreQualEvalWdg';
                                  kwargs = {'code': work_order_code}
                                  //spt.popup.close(spt.popup.get_popup(bvr.src_el));
                                  //spt.panel.load_popup('PreQual Evaluation for ' + work_order_code, class_name, kwargs);
                                  spt.tab.add_new('PreQualEvalWdg_qc_report_for_' + work_order_code,'PreQual Evalualtion for ' + work_order_code, class_name, kwargs);
                              }
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, pq_code)}
        return behavior

    def get_display(my):
        login = Environment.get_login()
        this_user = login.get_login()
        groups = Environment.get_group_names()
        show_save = False
        for g in groups:
            if 'qc' in g or 'edeliveries' in g:
                show_save = True
        if this_user == 'admin':
            show_save = True
        this_timestamp = str(datetime.datetime.now()).split('.')[0]
        code = my.kwargs.get('code')
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
        prequal_code = ''
        prequal = {
            'code': '',
            'description': '',
            'timestamp': this_timestamp,
            'login': this_user,
            'operator': this_user,
            'type': '',
            'bay': '',
            'machine_number': '',
            'client_code': my.kill_nothing(title.get('client_code')),
            'client_name': my.kill_nothing(title.get('client_name')),
            'title': my.kill_nothing(title.get('title')),
            'episode': my.kill_nothing(title.get('episode')),
            'version': '',
            'title_type': '',
            'timecode': '',
            'po_number': my.kill_nothing(title.get('po_number')),
            'style': '',
            'title_code': work_order.get('title_code'),
            'order_code': work_order.get('order_code'),
            'work_order_code': code,
            'conclusion': '',
            'source_code': '',
            'standard': my.kill_nothing(title.get('deliverable_standard')),
            'aspect_ratio': my.kill_nothing(title.get('deliverable_aspect_ratio')),
            'frame_rate': my.kill_nothing(title.get('deliverable_frame_rate')),
            'format': my.kill_nothing(title.get('deliverable_format'))
        }
        prequal_lines = [
            {
                'code': '',
                'description': '',
                'timestamp': this_timestamp,
                's_status': '',
                'keywords': '',
                'login': this_user,
                'id': '',
                'name': '',
                'prequal_eval_code': '',
                'order_code': work_order.get('order_code'),
                'title_code': work_order.get('title_code'),
                'work_order_code': code,
                'timecode': '',
                'media_type': '',
                'type_code': '',
                'scale': '',
                'sector_or_channel': '',
                'in_source': '',
                'source_code': ''
            }
        ]
        if 'prequal_code' in my.kwargs.keys():
            prequal_code = str(my.kwargs.get('prequal_code'))
            prequal = server.eval("@SOBJECT(twog/prequal_eval['code','%s'])" % prequal_code)[0]
            prequal_lines = server.eval("@SOBJECT(twog/prequal_eval_lines['prequal_eval_code','%s'])" % prequal_code)

        wo_pevals = server.eval("@SOBJECT(twog/prequal_eval['work_order_code','%s']['code','!=','%s'])" % (code, prequal_code))
        title_pevals = server.eval("@SOBJECT(twog/prequal_eval['title_code','%s']['work_order_code','!=','%s']['code','!=','%s'])" % (work_order.get('title_code'), work_order.get('code'), prequal_code))
        others = Table()
        others.add_style('background-color: #528B8B; width: 100%;')
        cols = ['#537072', '#518A1A']
        colsct = 0
        if len(title_pevals) > 0:
            trrr = others.add_row()
            trrr.add_style('background-color: #50EDA1;')
            others.add_cell('<b>Other PreQual Evals for Title</b>')
            for t in title_pevals:
                click_row = others.add_row()
                click_row.add_attr('prequal_code',t.get('code'))
                click_row.add_attr('work_order_code',t.get('work_order_code'))
                click_row.set_style('cursor: pointer; background-color: %s;' % cols[colsct%2])
                click_row.add_behavior(my.get_click_row(t.get('work_order_code'), t.get('code')))
                others.add_cell('<b>WO:</b> %s, <b>CODE:</b> %s' % (t.get('wo_name'), t.get('work_order_code')))
                others.add_cell('<b>OPERATOR:</b> %s' % t.get('operator'))
                others.add_cell('<b>STYLE:</b> %s' % t.get('style'))
                others.add_cell('<b>CONCLUSION:</b> %s' % t.get('conclusion'))
                others.add_cell('<b>DATETIME:</b> %s' % t.get('timestamp'))
                colsct += 1
        if len(wo_pevals) > 0:
            wrrr = others.add_row()
            wrrr.add_style('background-color: #50EDA1;')
            others.add_cell('<b>Other PreQual Evals for Work Order</b>')
            for w in wo_pevals:
                click_row = others.add_row()
                click_row.add_attr('prequal_code',w.get('code'))
                click_row.add_attr('work_order_code',w.get('work_order_code'))
                click_row.set_style('cursor: pointer; background-color: %s;' % cols[colsct%2])
                click_row.add_behavior(my.get_click_row(w.get('work_order_code'), w.get('code')))
                others.add_cell('<b>WO:</b> %s, <b>CODE:</b> %s' % (w.get('wo_name'), w.get('work_order_code')))
                others.add_cell('<b>OPERATOR:</b> %s' % w.get('operator'))
                others.add_cell('<b>STYLE:</b> %s' % w.get('style'))
                others.add_cell('<b>CONCLUSION:</b> %s' % w.get('conclusion'))
                others.add_cell('<b>DATETIME:</b> %s' % w.get('timestamp'))
                colsct += 1

        widget.add_attr('class', 'big_ol_prequal_wdg_%s' % code)
        widget.add_attr('prequal_code',prequal.get('code'))
        table = Table()
        table.add_attr('class', 'printable_prequal_form_%s' % code)
        table.add_attr('prequal_code',prequal.get('code'))
        table.add_attr('work_order_code',prequal.get('work_order_code'))
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
        acr_s = ['APPROVED', 'CONDITION', 'REJECTED']
        acr = Table()
        for mark in acr_s:
            acr.add_row()
            acr1 = CheckboxWdg('marked_%s' % mark)

            if mark in prequal.get('conclusion'):
                acr1.set_value(True)
            else:
                acr1.set_value(False)
            acr.add_cell(acr1)
            acr.add_cell('<b>%s</b>' % mark)
        rtbl = Table()
        rtbl.add_row()
        big = rtbl.add_cell("<b>PREQUAL EVALUATION</b>")
        big.add_attr('nowrap', 'nowrap')
        big.add_attr('align', 'center')
        big.add_attr('valign', 'center')
        big.add_style('font-size: 40px;')
        rtbl.add_cell(acr)
        toptbl = Table()
        toptbl.add_row()
        toptbl.add_cell(img_tbl)
        toptbl.add_cell(rtbl)
        bay_sel = SelectWdg('bay_select')
        bay_sel.add_attr('id','bay')
        bay_sel.add_style('width: 135px;')
        bay_sel.append_option('--Select--', '')
        for i in range(1, 13):
            bay_sel.append_option('Bay %s' % i, 'Bay %s' % i)
        if prequal.get('bay') not in [None,'']:
            bay_sel.set_value(prequal.get('bay'))

        style_sel = SelectWdg('style_select')
        style_sel.add_attr('id', 'style')
        style_sel.add_style('width: 135px;')
        style_sel.append_option('--Select--', '')
        for s in my.styles:
            style_sel.append_option(s,s)
        if prequal.get('style') not in [None, '']:
            style_sel.set_value(prequal.get('style'))

        machine_sel = SelectWdg('machine_select')
        machine_sel.add_attr('id', 'machine_number')
        machine_sel.add_style('width: 135px;')
        machine_sel.append_option('--Select--', '')
        for m in my.machines:
            machine_sel.append_option(m,m)
        if prequal.get('machine_number') not in [None,'']:
            machine_sel.set_value(prequal.get('machine_number'))

        format_sel = SelectWdg('format_select')
        format_sel.add_attr('id', 'format')
        format_sel.add_style('width: 153px;')
        format_sel.append_option('--Select--', '')
        for f in my.formats:
            format_sel.append_option(f, f)
        if prequal.get('format') not in [None,'']:
            format_sel.set_value(prequal.get('format'))

        ar_select = SelectWdg('aspect_ratio_select')
        ar_select.add_attr('id', 'aspect_ratio')
        ar_select.add_style('width: 153px;')
        ar_select.append_option('--Select--', '')
        for a in my.aspect_ratios:
            ar_select.append_option(a,a)
        if prequal.get('aspect_ratio') not in [None,'']:
            ar_select.set_value(prequal.get('aspect_ratio'))

        frame_rate_sel = SelectWdg('frame_rate_select')
        frame_rate_sel.add_attr('id', 'frame_rate')
        frame_rate_sel.add_style('width: 153px;')
        frame_rate_sel.append_option('--Select--','')
        for f in my.frame_rates:
            frame_rate_sel.append_option(f,f)
        if prequal.get('frame_rate') not in [None,'']:
            frame_rate_sel.set_value(prequal.get('frame_rate'))

        standard_sel = SelectWdg('standard_select')
        standard_sel.add_attr('id','standard')
        standard_sel.add_style('width: 153px;')
        standard_sel.append_option('--Select--','')
        for s in my.standards:
            standard_sel.append_option(s,s)
        if prequal.get('standard') not in [None,'']:
            standard_sel.set_value(prequal.get('standard'))

        majtbl = Table()
        majtbl.add_attr('class','majtbl')
        majtbl.add_row()
        majtbl.add_cell('DATE')
        majtbl.add_cell('OPERATOR')
        majtbl.add_cell('STYLE')
        majtbl.add_cell('BAY')
        majtbl.add_cell('MACHINE #')
        majtbl.add_row()
        majtbl.add_cell('<input type="text" id="timestamp" value="%s"/>' % prequal.get('timestamp'))
        if prequal.get('operator') not in [None,'']:
            that_login = server.eval("@SOBJECT(sthpw/login['login','%s'])" % prequal.get('operator'))
            if that_login:
                that_login = that_login[0]
                that_login_name = '%s %s' % (that_login.get('first_name'), that_login.get('last_name'))
                prequal['operator'] = that_login_name
        majtbl.add_cell('<input type="text" id="operator" value="%s"/>' % prequal.get('operator'))
        mm1 = majtbl.add_cell(style_sel)
        mm1.add_attr('class','select_cell')
        mm2 = majtbl.add_cell(bay_sel)
        mm2.add_attr('class','select_cell')
        mm3 = majtbl.add_cell(machine_sel)
        mm3.add_attr('class','select_cell')
        tittbl = Table()
        tittbl.add_row()
        tittbl.add_cell('CLIENT:')
        tittbl.add_cell('<input type="text" id="client_name" value="%s" style="width: 400px;"/>' % prequal.get('client_name'))
        tittbl.add_cell('&nbsp;&nbsp;&nbsp;FORMAT:')
        mm4 = tittbl.add_cell(format_sel)
        mm4.add_attr('class','select_cell')
        tittbl.add_row()
        tittbl.add_cell('TITLE:')
        tittbl.add_cell('<input type="text" id="title" value="%s" style="width: 400px;"/>' % prequal.get('title'))
        tittbl.add_cell('&nbsp;&nbsp;&nbsp;STANDARD:')
        mm5 = tittbl.add_cell(standard_sel)
        mm5.add_attr('class','select_cell')
        tittbl.add_row()
        tittbl.add_cell('EPISODE:')
        tittbl.add_cell('<input type="text" id="episode" value="%s" style="width: 400px;"/>' % prequal.get('episode'))
        ffr = tittbl.add_cell('&nbsp;&nbsp;&nbsp;FRAME RATE:')
        ffr.add_attr('nowrap','nowrap')
        mm6 = tittbl.add_cell(frame_rate_sel)
        mm6.add_attr('class','select_cell')
        tittbl.add_row()
        tittbl.add_cell('VERSION:')
        tittbl.add_cell('<input type="text" id="version" value="%s" style="width: 400px;"/>' % prequal.get('version'))
        tittbl.add_cell('&nbsp;&nbsp;&nbsp;PO #:')
        tittbl.add_cell('<input type="text" id="po_number" value="%s" style="width: 151px;"/>' % prequal.get('po_number'))
        tittbl.add_row()
        #tittbl.add_cell('TYPE:')
        #tittbl.add_cell('<input type="text" id="title_type" value="%s" style="width: 400px;"/>' % prequal.get('title_type'))
        tittbl.add_cell('')
        tittbl.add_cell('')
        frr = tittbl.add_cell('&nbsp;&nbsp;&nbsp;ASPECT RATIO:')
        frr.add_attr('nowrap','nowrap')
        mm7 = tittbl.add_cell(ar_select)
        mm7.add_attr('class','select_cell')

        ktbl = Table()
        ktbl.add_row()
        k1 = ktbl.add_cell('<i>Code Definitions: F=Film V=Video T=Telecine A=Audio</i>')
        k1.add_attr('align','left')
        k = ktbl.add_cell('&nbsp;&nbsp;&nbsp;')
        k.add_attr('align','right')
        k2 = ktbl.add_cell('<i>Severity Scale: 1=Minor 2=Marginal 3=Severe</i>')
        k2.add_attr('align','right')

        linestbl = PreQualEvalLinesWdg(code=prequal.get('code'),wo_code=code)

        fulllines = Table()
        fulllines.add_attr('border','2')
        fulllines.add_row()
        fulllines.add_cell(ktbl)
        fulllines.add_row()
        fulllines.add_cell(linestbl)



        table.add_row()
        table.add_cell(toptbl)
        table.add_row()
        table.add_cell(majtbl)
        table.add_row()
        table.add_cell(tittbl)

        darktbl = Table()
        darktbl.add_attr('id','darktbl')
        darktbl.add_style('padding-right: 10px;')
        #darktbl.add_style('width: 100%s;' % '%')
        darkrow = darktbl.add_row()
        darkrow.add_attr('id','darkrow')
        dkcell = darktbl.add_cell('<b><font color="#FFFFFF">GENERAL COMMENTS</font></b>')
        dkcell.add_attr('id','darkcell')
        dkcell.add_attr('width','700px')
        dkcell.set_style('background-color: #040404;')
        dk2 = darktbl.add_cell(' ')
        dk2.add_attr('width','20px')
        darktbl.add_row()
        darktbl.add_cell('''<textarea cols="160" rows="10" class="description" id="description" style="font-family: 'Arial, Helvetica, sans-serif'; font-size: 14px;">%s</textarea>''' % (prequal.get('description')))
        #darktbl.add_cell('''<textarea cols="160" rows="10" class="description" id="description">%s</textarea>''' % (prequal.get('description')))
        darktbl.add_cell(' ')

        table.add_row()
        table.add_cell(darktbl)

        printtbl = Table()
        printtbl.add_style('background-color: #528B8B; width: 100%s;' % '%')
        printtbl.add_row()
        p1 = printtbl.add_cell(' ')
        p1.add_style('width: 40%s;' % '%')
        p2 = printtbl.add_cell('<u><b>Print This Report</b></u>')
        p2.add_attr('nowrap','nowrap')
        p2.add_style('cursor: pointer;')
        p2.add_behavior(my.get_print_bvr(code, prequal.get('code'), 'prequal'))
        p3 = printtbl.add_cell(' ')
        p3.add_style('width: 40%s;' % '%')

        table.add_row()
        table.add_cell(fulllines)


        stbl = Table()
        stbl.add_row()
        s1 = stbl.add_cell(' ')
        s1.add_style('width: 40%s;' % '%')
        s2 = stbl.add_cell('<input type="button" value="Save"/>')
        s2.add_behavior(my.get_save_bvr(code, prequal_code))
        s3 = stbl.add_cell(' ')
        s3.add_style('width: 40%s;' % '%')
        if prequal.get('code') not in [None,'']:
            s33 = stbl.add_cell('<input type="button" value="Clone This Report"/>')
            s33.add_behavior(my.get_clone_report(code, prequal.get('code')))
            s4 = stbl.add_cell('<input type="button" value="Delete This Report"/>')
            s4.add_behavior(my.get_delete_report(code, prequal.get('code')))
        ttbl = Table()
        ttbl.add_style('background-color: #528B8B; width: 100%s;' % '%')
        ttbl.add_row()
        tt1 = ttbl.add_cell(others)
        tt1.add_attr('width','100%s' % '%')
        ttbl.add_row()
        tt2 = ttbl.add_cell(printtbl)
        tt2.add_attr('width','100%s' % '%')
        widget.add(ttbl)
        widget.add(table)
        widget.add_style("font-family: Arial, Helvetica, sans-serif;")
        widget.add_style("font-size: 14px;")
        if show_save and 'TITLE' not in original_code:
            widget.add(stbl)

        return widget


class PreQualEvalLinesWdg(BaseTableElementWdg):
    def init(my):
        nothing = 'true'

    def get_kill_bvr(my, rowct, wo_code, pl_code, pq_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                            var rowct = Number('%s');
                            var wo_code = '%s';
                            var pl_code = '%s';
                            var pq_code = '%s';
                            if(confirm("Do you really want to delete this evaluation line?")){
                                server = TacticServerStub.get();
                                server.retire_sobject(server.build_search_key('twog/prequal_eval_lines',pl_code));
                                top_els = document.getElementsByClassName('printable_prequal_form_' + wo_code);
                                top_el = null;
                                for(var r = 0; r < top_els.length; r++){
                                    if(top_els[r].getAttribute('prequal_code') == pq_code){
                                        top_el = top_els[r];
                                    }
                                }
                                linestbl = top_el.getElementsByClassName('linestbl')[0];
                                pq_lines = linestbl.getElementsByClassName('pq_lines');
                                pqer = null;
                                for(var r = 0; r < pq_lines.length; r++){
                                    if(pq_lines[r].getAttribute('line') == rowct){
                                        pq_lines[r].innerHTML = '';
                                        pq_lines[r].style.display = 'none';
                                    }
                                }
                                send_data = {'rowct': rowct, 'wo_code': wo_code, 'code': pl_code};
                            }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (rowct, wo_code, pl_code, pq_code)}
        return behavior

    def get_add_line(my, rowct, wo_code, prequal_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                            var rowct = Number('%s');
                            var wo_code = '%s';
                            var pq_code = '%s';
                            top_els = document.getElementsByClassName('printable_prequal_form_' + wo_code);
                            top_el = null;
                            for(var r = 0; r < top_els.length; r++){
                                if(top_els[r].getAttribute('prequal_code') == pq_code){
                                    top_el = top_els[r];
                                }
                            }
                            linestbl = top_el.getElementsByClassName('linestbl');
                            lastlinestbl = linestbl[linestbl.length - 1];
                            addportions = top_el.getElementsByClassName('new_pq_line');
                            addportion = addportions[addportions.length - 1];
                            addportion.setAttribute('class','pq_lines');
                            addportion.setAttribute('line',Number(rowct) + 1);
                            addportion.setAttribute('code','');
                            send_data = {'rowct': rowct + 1, 'wo_code': wo_code};
                            spt.api.load_panel(addportion, 'qc_reports.PreQualEvalLinesWdg', send_data);
                            newrow = lastlinestbl.insertRow(-1);
                            newrow.setAttribute('class','new_pq_line');
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (rowct, wo_code, prequal_code)}
        return behavior

    def get_select_fillin(my, wo_code, rowct, prequal_code):
        behavior = {'css_class': 'clickme', 'type': 'change', 'cbjs_action': '''
                try{
                   wo_code = '%s';
                   rowct = '%s';
                   pq_code = '%s';
                   top_els = document.getElementsByClassName('printable_prequal_form_' + wo_code);
                   top_el = null;
                   for(var r = 0; r < top_els.length; r++){
                       if(top_els[r].getAttribute('prequal_code') == pq_code){
                           top_el = top_els[r];
                       }
                   }
                   this_sel = top_el.getElementById('description-' + rowct);
                   val = this_sel.value;
                   if(val.indexOf('( )') != -1){
                       deets = prompt("Please enter more detail for: " + val);
                       newval = val.replace('( )','(' + deets + ')');
                       inner = this_sel.innerHTML;
                       newinner = inner + '<option value="' + newval + '" selected="selected">' + newval + '</option>';
                       this_sel.innerHTML = newinner;
                   }else if(val.indexOf('...') != -1){
                       deets = prompt("Please enter the new description.");
                       newval = deets;
                       if(val.indexOf('V -') != -1){
                           newval = 'V - ' + newval;
                       }else{
                           newval = 'A - ' + newval;
                       }
                       inner = this_sel.innerHTML;
                       newinner = inner + '<option value="' + newval + '" selected="selected">' + newval + '</option>';
                       this_sel.innerHTML = newinner;
                       //bottom lines would insert it into qc_report_vars to be remembered for future use in the pulldowns
                       //server = TacticServerStub.get();
                       //server.insert('twog/qc_report_vars', {'type': 'prequal', 'description': newval});
                   }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, rowct, prequal_code)}
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

    def txtbox(my, name, val, width='200px', js='no'):
        txt = TextWdg(name)
        txt.add_attr('id',name)
        txt.add_style('width: %s;' % width)
        txt.set_value(val)
        if js in ['Yes','yes']:
            txt.add_behavior(my.get_add_dots())
        return txt

    def get_display(my):
        from tactic_client_lib import TacticServerStub
        from pyasm.common import Environment
        login = Environment.get_login()
        this_user = login.get_login()
        code = ''
        prequal_lines = None
        rowct = 0
        server = TacticServerStub.get()
        descriptions = server.eval("@SOBJECT(twog/qc_report_vars['type','prequal']['@ORDER_BY','description'])")
        type_codes = ['F','A','T','V']
        scales = ['1','2','3','FYI']
        insrc = ['No','Yes']
        wo_code = str(my.kwargs.get('wo_code'))
        if 'code' in my.kwargs.keys():
            code = my.kwargs.get('code')
            prequal_lines = server.eval("@SOBJECT(twog/prequal_eval_lines['prequal_eval_code','%s']['@ORDER_BY','timecode'])" % code)
        elif 'rowct' in my.kwargs.keys():
            rowct = int(my.kwargs.get('rowct'))
        linestbl = Table()
        linestbl.add_attr('class','linestbl')
        longest_len = 0
        for d in descriptions:
            desc = d.get('description')
            lendesc = len(desc)
            if lendesc > longest_len:
                longest_len = lendesc
        if code not in [None,'']:
            for pl in prequal_lines:
                if len(pl.get('description')) > longest_len:
                    longest_len = len(pl.get('description'))
        if code not in [None,'']:
            linestbl.add_row()
            linestbl.add_cell("Timecode")
            linestbl.add_cell("F")
            linestbl.add_cell("Description")
            linestbl.add_cell("Code")
            linestbl.add_cell("Scale")
            linestbl.add_cell("Sector/Ch")
            linestbl.add_cell("In Source")
            plus_butt = linestbl.add_cell(" ")
            #plus_butt.add_style('cursor: pointer;')
            #plus_butt.add_behavior(my.get_add_line())
            for pl in prequal_lines:
                seen_descs = []
                if pl.get('code') != '':
                    row = linestbl.add_row()
                    row.add_attr('line',rowct)
                    row.add_attr('code',pl.get('code'))
                    row.add_attr('class','pq_lines')
                    #linestbl.add_cell('<input type="text" id="timecode-%s" name="timecode" value="%s" style="width: 75px;"/>' % (rowct, pl.get('timecode')))
                    linestbl.add_cell(my.txtbox('timecode-%s' % rowct, pl.get('timecode'),width='75px',js='yes'))
                    linestbl.add_cell('<input type="text" id="media_type-%s" name="media_type" value="%s" style="width: 20px;"/>' % (rowct, pl.get('media_type')))
                    desc_select = SelectWdg('description')
                    desc_select.append_option('--Select--','')
                    for d in descriptions:
                        desc = d.get('description')
                        desc_select.append_option(desc,desc)
                        seen_descs.append(desc)
                    desc_select.add_style('width: %spx;' % int(float(longest_len * 7.5)))
                    if pl.get('description') not in seen_descs:
                        desc_select.append_option(pl.get('description'), pl.get('description'))
                    desc_select.set_value(pl.get('description'))
                    desc_select.add_attr('id','description-%s' % rowct)
                    desc_select.add_behavior(my.get_select_fillin(wo_code, rowct, code))
                    mm1 = linestbl.add_cell(desc_select)
                    mm1.add_attr('class','select_cell')
                    type_code_select = SelectWdg('type_code')
                    type_code_select.append_option('-','')
                    for tc in type_codes:
                        type_code_select.append_option(tc,tc)
                    type_code_select.set_value(pl.get('type_code'))
                    type_code_select.add_attr('id','type_code-%s' % rowct)
                    mm2 = linestbl.add_cell(type_code_select)
                    mm2.add_attr('class','select_cell')
                    scale_select = SelectWdg('scale')
                    scale_select.append_option('-','')
                    for s in scales:
                        scale_select.append_option(s,s)
                    scale_select.set_value(pl.get('scale'))
                    scale_select.add_attr('id','scale-%s' % rowct)
                    mm3 = linestbl.add_cell(scale_select)
                    mm3.add_attr('class','select_cell')
                    linestbl.add_cell('<input type="text" id="sector_or_channel-%s" value="%s" style="width: 75px;"/>' % (rowct, pl.get('sector_or_channel')))
                    insrc_select = SelectWdg('in_source')
                    insrc_select.append_option('-','')
                    for i in insrc:
                        insrc_select.append_option(i,i)
                    insrc_select.set_value(pl.get('in_source'))
                    insrc_select.add_attr('id','in_source-%s' % rowct)
                    mm4 = linestbl.add_cell(insrc_select)
                    mm4.add_attr('class','select_cell')
                    killer = linestbl.add_cell('<b>X</b>')#This must delete the entry
                    killer.add_style('cursor: pointer;')
                    killer.add_behavior(my.get_kill_bvr(rowct, wo_code, pl.get('code'), code))
                    rowct = rowct + 1

        erow = linestbl.add_row()
        erow.add_attr('line',rowct)
        erow.add_attr('code','')
        erow.add_attr('class','pq_lines')
        #linestbl.add_cell('<input type="text" id="timecode-%s" name="timecode" value="" style="width: 75px;"/>' % (rowct))
        linestbl.add_cell(my.txtbox('timecode-%s' % rowct, '',width='75px',js='yes'))
        linestbl.add_cell('<input type="text" id="media_type-%s" name="media_type" value="" style="width: 20px;"/>' % (rowct))
        desc_select = SelectWdg('description')
        desc_select.append_option('--Select--','')
        desc_select.add_style('width: %spx;' % (longest_len * 7.5))
        for d in descriptions:
            desc = d.get('description')
            desc_select.append_option(desc,desc)
        desc_select.set_value('')
        desc_select.add_attr('id','description-%s' % rowct)
        desc_select.add_behavior(my.get_select_fillin(wo_code, rowct, code))
        linestbl.add_cell(desc_select)
        type_code_select = SelectWdg('type_code')
        type_code_select.append_option('-','')
        for tc in type_codes:
            type_code_select.append_option(tc,tc)
        type_code_select.add_attr('id','type_code-%s' % rowct)
        linestbl.add_cell(type_code_select)
        scale_select = SelectWdg('scale')
        scale_select.append_option('-','')
        for s in scales:
            scale_select.append_option(s,s)
        scale_select.add_attr('id','scale-%s' % rowct)
        linestbl.add_cell(scale_select)
        linestbl.add_cell('<input type="text" id="sector_or_channel-%s" value="" style="width: 75px;"/>' % rowct)
        insrc_select = SelectWdg('in_source')
        insrc_select.append_option('-','')
        for i in insrc:
            insrc_select.append_option(i,i)
        insrc_select.add_attr('id','in_source-%s' % rowct)
        linestbl.add_cell(insrc_select)
        addnew = linestbl.add_cell('<b>+</b>')#This must add new entry
        addnew.add_style('cursor: pointer;')
        addnew.add_behavior(my.get_add_line(rowct,wo_code,code))
        erow2 = linestbl.add_row()
        erow2.add_attr('class','new_pq_line')
        return linestbl
