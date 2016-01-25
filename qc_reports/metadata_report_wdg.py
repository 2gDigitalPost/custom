import datetime

from tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseTableElementWdg
from tactic.ui.widget import CalendarInputWdg

from pyasm.common import Environment
from pyasm.web import Table, DivWdg
from pyasm.widget import SelectWdg, CheckboxWdg

class MetaDataReportWdg(BaseTableElementWdg):

    def init(my):
        nothing = 'true'
        my.ynd = ['Yes','No','-']
        my.yn = ['Yes','No']
        my.server = None
        my.languages = None

    def get_stub(my):
        my.server = TacticServerStub.get()

    def fill_languages(my):
        my.languages = my.server.eval("@GET(twog/language['@ORDER_BY','name'].name)")

    def get_clone_report(my, wo_code, el_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          var work_order_code = '%s';
                          var report_code = '%s';
                          var class_name = 'qc_reports.qc_reports.QCReportClonerWdg';
                          kwargs = {'wo_code': work_order_code, 'report_code': report_code, 'type': 'metadata'}
                          spt.panel.load_popup('Clone Report To ... ', class_name, kwargs);
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, el_code)}
        return behavior

    def get_save_bvr(my, wo_code, meta_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          wo_code = '%s';
                          meta_code = '%s';
                          top_els = document.getElementsByClassName('printable_metadata_form_' + wo_code);
                          top_el = null;
                          for(var r = 0; r < top_els.length; r++){
                              if(top_els[r].getAttribute('metadata_code') == meta_code){
                                  top_el = top_els[r];
                              }
                          }
                          big_els = document.getElementsByClassName('big_ol_metadata_wdg_' + wo_code);
                          big_el = null;
                          for(var r = 0; r < big_els.length; r++){
                              if(big_els[r].getAttribute('metadata_code') == meta_code){
                                  big_el = big_els[r];
                              }
                          }
                          metadata_code_old = top_el.getAttribute('metadata_code');
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
                              work_order = server.eval("@SOBJECT(twog/work_order['code','" + wo_code + "'])")[0];
                              title = server.eval("@SOBJECT(twog/title['code','" + work_order.title_code + "'])")[0];
                              md_rs = top_el.getElementsByClassName('metadata_r_var');
                              st_sel = top_el.getElementById('source_type');
                              new_data = {'work_order_code': wo_code, 'title_code': title.code, 'order_code': title.order_code, 'client_code': work_order.client_code, 'client_name': work_order.client_name, 'wo_name': work_order.process, 'conclusion': whole_status};
                              for(var r = 0; r < md_rs.length; r++){
                                  md_id = md_rs[r].getAttribute('id');
                                  new_data[md_id] = md_rs[r].value;
                              }
                              m2 = st_sel.getAttribute('id');
                              new_data[m2] = st_sel.value;
                              date_els = top_el.getElementsByClassName('spt_calendar_input');
                              for(var w = 0; w < date_els.length; w++){
                                  if(date_els[w].name == 'qc_date'){
                                      new_data['qc_date'] = date_els[w].value;
                                  }
                              }
                              inputsels = top_el.getElementsByClassName('inputfield');
                              for(var r = 0; r < inputsels.length; r++){
                                  iname = inputsels[r].getAttribute('name');
                                  if(iname.indexOf('_language') != -1){
                                      new_data[iname] = inputsels[r].value;
                                  }
                              }
                              new_metadata_report = null;
                              if(metadata_code_old == ''){
                                  new_metadata_report = server.insert('twog/metadata_report', new_data);
                              }else{
                                  new_metadata_report = server.update(server.build_search_key('twog/metadata_report', metadata_code_old), new_data);
                              }
                              var class_name = 'qc_reports.metadata_report_wdg.MetaDataReportWdg';
                              kwargs = {'code': wo_code, 'metadata_code': new_metadata_report.code}
                              //spt.popup.close(spt.popup.get_popup(bvr.src_el));
                              //spt.panel.load_popup('MetaData Report for ' + wo_code, class_name, kwargs);
                              spt.tab.add_new('MetaDataReportWdg_qc_report_for_' + wo_code,'MetaData Report for ' + wo_code, class_name, kwargs);
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, meta_code)}
        return behavior

    def get_print_bvr(my, wo_code, meta_code, type):
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
                          meta_code = '%s';
                          type = '%s';
                          top_els = document.getElementsByClassName('printable_metadata_form_' + wo_code);
                          top_el = null;
                          for(var r = 0; r < top_els.length; r++){
                              if(top_els[r].getAttribute('metadata_code') == meta_code){
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
                          top_els = document.getElementsByClassName('printable_metadata_form_' + wo_code);
                          top_el = null;
                          for(var r = 0; r < top_els.length; r++){
                              if(top_els[r].getAttribute('metadata_code') == meta_code){
                                  top_el = top_els[r];
                              }
                          }
                          //MTM THIS STUFF WAS TO SHRINK THE REPORT SIZE - OFF CUZ IT DOESN'T WERK
                          new_html = top_el.innerHTML;
//                          new_new_html = '';
//
//                          finding = true;
//                          last_index = 0;
//                          next_index = 0;
//                          remaining = new_html;
//                          new_new_html = '';
//                          while(finding){
//                              last_index = next_index;
//                              next_index = remaining.indexOf('font-size:');
//                              if(next_index > 0){
//                                  finding = true;
//                              }else{
//                                  finding = false;
//                              }
//                              if(next_index == 0){
//                                  next_index = remaining.length;
//                              }
//                              pre = remaining.substring(last_index, next_index);
//                              post = remaining.substring(next_index+10, remaining.length);
//                              the_font_s = post.split('px')[0].trim();
//                              alert('TFS = ' + the_font_s);
//                              el_fonte = Number(the_font_s);
//                              smaller_el_fonte = parseInt(el_fonte/2);
//                              new_new_html = new_new_html + pre + 'font_size: ' + smaller_el_fonte + 'px;';
//                              alert(new_new_html);
//                              firstpx = post.indexOf('px;');
//                              remaining = post.substring(firstpx+3, remaining.length);
//                          }
//                          new_html = new_new_html;
                          //END MTM
                          thing = server.execute_cmd('qc_reports.qc_reports.PrintQCReportWdg', {'html': '<table style="font-family: Calibri, sans-serif;">' + new_html + '</table>','preppend_file_name': wo_code, 'type': type});
                          var url = 'http://tactic01/qc_reports/work_orders/' + wo_code + '_metadata.html';
                          printExternal(url);
                          if(meta_code != '' && meta_code != null){
                              //close, then reload page
                              var class_name = 'qc_reports.metadata_report_wdg.MetaDataReportWdg';
                              kwargs = {'code': wo_code, 'meta_code': meta_code}
                              //if(confirm("Reload Report?")){
                                  //spt.popup.close(spt.popup.get_popup(bvr.src_el));
                                  //spt.panel.load_popup('MetaData Report for ' + wo_code, class_name, kwargs);
                                  spt.tab.add_new('MetaDataReportWdg_qc_report_for_' + wo_code,'MetaData Report for ' + wo_code, class_name, kwargs);
                              //}
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, meta_code, type)}
        return behavior

    def get_delete_report(my, wo_code, meta_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          var work_order_code = '%s';
                          var metadata_code = '%s';
                          if(confirm("Are you sure you want to delete this report?")){
                              if(confirm("Checking again. You really want to delete this report?")){
                                  var server = TacticServerStub.get();
                                  server.retire_sobject(server.build_search_key('twog/metadata_report', metadata_code));
                                  var class_name = 'qc_reports.metadata_report_wdg.MetaDataReportWdg';
                                  kwargs = {'code': work_order_code}
                                  //spt.popup.close(spt.popup.get_popup(bvr.src_el));
                                  //spt.panel.load_popup('MetaData Report for ' + work_order_code, class_name, kwargs);
                                  spt.tab.add_new('MetaDataReportWdg_qc_report_for_' + work_order_code,'MetaData Report for ' + work_order_code, class_name, kwargs);
                              }
                          }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, meta_code)}
        return behavior

    def get_click_row(my, wo_code, meta_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          var work_order_code = '%s';
                          var metadata_code = '%s';
                          var class_name = 'qc_reports.metadata_report_wdg.MetaDataReportWdg';
                          kwargs = {'code': work_order_code, 'metadata_code': metadata_code}
                          //spt.popup.close(spt.popup.get_popup(bvr.src_el));
                          //spt.panel.load_popup('MetaData Report for ' + work_order_code, class_name, kwargs);
                          spt.tab.add_new('MetaDataReportWdg_qc_report_for_' + work_order_code,'MetaData Report for ' + work_order_code, class_name, kwargs);
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, meta_code)}
        return behavior

    def lang_change(my, wo_code, meta_code):
        behavior = {'css_class': 'clickme', 'type': 'change', 'cbjs_action': '''
                try{
                    wo_code = '%s';
                    meta_code = '%s';
                    new_val = bvr.src_el.value;
                    if(new_val.indexOf('...') != -1){
                        top_els = document.getElementsByClassName('printable_metadata_form_' + wo_code);
                        top_el = null;
                        for(var r = 0; r < top_els.length; r++){
                            if(top_els[r].getAttribute('metadata_code') == meta_code){
                                top_el = top_els[r];
                            }
                        }
                        var server = TacticServerStub.get();
                        gotit = false;
                        new_lang = '';
                        while(!gotit){
                            new_lang = prompt("Please enter the name of the new language.");
                            if(new_lang != '' && new_lang != ' ' && new_lang != null){
                                gotit = true;
                            }
                        }
                        server.insert('twog/language', {'name': new_lang});
                        me_id = bvr.src_el.getAttribute('id');
                        all_sels = top_el.getElementsByTagName('select');
                        for(var r = 0; r < all_sels.length; r++){
                            sel_id = all_sels[r].getAttribute('id');
                            if(sel_id.indexOf('language') != -1){
                                old_val = all_sels[r].value;
                                all_sels[r].innerHTML = all_sels[r].innerHTML + '<option>' + new_lang + '</option>';
                                if(sel_id == me_id){
                                    all_sels[r].value = new_lang;
                                }else{
                                    all_sels[r].value = old_val;
                                }
                            }
                        }
                    }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, meta_code)}
        return behavior

    def source_type_change(my, wo_code, meta_code):
        behavior = {'css_class': 'clickme', 'type': 'change', 'cbjs_action': '''
                try{
                    st_fr = {'HD FEATURE': 'FRAME RATE IS THE SAME AS THE NATIVE SOURCE (23.976, 24, 25, 29.97)?','SD FEATURE NTSC': 'FRAME RATE IS THE SAME AS THE NATIVE SOURCE (23.976, 24, 29.97)?','SD FEATURE PAL': 'FRAME RATE IS THE SAME AS THE NATIVE SOURCE (23.976, 24, 25)?','HD TV': 'FRAME RATE IS THE SAME AS THE NATIVE SOURCE (23.976, 24, 25, 29.97)?','SD TV NTSC': 'FRAME RATE IS THE SAME AS THE NATIVE SOURCE (23.976, 24, 29.97)?','SD TV PAL': 'FRAME RATE IS THE SAME AS THE NATIVE SOURCE (23.976, 24, 25)?'};
                    st_res = {'HD FEATURE': 'HD RESOLUTION IS 1920X1080 (SQUARE PIXEL ASPECT RATIO)?','SD FEATURE NTSC': 'SD NTSC RESOLUTION IS 720X480 OR 720X486?','SD FEATURE PAL': 'SD PAL RESOLUTION IS 720X576?','HD TV': 'HD RESOLUTION IS 1920X1080 (SQUARE PIXEL ASPECT RATIO)?','SD TV NTSC': 'SD NTSC RESOLUTION IS 720X480 OR 720X486?','SD TV PAL': 'SD PAL RESOLUTION IS 720X576?'};
                    st_pasp = {'HD FEATURE': 'PASP IS CORRECT? (1:1)','SD FEATURE NTSC': 'PASP IS CORRECT? (4x3 = 0.889:1, 16x9 = 1.185:1)','SD FEATURE PAL': 'PASP IS CORRECT? (4x3 = 1.067:1, 16x9 = 1.422:1)','HD TV': 'PASP IS CORRECT? (1:1)','SD TV NTSC': 'PASP IS CORRECT? (4x3 = 0.889:1, 16x9 = 1.185:1)','SD TV PAL': 'PASP IS CORRECT? (4x3 = 1.067:1, 16x9 = 1.422:1)'};
                    st_asterix = {'HD FEATURE': '&nbsp;','SD FEATURE NTSC': '<i>*SD CONTENT FROM 525 720x486 SOURCES = MIN CROP OF 4 FROM TOP AND 2 FROM BOTTOM</i>','SD FEATURE PAL': '&nbsp;','HD TV': '&nbsp;','SD TV NTSC': '<i>*SD CONTENT FROM 525 720x486 SOURCES = MIN CROP OF 4 FROM TOP AND 2 FROM BOTTOM</i>','SD TV PAL': '&nbsp;'};
                    st_featepis = {'HD FEATURE': 'FEATURE|EPISODE','SD FEATURE NTSC': 'FEATURE|EPISODE','SD FEATURE PAL': 'FEATURE|EPISODE','HD TV': 'EPISODE|FEATURE','SD TV NTSC': 'EPISODE|FEATURE','SD TV PAL': 'EPISODE|FEATURE'};
                    wo_code = '%s';
                    meta_code = '%s';
                    top_els = document.getElementsByClassName('printable_metadata_form_' + wo_code);
                    top_el = null;
                    for(var r = 0; r < top_els.length; r++){
                        if(top_els[r].getAttribute('metadata_code') == meta_code){
                            top_el = top_els[r];
                        }
                    }
                    val = bvr.src_el.value;
                    frame_rate_txt = top_el.getElementById('frame_rate_text');
                    frame_rate_txt.innerHTML = st_fr[val];
                    resolution_txt = top_el.getElementById('resolution_text');
                    resolution_txt.innerHTML = st_res[val];
                    pasp_txt = top_el.getElementById('pasp_text');
                    pasp_txt.innerHTML = st_pasp[val];
                    asterixer_txt = top_el.getElementById('asterixer');
                    asterixer_txt.innerHTML = st_asterix[val];
                    feps = top_el.getElementsByClassName('feat_epi');
                    featepi_s = st_featepis[val].split('|');
                    for(var r = 0; r < feps.length; r++){
                        feps[r].innerHTML = feps[r].innerHTML.replace(featepi_s[1], featepi_s[0]);
                    }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, meta_code)}
        return behavior

    def make_a_sel(my, wholedict, wannabeid, options, width, empty_top=True, class_name="metadata_r_var", preppend=""):
        select = SelectWdg(wannabeid)
        select.add_attr('id',wannabeid)
        if class_name not in [None,'',False]:
            select.add_attr('class','metadata_r_var')
        select.add_style('width: %spx;' % width)
        if empty_top:
            select.append_option('--Select--','')
        if preppend != '':
            ps = preppend.split(',')
            for pp in ps:
                select.append_option(pp,pp)
        for g in options:
            select.append_option(g,g)
        if wholedict.get(wannabeid) not in [None,'']:
            select.set_value(wholedict.get(wannabeid))
        return select

    def make_audio_tbl(my, wholedict, top_title, pairs, meta_code):
        type_pull = ['(5.1) L', '(5.1) R', '(5.1) C', '(5.1) Lfe', '(5.1) Ls', '(5.1) Rs',
                     '(7.1) L', '(7.1) R', '(7.1) C', '(7.1) Lfe', '(7.1) Ls', '(7.1) Rs', '(7.1) SBL', '(7.1) SBR',
                     '(Stereo) Lt', '(Stereo) Rt', '(Stereo) Lt, Rt', '(Stereo) L', '(Stereo) R', '(Stereo) L, R',
                     'Mono', '-']
        tbl = Table()
        tbl.add_row()
        tbl.add_cell('&nbsp;')

        ttl = Table()
        ttl.add_attr('border', '1')
        ttl.add_attr('width', '100%s' % '%')
        ttl.add_style('border-width: 3px;')
        ttl.add_row()
        tcr = ttl.add_cell('<b>%s</b>' % top_title)
        tcr.add_attr('align', 'center')
        tcr.add_attr('width', '100%s' % '%')

        tbl.add_cell(ttl)
        ctr = 1
        for pair in pairs:
            tbl.add_row()
            trk = tbl.add_cell('TRK. %s' % ctr)
            trk.add_attr('nowrap', 'nowrap')
            spl = pair.split('|')
            t2 = Table()
            t2.add_attr('border', '1')
            t2.add_row()
            lang_sel = my.make_a_sel(wholedict, spl[0], my.languages, 100, True, False, '--')
            mm1 = t2.add_cell(lang_sel)
            mm1.add_attr('class', 'select_cell')

            mm2 = t2.add_cell(my.make_a_sel(wholedict, spl[1], type_pull, 100))
            mm2.add_attr('class', 'select_cell')
            tbl.add_cell(t2)
            ctr += 1
        return tbl

    def fix_date(my, date):
        #This is needed due to the way Tactic deals with dates (using timezone info), post v4.0
        from pyasm.common import SPTDate
        return_date = ''
        date_obj = SPTDate.convert_to_local(date)
        if date_obj not in [None,'']:
            return_date = date_obj.strftime("%Y-%m-%d  %H:%M")
        return return_date

    def get_display(my):
        my.get_stub()
        my.fill_languages()
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
        metadata_code = ''
        metadata = {
            'code': '',
            'description': '',
            'login': this_user,
            'order_code': title.get('order_code'),
            'title_code': title.get('code'),
            'work_order_code': work_order.get('code'),
            'title': title.get('title'),
            'episode': title.get('episode'),
            'content': '',
            'source_type': '',
            'source_codes': '',
            'qc_operator': '',
            'qc_date': this_timestamp,
            'qc_notes': '',
            'encoding_log_no_errors_f': '',
            'encoding_log_no_errors_p': '',
            'correct_codec_used_f': '',
            'correct_codec_used_p': '',
            'conclusion': '',
            'fr_same_as_native_source_f': '',
            'fr_same_as_native_source_p': '',
            'hd_res_is_1920x1080_f': '',
            'hd_res_is_1920x1080_p': '',
            'field_dominance_is_none_f': '',
            'field_dominance_is_none_p': '',
            'tagged_as_progressive_f': '',
            'tagged_as_progressive_p': '',
            'clap_tag_removed_f': '',
            'clap_tag_removed_p': '',
            'pasp_is_correct_f': '',
            'pasp_is_correct_p': '',
            'gamma_tag_removed_f': '',
            'gamma_tag_removed_p': '',
            'no_fbimpaareleasedate_tagging_f': '',
            'no_fbimpaareleasedate_tagging_p': '',
            'proper_aspect_ratio_f': '',
            'proper_aspect_ratio_p': '',
            'websites_not_listed_f': '',
            'websites_not_listed_p': '',
            'cropping_values_correct_f': '',
            'cropping_values_correct_p': '',
            'no_promotional_bumpers_p': '',
            'same_aspect_ratio_as_feature_p': '',
            'suitable_for_general_audience_p': '',
            'file_starts_at_5959_w_black_f': '',
            'file_starts_at_1hr_w_fade_p': '',
            'program_starts_at_1hr_f': '',
            'program_begins_with_black_frame_p': '',
            'program_ends_with_black_frame_f': '',
            'program_ends_with_fade_p': '',
            'video_notes': '',
            'aconfig_trk1_language': '',
            'aconfig_trk1_type': '',
            'aconfig_trk2_language': '',
            'aconfig_trk2_type': '',
            'aconfig_trk3_language': '',
            'aconfig_trk3_type': '',
            'aconfig_trk4_language': '',
            'aconfig_trk4_type': '',
            'aconfig_trk5_language': '',
            'aconfig_trk5_type': '',
            'aconfig_trk6_language': '',
            'aconfig_trk6_type': '',
            'aconfig_trk7_language': '',
            'aconfig_trk7_type': '',
            'aconfig_trk8_language': '',
            'aconfig_trk8_type': '',
            'abundle_trk1_language': '',
            'abundle_trk1_type': '',
            'abundle_trk2_language': '',
            'abundle_trk2_type': '',
            'abundle_trk3_language': '',
            'abundle_trk3_type': '',
            'abundle_trk4_language': '',
            'abundle_trk4_type': '',
            'abundle_trk5_language': '',
            'abundle_trk5_type': '',
            'abundle_trk6_language': '',
            'abundle_trk6_type': '',
            'abundle_trk7_language': '',
            'abundle_trk7_type': '',
            'abundle_trk8_language': '',
            'abundle_trk8_type': '',
            'aconfig_trk1_language_p': '',
            'aconfig_trk1_type_p': '',
            'aconfig_trk2_language_p': '',
            'aconfig_trk2_type_p': '',
            'aconfig_trk3_language_p': '',
            'aconfig_trk3_type_p': '',
            'aconfig_trk4_language_p': '',
            'aconfig_trk4_type_p': '',
            'aconfig_trk5_language_p': '',
            'aconfig_trk5_type_p': '',
            'aconfig_trk6_language_p': '',
            'aconfig_trk6_type_p': '',
            'aconfig_trk7_language_p': '',
            'aconfig_trk7_type_p': '',
            'aconfig_trk8_language_p': '',
            'aconfig_trk8_type_p': '',
            'aconfig_verified_f': '',
            'aconfig_verified_b': '',
            'aconfig_verified_p': '',
            'audio_in_sync_with_video_f': '',
            'audio_in_sync_with_video_b': '',
            'audio_in_sync_with_video_p': '',
            'audio_tagged_correctly_f': '',
            'audio_tagged_correctly_b': '',
            'audio_tagged_correctly_p': '',
            'no_audio_cut_off_f': '',
            'no_audio_cut_off_b': '',
            'no_audio_cut_off_p': '',
            'trt_audio_is_trt_video_f': '',
            'trt_audio_is_trt_video_b': '',
            'trt_audio_is_trt_video_p': '',
            'correct_audio_language_f': '',
            'correct_audio_language_b': '',
            'correct_audio_language_p': '',
            'audio_notes': '',
            'delivery_snapshot_feature': '',
            'delivery_snapshot_trailer': '',
            'delivery_snapshot_alt_audio': '',
            'delivery_snapshot_subtitle': '',
            'delivery_snapshot_cc': '',
            'delivery_snapshot_vendor_notes': '',
            'delivery_snapshot_poster_art': '',
            'delivery_snapshot_dub_card': '',
            'delivery_snapshot_other': '',
            'forced_narrative_f': '',
            'forced_narrative_p': '',
            'subtitles_on_feature': '',
            'subtitles_on_trailer': '',
            'forced_narrative_not_overlapping_f': '',
            'forced_narrative_not_overlapping_p': '',
            'subtitles_on_feature_not_overlapping': '',
            'subtitles_on_trailer_not_overlapping': '',
            'dub_card_dimensions_match_feature': '',
            'dub_card_fps_match_feature': '',
            'dub_card_language_match_locale': '',
            'dub_card_duration_4_to_5': '',
            'dub_card_has_no_audio_tracks': '',
            'dub_card_text_not_cutoff_with_cropping': '',
            'cc_in_synch_with_video': '',
            'subtitles_in_synch_with_video': '',
            'subtitles_have_correct_language': '',
            'assets_notes': '',
            'thumb_is_jpeg': '',
            'thumb_dpi_72_or_more': '',
            'thumb_profile_is_rgb': '',
            'thumb_same_aspect_ratio_as_video': '',
            'thumb_only_active_pixels': '',
            'thumb_horiz_at_least_640': '',
            'thumb_for_each_chapter_stop': '',
            'poster_is_jpeg': '',
            'poster_dpi_72_or_more': '',
            'poster_profile_is_rgb': '',
            'poster_rez_at_least_1400x2100': '',
            'poster_aspect_ratio_2x3': '',
            'poster_key_art_and_title_only': '',
            'poster_no_dvdcover_date_urlpromo_tagging': '',
            'image_notes': '',
            'trt_f': '',
            'trt_p': ''
        }

        if 'metadata_code' in my.kwargs.keys():
            metadata_code = str(my.kwargs.get('metadata_code'))
            if metadata_code not in [None,'']:
                metadata = my.server.eval("@SOBJECT(twog/metadata_report['code','%s'])" % metadata_code)[0]
            else:
                metadata_code = ''
        wo_reports = my.server.eval("@SOBJECT(twog/metadata_report['work_order_code','%s']['code','!=','%s'])" % (code, metadata_code))
        title_reports = my.server.eval("@SOBJECT(twog/metadata_report['title_code','%s']['work_order_code','!=','%s']['code','!=','%s'])" % (work_order.get('title_code'), work_order.get('code'), metadata_code))
        others = Table()
        others.add_style('background-color: #528B8B; width: 100%s;' % '%')
        cols = ['#537072','#518A1A']
        colsct = 0
        if len(title_reports) > 0:
            trrr = others.add_row()
            trrr.add_style('background-color: #50EDA1;')
            others.add_cell('<b>Other Element Evals for Title</b>')
            for t in title_reports:
                click_row = others.add_row()
                click_row.add_attr('metadata_code',t.get('code'))
                click_row.add_attr('work_order_code',t.get('work_order_code'))
                click_row.set_style('cursor: pointer; background-color: %s;' % cols[colsct%2])
                click_row.add_behavior(my.get_click_row(t.get('work_order_code'), t.get('code')))
                others.add_cell('<b>WO:</b> %s, <b>CODE:</b> %s' % (t.get('wo_name'), t.get('work_order_code')))
                others.add_cell('<b>OPERATOR:</b> %s' % t.get('qc_operator'))
                others.add_cell('<b>CONCLUSION:</b> %s' % t.get('conclusion'))
                others.add_cell('<b>DATETIME:</b> %s' % my.fix_date(t.get('qc_date')))
                colsct = colsct + 1
        if len(wo_reports) > 0:
            wrrr = others.add_row()
            wrrr.add_style('background-color: #50EDA1;')
            others.add_cell('<b>Other Element Evals for Work Order</b>')
            for w in wo_reports:
                click_row = others.add_row()
                click_row.add_attr('metadata_code',w.get('code'))
                click_row.add_attr('work_order_code',w.get('work_order_code'))
                click_row.set_style('cursor: pointer; background-color: %s;' % cols[colsct%2])
                click_row.add_behavior(my.get_click_row(w.get('work_order_code'), w.get('code')))
                others.add_cell('<b>WO:</b> %s, <b>CODE:</b> %s' % (w.get('wo_name'), w.get('work_order_code')))
                others.add_cell('<b>OPERATOR:</b> %s' % w.get('qc_operator'))
                others.add_cell('<b>CONCLUSION:</b> %s' % w.get('conclusion'))
                others.add_cell('<b>DATETIME:</b> %s' % my.fix_date(w.get('qc_date')))
                colsct = colsct + 1


        widget.add_attr('class','big_ol_metadata_wdg_%s' % code)
        widget.add_attr('metadata_code',metadata.get('code'))
        table = Table()
        table.add_attr('class','printable_metadata_form_%s' % code)
        table.add_attr('metadata_code',metadata.get('code'))
        table.add_attr('work_order_code',metadata.get('work_order_code'))
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
        acr_s = ['APPROVED','CONDITION','REJECTED']
        acr = Table()
        for mark in acr_s:
            acr.add_row()
            acr1 = CheckboxWdg('marked_%s' % mark)
            #acr1.set_persistence()
            if mark in metadata.get('conclusion'):
                acr1.set_value(True)
            else:
                acr1.set_value(False)
            acr.add_cell(acr1)
            acr.add_cell('<b>%s</b>' % mark)

        rtbl = Table()
        rtbl.add_row()
        big = rtbl.add_cell("<b>METADATA REPORT</b>")
        big.add_attr('nowrap','nowrap')
        big.add_attr('align','center')
        big.add_attr('valign','center')
        big.add_style('font-size: 40px;')
        rtbl.add_cell(acr)
        toptbl = Table()
        toptbl.add_row()
        toptbl = Table()
        toptbl.add_row()
        toptbl.add_cell(img_tbl)
        toptbl.add_cell(rtbl)

        qcd = CalendarInputWdg("qc_date")
        qcd.set_option('show_activator', True)
        qcd.set_option('show_confirm', False)
        qcd.set_option('show_text', True)
        qcd.set_option('show_today', False)
        qcd.set_option('read_only', False)
        qcd.set_option('width', '320px')
        qcd.set_option('id', 'qc_date')
        if metadata.get('qc_date') not in [None,'']:
            qcd.set_option('default', my.fix_date(metadata.get('qc_date')))
        qcd.get_top().add_attr('id','qc_date')
        qcd.set_persist_on_submit()

        majtbl = Table()
        majtbl.add_row()
        mt = majtbl.add_cell('TITLE:')
        mt.add_attr('align','right')
        majtbl.add_cell('<input type="text" value="%s" class="metadata_r_var" id="title" style="width: 340px;"/>' % metadata.get('title'))
        mo = majtbl.add_cell('QC OPERATOR:')
        mo.add_attr('align','right')
        mo.add_attr('nowrap','nowrap')
        if metadata.get('qc_operator') not in [None,'']:
            that_login = my.server.eval("@SOBJECT(sthpw/login['login','%s'])" % metadata.get('qc_operator'))
            if that_login:
                that_login = that_login[0]
                that_login_name = '%s %s' % (that_login.get('first_name'), that_login.get('last_name'))
                metadata['qc_operator'] = that_login_name
        majtbl.add_cell('<input type="text" value="%s" class="metadata_r_var" id="qc_operator" style="width: 340px;"/>' % metadata.get('qc_operator'))
        majtbl.add_row()
        me = majtbl.add_cell('EPISODE:')
        me.add_attr('align','right')
        majtbl.add_cell('<input type="text" value="%s" class="metadata_r_var" id="episode" style="width: 340px;"/>' % metadata.get('episode'))
        md = majtbl.add_cell('QC DATE:')
        md.add_attr('nowrap','nowrap')
        md.add_attr('align','right')
        qcd_date = majtbl.add_cell(qcd)
        qcd_date.add_attr('nowrap','nowrap')
        majtbl.add_row()
        mc = majtbl.add_cell('CONT:')
        mc.add_attr('align','right')
        majtbl.add_cell('<input type="text" value="%s" class="metadata_r_var" id="content" style="width: 340px;"/>' % metadata.get('content'))
        mo2 = majtbl.add_cell('TRT FEATURE:')
        mo2.add_attr('align','right')
        mo2.add_attr('nowrap','nowrap')
        majtbl.add_cell('<input type="text" value="%s" class="metadata_r_var" id="trt_f" style="width: 340px;"/>' % metadata.get('trt_f'))
        majtbl.add_row()
        ms = majtbl.add_cell('SOURCE TYPE:')
        ms.add_attr('nowrap','nowrap')
        ms.add_attr('align','right')
        source_types = ['HD FEATURE','SD FEATURE NTSC','SD FEATURE PAL','HD TV','SD TV NTSC','SD TV PAL']
        st_sel = my.make_a_sel(metadata, 'source_type', source_types, 340, False, False)
        st_sel.add_behavior(my.source_type_change(work_order.get('code'),metadata.get('code')))
        mmm = majtbl.add_cell(st_sel)
        mmm.add_attr('class','select_cell')
        mo3 = majtbl.add_cell('&nbsp;&nbsp;TRT TRAILER/PREVIEW:')
        mo3.add_attr('align','right')
        mo3.add_attr('nowrap','nowrap')
        majtbl.add_cell('<input type="text" value="%s" class="metadata_r_var" id="trt_p" style="width: 340px;"/>' % metadata.get('trt_p'))
        #majtbl.add_cell('<input type="text" value="%s" class="metadata_r_var" id="source_type" style="width: 340px;"/>' % metadata.get('source_type'))
        majtbl.add_row()
        qcnl = majtbl.add_cell('QC NOTES:')
        qcnl.add_attr('align','right')
        qcnl.add_attr('nowrap','nowrap')
        qcnl.add_attr('valign','top')
        qcn = majtbl.add_cell('<textarea cols="156" rows="5" class="metadata_r_var" id="qc_notes">%s</textarea>' % metadata.get('qc_notes'))
        qcn.add_attr('colspan','3')


        s1 = Table()
        s1.add_attr('class','section1')
        s1.add_row()
        c1 = s1.add_cell('<b>SECTION 1 - VIDEO CONFIGURATION</b>')
        c1.add_attr('nowrap','nowrap')
        s1.add_row()
        spcc = s1.add_cell('&nbsp;')
        s1.add_row()
        c2 = s1.add_cell('<b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;CONFIRM THE FOLLOWING FOR THE FULL VIDEO FILE AND THE TRAILER/PREVIEW FILE</b>')
        c2.add_attr('nowrap','nowrap')

        s1_list1 = ['ENCODING LOG SHOWS NO ERRORS?', 'CORRECT VIDEO CODEC USED (APPLE PRORES (HQ)422)?', 'FRAME RATE SAME AS THE NATIVE SOURCE (23.976, 24, 25, 29.97)?', 'HD RESOLUTION IS 1920X1080 (SQUARE PIXEL ASPECT RATIO)?', 'FIELD DOMINANCE SET TO NONE?', 'TAGGED AS PROGRESSIVE?', 'CLAP TAG HAS BEEN REMOVED?', 'PASP IS CORRECT (1:1)?', 'GAMMA TAG HAS BEEN REMOVED?', 'VIDEO ASSET DOES NOT CONTAIN FBI, MPAA, OR RELEASE DATE TAGGING?', 'VIDEO IS PROPER ASPECT RATIO (PIC IS NOT SQUEEZED, CUT OFF, DISTORTED)?', 'WEBSITES ARE NOT LISTED IN PROGRAM AND CREDITS?', '*CROPPING VALUES ARE CORRECT (NO INACTIVE PIXELS)?']
        s1_dict1 = {'ENCODING LOG SHOWS NO ERRORS?': 'encoding_log_no_errors_', 'CORRECT VIDEO CODEC USED (APPLE PRORES (HQ)422)?': 'correct_codec_used_', 'FRAME RATE SAME AS THE NATIVE SOURCE (23.976, 24, 25, 29.97)?': 'fr_same_as_native_source_', 'HD RESOLUTION IS 1920X1080 (SQUARE PIXEL ASPECT RATIO)?': 'hd_res_is_1920x1080_', 'FIELD DOMINANCE SET TO NONE?': 'field_dominance_is_none_', 'TAGGED AS PROGRESSIVE?': 'tagged_as_progressive_', 'CLAP TAG HAS BEEN REMOVED?': 'clap_tag_removed_', 'PASP IS CORRECT (1:1)?': 'pasp_is_correct_', 'GAMMA TAG HAS BEEN REMOVED?': 'gamma_tag_removed_', 'VIDEO ASSET DOES NOT CONTAIN FBI, MPAA, OR RELEASE DATE TAGGING?': 'no_fbimpaareleasedate_tagging_', 'VIDEO IS PROPER ASPECT RATIO (PIC IS NOT SQUEEZED, CUT OFF, DISTORTED)?': 'proper_aspect_ratio_', 'WEBSITES ARE NOT LISTED IN PROGRAM AND CREDITS?': 'websites_not_listed_', '*CROPPING VALUES ARE CORRECT (NO INACTIVE PIXELS)?': 'cropping_values_correct_'}
        s1_list2 = ['TRAILER DOES NOT CONTAIN ANY PROMOTIONAL BUMPERS?', 'TRAILER IS SAME ASPECT RATIO AS FEATURE?', '*TRAILER CONTAINS CONTENT SUITABLE FOR A GENERAL AUDIENCE?']
        s1_dict2 = {'TRAILER DOES NOT CONTAIN ANY PROMOTIONAL BUMPERS?': 'no_promotional_bumpers_p', 'TRAILER IS SAME ASPECT RATIO AS FEATURE?': 'same_aspect_ratio_as_feature_p', '*TRAILER CONTAINS CONTENT SUITABLE FOR A GENERAL AUDIENCE?': 'suitable_for_general_audience_p'}

        st_fr = {'HD FEATURE': 'FRAME RATE IS THE SAME AS THE NATIVE SOURCE (23.976, 24, 25, 29.97)?','SD FEATURE NTSC': 'FRAME RATE IS THE SAME AS THE NATIVE SOURCE (23.976, 24, 29.97)?','SD FEATURE PAL': 'FRAME RATE IS THE SAME AS THE NATIVE SOURCE (23.976, 24, 25)?','HD TV': 'FRAME RATE IS THE SAME AS THE NATIVE SOURCE (23.976, 24, 25, 29.97)?','SD TV NTSC': 'FRAME RATE IS THE SAME AS THE NATIVE SOURCE (23.976, 24, 29.97)?','SD TV PAL': 'FRAME RATE IS THE SAME AS THE NATIVE SOURCE (23.976, 24, 25)?'}
        st_res = {'HD FEATURE': 'HD RESOLUTION IS 1920X1080 (SQUARE PIXEL ASPECT RATIO)?','SD FEATURE NTSC': 'SD NTSC RESOLUTION IS 720X480 OR 720X486?','SD FEATURE PAL': 'SD PAL RESOLUTION IS 720X576?','HD TV': 'HD RESOLUTION IS 1920X1080 (SQUARE PIXEL ASPECT RATIO)?','SD TV NTSC': 'SD NTSC RESOLUTION IS 720X480 OR 720X486?','SD TV PAL': 'SD PAL RESOLUTION IS 720X576?'}
        st_pasp = {'HD FEATURE': 'PASP IS CORRECT? (1:1)','SD FEATURE NTSC': 'PASP IS CORRECT? (4x3 = 0.889:1, 16x9 = 1.185:1)','SD FEATURE PAL': 'PASP IS CORRECT? (4x3 = 1.067:1, 16x9 = 1.422:1)','HD TV': 'PASP IS CORRECT? (1:1)','SD TV NTSC': 'PASP IS CORRECT? (4x3 = 0.889:1, 16x9 = 1.185:1)','SD TV PAL': 'PASP IS CORRECT? (4x3 = 1.067:1, 16x9 = 1.422:1)'}
        st_asterix = {'HD FEATURE': '&nbsp;','SD FEATURE NTSC': '<i>*SD CONTENT FROM 525 720x486 SOURCES = MIN CROP OF 4 FROM TOP AND 2 FROM BOTTOM</i>','SD FEATURE PAL': '&nbsp;','HD TV': '&nbsp;','SD TV NTSC': '<i>*SD CONTENT FROM 525 720x486 SOURCES = MIN CROP OF 4 FROM TOP AND 2 FROM BOTTOM</i>','SD TV PAL': '&nbsp;'}
        st_featepis = {'HD FEATURE': 'FEATURE','SD FEATURE NTSC': 'FEATURE','SD FEATURE PAL': 'FEATURE','HD TV': 'EPISODE','SD TV NTSC': 'EPISODE','SD TV PAL': 'EPISODE'}
        pulls = Table()
        pulls_l = Table()
        pulls_r = Table()
        source_type = metadata.get('source_type')
        for s in s1_list1:
            pulls_l.add_row()
            pulls_r.add_row()
            stext = s
            id_to_set = ''
            field_name = s1_dict1[s]
            if source_type not in [None,'']:
                if 'pasp_' in field_name:
                    id_to_set = 'pasp_text'
                    stext = st_pasp[metadata.get('source_type')]
                elif '1920x1080' in field_name:
                    id_to_set = 'resolution_text'
                    stext = st_res[metadata.get('source_type')]
                elif 'fr_same_as_native' in field_name:
                    id_to_set = 'frame_rate_text'
                    stext = st_fr[metadata.get('source_type')]
            scl = pulls_l.add_cell('%s&nbsp;&nbsp;' % stext)
            scl.add_attr('align','right')
            if id_to_set != '':
                scl.add_attr('id',id_to_set)
            mm1 = pulls_l.add_cell(my.make_a_sel(metadata, '%sf' % field_name, my.ynd, 70))
            mm1.add_attr('class','select_cell')
            mm2 = pulls_r.add_cell(my.make_a_sel(metadata, '%sp' % field_name, my.ynd, 70))
            mm2.add_attr('class','select_cell')
        pulls_l.add_row()
        ast_text = '&nbsp;'
        if source_type not in [None,'']:
            ast_text = st_asterix[source_type]
        asterixer = pulls_l.add_cell(ast_text)
        asterixer.add_attr('id','asterixer')
        pulls_l.add_cell('&nbsp;')
        pulls_r.add_row()
        pulls_r.add_cell('&nbsp;')
        for s in s1_list2:
            pulls_l.add_row()
            pulls_r.add_row()
            scl = pulls_l.add_cell('%s&nbsp;&nbsp;' % s)
            scl.add_attr('align','right')
            pulls_l.add_cell('__________')
            mm1 = pulls_r.add_cell(my.make_a_sel(metadata, s1_dict2[s], my.ynd, 70))
            mm1.add_attr('class','select_cell')
        pulls.add_row()
        feat_text = 'FEATURE'
        if source_type not in [None,'']:
            feat_text = st_featepis[source_type]
        p1 = pulls.add_cell('<b>%s&nbsp;&nbsp;</b>' % feat_text)
        p1.add_attr('class','feat_epi')
        p1.add_attr('align','right')
        p1 = pulls.add_cell('&nbsp;&nbsp;')
        pulls.add_cell('<b>TRAILER/PREVIEW</b>')
        pulls.add_row()
        ddd1 = pulls.add_cell(pulls_l)
        dp1 = pulls.add_cell('&nbsp;&nbsp;')
        ddd2 = pulls.add_cell(pulls_r)
        ddd1.add_attr('valign','top')
        ddd2.add_attr('valign','top')
        pulls.add_row()
        pulls.add_cell(' ')
        pulls.add_cell(' ')
        ps = pulls.add_cell('*Flag all nudity, profanity, or gore for approval')
        ps.add_style('font-size: 9px;')

        s1.add_row()
        ssr = s1.add_cell(pulls)
        ssr.add_attr('align','center')



        s1_listc1 = ['FILE STARTS @ 00:59:59:00 WITH BLACK?','PROGRAM STARTS @ 1:00:00:00?', '&nbsp;&nbsp;&nbsp;PROGRAM ENDS WITH AT LEAST ONE BLACK FRAME?']
        s1_dictc1 = {'FILE STARTS @ 00:59:59:00 WITH BLACK?': 'file_starts_at_5959_w_black_f', 'PROGRAM STARTS @ 1:00:00:00?': 'program_starts_at_1hr_f', '&nbsp;&nbsp;&nbsp;PROGRAM ENDS WITH AT LEAST ONE BLACK FRAME?': 'program_ends_with_black_frame_f'}
        s1_listc2 = ['FILE STARTS @ 00:01:00:00 WITH FADE UP/DOWN?', 'PROGRAM BEGINS WITH AT LEAST ONE BLACK FRAME?', '&nbsp;&nbsp;&nbsp;PROGRAM ENDS WITH FADE DOWN (WITH AT LEAST ONCE BLACK FRAME)?']
        s1_dictc2 = {'FILE STARTS @ 00:01:00:00 WITH FADE UP/DOWN?': 'file_starts_at_1hr_w_fade_p', 'PROGRAM BEGINS WITH AT LEAST ONE BLACK FRAME?': 'program_begins_with_black_frame_p', '&nbsp;&nbsp;&nbsp;PROGRAM ENDS WITH FADE DOWN (WITH AT LEAST ONCE BLACK FRAME)?': 'program_ends_with_fade_p'}
        ctbl = Table()
        ctbl.add_row()
        cc1 = ctbl.add_cell('<b>CONFIRM THE BUILD OF FEATURE</b>')
        cc1.add_attr('nowrap','nowrap')
        cc1.add_attr('align','right')
        ctbl.add_cell(' ')
        cc2 = ctbl.add_cell('<b>CONFIRM THE BUILD OF TRAILER/PREVIEW</b>')
        cc2.add_attr('nowrap','nowrap')
        cc2.add_attr('align','middle')
        ctbl.add_cell(' ')
        ctr = 0
        for s in s1_listc1:
            ctbl.add_row()
            nc = ctbl.add_cell('%s&nbsp;&nbsp;' % s)
            nc.add_attr('align','right')
            nc.add_attr('nowrap','nowrap')
            mm1 = ctbl.add_cell(my.make_a_sel(metadata, s1_dictc1[s], my.ynd, 70))
            mm1.add_attr('class','select_cell')
            s2 = s1_listc2[ctr]
            nc2 = ctbl.add_cell('%s&nbsp;&nbsp;' % s2)
            nc2.add_attr('align','right')
            nc2.add_attr('nowrap','nowrap')
            mm2 = ctbl.add_cell(my.make_a_sel(metadata, s1_dictc2[s2], my.ynd, 70))
            mm2.add_attr('class','select_cell')
            ctr = ctr + 1
        ntbl = Table()
        ntbl.add_row()
        vn = ntbl.add_cell('VIDEO NOTES:')
        vn.add_attr('nowrap','nowrap')
        vn.add_attr('align','right')
        vn.add_attr('valign','top')
        lng = ntbl.add_cell('<textarea cols="156" rows="5" class="metadata_r_var" id="video_notes">%s</textarea>' % metadata.get('video_notes'))
        lng.add_attr('colspan','3')
        ctbl.add_row()
        cct = ctbl.add_cell(ntbl)
        cct.add_attr('align','left')

        s1.add_row()
        s1.add_cell('&nbsp;')
        s1.add_row()
        s1.add_cell(ctbl)

        s1_tbl = Table()
        s1_tbl.add_row()
        s1_tbl.add_cell(s1)
        s1_tbl.add_attr('border','1')
        s1_tbl.add_style('border-width: 5px;')

        s2 = Table()
        s2.add_attr('class','section2')
        s2.add_attr('width','100%s' % '%')
        s2.add_row()
        c1 = s2.add_cell('<b>SECTION 2 - AUDIO CONFIGURATION</b>')
        c1.add_attr('nowrap','nowrap')
        s2.add_row()
        spcc = s2.add_cell('&nbsp;')

        audio_config_tbl = my.make_audio_tbl(metadata, 'FEATURE: AUDIO CONFIG', ['aconfig_trk1_language|aconfig_trk1_type', 'aconfig_trk2_language|aconfig_trk2_type', 'aconfig_trk3_language|aconfig_trk3_type','aconfig_trk4_language|aconfig_trk4_type', 'aconfig_trk5_language|aconfig_trk5_type', 'aconfig_trk6_language|aconfig_trk6_type', 'aconfig_trk7_language|aconfig_trk7_type', 'aconfig_trk8_language|aconfig_trk8_type'], metadata.get('code'))
        audio_bundle_tbl = my.make_audio_tbl(metadata, 'AUDIO BUNDLE', ['abundle_trk1_language|abundle_trk1_type', 'abundle_trk2_language|abundle_trk2_type', 'abundle_trk3_language|abundle_trk3_type', 'abundle_trk4_language|abundle_trk4_type', 'abundle_trk5_language|abundle_trk5_type', 'abundle_trk6_language|abundle_trk6_type', 'abundle_trk7_language|abundle_trk7_type', 'abundle_trk8_language|abundle_trk8_type'], metadata.get('code'))
        audio_preview_tbl = my.make_audio_tbl(metadata, 'PREVIEW/TRAILER: AUDIO CONFIG', ['aconfig_trk1_language_p|aconfig_trk1_type_p', 'aconfig_trk2_language_p|aconfig_trk2_type_p', 'aconfig_trk3_language_p|aconfig_trk3_type_p', 'aconfig_trk4_language_p|aconfig_trk4_type_p', 'aconfig_trk5_language_p|aconfig_trk5_type_p', 'aconfig_trk6_language_p|aconfig_trk6_type_p', 'aconfig_trk7_language_p|aconfig_trk7_type_p', 'aconfig_trk8_language_p|aconfig_trk8_type_p'], metadata.get('code'))

        s2_pulls = Table()

        s2_pulls.add_row()
        s2_pulls.add_cell(audio_config_tbl)
        s2_pulls.add_cell('&nbsp;')
        s2_pulls.add_cell(audio_bundle_tbl)
        s2_pulls.add_cell('&nbsp;')
        s2_pulls.add_cell(audio_preview_tbl)

        s2.add_row()
        s2pc = s2.add_cell(s2_pulls)
        s2pc.add_attr('align','center')

        s2.add_row()
        s2.add_cell('&nbsp;&nbsp;')
        s2.add_row()
        s21 = s2.add_cell('<b>&nbsp;&nbsp;&nbsp;CONFIRM THE FOLLOWING FOR THE FULL VIDEO FILE, AUDIO BUNDLE, AND THE TRAILER/PREVIEW FILE</b>')
        s21.add_attr('nowrap','nowrap')

        s2_list = ['AUDIO CONFIGURATION VERIFIED (STEREO OR MONO/MAPPING IS CORRECT)?&nbsp;&nbsp;','AUDIO IS IN SYNC WITH VIDEO (CHECKED IN 3 RANDOM SPOTS AND HEAD/TAIL)?&nbsp;&nbsp;','AUDIO IS TAGGED CORRECTLY?&nbsp;&nbsp;','NO AUDIO IS CUT OFF (AT BEGINNING OR END)?&nbsp;&nbsp;', 'TRT OF AUDIO EQUALS TRT OF THE VIDEO?&nbsp;&nbsp;','CORRECT LANGUAGE IS PRESENT (ON APPLICABLE CHANNELS)?&nbsp;&nbsp;']
        s2_dict = {'AUDIO CONFIGURATION VERIFIED (STEREO OR MONO/MAPPING IS CORRECT)?&nbsp;&nbsp;': 'aconfig_verified_', 'AUDIO IS IN SYNC WITH VIDEO (CHECKED IN 3 RANDOM SPOTS AND HEAD/TAIL)?&nbsp;&nbsp;': 'audio_in_sync_with_video_', 'AUDIO IS TAGGED CORRECTLY?&nbsp;&nbsp;': 'audio_tagged_correctly_', 'NO AUDIO IS CUT OFF (AT BEGINNING OR END)?&nbsp;&nbsp;': 'no_audio_cut_off_', 'TRT OF AUDIO EQUALS TRT OF THE VIDEO?&nbsp;&nbsp;': 'trt_audio_is_trt_video_', 'CORRECT LANGUAGE IS PRESENT (ON APPLICABLE CHANNELS)?&nbsp;&nbsp;': 'correct_audio_language_'}
        ctr = 0
        s2_l = Table()
        s2_c = Table()
        s2_r = Table()
        for s in s2_list:
            s2_l.add_row()
            s2_c.add_row()
            s2_r.add_row()
            s2c = s2_l.add_cell('%s&nbsp;&nbsp;' % s)
            s2c.add_attr('nowrap','nowrap')
            s2c.add_attr('align','right')
            mm1 = s2_l.add_cell(my.make_a_sel(metadata, '%sf' % s2_dict[s], my.ynd, 70))
            mm1.add_attr('class','select_cell')

            mm2 = s2_c.add_cell(my.make_a_sel(metadata, '%sb' % s2_dict[s], my.ynd, 70))
            mm2.add_attr('class','select_cell')

            mm3 = s2_r.add_cell(my.make_a_sel(metadata, '%sp' % s2_dict[s], my.ynd, 70))
            mm3.add_attr('class','select_cell')

        s2_annoy = Table()
        s2_annoy.add_row()
        s2f = s2_annoy.add_cell('<b>FEATURE</b>')
        s2f.add_attr('class','feat_epi')
        s2f.add_attr('align','right')
        s2_annoy.add_cell('&nbsp;&nbsp;')
        s2b = s2_annoy.add_cell('<b>AUDIO BUNDLE</b>')
        s2b.add_attr('align','center')
        s2_annoy.add_cell('&nbsp;&nbsp;')
        s2p = s2_annoy.add_cell('<b>TRAILER/PREVIEW</b>')
        s2p.add_attr('align','center')
        s2_annoy.add_row()
        s2_annoy.add_cell(s2_l)
        s2_annoy.add_cell('&nbsp;&nbsp;')
        s2_annoy.add_cell(s2_c)
        s2_annoy.add_cell('&nbsp;&nbsp;')
        s2_annoy.add_cell(s2_r)

        s2.add_row()
        s2.add_cell(s2_annoy)

        s2_n = Table()
        s2_n.add_row()
        s2nc = s2_n.add_cell('AUDIO NOTES:')
        s2nc.add_attr('nowrap','nowrap')
        s2nc.add_attr('valign','top')
        s2_n.add_cell('<textarea cols="156" rows="5" class="metadata_r_var" id="audio_notes">%s</textarea>' % metadata.get('audio_notes'))
        s2.add_row()
        s2.add_cell(s2_n)

        s2_tbl = Table()
        s2_tbl.add_row()
        s2_tbl.add_cell(s2)
        s2_tbl.add_attr('border','1')
        s2_tbl.add_attr('width','100%s' % '%')
        s2_tbl.add_style('border-width: 5px;')


        s3 = Table()
        s3.add_attr('class','section3')
        s3.add_attr('width','100%s' % '%')
        s3.add_row()
        c1 = s3.add_cell('<b>SECTION 3 - ASSETS</b>')
        c1.add_attr('nowrap','nowrap')
        s3.add_row()
        spcc = s3.add_cell('&nbsp;')

        s3_list1 = ['FEATURE:', 'TRAILER:', 'ALT AUDIO:', 'SUBTITLE:', 'CC:', 'VENDOR NOTES:', 'POSTER ART:', 'DUB CARD:']
        s3_dict1 = {'FEATURE:': 'delivery_snapshot_feature', 'TRAILER:': 'delivery_snapshot_trailer', 'ALT AUDIO:': 'delivery_snapshot_alt_audio', 'SUBTITLE:': 'delivery_snapshot_subtitle', 'CC:': 'delivery_snapshot_cc', 'VENDOR NOTES:': 'delivery_snapshot_vendor_notes', 'POSTER ART:': 'delivery_snapshot_poster_art', 'DUB CARD:': 'delivery_snapshot_dub_card'}

        snap = Table()
        snap.add_row()
        scen = snap.add_cell('<b>DELIVERY SNAPSHOT</b>')
        scen.add_attr('colspan','2')
        scen.add_attr('align','center')
        for s in s3_list1:
            snap.add_row()
            sn1 = snap.add_cell('%s&nbsp;&nbsp;' % s)
            sn1.add_attr('nowrap','nowrap')
            sn1.add_attr('align','right')
            mm1 = snap.add_cell(my.make_a_sel(metadata, s3_dict1[s], my.ynd, 70))
            mm1.add_attr('class','select_cell')
        snap.add_row()
        sn2 = snap.add_cell('OTHER:')
        sn2.add_attr('align','right')
        snap.add_cell('<input type="text" value="%s" class="metadata_r_var" id="delivery_snapshot_other" style="width: 70px;"/>' % metadata.get('delivery_snapshot_other'))


        snap_t = Table()
        snap_t.add_attr('border','1')
        snap_t.add_style('border-width: 2px;')
        snap_t.add_cell(snap)


        s3_list2 = ['FORCED NARRATIVE ON FEATURE?', 'FORCED NARRATIVE ON TRAILER?', 'SUBTITLES ON FEATURE?', 'SUBTITLES ON TRAILER?']
        s3_dict2 = {'FORCED NARRATIVE ON FEATURE?': 'forced_narrative_f|forced_narrative_not_overlapping_f', 'FORCED NARRATIVE ON TRAILER?': 'forced_narrative_p|forced_narrative_not_overlapping_p', 'SUBTITLES ON FEATURE?': 'subtitles_on_feature|subtitles_on_feature_not_overlapping', 'SUBTITLES ON TRAILER?': 'subtitles_on_trailer|subtitles_on_trailer_not_overlapping'}
        s32 = Table()
        for s in s3_list2:
            s32.add_row()
            s32c = s32.add_cell('%s&nbsp;&nbsp;' % s)
            s32c.add_attr('nowrap','nowrap')
            s32c.add_attr('align','right')
            mm1 = s32.add_cell(my.make_a_sel(metadata, s3_dict2[s].split('|')[0], my.ynd, 70))
            mm1.add_attr('class','select_cell')
            s32.add_cell('->')
            s32c2 = s32.add_cell('...DOES NOT OVERLAP ANY CREDITS OR OTHER TEXT?&nbsp;&nbsp;')
            s32c2.add_attr('nowrap','nowrap')
            mm2 = s32.add_cell(my.make_a_sel(metadata, s3_dict2[s].split('|')[1], my.ynd, 70))
            mm2.add_attr('class','select_cell')

        s3_list3 = ['DUB CARD DIMENSIONS MATCH FEATURE?', 'DUB CARD FPS MATCHES FEATURE?', 'DUB CARD LANG. MATCHES LOCALE?', 'DUB CARD DURATION IS 4 TO 5 SEC?', 'DUB CARD CONTAINS NO AUDIO TRACKS?']
        s3_dict3 = {'DUB CARD DIMENSIONS MATCH FEATURE?': 'dub_card_dimensions_match_feature', 'DUB CARD FPS MATCHES FEATURE?': 'dub_card_fps_match_feature', 'DUB CARD LANG. MATCHES LOCALE?': 'dub_card_language_match_locale', 'DUB CARD DURATION IS 4 TO 5 SEC?': 'dub_card_duration_4_to_5', 'DUB CARD CONTAINS NO AUDIO TRACKS?': 'dub_card_has_no_audio_tracks'}
        s33 = Table()
        for s in s3_list3:
            s33.add_row()
            s33b = s33.add_cell('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
            s33c = s33.add_cell('%s&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' % s)
            s33c.add_attr('nowrap','nowrap')
            s33c.add_attr('align','right')
            mm1 = s33.add_cell(my.make_a_sel(metadata, s3_dict3[s], my.ynd, 70))
            mm1.add_attr('class','select_cell')

        s3_list4 = ['CC IS IN SYNC WITH VIDEO?','SUBTITLES ARE IN SYNC WITH VIDEO?','SUBTITLES HAVE CORRECT LANGUAGE?']
        s3_dict4 = {'CC IS IN SYNC WITH VIDEO?': 'cc_in_synch_with_video','SUBTITLES ARE IN SYNC WITH VIDEO?': 'subtitles_in_synch_with_video','SUBTITLES HAVE CORRECT LANGUAGE?': 'subtitles_have_correct_language'}
        s34 = Table()
        for s in s3_list4:
            s34.add_row()
            s34c = s34.add_cell('%s&nbsp;&nbsp;' % s)
            s34c.add_attr('nowrap','nowrap')
            s34c.add_attr('align','right')
            mm1 = s34.add_cell(my.make_a_sel(metadata, s3_dict4[s], my.ynd, 70))
            mm1.add_attr('class','select_cell')

        s3.add_row()
        s3.add_cell(snap_t)

        sj = Table()
        sj.add_row()
        lcell2 = sj.add_cell(s32)
        lcell2.add_attr('colspan','3')
        sj.add_row()
        sj.add_cell('&nbsp;')
        sj.add_row()
        sj.add_cell(s33)
        sj.add_cell('&nbsp;&nbsp;&nbsp;')
        sj4c = sj.add_cell(s34)
        sj4c.add_attr('valign','top')

        sj2 = Table()
        sj2.add_row()
        sjc = sj2.add_cell('DUB CARD TEXT IS NOT CUT OFF WHEN FEATURE CROPPING VALUES ARE APPLIED?&nbsp;')
        sjc.add_attr('nowrap','nowrap')
        mm11 = sj2.add_cell(my.make_a_sel(metadata, 'dub_card_text_not_cutoff_with_cropping', my.ynd, 70))
        mm11.add_attr('class','select_cell')


        s3.add_cell(sj)
        s3.add_row()
        sj2c = s3.add_cell(sj2)
        sj2c.add_attr('colspan','2')

        s3.add_row()
        ltbl = Table()
        ltbl.add_row()
        tll = ltbl.add_cell('ASSETS NOTES:')
        tll.add_attr('nowrap','nowrap')
        tll.add_attr('valign','top')
        tlong = ltbl.add_cell('<textarea cols="156" rows="5" class="metadata_r_var" id="assets_notes">%s</textarea>' % metadata.get('assets_notes'))
        s3.add_cell(ltbl)

        s3_tbl = Table()
        s3_tbl.add_row()
        s3_tbl.add_cell(s3)
        s3_tbl.add_attr('border','1')
        s3_tbl.add_attr('width','100%s' % '%')
        s3_tbl.add_style('border-width: 5px;')

        s4 = Table()
        s4.add_attr('class','section3')
        s4.add_attr('width','100%s' % '%')
        s4.add_row()
        c1 = s4.add_cell('<b>SECTION 4 - CHAPTER THUMBNAILS AND POSTER ART (FEATURES ONLY)</b>')
        c1.add_attr('nowrap','nowrap')
        s4.add_row()
        spc4 = s4.add_cell('&nbsp;')

        s4_list1 = ['IMAGE IS A JPEG (.JPG EXTENSION)?', 'DPI IS 72 OR GREATER?', 'COLOR PROFILE IS RGB?', 'SAME ASPECT RATIO AS VIDEO?', 'ONLY ACTIVE PIXELS ARE INCLUDED (NO DIRTY EDGES)?', 'HORIZONTAL DIMENSION IS AT LEAST 640?', 'EACH CHAPTER STOP HAS A THUMBNAIL?']
        s4_dict1 = {'IMAGE IS A JPEG (.JPG EXTENSION)?': 'thumb_is_jpeg', 'DPI IS 72 OR GREATER?': 'thumb_dpi_72_or_more', 'COLOR PROFILE IS RGB?': 'thumb_profile_is_rgb', 'SAME ASPECT RATIO AS VIDEO?': 'thumb_same_aspect_ratio_as_video', 'ONLY ACTIVE PIXELS ARE INCLUDED (NO DIRTY EDGES)?': 'thumb_only_active_pixels', 'HORIZONTAL DIMENSION IS AT LEAST 640?': 'thumb_horiz_at_least_640', 'EACH CHAPTER STOP HAS A THUMBNAIL?': 'thumb_for_each_chapter_stop'}
        s41 = Table()
        for s in s4_list1:
            s41.add_row()
            s41c = s41.add_cell('%s&nbsp;&nbsp;' % s)
            s41c.add_attr('nowrap','nowrap')
            s41c.add_attr('align','right')
            mm1 = s41.add_cell(my.make_a_sel(metadata, s4_dict1[s], my.ynd, 70))
            mm1.add_attr('class','select_cell')

        s4_list2 = ['IMAGE IS A JPEG (.JPG EXTENSION)?', 'DPI IS 72 OR GREATER?', 'COLOR PROFILE IS RGB?', 'RESOLUTION IS AT LEAST 1400x2100?', 'ASPECT RATIO IS 2:3?', 'CONTAINS KEY ART AND TITLE ONLY (NO FILM RATING ON IMAGE)?', 'NO DVD COVER, DATE STAMP, URL OR PROMO TAGGING INCLUDED?']
        s4_dict2 = {'IMAGE IS A JPEG (.JPG EXTENSION)?': 'poster_is_jpeg' , 'DPI IS 72 OR GREATER?': 'poster_dpi_72_or_more', 'COLOR PROFILE IS RGB?': 'poster_profile_is_rgb', 'RESOLUTION IS AT LEAST 1400x2100?': 'poster_rez_at_least_1400x2100', 'ASPECT RATIO IS 2:3?': 'poster_aspect_ratio_2x3', 'CONTAINS KEY ART AND TITLE ONLY (NO FILM RATING ON IMAGE)?': 'poster_key_art_and_title_only', 'NO DVD COVER, DATE STAMP, URL OR PROMO TAGGING INCLUDED?': 'poster_no_dvdcover_date_urlpromo_tagging'}
        s42 = Table()
        for s in s4_list2:
            s42.add_row()
            s42c = s42.add_cell('%s&nbsp;&nbsp;' % s)
            s42c.add_attr('nowrap','nowrap')
            s42c.add_attr('align','right')
            mm1 = s42.add_cell(my.make_a_sel(metadata, s4_dict2[s], my.ynd, 70))
            mm1.add_attr('class','select_cell')

        cmbn = Table()
        cmbn.add_row()
        ct1 = cmbn.add_cell('<b>CHAPTER THUMBNAILS</b>')
        ct1.add_attr('nowrap','nowrap')
        ct1.add_attr('align','center')
        ct2 = cmbn.add_cell('<b>POSTER ART (ONE SHEET)</b>')
        ct2.add_attr('nowrap','nowrap')
        ct2.add_attr('align','center')
        cmbn.add_row()
        cmbn.add_cell(s41)
        cmbn.add_cell(s42)

        ltbl2 = Table()
        ltbl2.add_row()
        tll = ltbl2.add_cell('IMAGES NOTES:')
        tll.add_attr('nowrap','nowrap')
        tll.add_attr('valign','top')
        tlong = ltbl2.add_cell('<textarea cols="156" rows="5" class="metadata_r_var" id="image_notes">%s</textarea>' % metadata.get('image_notes'))

        cmbn.add_row()
        cd4 = cmbn.add_cell(ltbl2)
        cd4.add_attr('colspan','2')

        s4.add_row()
        s4.add_cell(cmbn)

        s4_tbl = Table()
        s4_tbl.add_row()
        s4_tbl.add_cell(s4)
        s4_tbl.add_attr('border','1')
        s4_tbl.add_attr('width','100%s' % '%')
        s4_tbl.add_style('border-width: 5px;')

        table.add_row()
        table.add_cell(toptbl)
        table.add_row()
        table.add_cell(majtbl)
        table.add_row()
        table.add_cell(s1_tbl)
        table.add_row()
        table.add_cell(s2_tbl)
        table.add_row()
        table.add_cell(s3_tbl)
        table.add_row()
        table.add_cell(s4_tbl)

        printtbl = Table()
        printtbl.add_style('background-color: #528B8B; width: 100%s;' % '%')
        printtbl.add_row()
        p1 = printtbl.add_cell(' ')
        p1.add_style('width: 40%s;' % '%')
        p2 = printtbl.add_cell('<u><b>Print This Report</b></u>')
        p2.add_attr('nowrap','nowrap')
        p2.add_style('cursor: pointer;')
        p2.add_behavior(my.get_print_bvr(code, metadata.get('code'), 'metadata'))
        p3 = printtbl.add_cell(' ')
        p3.add_style('width: 40%s;' % '%')

        stbl = Table()
        stbl.add_row()
        s1 = stbl.add_cell(' ')
        s1.add_style('width: 40%s;' % '%')
        s2 = stbl.add_cell('<input type="button" value="Save"/>')
        s2.add_behavior(my.get_save_bvr(code, metadata.get('code')))
        s3 = stbl.add_cell(' ')
        s3.add_style('width: 40%s;' % '%')
        if metadata.get('code') not in [None,'']:
            #s33 = stbl.add_cell('<input type="button" value="Clone This Report"/>')
            #s33.add_behavior(my.get_clone_report(code, metadata.get('code')))
            s4 = stbl.add_cell('<input type="button" value="Delete This Report"/>')
            s4.add_behavior(my.get_delete_report(code, metadata.get('code')))

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

        return widget