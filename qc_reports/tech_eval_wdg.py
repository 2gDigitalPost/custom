import datetime

from tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseTableElementWdg
from tactic.ui.widget import CalendarInputWdg

from pyasm.common import Environment
from pyasm.web import Table, DivWdg


class TechEvalWdg(BaseTableElementWdg):

    def init(my):
        nothing = 'true'

    def get_stub(my):
        my.server = TacticServerStub.get()

    def get_save_bvr(my, wo_code, tech_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          wo_code = '%s';
                          tech_code = '%s';
                          top_els = document.getElementsByClassName('printable_tech_form_' + wo_code);
                          top_el = null;
                          for(var r = 0; r < top_els.length; r++){
                              if(top_els[r].getAttribute('tech_code') == tech_code){
                                  top_el = top_els[r];
                              }
                          }
                          big_els = document.getElementsByClassName('big_ol_tech_wdg_' + wo_code);
                          big_el = null;
                          for(var r = 0; r < big_els.length; r++){
                              if(big_els[r].getAttribute('tech_code') == tech_code){
                                  big_el = big_els[r];
                              }
                          }
                          tech_code_old = top_el.getAttribute('tech_code');
                          var server = TacticServerStub.get();
                          work_order = server.eval("@SOBJECT(twog/work_order['code','" + wo_code + "'])")[0];
                          title = server.eval("@SOBJECT(twog/title['code','" + work_order.title_code + "'])")[0];
                          md_rs = top_el.getElementsByClassName('tech_r_var');
                          new_data = {'work_order_code': wo_code, 'title_code': title.code, 'order_code': title.order_code, 'client_code': work_order.client_code, 'client_name': work_order.client_name, 'wo_name': work_order.process};
                          for(var r = 0; r < md_rs.length; r++){
                              md_id = md_rs[r].getAttribute('id');
                              new_data[md_id] = md_rs[r].value;
                          }
                          date_els = top_el.getElementsByClassName('spt_calendar_input');
                          for(var w = 0; w < date_els.length; w++){
                              if(date_els[w].name == 'date'){
                                  new_data['date'] = date_els[w].value;
                              }
                          }
                          new_tech_eval = null;
                          if(tech_code_old == ''){
                              new_tech_eval = server.insert('twog/tech_eval', new_data);
                          }else{
                              new_tech_eval = server.update(server.build_search_key('twog/tech_eval', tech_code_old), new_data);
                          }
                          var class_name = 'qc_evals.qc_evals.TechEvalWdg';
                          kwargs = {'code': wo_code, 'tech_code': new_tech_eval.code}
                          //spt.popup.close(spt.popup.get_popup(bvr.src_el));
                          //spt.panel.load_popup('Tech Eval for ' + wo_code, class_name, kwargs);
                          spt.tab.add_new('TechEvalWdg_qc_report_for_' + wo_code,'Tech Eval for ' + wo_code, class_name, kwargs);
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, tech_code)}
        return behavior

    def get_print_bvr(my, wo_code, tech_code, type):
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
                          tech_code = '%s';
                          type = '%s';
                          top_els = document.getElementsByClassName('printable_tech_form_' + wo_code);
                          top_el = null;
                          for(var r = 0; r < top_els.length; r++){
                              if(top_els[r].getAttribute('tech_code') == tech_code){
                                  top_el = top_els[r];
                              }
                          }
                          var server = TacticServerStub.get();
                          sels = top_el.getElementsByClassName('select_cell');
                          for(var r = 0; r < sels.length; r++){
                              select_el = sels[r].getElementsByTagName('select')[0];
                              offset_width = select_el.offsetWidth;
                              value = select_el.value;
                              sels[r].innerHTML = '<input type="text" value="' + value + '" style="width: ' + offset_width + ';"/>';
                          }
                          top_el = document.getElementsByClassName('printable_tech_form_' + wo_code)[0];
                          new_html = top_el.innerHTML;
                          thing = server.execute_cmd('qc_evals.qc_evals.PrintQCReportWdg', {'html': '<table style="font-family: Calibri, sans-serif;">' + new_html + '</table>','preppend_file_name': wo_code, 'type': type});
                          var url = 'http://tactic01/qc_evals/work_orders/' + wo_code + '_tech.html';
                          printExternal(url);
                          if(tech_code != '' && tech_code != null){
                              //close, then reload page
                              var class_name = 'qc_evals.qc_evals.TechEvalWdg';
                              kwargs = {'code': wo_code, 'tech_code': tech_code}
                              //if(confirm("Reload Report?")){
                                  //spt.popup.close(spt.popup.get_popup(bvr.src_el));
                                  //spt.panel.load_popup('Tech Eval for ' + wo_code, class_name, kwargs);
                                  spt.tab.add_new('TechEvalWdg_qc_report_for_' + wo_code,'Tech Eval for ' + wo_code, class_name, kwargs);
                              //}
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, tech_code, type)}
        return behavior

    def get_delete_eval(my, wo_code, el_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          var work_order_code = '%s';
                          var tech_code = '%s';
                          if(confirm("Are you sure you want to delete this eval?")){
                              if(confirm("Checking again. You really want to delete this eval?")){
                                  var server = TacticServerStub.get();
                                  server.retire_sobject(server.build_search_key('twog/tech_eval', tech_code));
                                  var class_name = 'qc_evals.qc_evals.TechEvalWdg';
                                  kwargs = {'code': work_order_code}
                                  //spt.popup.close(spt.popup.get_popup(bvr.src_el));
                                  //spt.panel.load_popup('Tech Eval for ' + work_order_code, class_name, kwargs);
                                  spt.tab.add_new('TechEvalWdg_qc_report_for_' + work_order_code,'Tech Eval for ' + work_order_code, class_name, kwargs);
                              }
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, el_code)}
        return behavior

    def get_click_row(my, wo_code, el_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          var work_order_code = '%s';
                          var tech_code = '%s';
                          var class_name = 'qc_evals.qc_evals.TechEvalWdg';
                          kwargs = {'code': work_order_code, 'tech_code': tech_code}
                          //spt.popup.close(spt.popup.get_popup(bvr.src_el));
                          //spt.panel.load_popup('Tech Eval for ' + work_order_code, class_name, kwargs);
                          spt.tab.add_new('TechEvalWdg_qc_report_for_' + work_order_code,'Tech Eval for ' + work_order_code, class_name, kwargs);
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, el_code)}
        return behavior

    def fix_date(my, date):
        #This is needed due to the way Tactic deals with dates (using timezone info), post v4.0
        from pyasm.common import SPTDate
        return_date = ''
        date_obj = SPTDate.convert_to_local(date)
        if date_obj not in [None,'']:
            return_date = date_obj.strftime("%Y-%m-%d  %H:%M")
        return return_date

    def get_display(my):
        login = Environment.get_login()
        this_user = login.get_login()
        groups = Environment.get_group_names()
        my.get_stub()
        show_save = False
        for g in groups:
            if 'qc' in g or 'edeliveries' in g:
                show_save = True
        if this_user == 'admin':
            show_save = True
        this_timestamp = str(datetime.datetime.now()).split('.')[0]
        code = my.kwargs.get('code')
        original_code = code

        widget = DivWdg()

        if 'TITLE' in code:
            wos = my.server.eval("@GET(twog/work_order['title_code','%s'].code)" % code)
            if len(wos) > 0:
                code = wos[0]
            else:
                none_msg = 'THERE ARE NO WORK ORDERS IN THIS TITLE'
                none_tbl = Table()
                none_tbl.add_row()
                none_tbl.add_cell(none_msg)
                widget.add(none_tbl)
                return widget
        work_order = my.server.eval("@SOBJECT(twog/work_order['code','%s'])" % code)[0]
        title = my.server.eval("@SOBJECT(twog/title['code','%s'])" % work_order.get('title_code'))[0]
        tech_code = ''
        tech = {
            'code': '',
            'description': '',
            'timestamp': this_timestamp,
            'login': this_user,
            'barcode': '',
            'client_code': '',
            'client_name': '',
            'title': title.get('title'),
            'title_code': title.get('code'),
            'episode': '',
            'type': '',
            'trt': '',
            'part': '',
            'label_date': '',
            'capture_or_layoff': '',
            'date': this_timestamp,
            'order_code': work_order.get('order_code'),
            'source_deck': '',
            'record_deck': '',
            'aspect_ratio': '',
            'format': '',
            'standard': '',
            'timecode': '',
            'text': '',
            'vitc_lines': '',
            'horiz_blank': '',
            'active_video_lines': '',
            'title_safe': '',
            'error_logger': '',
            'audio_ch01': '',
            'audio_ch02': '',
            'audio_ch03': '',
            'audio_ch04': '',
            'audio_ch05': '',
            'audio_ch06': '',
            'audio_ch07': '',
            'audio_ch08': '',
            'audio_ch09': '',
            'audio_ch10': '',
            'audio_ch11': '',
            'audio_ch12': '',
            'peak_ch01': '',
            'peak_ch02': '',
            'peak_ch03': '',
            'peak_ch04': '',
            'peak_ch05': '',
            'peak_ch06': '',
            'peak_ch07': '',
            'peak_ch08': '',
            'peak_ch09': '',
            'peak_ch10': '',
            'peak_ch11': '',
            'peak_ch12': '',
            'in_phase_0102': '',
            'in_phase_0304': '',
            'in_phase_0506': '',
            'in_phase_0708': '',
            'in_phase_0910': '',
            'in_phase_1112': '',
            'first_cut': '',
            'first_cut_field': '',
            'last_cut': '',
            'last_cut_field': '',
            'tc_verify': '',
            'error_logger_messages': '',
            'general_comments': '',
            'operator': this_user,
            'source_code': '',
            'work_order_code': work_order.get('code'),
            'wo_name': work_order.get('process')
        }
        if 'tech_code' in my.kwargs.keys():
            tech_code = str(my.kwargs.get('tech_code'))
            if tech_code not in [None,'']:
                tech = my.server.eval("@SOBJECT(twog/tech_eval['code','%s'])" % tech_code)[0]
            else:
                tech_code = ''
        wo_evals = my.server.eval("@SOBJECT(twog/tech_eval['work_order_code','%s']['code','!=','%s'])" % (code, tech_code))
        title_evals = my.server.eval("@SOBJECT(twog/tech_eval['title_code','%s']['work_order_code','!=','%s']['code','!=','%s'])" % (work_order.get('title_code'), work_order.get('code'), tech_code))
        others = Table()
        others.add_style('background-color: #528B8B; width: 100%s;' % '%')
        cols = ['#537072','#518A1A']
        colsct = 0
        if len(title_evals) > 0:
            trrr = others.add_row()
            trrr.add_style('background-color: #50EDA1;')
            others.add_cell('<b>Other Tech Evals for Title</b>')
            for t in title_evals:
                click_row = others.add_row()
                click_row.add_attr('tech_code',t.get('code'))
                click_row.add_attr('work_order_code',t.get('work_order_code'))
                click_row.set_style('cursor: pointer; background-color: %s;' % cols[colsct%2])
                click_row.add_behavior(my.get_click_row(t.get('work_order_code'), t.get('code')))
                others.add_cell('<b>WO:</b> %s, <b>CODE:</b> %s' % (t.get('wo_name'), t.get('work_order_code')))
                others.add_cell('<b>OPERATOR:</b> %s' % t.get('operator'))
                others.add_cell('<b>DATETIME:</b> %s' % my.fix_date(t.get('date')))
                colsct = colsct + 1
        if len(wo_evals) > 0:
            wrrr = others.add_row()
            wrrr.add_style('background-color: #50EDA1;')
            others.add_cell('<b>Other Tech Evals for Work Order</b>')
            for w in wo_evals:
                click_row = others.add_row()
                click_row.add_attr('tech_code',w.get('code'))
                click_row.add_attr('work_order_code',w.get('work_order_code'))
                click_row.set_style('cursor: pointer; background-color: %s;' % cols[colsct%2])
                click_row.add_behavior(my.get_click_row(w.get('work_order_code'), w.get('code')))
                others.add_cell('<b>WO:</b> %s, <b>CODE:</b> %s' % (w.get('wo_name'), w.get('work_order_code')))
                others.add_cell('<b>OPERATOR:</b> %s' % w.get('operator'))
                others.add_cell('<b>DATETIME:</b> %s' % my.fix_date(w.get('date')))
                colsct = colsct + 1

        widget.add_attr('class','big_ol_tech_wdg_%s' % code)
        widget.add_attr('tech_code',tech.get('code'))
        table = Table()
        table.add_attr('class','printable_tech_form_%s' % code)
        table.add_attr('tech_code',tech.get('code'))
        table.add_attr('work_order_code',tech.get('work_order_code'))
        table.add_style('font-family: Calibri, sans-serif;')
        img_tbl = Table()
        img_tbl.add_row()
        i2 = Table()
        i2.add_row()
        i2.add_cell('<img src="/source_labels/2GLogo_small4.png"/>')
        img_tbl.add_cell(i2)
        ad = Table()
        ad.add_row()
        address = ad.add_cell('<b>2G Digital Post, Inc.</b><br/>280 E. Magnolia Blvd.<br/>Burbank, CA 91502<br/>310-840-0600<br/>www.2gdigitalpost.com')
        address.add_attr('nowrap','nowrap')
        address.add_style('font-size: 9px;')
        img_tbl.add_cell(ad)

        rtbl = Table()
        rtbl.add_row()
        big = rtbl.add_cell("<b>LOAD/LAY-OFF TECH EVALUATION</b>")
        big.add_attr('nowrap','nowrap')
        big.add_attr('align','center')
        big.add_attr('valign','center')
        big.add_style('font-size: 40px;')
        rtbl.add_cell('')
        toptbl = Table()
        toptbl.add_row()
        toptbl = Table()
        toptbl.add_row()
        toptbl.add_cell(img_tbl)
        toptbl.add_cell(rtbl)

        printtbl = Table()
        printtbl.add_style('background-color: #528B8B; width: 100%s;' % '%')
        printtbl.add_row()
        p1 = printtbl.add_cell(' ')
        p1.add_style('width: 40%s;' % '%')
        p2 = printtbl.add_cell('<u><b>Print This Report</b></u>')
        p2.add_attr('nowrap','nowrap')
        p2.add_style('cursor: pointer;')
        p2.add_behavior(my.get_print_bvr(code, tech.get('code'), 'tech'))
        p3 = printtbl.add_cell(' ')
        p3.add_style('width: 40%s;' % '%')


        qcd = CalendarInputWdg("timestamp")
        qcd.set_option('show_activator', True)
        qcd.set_option('show_confirm', False)
        qcd.set_option('show_text', True)
        qcd.set_option('show_today', False)
        qcd.set_option('read_only', False)
        qcd.set_option('width', '120px')
        qcd.set_option('id', 'timestamp')
        if tech.get('timestamp') not in [None,'']:
            qcd.set_option('default', my.fix_date(tech.get('timestamp')))
        qcd.get_top().add_attr('id','timestamp')
        qcd.set_persist_on_submit()

        lbld = CalendarInputWdg("label_date")
        lbld.set_option('show_activator', True)
        lbld.set_option('show_confirm', False)
        lbld.set_option('show_text', True)
        lbld.set_option('show_today', False)
        lbld.set_option('read_only', False)
        lbld.set_option('width', '120px')
        lbld.set_option('id', 'label_date')
        if tech.get('label_date') not in [None,'']:
            lbld.set_option('default', my.fix_date(tech.get('label_date')))
        lbld.get_top().add_attr('id','label_date')
        lbld.set_persist_on_submit()

        majtbl = Table()
        majtbl.add_row()
        mt = majtbl.add_cell('2G BARCODE')
        mt.add_attr('align','left')
        mt.add_attr('nowrap','nowrap')
        mc = majtbl.add_cell('CLIENT')
        mc.add_attr('align','left')
        mc.add_attr('nowrap','nowrap')
        mp = majtbl.add_cell('ENTRY DATE')
        mp.add_attr('align','left')
        mp.add_attr('nowrap','nowrap')
        majtbl.add_row()
        majtbl.add_cell('<input type="text" value="%s" class="tech_r_var" id="barcode" style="width: 240px;"/>' % tech.get('barcode'))
        majtbl.add_cell('<input type="text" value="%s" class="tech_r_var" id="client_name" style="width: 340px;"/>' % tech.get('client_name'))
        majtbl.add_cell(qcd)

        titbl = Table()
        titbl.add_row()
        t1 = titbl.add_cell('TITLE')
        t1.add_attr('align','left')
        t2 = titbl.add_cell('EPISODE')
        t2.add_attr('align','left')
        titbl.add_row()
        titbl.add_cell('<input type="text" value="%s" class="tech_r_var" id="title" style="width: 340px;"/>' % tech.get('title'))
        titbl.add_cell('<input type="text" value="%s" class="tech_r_var" id="episode" style="width: 240px;"/>' % tech.get('episode'))

        majtbl.add_row()
        titc = majtbl.add_cell(titbl)
        titc.add_attr('colspan','3')

        trtbl = Table()
        trtbl.add_row()
        tr1 = trtbl.add_cell('TYPE')
        tr1.add_attr('align','left')
        tr2 = trtbl.add_cell('TRT')
        tr2.add_attr('align','left')
        trtbl.add_row()
        trtbl.add_cell('<input type="text" value="%s" class="tech_r_var" id="type" style="width: 340px;"/>' % tech.get('type'))
        trtbl.add_cell('<input type="text" value="%s" class="tech_r_var" id="trt" style="width: 240px;"/>' % tech.get('trt'))

        majtbl.add_row()
        titr = majtbl.add_cell(trtbl)
        titr.add_attr('colspan','3')

        dtbl = Table()
        dtbl.add_row()
        d1 = dtbl.add_cell('DESCRIPTION')
        d1.add_attr('valign','top')
        d2 = dtbl.add_cell('<textarea cols="100" rows="3" class="metadata_r_var" id="description">%s</textarea>' % tech.get('description'))

        d2tbl = Table()
        d2tbl.add_row()
        d2tbl.add_cell('PART')
        d2tbl.add_cell('<input type="text" value="%s" class="tech_r_var" id="part" style="width: 140px;"/>' % tech.get('part'))
        d2tbl.add_row()
        d21 = d2tbl.add_cell('LABEL DATE')
        d21.add_attr('nowrap','nowrap')
        d2tbl.add_cell(lbld)

        dtbl.add_cell(d2tbl)

        majtbl.add_row()
        titr = majtbl.add_cell(dtbl)
        titr.add_attr('colspan','3')

        radio = '<form class="navbar-form pull-right"><label><input type="radio" name="capture_or_layoff" value="capture" /> Capture</label><label><input type="radio" name="sex" value="layoff" /> Layoff</label></form>'


        ltbl = Table()
        ltbl.add_style('background-color: #4a4a4a;')
        ltbl.add_style('font-size: 15px;')
        ltbl.add_row()
        ltbl.add_cell(radio)

        majtbl.add_row()
        titr = majtbl.add_cell(ltbl)
        titr.add_attr('colspan','3')


        table.add_row()
        table.add_cell(toptbl)
        table.add_row()
        table.add_cell(majtbl)

        stbl = Table()
        stbl.add_row()
        s1 = stbl.add_cell(' ')
        s1.add_style('width: 40%s;' % '%')
        s2 = stbl.add_cell('<input type="button" value="Save"/>')
        s2.add_behavior(my.get_save_bvr(code, tech.get('code')))
        s3 = stbl.add_cell(' ')
        s3.add_style('width: 40%s;' % '%')
        if tech.get('code') not in [None,'']:
            s4 = stbl.add_cell('<input type="button" value="Delete This Report"/>')
            s4.add_behavior(my.get_delete_eval(code, tech.get('code')))
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
        if show_save and 'TITLE' not in original_code:
            widget.add(stbl)

        widget.add(table)

        return widget
