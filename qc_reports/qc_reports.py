__all__ = ["QCReportLauncherWdg","QCReportClonerWdg","QCReportSelectorWdg","PreQualEvalLinesWdg","PrintQCReportWdg","PreQualEvalWdg","ElementEvalAudioWdg","ElementEvalBarcodesWdg","ElementEvalLinesWdg","ElementEvalWdg","TechEvalWdg","MetaDataReportWdg","ReportTimecodeShifterWdg"]
import tacticenv
import os, datetime
from pyasm.common import Environment
from pyasm.biz import *
from pyasm.web import Table, DivWdg
from pyasm.widget import SelectWdg, IconWdg, TextWdg, CheckboxWdg
from tactic.ui.common import BaseTableElementWdg
from tactic.ui.common import BaseRefreshWdg
from pyasm.command import *

class QCReportLauncherWdg(BaseTableElementWdg):

    def init(my):
        nothing = 'true'
        my.server = None

    def get_launch_behavior(my, code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                          var code = '%s';
                          var class_name = 'qc_reports.qc_reports.QCReportSelectorWdg';
                          kwargs = {
                                           'code': code
                                   };
                          spt.panel.load_popup('Select Report for ' + code, class_name, kwargs);
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % code}
        return behavior

    def get_display(my):
        code = ''
        order_name = ''
        sob_sk = ''
        if 'code' in my.kwargs.keys():
            code = str(my.kwargs.get('code'))
        else: 
            sobject = my.get_current_sobject()
            code = sobject.get_code()
        widget = DivWdg()
        table = Table()
        table.add_attr('width', '50px')
        table.add_row()
        cell1 =  table.add_cell('<img border="0" style="vertical-align: middle" title="" src="/context/icons/common/reference.png">')
        launch_behavior = my.get_launch_behavior(code)
        cell1.add_style('cursor: pointer;')
        cell1.add_behavior(launch_behavior)
        widget.add(table)

        return widget

class QCReportClonerWdg(BaseTableElementWdg):

    def init(my):
        nothing = 'true'
 
    def get_clone_behavior(my, report_code, type, login_name):
        behavior =  {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        alert('This type of report cannot be cloned yet.');
                     '''}
        if type == 'prequal':
            behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                            function oc(a){
                                var o = {};
                                for(var i=0;i<a.length;i++){
                                    o[a[i]]='';
                                }
                                return o;
                            }
                            function kill_nothing(something){
                                returner = something;
                                if(something == null || something == 'NOTHINGXsXNOTHING'){
                                    returner = '';
                                } 
                                return returner;
                            }
                            try{
                                var report_code = '%s';
                                var login_name = '%s';
                                var top_el = document.getElementById('cloner_for_' + report_code);
                                type = top_el.getAttribute('type');
                                wo_code = top_el.getAttribute('wo_code');
                                server = TacticServerStub.get();
                                the_report = server.eval("@SOBJECT(twog/prequal_eval['code','" + report_code + "'])")[0];
                                the_lines = server.eval("@SOBJECT(twog/prequal_eval_lines['prequal_eval_code','" + the_report.code + "'])");
                                original_title_sk = server.build_search_key('twog/title', the_report.title_code);
                                checks = top_el.getElementsByClassName('spt_input');
                                titles = {};
                                title_sources = {};
                                title_sources_tcodes = [];
                                title_codes = [];
                                out_lines = [];
                                cloned_some = false;
                                for(var r = 0; r < checks.length; r++){
                                    if(checks[r].type == 'checkbox' && checks[r].name != 'clone_toggler'){
                                        if(checks[r].checked){
                                            name = checks[r].getAttribute('name');
                                            code = name.split('lonecheck_')[1];
                                            wo = server.eval("@SOBJECT(twog/work_order['code','" + code + "'])")[0];
                                            spt.app_busy.show('Cloning report and attaching to ' + wo.process + '(' + wo.code + ')');
                                            title_code = wo.title_code;
                                            title = null;
                                            if(!(title_code in oc(title_codes))){
                                                title = server.eval("@SOBJECT(twog/title['code','" + wo.title_code + "'])")[0];
                                                title_codes.push(title.code);
                                                titles[title.code] = title; 
                                            }else{
                                                title = titles[title_code]
                                            } 
                                            source_codes = '';
                                            if(!(title_code in oc(title_sources_tcodes))){
                                                sources = server.eval("@SOBJECT(twog/title_origin['title_code','" + title_code + "'])");
                                                for(var f = 0; f < sources.length; f++){
                                                    if(source_codes == ''){
                                                        source_codes = sources[f].source_code;
                                                    }else{
                                                        source_codes = source_codes + ',' + sources[f].source_code;
                                                    }
                                                }
                                                title_sources_tcodes.push(title_code);
                                                title_sources[title_code] = source_codes;
                                            }else{
                                                source_codes = title_sources[title_code];
                                            }
                                            cloned_some = true;
                                            out_lines.push('Cloned WO: ' + wo.process + '(' + wo.code + ') from Title: ' + title.title + ' ' + title.episode + ' (' + title.code + ') Report Type: ' + type.toUpperCase()); 
                                            new_pq = server.insert('twog/prequal_eval', {'title': title.title, 'episode': kill_nothing(title.episode), 'title_code': title.code, 'client_code': kill_nothing(title.client_code), 'client_name': kill_nothing(title.client_name), 'title_type': kill_nothing(the_report.title_type), 'po_number': kill_nothing(title.po_number), 'order_code': title.order_code, 'wo_name': wo.process, 'work_order_code': wo.code, 'source_code': kill_nothing(source_codes), 'standard': kill_nothing(title.deliverable_standard), 'aspect_ratio': kill_nothing(title.deliverable_aspect_ratio), 'format': kill_nothing(title.deliverable_format), 'frame_rate': kill_nothing(title.deliverable_frame_rate), 'operator': login_name, 'login': login_name, 'description': the_report.description}); 
                                            for(var f = 0; f < the_lines.length; f++){
                                                server.insert('twog/prequal_eval_lines', {'prequal_eval_code': new_pq.code, 'description': kill_nothing(the_lines[f].description), 'login': login_name, 'order_code': title.order_code, 'title_code': title_code, 'work_order_code': wo.code, 'timecode': kill_nothing(the_lines[f].timecode), 'media_type': kill_nothing(the_lines[f].media_type), 'type_code': kill_nothing(the_lines[f].type_code), 'scale': kill_nothing(the_lines[f].scale), 'sector_or_channel': kill_nothing(the_lines[f].sector_or_channel), 'in_source': kill_nothing(the_lines[f].in_source), 'source_code': kill_nothing(source_codes)});
                                            } 
                                        }
                                        spt.app_busy.hide();
                                    }
                                }
                                if(cloned_some){
                                    ccs = '';
                                    emails = server.eval("@GET(sthpw/login_in_group['login_group','in','qc supervisor|scheduling supervisor'].sthpw/login.email)");
                                    for(var r = 0; r < emails.length; r++){
                                        if(ccs == ''){
                                            ccs = emails[r];
                                        }else{
                                            ccs = ccs + ';' + emails[r];
                                        }
                                    }
                                    note = '';
                                    for(var r = 0; r < out_lines.length; r++){
                                        if(note == ''){
                                            note = out_lines[r];
                                        }else{
                                            note = note + '\\n' + out_lines[r]; 
                                        }
                                    } 
                                    thing = server.execute_cmd('operator_view.MakeNoteWdg', {'obj_sk': original_title_sk, 'header': wo_code + " - Cloned", 'note': note, 'note_ccs': ccs});
                                    spt.alert('Done');
                                    spt.popup.close(spt.popup.get_popup(bvr.src_el));
                                    top_to_reload = document.getElementsByClassName('big_ol_prequal_wdg_' +  wo_code)[0];
                                    kwargs = {'code': wo_code, 'prequal_code': report_code}
                                    var class_name = 'qc_reports.qc_reports.PreQualEvalWdg';
                                    spt.api.load_panel(top_to_reload, class_name, kwargs);
                                }
                    }
                    catch(err){
                              spt.app_busy.hide();
                              spt.alert(spt.exception.handler(err));
                    }
             ''' % (report_code, login_name)}
        elif type == 'metadata':
            behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                            function oc(a){
                                var o = {};
                                for(var i=0;i<a.length;i++){
                                    o[a[i]]='';
                                }
                                return o;
                            }
                            function kill_nothing(something){
                                returner = something;
                                if(something == null || something == 'NOTHINGXsXNOTHING'){
                                    returner = '';
                                } 
                                return returner;
                            }
                            function make_date(){
                                var today = new Date();
                                var dd = today.getDate();
                                var mm = today.getMonth()+1; //January is 0!
                                var yyyy = today.getFullYear();
                                
                                if(dd<10) {
                                    dd='0'+dd
                                } 
                                
                                if(mm<10) {
                                    mm='0'+mm
                                } 
                                
                                today = yyyy + '-' + mm + '-' + dd;
                                return today;
                            }
                            try{
                                alert('This feature has not been tested yet. Cloning anyway...');
                                var report_code = '%s';
                                var login_name = '%s';
                                var top_el = document.getElementById('cloner_for_' + report_code);
                                type = top_el.getAttribute('type');
                                wo_code = top_el.getAttribute('wo_code');
                                server = TacticServerStub.get();
                                the_report = server.eval("@SOBJECT(twog/metadata_report['code','" + report_code + "'])")[0];
                                original_title_sk = server.build_search_key('twog/title', the_report.title_code);
                                checks = top_el.getElementsByClassName('spt_input');
                                titles = {};
                                title_sources = {};
                                title_sources_tcodes = [];
                                title_codes = [];
                                out_lines = [];
                                cloned_some = false;
                                today = make_date();
                                for(var r = 0; r < checks.length; r++){
                                    if(checks[r].type == 'checkbox' && checks[r].name != 'clone_toggler'){
                                        if(checks[r].checked){
                                            name = checks[r].getAttribute('name');
                                            code = name.split('lonecheck_')[1];
                                            wo = server.eval("@SOBJECT(twog/work_order['code','" + code + "'])")[0];
                                            spt.app_busy.show('Cloning report and attaching to ' + wo.process + '(' + wo.code + ')');
                                            title_code = wo.title_code;
                                            title = null;
                                            if(!(title_code in oc(title_codes))){
                                                title = server.eval("@SOBJECT(twog/title['code','" + wo.title_code + "'])")[0];
                                                title_codes.push(title.code);
                                                titles[title.code] = title; 
                                            }else{
                                                title = titles[title_code]
                                            } 
                                            source_codes = '';
                                            if(!(title_code in oc(title_sources_tcodes))){
                                                sources = server.eval("@SOBJECT(twog/title_origin['title_code','" + title_code + "'])");
                                                for(var f = 0; f < sources.length; f++){
                                                    if(source_codes == ''){
                                                        source_codes = sources[f].source_code;
                                                    }else{
                                                        source_codes = source_codes + ',' + sources[f].source_code;
                                                    }
                                                }
                                                title_sources_tcodes.push(title_code);
                                                title_sources[title_code] = source_codes;
                                            }else{
                                                source_codes = title_sources[title_code];
                                            }
                                            cloned_some = true;
                                            out_lines.push('Cloned WO: ' + wo.process + '(' + wo.code + ') from Title: ' + title.title + ' ' + title.episode + ' (' + title.code + ') Report Type: ' + type.toUpperCase()); 
                                            new_md = server.insert('twog/metadata_report', {'title': title.title, 'episode': kill_nothing(title.episode), 'title_code': title.code, 'client_code': kill_nothing(title.client_code), 'client_name': kill_nothing(title.client_name), 'order_code': title.order_code, 'wo_name': wo.process, 'work_order_code': wo.code, 'login': login_name, 'description': the_report.description, 'content': the_report.content, 'source_type': the_report.source_type, 'source_codes': source_codes, 'qc_operator': login_name, 'qc_date': today, 'qc_notes': the_report.qc_notes, 'encoding_log_no_errors_f': the_report.encoding_log_no_errors_f, 'encoding_log_no_errors_p': the_report.encoding_log_no_errors_p, 'correct_codec_used_f': the_report.correct_codec_used_f, 'correct_codec_used_p': the_report.correct_codec_used_p, 'fr_same_as_native_source_f': the_report.fr_same_as_native_source_f, 'fr_same_as_native_source_p': the_report.fr_same_as_native_source_p, 'hd_res_is_1920x1080_f': the_report.hd_res_is_1920x1080_f, 'hd_res_is_1920x1080_p': the_report.hd_res_is_1920x1080_p, 'field_dominance_is_none_f': the_report.field_dominance_is_none_f, 'field_dominance_is_none_p': the_report.field_dominance_is_none_p, 'tagged_as_progressive_f': the_report.tagged_as_progressive_f, 'tagged_as_progressive_p': the_report.tagged_as_progressive_p, 'clap_tag_removed_f': the_report.clap_tag_removed_f, 'clap_tag_removed_p': the_report.clap_tag_removed_p, 'pasp_is_correct_f': the_report.pasp_is_correct_f, 'pasp_is_correct_p': the_report.pasp_is_correct_p, 'gamma_tag_removed_f': the_report.gamme_tag_removed_f, 'gamma_tag_removed_p': the_report.gamme_tag_removed_p, 'no_fbimpaareleasedate_tagging_f': the_report.no_fbimpaareleasedate_tagging_f, 'no_fbimpaareleasedate_tagging_p': the_report.no_fbimpaareleasedate_tagging_p, 'proper_aspect_ratio_f': the_report.proper_aspect_ratio_f, 'proper_aspect_ratio_p': the_report.proper_aspect_ratio_p, 'websites_not_listed_f': the_report.websites_not_listed_f, 'websites_not_listed_p': the_report.websites_not_listed_p, 'cropping_values_correct_f': the_report.cropping_values_correct_f, 'cropping_values_correct_p': the_report.cropping_values_correct_p, 'no_promotional_bumpers_p': the_report.no_promotional_bumpers_p, 'same_aspect_ratio_as_feature_p': the_report.same_aspect_ratio_as_feature_p, 'suitable_for_general_audience_p': the_report.suitable_for_general_audience_p, 'file_starts_at_5959_w_black_f': the_report.file_starts_at_5959_w_black_f, 'file_starts_at_1hr_w_fade_p': the_report.file_starts_at_1hr_w_fade_p, 'program_starts_at_1hr_f': the_report.program_starts_at_1hr_f, 'program_begins_with_black_frame_p': the_report.program_begins_with_black_frame_p, 'program_ends_with_black_frame_f': the_report.program_ends_with_black_frame_f, 'program_ends_with_fade_p': the_report.program_ends_with_fade_p, 'video_notes': the_report.video_notes, 'aconfig_trk1_language': the_report.aconfig_trk1_language, 'aconfig_trk1_type': the_report.aconfig_trk1_type, 'aconfig_trk2_language': the_report.aconfig_trk2_language, 'aconfig_trk2_type': the_report.aconfig_trk2_type, 'aconfig_trk3_language': the_report.aconfig_trk3_language, 'aconfig_trk3_type': the_report.aconfig_trk3_type, 'aconfig_trk4_language': the_report.aconfig_trk4_language, 'aconfig_trk4_type': the_report.aconfig_trk4_type, 'aconfig_trk5_language': the_report.aconfig_trk5_language, 'aconfig_trk5_type': the_report.aconfig_trk5_type, 'aconfig_trk6_language': the_report.aconfig_trk6_language, 'aconfig_trk6_type': the_report.aconfig_trk6_type, 'aconfig_trk7_language': the_report.aconfig_trk7_language, 'aconfig_trk7_type': the_report.aconfig_trk7_type, 'aconfig_trk8_language': the_report.aconfig_trk8_language, 'aconfig_trk8_type': the_report.aconfig_trk8_type, 'abundle_trk1_language': the_report.abundle_trk1_language, 'abundle_trk1_type': the_report.abundle_trk1_type, 'abundle_trk2_language': the_report.abundle_trk2_language, 'abundle_trk2_type': the_report.abundle_trk2_type, 'abundle_trk3_language': the_report.abundle_trk3_language, 'abundle_trk3_type': the_report.abundle_trk3_type,'abundle_trk4_language': the_report.abundle_trk4_language, 'abundle_trk4_type': the_report.abundle_trk4_type,'abundle_trk5_language': the_report.abundle_trk5_language, 'abundle_trk5_type': the_report.abundle_trk5_type,'abundle_trk6_language': the_report.abundle_trk6_language, 'abundle_trk6_type': the_report.abundle_trk6_type,'abundle_trk7_language': the_report.abundle_trk7_language, 'abundle_trk7_type': the_report.abundle_trk7_type,'abundle_trk8_language': the_report.abundle_trk8_language, 'abundle_trk8_type': the_report.abundle_trk8_type, 'aconfig_trk1_language_p': the_report.aconfig_trk1_language_p, 'aconfig_trk1_type_p': the_report.aconfig_trk1_type_p,'aconfig_trk2_language_p': the_report.aconfig_trk2_language_p, 'aconfig_trk2_type_p': the_report.aconfig_trk2_type_p,'aconfig_trk3_language_p': the_report.aconfig_trk3_language_p, 'aconfig_trk3_type_p': the_report.aconfig_trk3_type_p,'aconfig_trk4_language_p': the_report.aconfig_trk4_language_p, 'aconfig_trk4_type_p': the_report.aconfig_trk4_type_p,'aconfig_trk5_language_p': the_report.aconfig_trk5_language_p, 'aconfig_trk5_type_p': the_report.aconfig_trk5_type_p,'aconfig_trk6_language_p': the_report.aconfig_trk6_language_p, 'aconfig_trk6_type_p': the_report.aconfig_trk6_type_p,'aconfig_trk7_language_p': the_report.aconfig_trk7_language_p, 'aconfig_trk7_type_p': the_report.aconfig_trk7_type_p,'aconfig_trk8_language_p': the_report.aconfig_trk8_language_p, 'aconfig_trk8_type_p': the_report.aconfig_trk8_type_p, 'aconfig_verified_f': the_report.aconfig_verified_f, 'aconfig_verified_b': the_report.aconfig_verified_b, 'aconfig_verified_p': the_report.aconfig_verified_p, 'audio_in_sync_with_video_f': the_report.audio_in_sync_with_video_f, 'audio_in_sync_with_video_b': the_report.audio_in_sync_with_video_b, 'audio_in_sync_with_video_p': the_report.audio_in_sync_with_video_p, 'audio_tagged_correctly_f': the_report.audio_tagged_correctly_f, 'audio_tagged_correctly_b': the_report.audio_tagged_correctly_b, 'audio_tagged_correctly_p': the_report.audio_tagged_correctly_p, 'no_audio_cut_off_f': the_report.no_audio_cut_off_f, 'no_audio_cut_off_b': the_report.no_audio_cut_off_b, 'no_audio_cut_off_p': the_report.no_audio_cut_off_p, 'trt_audio_is_trt_video_f': the_report.trt_audio_is_trt_video_f, 'trt_audio_is_trt_video_b': the_report.trt_audio_is_trt_video_b, 'trt_audio_is_trt_video_p': the_report.trt_audio_is_trt_video_p, 'correct_audio_language_f': the_report.correct_audio_language_f, 'correct_audio_language_b': the_report.correct_audio_language_b,'correct_audio_language_p': the_report.correct_audio_language_p, 'audio_notes': the_report.audio_notes, 'delivery_snapshot_feature': the_report.delivery_snapshot_feature, 'delivery_snapshot_alt_audio': the_report.delivery_snapshot_alt_audio, 'delivery_snapshot_subtitle': the_report.delivery_snapshot_subtitle, 'delivery_snapshot_cc': the_report.delivery_snapshot_cc, 'delivery_snapshot_vendor_notes': the_report.delivery_snapshot_vendor_notes, 'delivery_snapshot_poster_art': the_report.delivery_snapshot_poster_art, 'delivery_snapshot_dub_card': the_report.delivery_snapshot_dub_card, 'delivery_snapshot_other': the_report.delivery_snapshot_other, 'forced_narrative_f': the_report.forced_narrative_f, 'forced_narrative_p': the_report.forced_narrative_p, 'subtitles_on_feature': the_report.subtitles_on_feature, 'subtitles_on_trailer': the_report.subtitles_on_trailer, 'forced_narrative_not_overlapping_f': the_report.forced_narrative_not_overlapping_f, 'forced_narrative_not_overlapping_p': the_report.forced_narrative_not_overlapping_p, 'subtitles_on_feature_not_overlapping': the_report.subtitles_on_feature_not_overlapping, 'subtitles_on_trailer_not_overlapping': the_report.subtitles_on_trailer_not_overlapping, 'dub_card_dimensions_match_feature': the_report.dub_card_dimensions_match_feature, 'dub_card_fps_match_feature': the_report.dub_card_fps_match_feature, 'dub_card_language_match_locale': the_report.dub_card_language_match_locale, 'dub_card_duration_4_to_5': the_report.dub_card_duration_4_to_5, 'dub_card_has_no_audio_tracks': the_report.dub_card_has_no_audio_tracks, 'dub_card_text_not_cutoff_with_cropping': the_report.dub_card_text_not_cutoff_with_cropping, 'cc_in_sync_with_video': the_report.cc_in_sync_with_video, 'subtitles_in_sync_with_video': the_report.subtitles_in_sync_with_video, 'subtitles_have_correct_language': the_report.subtitles_have_correct_language, 'assets_notes': the_report.assets_notes, 'thumb_is_jpeg': the_report.thumb_is_jpeg, 'thumb_dpi_72_or_more': the_report.thumb_dpi_72_or_more, 'thumb_profile_is_rgb': the_report.thumb_profile_is_rgb, 'thumb_same_aspect_ratio_as_video': the_report.thumb_same_aspect_ratio_as_video, 'thumb_only_active_pixels': the_report.thumb_only_active_pixels, 'thumb_horiz_at_least_640': the_report.thumb_horiz_at_least_640, 'thumb_for_each_chapter_stop': the_report.thumb_for_each_chapter_stop, 'poster_is_jpeg': the_report.poster_is_jpeg, 'poster_dpi_72_or_more': the_report.poster_dpi_72_or_more, 'poster_profile_is_rgb': the_report.poster_profile_is_rgb, 'poster_rez_at_least_1400x2100': the_report.poster_rez_at_least_1400x2100, 'poster_aspect_ratio_2x3': the_report.poster_aspect_ratio_2x3, 'poster_key_art_and_title_only': the_report.poster_key_art_and_title_only, 'poster_no_dvdcover_date_urlpromo_tagging': the_report.poster_no_dvdcover_date_urlpromo_tagging, 'image_notes': the_report.image_notes, 'delivery_snapshot_trailer': the_report.delivery_snapshot_trailer, 'trt_f': the_report.trt_f, 'trt_p': the_report.trt_p}); 
                                        }
                                        spt.app_busy.hide();
                                    }
                                }
                                if(cloned_some){
                                    ccs = '';
                                    emails = server.eval("@GET(sthpw/login_in_group['login_group','in','qc supervisor|scheduling supervisor'].sthpw/login.email)");
                                    for(var r = 0; r < emails.length; r++){
                                        if(ccs == ''){
                                            ccs = emails[r];
                                        }else{
                                            ccs = ccs + ';' + emails[r];
                                        }
                                    }
                                    note = '';
                                    for(var r = 0; r < out_lines.length; r++){
                                        if(note == ''){
                                            note = out_lines[r];
                                        }else{
                                            note = note + '\\n' + out_lines[r]; 
                                        }
                                    } 
                                    thing = server.execute_cmd('operator_view.MakeNoteWdg', {'obj_sk': original_title_sk, 'header': wo_code + " - Cloned", 'note': note, 'note_ccs': ccs});
                                    spt.alert('Done');
                                    spt.popup.close(spt.popup.get_popup(bvr.src_el));
                                    top_to_reload = document.getElementsByClassName('big_ol_metadata_wdg_' +  wo_code)[0];
                                    kwargs = {'code': wo_code, 'metadata_code': report_code}
                                    spt.api.load_panel(top_to_reload, class_name, kwargs);
                                }
                    }
                    catch(err){
                              spt.app_busy.hide();
                              spt.alert(spt.exception.handler(err));
                    }
             ''' % (report_code, login_name)}
        elif type == 'element':
            behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                            function oc(a){
                                var o = {};
                                for(var i=0;i<a.length;i++){
                                    o[a[i]]='';
                                }
                                return o;
                            }
                            function kill_nothing(something){
                                returner = something;
                                if(something == null || something == 'NOTHINGXsXNOTHING'){
                                    returner = '';
                                } 
                                return returner;
                            }
                            try{
                                var report_code = '%s';
                                var login_name = '%s';
                                var top_el = document.getElementById('cloner_for_' + report_code);
                                type = top_el.getAttribute('type');
                                wo_code = top_el.getAttribute('wo_code');
                                server = TacticServerStub.get();
                                the_report = server.eval("@SOBJECT(twog/element_eval['code','" + report_code + "'])")[0];
                                the_lines = server.eval("@SOBJECT(twog/element_eval_lines['element_eval_code','" + the_report.code + "'])");
                                the_barcodes = server.eval("@SOBJECT(twog/element_eval_barcodes['element_eval_code','" + the_report.code + "'])");
                                the_audio = server.eval("@SOBJECT(twog/element_eval_audio['element_eval_code','" + the_report.code + "'])");
                                original_title_sk = server.build_search_key('twog/title', the_report.title_code);
                                checks = top_el.getElementsByClassName('spt_input');
                                titles = {};
                                title_sources = {};
                                title_sources_tcodes = [];
                                title_codes = [];
                                out_lines = [];
                                cloned_some = false;
                                for(var r = 0; r < checks.length; r++){
                                    if(checks[r].type == 'checkbox' && checks[r].name != 'clone_toggler'){
                                        if(checks[r].checked){
                                            name = checks[r].getAttribute('name');
                                            code = name.split('lonecheck_')[1];
                                            wo = server.eval("@SOBJECT(twog/work_order['code','" + code + "'])")[0];
                                            spt.app_busy.show('Cloning report and attaching to ' + wo.process + '(' + wo.code + ')');
                                            title_code = wo.title_code;
                                            title = null;
                                            if(!(title_code in oc(title_codes))){
                                                title = server.eval("@SOBJECT(twog/title['code','" + wo.title_code + "'])")[0];
                                                title_codes.push(title.code);
                                                titles[title.code] = title; 
                                            }else{
                                                title = titles[title_code]
                                            } 
                                            source_codes = '';
                                            if(!(title_code in oc(title_sources_tcodes))){
                                                sources = server.eval("@SOBJECT(twog/title_origin['title_code','" + title_code + "'])");
                                                for(var f = 0; f < sources.length; f++){
                                                    if(source_codes == ''){
                                                        source_codes = sources[f].source_code;
                                                    }else{
                                                        source_codes = source_codes + ',' + sources[f].source_code;
                                                    }
                                                }
                                                title_sources_tcodes.push(title_code);
                                                title_sources[title_code] = source_codes;
                                            }else{
                                                source_codes = title_sources[title_code];
                                            }
                                            cloned_some = true;
                                            out_lines.push('Cloned WO: ' + wo.process + '(' + wo.code + ') from Title: ' + title.title + ' ' + title.episode + ' (' + title.code + ') Report Type: ' + type.toUpperCase()); 
                                            ele_dict = {'description': kill_nothing(the_report.description),'login': login_name,'operator': login_name,'type': kill_nothing(the_report.type),'bay': kill_nothing(the_report.bay),'machine_number': kill_nothing(the_report.machine_number),'client_code': kill_nothing(title.client_code),'client_name': kill_nothing(title.client_name),'title': kill_nothing(title.title),'episode': kill_nothing(title.episode),'version': kill_nothing(the_report.version),'title_type': kill_nothing(the_report.title_type),'format': kill_nothing(the_report.format),'standard': kill_nothing(the_report.standard),'timecode': kill_nothing(the_report.timecode),'po_number': kill_nothing(title.po_number),'style': kill_nothing(the_report.style),'order_code': kill_nothing(title.order_code),'title_code': kill_nothing(title.code),'work_order_code': kill_nothing(wo.code),'conclusion': kill_nothing(the_report.conclusion),'source_code': kill_nothing(source_codes),'wo_name': kill_nothing(wo.process),'aspect_ratio': kill_nothing(the_report.aspect_ratio),'frame_rate': kill_nothing(the_report.frame_rate),'roll_up': kill_nothing(the_report.roll_up),'bars_tone': kill_nothing(the_report.bars_tone),'black_silence_1': kill_nothing(the_report.black_silence_1),'slate_silence': kill_nothing(the_report.slate_silence),'black_silence_2': kill_nothing(the_report.black_silence_2),'video_mod_disclaimer': kill_nothing(the_report.video_mod_disclaimer),'start_of_program': kill_nothing(the_report.start_of_program),'end_of_program': kill_nothing(the_report.end_of_program),'active_video_begins': kill_nothing(the_report.active_video_begins),'active_video_ends': kill_nothing(the_report.active_video_ends),'horizontal_blanking': kill_nothing(the_report.horizontal_blanking),'vertical_blanking': kill_nothing(the_report.vertical_blanking),'video_average': kill_nothing(the_report.video_average),'video_peak': kill_nothing(the_report.video_peak),'chroma_average': kill_nothing(the_report.chroma_average),'chroma_peak': kill_nothing(the_report.chroma_peak),'video_sync': kill_nothing(the_report.video_sync),'chroma_burst': kill_nothing(the_report.chroma_burst),'setup': kill_nothing(the_report.setup),'control_track': kill_nothing(the_report.control_track),'video_rf': kill_nothing(the_report.video_rf),'front_porch': kill_nothing(the_report.front_porch),'sync_duration': kill_nothing(the_report.sync_duration),'burst_duration': kill_nothing(the_report.burst_duration),'total_runtime': kill_nothing(the_report.total_runtime),'tv_feature_trailer': kill_nothing(the_report.tv_feature_trailer),'video_aspect_ratio': kill_nothing(the_report.video_aspect_ratio),'textless_at_tail': kill_nothing(the_report.textless_at_tail),'cc_subtitles': kill_nothing(the_report.cc_subtitles),'timecodes': kill_nothing(the_report.timecodes),'vitc': kill_nothing(the_report.vitc),'ltc': kill_nothing(the_report.ltc),'record_vendor': kill_nothing(the_report.record_vendor),'record_date': kill_nothing(the_report.record_date),'language': kill_nothing(the_report.language),'comp_mne_sync': kill_nothing(the_report.comp_mne_sync),'comp_mne_phase': kill_nothing(the_report.comp_mne_phase),'missing_mne': kill_nothing(the_report.missing_mne),'average_dialogue': kill_nothing(the_report.average_dialogue),'dec_a1': kill_nothing(the_report.dec_a1),'dec_a2': kill_nothing(the_report.dec_a2),'dec_a3': kill_nothing(the_report.dec_a3),'dec_a4': kill_nothing(the_report.dec_a4),'dec_b1': kill_nothing(the_report.dec_b1),'dec_b2': kill_nothing(the_report.dec_b2),'dec_b3': kill_nothing(the_report.dec_b3),'dec_b4': kill_nothing(the_report.dec_b4),'dec_c1': kill_nothing(the_report.dec_c1),'dec_c2': kill_nothing(the_report.dec_c2),'dec_c3': kill_nothing(the_report.dec_c3),'dec_c4': kill_nothing(the_report.dec_c4),'dec_d1': kill_nothing(the_report.dec_d1),'dec_d2': kill_nothing(the_report.dec_d2),'dec_d3': kill_nothing(the_report.dec_d3),'dec_d4': kill_nothing(the_report.dec_d4),'tape_pack': kill_nothing(the_report.tape_pack),'label': kill_nothing(the_report.label),'head_logo': kill_nothing(the_report.head_logo),'tail_logo': kill_nothing(the_report.tail_logo),'notices': kill_nothing(the_report.notices),'vendor_id': kill_nothing(the_report.vendor_id),'roll_up_f': kill_nothing(the_report.roll_up_f),'bars_tone_f': kill_nothing(the_report.bars_tone_f),'black_silence_1_f': kill_nothing(the_report.black_silence_1_f),'black_silence_2_f': kill_nothing(the_report.black_silence_2_f),'slate_silence_f': kill_nothing(the_report.slate_silence_f),'video_mod_disclaimer_f': kill_nothing(the_report.video_mod_disclaimer_f),'start_of_program_f': kill_nothing(the_report.start_of_program_f),'end_of_program_f': kill_nothing(the_report.end_of_program_f)}
                                            new_ele = server.insert('twog/element_eval', ele_dict); 
                                            for(var f = 0; f < the_lines.length; f++){
                                                server.insert('twog/element_eval_lines', {'element_eval_code': new_ele.code, 'description': kill_nothing(the_lines[f].description), 'login': login_name, 'order_code': title.order_code, 'title_code': title.code, 'work_order_code': wo.code, 'timecode_in': kill_nothing(the_lines[f].timecode_in), 'timecode_out': kill_nothing(the_lines[f].timecode_out), 'field_out': kill_nothing(the_lines[f].field_out), 'field_in': kill_nothing(the_lines[f].field_in), 'media_type': kill_nothing(the_lines[f].media_type), 'type_code': kill_nothing(the_lines[f].type_code), 'scale': kill_nothing(the_lines[f].scale), 'sector_or_channel': kill_nothing(the_lines[f].sector_or_channel), 'in_source': kill_nothing(the_lines[f].in_source), 'source_code': kill_nothing(source_codes), 'in_safe': kill_nothing(the_lines[f].in_safe)});
                                            } 
                                            for(var f = 0; f < the_barcodes.length; f++){
                                                server.insert('twog/element_eval_barcodes', {'element_eval_code': new_ele.code, 'barcode': kill_nothing(the_barcodes[f].barcode), 'program_start': kill_nothing(the_barcodes[f].program_start), 'f1': kill_nothing(the_barcodes[f].f1), 'f2': kill_nothing(the_barcodes[f].f2), 'program_end': kill_nothing(the_barcodes[f].program_end), 'length': kill_nothing(the_barcodes[f].length), 'label_info': kill_nothing(the_barcodes[f].label_info), 'slate_info': kill_nothing(the_barcodes[f].slate_info), 'source_code': kill_nothing(the_barcodes[f].source_code)});
                                            } 
                                            for(var f = 0; f < the_audio.length; f++){
                                                server.insert('twog/element_eval_audio', {'element_eval_code': new_ele.code, 'content': kill_nothing(the_audio[f].content), 'tone': kill_nothing(the_audio[f].tone), 'peak': kill_nothing(the_audio[f].peak), 'channel': kill_nothing(the_audio[f].channel)});
                                            } 
                                        }
                                        spt.app_busy.hide();
                                    }
                                }
                                if(cloned_some){
                                    ccs = '';
                                    emails = server.eval("@GET(sthpw/login_in_group['login_group','in','qc supervisor|scheduling supervisor'].sthpw/login['license_type','user'].email)");
                                    for(var r = 0; r < emails.length; r++){
                                        if(ccs == ''){
                                            ccs = emails[r];
                                        }else{
                                            ccs = ccs + ';' + emails[r];
                                        }
                                    }
                                    note = '';
                                    for(var r = 0; r < out_lines.length; r++){
                                        if(note == ''){
                                            note = out_lines[r];
                                        }else{
                                            note = note + '\\n' + out_lines[r]; 
                                        }
                                    }
                                    note_data = {'obj_sk': original_title_sk,
                                                 'header': wo_code + " - Cloned",
                                                 'note': note,
                                                 'note_ccs': ccs,
                                                 'note_process': 'Cloned WO: ' + wo_code};
                                    thing = server.execute_cmd('operator_view.MakeNoteWdg', note_data);
                                    spt.alert('Done');
                                    spt.popup.close(spt.popup.get_popup(bvr.src_el));
                                    top_to_reload = document.getElementsByClassName('big_ol_element_wdg_' +  wo_code)[0];
                                    kwargs = {'code': wo_code, 'element_eval_code': report_code}
                                    var class_name = 'qc_reports.qc_reports.ElementEvalWdg';
                                    spt.api.load_panel(top_to_reload, class_name, kwargs);
                                }
                    }
                    catch(err){
                              spt.app_busy.hide();
                              spt.alert(spt.exception.handler(err));
                    }
             ''' % (report_code, login_name)}

        return behavior

    def get_toggle_behavior(my, report_code):
        toggle_behavior = {'css_class': 'clickme', 'type': 'change', 'cbjs_action': '''        
                        try{
                            var report_code = '%s';
                            var top_el = document.getElementById('cloner_for_' + report_code);
                            inputs = top_el.getElementsByClassName('spt_input');
                            var curr_val = bvr.src_el.checked;
                            for(var r = 0; r < inputs.length; r++){
                                if(inputs[r].type == 'checkbox' && inputs[r].name != 'clone_toggler'){
                                    inputs[r].checked = curr_val;
                                }
                            }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
        ''' % report_code}
        return toggle_behavior

    def get_add_titles_behavior(my, report_code):
        behavior = {'css_class': 'clickme', 'type': 'change', 'cbjs_action': '''        
                        function oc(a){
                            var o = {};
                            for(var i=0;i<a.length;i++){
                                o[a[i]]='';
                            }
                            return o;
                        }
                        try{
                          var server = TacticServerStub.get();
                          report_code = '%s';
                          top_el = document.getElementById('cloner_for_' + report_code);
                          wo_code = top_el.getAttribute('wo_code');
                          type = top_el.getAttribute('type');
                          title_codes = bvr.src_el.value;
                          bvr.src_el.value = '';
                          loader_el = top_el.getElementById('new_titles');
                          loader_el.setAttribute('id','added_titles');
                          spt.app_busy.show('Adding title(s) to list...');
                          spt.api.load_panel(loader_el, 'qc_reports.qc_reports.QCReportClonerWdg', {'type': type, 'wo_code': wo_code, 'report_code': report_code, 'new_titles': title_codes}); 
                          spt.app_busy.hide();
                          
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (report_code)}
        return behavior

    def get_display(my):
        from tactic_client_lib import TacticServerStub
        from pyasm.common import Environment
        login = Environment.get_login()
        this_user = login.get_login()
        wo_code = my.kwargs.get('wo_code');
        report_code = my.kwargs.get('report_code');
        type = my.kwargs.get('type')
        widget = DivWdg()
        server = TacticServerStub.get()
        thing = None
        if 'new_titles' not in my.kwargs.keys():
            widget.add_attr('id','cloner_for_%s' % report_code)
            widget.add_attr('wo_code',wo_code)
            widget.add_attr('report_code',report_code)
            widget.add_attr('type',type)
            widget.add_style('width: 400px;')
            wo = server.eval("@SOBJECT(twog/work_order['code','%s'])" % wo_code)[0]
            order = server.eval("@SOBJECT(twog/order['code','%s'])" % wo.get('order_code'))[0]
            this_title = server.eval("@SOBJECT(twog/title['code','%s'])" % wo.get('title_code'))[0]
            #all_titles = server.eval("@SOBJECT(twog/title['order_code','%s'])" % wo.get('order_code'))
            all_titles = [this_title]
            table = Table()
            table.add_style('width: 100%s;' % '%')
            #Need Select All Checkbox Here
            toggler = CheckboxWdg('clone_toggler')
            toggler.set_value(False)
            toggler.add_behavior(my.get_toggle_behavior(report_code))
            chktbl = Table()
            chktbl.add_row()
            chktbl.add_cell(' ') 
            ct = chktbl.add_cell('Select/Deselect All')
            ct.add_attr('align','right')
            chktbl.add_cell(toggler)
            table.add_row()
            table.add_cell(chktbl)
            #Need Title/Order Adder Here
            tt3 = Table()
            tt3.add_row()
            tt3.add_cell(' ')
            tt3.add_cell('Include Titles (Comma delimited codes):')
            adder = TextWdg('additional_titles')
            adder.add_behavior(my.get_add_titles_behavior(report_code))
            tt3.add_cell(adder)
            table.add_row()
            table.add_cell(tt3)
            order_row = table.add_row()
            order_row.add_style('background-color: #2e3a52;')
            nw1 = table.add_cell('ORDER: %s (%s)' % (order.get('name'), order.get('code')))
            nw1.add_attr('nowrap','nowrap')
            for title in all_titles:
                title_color = '#2e6ce4'
                title_code = title.get('code')
                if title_code != this_title.get('code'):
                    title_color = '#6e4e0f'
                title_row = table.add_row()
                title_row.add_style('background-color: %s;' % title_color)
                tname = title.get('title')
                ep = title.get('episode')
                if ep not in [None,'']:
                    tname = '%s Episode: %s' % (tname, ep)
                nw2 = table.add_cell('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TITLE: %s (%s)' % (tname, title_code))
                nw2.add_attr('nowrap','nowrap')
                wotbl = Table()
                wotbl.add_style('width: 100%s;' % '%')
                wotbl.add_style('background-color: %s;' % title_color)
                #qc_wos = server.eval("@SOBJECT(sthpw/task['title_code','%s']['search_type','twog/proj?project=twog']['assigned_login_group','in','qc|qc supervisor']['process','~','eature'])" % title_code)
                qc_wos = server.eval("@SOBJECT(sthpw/task['title_code','%s']['search_type','twog/proj?project=twog']['assigned_login_group','in','qc|qc supervisor'])" % title_code)
                for qcwo in qc_wos:
                    qcwocode = qcwo.get('lookup_code')
                    if qcwocode != wo_code:
                        wotbl.add_row()
                        check = CheckboxWdg('clonecheck_%s' % qcwocode)
                        #check.set_persistence()
                        check.set_value(False)
                        wotbl.add_cell('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
                        wotbl.add_cell(check)
                        nw3 = wotbl.add_cell('WO: %s,  Assigned: %s, Code: %s' % (qcwo.get('process'), qcwo.get('assigned'), qcwocode)) 
                        nw3.add_attr('nowrap','nowrap')
                table.add_row()
                table.add_cell(wotbl)
                        
            widget.add(table)
            loader_tbl = Table()
            loader_tbl.add_attr('id','new_titles')
            loader_tbl.add_style('width: 100%s;' % '%')
            widget.add(loader_tbl)
            tbl2 = Table()
            tbl2.add_style('width: 100%s;' % '%')
            tbl2.add_row()
            t1 = tbl2.add_cell(' ')
            t1.add_attr('width','47%s' % '%')
            cloner = tbl2.add_cell('<input type="button" value="Clone"/>')
            cloner.add_attr('align','center')
            cloner.add_behavior(my.get_clone_behavior(report_code, type, this_user))
            t2 = tbl2.add_cell(' ')
            t2.add_attr('width','47%s' % '%')
            widget.add(tbl2)
            thing = widget
        else:
            new_titles = my.kwargs.get('new_titles').split(',')
            new_titles2 = []
            for t in new_titles:
                if 'TITLE' in t:
                    new_titles2.append(t)
                elif 'WORK_ORDER' in t:
                    that_title = server.eval("@GET(twog/work_order['code','%s'].title_code)" % t)
                    if that_title not in [None,'']:
                        that_title = that_title[0]
                        new_titles2.append(that_title)
                elif 'ORDER' in t:
                    other_titles = server.eval("@GET(twog/title['order_code','%s'].code)" % t)
                    for ot in other_titles:
                        new_titles2.append(ot)
                else:
                    other_titles = server.eval("@GET(twog/order['po_number','%s'].twog/title.code)" % t)
                    for ot in other_titles:
                        new_titles2.append(ot)
                    
            orders = {}
            for t in new_titles2:
                t = t.strip()
                this_title = server.eval("@SOBJECT(twog/title['code','%s'])" % t)[0]
                title_code = this_title.get('code')
                order = None
                if this_title.get('order_code') not in orders.keys():
                    order = server.eval("@SOBJECT(twog/order['code','%s'])" % this_title.get('order_code'))[0]
                    orders[order.get('code')] = order
                else:
                    order = orders[this_title.get('order_code')]
                table = Table()
                table.add_style('width: 100%s;' % '%')
                #Need Select All Checkbox Here
                order_row = table.add_row()
                order_row.add_style('background-color: #2e3a52;')
                nw1 = table.add_cell('ORDER: %s (%s)' % (order.get('name'), order.get('code')))
                nw1.add_attr('nowrap','nowrap')
                title_color = '#6e4e0f'
                title_row = table.add_row()
                title_row.add_style('background-color: %s;' % title_color)
                tname = this_title.get('title')
                ep = this_title.get('episode')
                if ep not in [None,'']:
                    tname = '%s Episode: %s' % (tname, ep)
                nw2 = table.add_cell('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;TITLE: %s (%s)' % (tname, title_code))
                nw2.add_attr('nowrap','nowrap')
                wotbl = Table()
                wotbl.add_style('width: 100%s;' % '%')
                wotbl.add_style('background-color: %s;' % title_color)
                #qc_wos = server.eval("@SOBJECT(twog/work_order.WT:sthpw/task['title_code','%s']['assigned_login_group','in','qc|qc supervisor'])" % title_code)
                qc_wos_expr = "@SOBJECT(sthpw/task['title_code','%s']['search_type','twog/proj?project=twog']['assigned_login_group','in','qc|qc supervisor'])" % title_code
                qc_wos = server.eval(qc_wos_expr)
                for qcwo in qc_wos:
                    qcwocode = qcwo.get('lookup_code')
                    if qcwocode != wo_code:
                    #I don't know if we will want this back or not, but requiring 'feature' to be in the name is off for testing purposes
#                        if 'feature' in qcwo.get('process').lower(): 
#                            wotbl.add_row()
#                            check = CheckboxWdg('clonecheck_%s' % qcwocode)
#                            #check.set_persistence()
#                            check.set_value(False)
#                            wotbl.add_cell('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
#                            wotbl.add_cell(check)
#                            nw3 = wotbl.add_cell('WO: %s,  Assigned: %s, Code: %s' % (qcwo.get('process'), qcwo.get('assigned'), qcwocode)) 
#                            nw3.add_attr('nowrap','nowrap')
                        wotbl.add_row()
                        check = CheckboxWdg('clonecheck_%s' % qcwocode)
                        #check.set_persistence()
                        check.set_value(False)
                        wotbl.add_cell('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
                        wotbl.add_cell(check)
                        nw3 = wotbl.add_cell('WO: %s,  Assigned: %s, Code: %s' % (qcwo.get('process'), qcwo.get('assigned'), qcwocode)) 
                        nw3.add_attr('nowrap','nowrap')
                table.add_row()
                table.add_cell(wotbl)
                            
                loader_tbl = Table()
                loader_tbl.add_attr('id','new_titles')
                loader_tbl.add_style('width: 100%s;' % '%')
                table.add_row()
                table.add_cell(loader_tbl)
                thing = table
        return thing

class QCReportSelectorWdg(BaseTableElementWdg):

    def init(my):
        nothing = 'true'
 
    def report_chosen(my, code, type, name):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                          var code = '%s';
                          var type = '%s';
                          var name = '%s';
                          var class_name = 'qc_reports.qc_reports.' + type;
                          kwargs = {'code': code}
                          spt.popup.close(spt.popup.get_popup(bvr.src_el));
                          //spt.panel.load_popup(name + ' for ' + code, class_name, kwargs);
                          spt.tab.add_new(type + '_qc_report_for_' + code, name + ' for ' + code, class_name, kwargs); 
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (code, type, name)}

        return behavior

    def get_display(my):
        code = my.kwargs.get('code');
        widget = DivWdg()
        table = Table()
        types = {'PreQual Evaluation': 'PreQualEvalWdg', 'Element Evaluation': 'ElementEvalWdg', 'Technical Evaluation': 'TechEvalWdg', 'MetaData Report': 'MetaDataReportWdg'}
        colors = {'PreQual Evaluation': '#a2b2d2', 'Element Evaluation': '#d5c9dd', 'Technical Evaluation': '#aa8e98', 'MetaData Report': '#c6e2d9'}
        table.add_row()
        t1 = table.add_cell("<b>Please Choose the type of QC Report to attach to %s</b>" % code)
        t1.add_attr('nowrap','nowrap')
        for type in types.keys():
            table.add_row()
            n = table.add_cell(' ')
            gr = table.add_row()
            gr.add_style('background-color: %s;' % (colors[type]))
            c = table.add_cell('<b><u>%s</u></b>' % type)
            c.add_attr('goclass',types[type])
            c.add_style('cursor: pointer;')
            c.add_behavior(my.report_chosen(code, types[type], type))
             
        widget.add(table)
 
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
                                //spt.api.load_panel(linestbl, 'qc_reports.qc_reports.PreQualEvalLinesWdg', send_data); 
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
                            spt.api.load_panel(addportion, 'qc_reports.qc_reports.PreQualEvalLinesWdg', send_data); 
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
        import time, datetime
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
        

class PrintQCReportWdg(Command):

    def __init__(my, **kwargs):
        from client.tactic_client_lib import TacticServerStub
        from pyasm.common import Environment
        super(PrintQCReportWdg, my).__init__(**kwargs)
        my.html = str(kwargs.get('html'))
        my.preppend_file_name = str(kwargs.get('preppend_file_name'))
        my.type = str(kwargs.get('type'))

    def check(my):
        return True
    
    def execute(my):   
        new_qc_file = 'generic_blah'
        if my.type == '':
            new_qc_file = '/var/www/html/qc_reports/work_orders/%s.html' % (my.preppend_file_name)
        else:
            new_qc_file = '/var/www/html/qc_reports/work_orders/%s_%s.html' % (my.preppend_file_name, my.type)
        if os.path.exists(new_qc_file):
            os.system('rm -rf %s' % new_qc_file)
        new_guy = open(new_qc_file, 'w') 
        new_guy.write(my.html.encode('utf-8'))
        new_guy.close()
        return ''


    def check_security(my):
        '''give the command a callback that allows it to check security'''
        return True

    def get_title(my):
        return "Print"

class PreQualEvalWdg(BaseTableElementWdg):

    def init(my):
        nothing = 'true'
        my.formats = ['Electronic/File', 'DBC', 'D5', 'HDCAM SR', 'NTSC', 'PAL']
        my.frame_rates = ['23.98fps','59.94i','50i','29.97fps','59.94p','DFTC','NDFTC','PAL/EBU']
        my.machines = ['VTR221','VTR222','VTR223','VTR224','VTR225','VTR231','VTR232','VTR233','VTR234','VTR235','VTR251','VTR252','VTR253','VTR254','VTR255','VTR261','VTR262','VTR263','VTR264','VTR265','VTR281','VTR282','VTR283','VTR284','VTR285','FCP01','FCP02','FCP03','FCP04','FCP05','FCP06','FCP07','FCP08','FCP09','FCP10','FCP11','FCP12','Amberfin','Clipster','Stradis']
        my.styles = ['Technical','Spot QC','Mastering']
        my.aspect_ratios = ['16x9 1.33','16x9 1.33 Pan & Scan','16x9 1.78 Anamorphic','16x9 1.78 Full Frame','16x9 1.85 Letterbox','16x9 1.85 Matted','16x9 1.85 Matted Anamorphic','16x9 2.20','16x9 2.20 Letterbox','16x9 2.35 Anamorphic','16x9 2.35 Letterbox','16x9 2.40 Letterbox','16x9 2.55 Letterbox','4x3 1.33 Full Frame','4x3 1.78 Letterbox','4x3 1.85 Letterbox','4x3 2.35 Letterbox','4x3 2.40 Letterbox']

        my.standards = ['625','525','720','1080 (4:4:4)','1080','PAL','NTSC']

    def kill_nothing(my, val):
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
                                  var class_name = 'qc_reports.qc_reports.PreQualEvalWdg';
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
                          //thing = server.execute_cmd('qc_reports.qc_reports.PrintQCReportWdg', {'html': '<table>' + top_el.innerHTML + '</table>','wo_code': wo_code, 'type': type});
                          thing = server.execute_cmd('qc_reports.qc_reports.PrintQCReportWdg', {'html': '<table>' + new_html + '</table>','preppend_file_name': wo_code, 'type': type});
                          var url = 'http://tactic01/qc_reports/work_orders/' + wo_code + '_prequal.html';
                          printExternal(url);
                          if(pq_code != '' && pq_code != null){
                              //close, then reload page
                              var class_name = 'qc_reports.qc_reports.PreQualEvalWdg';
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
                          var class_name = 'qc_reports.qc_reports.PreQualEvalWdg';
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
                          var class_name = 'qc_reports.qc_reports.QCReportClonerWdg';
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
                                  var class_name = 'qc_reports.qc_reports.PreQualEvalWdg';
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
        import time, datetime
        from tactic_client_lib import TacticServerStub
        from pyasm.common import Environment
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
        code = my.kwargs.get('code');
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
        prequal = {'code': '', 'description': '', 'timestamp': this_timestamp, 'login': this_user, 'operator': this_user, 'type': '', 'bay': '', 'machine_number': '', 'client_code': my.kill_nothing(title.get('client_code')), 'client_name': my.kill_nothing(title.get('client_name')), 'title': my.kill_nothing(title.get('title')), 'episode': my.kill_nothing(title.get('episode')), 'version': '', 'title_type': '', 'timecode': '', 'po_number': my.kill_nothing(title.get('po_number')), 'style': '', 'title_code': work_order.get('title_code'), 'order_code': work_order.get('order_code'), 'work_order_code': code, 'conclusion': '', 'source_code': '', 'standard': my.kill_nothing(title.get('deliverable_standard')), 'aspect_ratio': my.kill_nothing(title.get('deliverable_aspect_ratio')), 'frame_rate': my.kill_nothing(title.get('deliverable_frame_rate')), 'format': my.kill_nothing(title.get('deliverable_format'))}
        prequal_lines = [{'code': '', 'description': '', 'timestamp': this_timestamp, 's_status': '', 'keywords': '', 'login': this_user, 'id': '', 'name': '', 'prequal_eval_code': '', 'order_code': work_order.get('order_code'), 'title_code': work_order.get('title_code'), 'work_order_code': code, 'timecode': '', 'media_type': '', 'type_code': '', 'scale': '', 'sector_or_channel': '', 'in_source': '', 'source_code': ''}]
        if 'prequal_code' in my.kwargs.keys():
            prequal_code = str(my.kwargs.get('prequal_code'))
            prequal = server.eval("@SOBJECT(twog/prequal_eval['code','%s'])" % prequal_code)[0]
            prequal_lines = server.eval("@SOBJECT(twog/prequal_eval_lines['prequal_eval_code','%s'])" % prequal_code)
        
        wo_pevals = server.eval("@SOBJECT(twog/prequal_eval['work_order_code','%s']['code','!=','%s'])" % (code, prequal_code))
        title_pevals = server.eval("@SOBJECT(twog/prequal_eval['title_code','%s']['work_order_code','!=','%s']['code','!=','%s'])" % (work_order.get('title_code'), work_order.get('code'), prequal_code))
        others = Table()
        others.add_style('background-color: #528B8B; width: 100%s;' % '%');
        cols = ['#537072','#518A1A']
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
                colsct = colsct + 1
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
                colsct = colsct + 1
            
        
        widget.add_attr('class','big_ol_prequal_wdg_%s' % code)
        widget.add_attr('prequal_code',prequal.get('code'))
        table = Table()
        table.add_attr('class','printable_prequal_form_%s' % code)
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
        address.add_attr('nowrap','nowrap')
        address.add_style('font-size: 9px;')
        img_tbl.add_cell(ad)
        acr_s = ['APPROVED','CONDITION','REJECTED']
        acr = Table()
        for mark in acr_s:
            acr.add_row()
            acr1 = CheckboxWdg('marked_%s' % mark)
            #acr1.set_persistence()
            if mark in prequal.get('conclusion'):
                acr1.set_value(True)
            else:
                acr1.set_value(False)
            acr.add_cell(acr1)
            acr.add_cell('<b>%s</b>' % mark)
        rtbl = Table()
        rtbl.add_row()
        big = rtbl.add_cell("<b>PREQUAL EVALUATION</b>")
        big.add_attr('nowrap','nowrap')
        big.add_attr('align','center')
        big.add_attr('valign','center')
        big.add_style('font-size: 40px;')
        rtbl.add_cell(acr)
        toptbl = Table()
        toptbl.add_row()
        toptbl.add_cell(img_tbl)
        toptbl.add_cell(rtbl)
        bay_sel = SelectWdg('bay_select')
        bay_sel.add_attr('id','bay')
        bay_sel.add_style('width: 135px;')
        bay_sel.append_option('--Select--','')
        for i in range(1,13):
            bay_sel.append_option('Bay %s' % i,'Bay %s' % i)
        if prequal.get('bay') not in [None,'']:
            bay_sel.set_value(prequal.get('bay'))

        style_sel = SelectWdg('style_select')
        style_sel.add_attr('id','style')
        style_sel.add_style('width: 135px;')
        style_sel.append_option('--Select--','')
        for s in my.styles:
            style_sel.append_option(s,s)
        if prequal.get('style') not in [None,'']:
            style_sel.set_value(prequal.get('style'))

        machine_sel = SelectWdg('machine_select')
        machine_sel.add_attr('id','machine_number')
        machine_sel.add_style('width: 135px;')
        machine_sel.append_option('--Select--','')
        for m in my.machines:
            machine_sel.append_option(m,m)
        if prequal.get('machine_number') not in [None,'']:
            machine_sel.set_value(prequal.get('machine_number'))

        format_sel = SelectWdg('format_select')
        format_sel.add_attr('id','format')
        format_sel.add_style('width: 153px;')
        format_sel.append_option('--Select--','')
        for f in my.formats: 
            format_sel.append_option(f,f)
        if prequal.get('format') not in [None,'']:
            format_sel.set_value(prequal.get('format'))

        ar_select = SelectWdg('aspect_ratio_select')
        ar_select.add_attr('id','aspect_ratio')
        ar_select.add_style('width: 153px;')
        ar_select.append_option('--Select--','')
        for a in my.aspect_ratios:
            ar_select.append_option(a,a)
        if prequal.get('aspect_ratio') not in [None,'']:
            ar_select.set_value(prequal.get('aspect_ratio'))

        frame_rate_sel = SelectWdg('frame_rate_select')
        frame_rate_sel.add_attr('id','frame_rate')
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
        printtbl.add_style('background-color: #528B8B; width: 100%s;' % '%');
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
        ttbl.add_style('background-color: #528B8B; width: 100%s;' % '%');
        ttbl.add_row()
        tt1 = ttbl.add_cell(others)
        tt1.add_attr('width','100%s' % '%')
        ttbl.add_row()
        tt2 = ttbl.add_cell(printtbl)
        tt2.add_attr('width','100%s' % '%')
        widget.add(ttbl)
        widget.add(table)
        widget.add_style("font-family: Arial, Helvetica, sans-serif;") 
        widget.add_style("font-size: 14px;");
        if show_save and 'TITLE' not in original_code:
            widget.add(stbl)

        return widget

class ElementEvalAudioWdg(BaseTableElementWdg):
    def init(my):
        nothing = 'true'
        my.content_pull = '<select REPLACE_ME><option value="">--Select--</option>'
        my.contents = ['5.1 Left', '5.1 Right', '5.1 Center','5.1 LFE','5.1 Left Surround','5.1 Right Surround','Stereo Left','Stereo Right','Stereo Music Left','Stereo Music Right','Stereo FX Left','Stereo FX Right','Stereo M&E Left','Stereo M&E Right','Stereo Dialogue','Mono Narration','M.O.S','Mono','Mono Dialogue','Mono Music','Mono FX','Various']
        for c in my.contents:
            my.content_pull = '%s<option value="%s">%s</option>' % (my.content_pull, c, c)
        my.content_pull = '%s</select>' % my.content_pull


    def get_nums_only(my):
        behavior = {'css_class': 'clickme', 'type': 'keyup', 'cbjs_action': '''        
                try{
                    var entered = bvr.src_el.value;
                    var old_val = bvr.src_el.getAttribute('old_val');
                    if(isNaN(entered)){
                        alert(entered + " is not a number. Please only enter numbers here.")
                        bvr.src_el.value = old_val;
                    }else{
                        bvr.src_el.setAttribute('old_val',entered);
                    }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         '''}
        return behavior

    def selbox(my, name, val, code, old_val, width='200px'):
        fresh = my.content_pull
        build_str = 'id="%s" code="%s" old_val="%s" width="%s"' % (name, code, old_val, width) 
        fresh = fresh.replace('REPLACE_ME',build_str)
        selected_str = 'value="%s"' % val
        if selected_str in fresh:
            fresh = fresh.replace(selected_str, '%s selected="selected"' % selected_str)
        else:
            fresh = fresh.replace('</select>', '<option value="%s" selected="selected">%s</option></select>' % (val, val))
        return fresh

    def txtbox(my, name, val, code, old_val, width='200px', js='no'):
        txt = TextWdg(name)
        txt.add_attr('id',name)
        txt.add_attr('code',code)
        txt.add_attr('old_val',old_val)
        txt.add_style('width: %s;' % width)
        txt.set_value(val) 
        if js == 'yes':
            txt.add_behavior(my.get_nums_only())
        return txt

    def get_display(my):
        import time, datetime
        from tactic_client_lib import TacticServerStub
        from pyasm.common import Environment
        code = ''
        element_auds = []
        server = TacticServerStub.get()
        wo_code = str(my.kwargs.get('wo_code'))
        if 'code' in my.kwargs.keys():
            code = my.kwargs.get('code')
            element_auds = server.eval("@SOBJECT(twog/element_eval_audio['element_eval_code','%s']['@ORDER_BY','channel'])" % code)
        force_it = False
        if 'force_it' in my.kwargs.keys():
            if my.kwargs.get('force_it') == 'true':
                force_it = True
        channels = 21
        if 'channels' in my.kwargs.keys():
            channels = int(my.kwargs.get('channels'))
        if len(element_auds) > 0 and not force_it:
            channels = len(element_auds)
        leng = len(element_auds) 
        for i in range(leng, channels - leng):
            element_auds.append(None)
        a_third = int(channels/3) 
        if int(float(float(float(channels)/float(3))*1000)) != a_third * 1000:
            a_third = a_third + 1
        grand_table = Table()
        grand_table.add_attr('id','audio_information')
        grand_table.add_attr('channels',channels)
        grand_table.add_row()
        atable = None
        for i in range(0,channels):
            if i in [0,a_third,(a_third * 2)]:
                atable = Table()
                atable.add_attr('class','atable')
                atable.add_attr('border','1')
                atable.add_row()
                atable.add_cell('Channel')
                atable.add_cell('Content')
                atable.add_cell('Tone')
                atable.add_cell('Peak')
            atable.add_row()
            the_code = ''
            channel = ''
            content = ''
            tone = ''
            peak = ''
            if i < len(element_auds):
                if element_auds[i] != None:
                    the_code = element_auds[i].get('code')
                    channel = element_auds[i].get('channel')     
                    content = element_auds[i].get('content')     
                    tone = element_auds[i].get('tone')     
                    peak = element_auds[i].get('peak')     
            #atable.add_cell('<input type="text" id="channel-%s" class="channel" code="%s" value="%s" old_val="%s" style="width: 55px;"/>' % (i, the_code, channel, channel))
            atable.add_cell(my.txtbox('channel-%s' % i,channel,the_code,channel,width='68px',js='yes'))
            #atable.add_cell('<input type="text" id="content-%s" class="content" code="%s" value="%s" style="width: 126px;"/>' % (i, the_code, content))
            #sellie = atable.add_cell(my.selbox('content-%s' % i,content,the_code,content,width='162px'))
            #sellie.add_attr('class','select_cell')
            sellie = atable.add_cell(my.txtbox('content-%s' % i,content,the_code,content,width='132px'))
            #atable.add_cell('<input type="text" id="tone-%s" class="tone" code="%s" value="%s" style="width: 55px;"/>' % (i, the_code, tone))
            atable.add_cell(my.txtbox('tone-%s' % i,tone,the_code,tone,width='68px'))
            #atable.add_cell('<input type="text" id="peak-%s" class="peak" code="%s" value="%s" style="width: 55px;"/>' % (i, the_code, peak))
            atable.add_cell(my.txtbox('peak-%s' % i,peak,the_code,peak,width='68px'))
            if i in [a_third-1,(a_third*2)-1,channels-1]:
                grand_cell = grand_table.add_cell(atable)
                grand_cell.add_attr('valign','top')
                if i != channels-1:
                    grand_table.add_cell('&nbsp;')
                atable = None
        return grand_table

class ElementEvalBarcodesWdg(BaseTableElementWdg):
    def init(my):
        nothing = 'true'

    def get_kill_bvr(my, rowct, wo_code, ell_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                            var rowct = Number('%s');
                            var wo_code = '%s';
                            var ell_code = '%s';
                            if(confirm("Do you really want to delete this evaluation line?")){
                                server = TacticServerStub.get();
                                server.retire_sobject(server.build_search_key('twog/element_eval_barcodes',ell_code));
                                top_els = document.getElementsByClassName('printable_element_form_' + wo_code);
                                top_el = null;
                                for(var r = 0; r < top_els.length; r++){
                                    if(top_els[r].getAttribute('element_code') == ell_code){
                                        top_el = top_els[r];
                                    }
                                }
                                bctable = top_el.getElementsByClassName('bctable')[0];
                                element_barcodes = bctable.getElementsByClassName('element_barcodes');
                                for(var r = 0; r < element_barcodes.length; r++){
                                    if(element_barcodes[r].getAttribute('line') == rowct){
                                        element_barcodes[r].innerHTML = '';
                                        element_barcodes[r].style.display = 'none';
                                    }
                                }
                                //send_data = {'rowct': rowct, 'wo_code': wo_code, 'code': ell_code};
                                //spt.api.load_panel(bctable, 'qc_reports.qc_reports.ElementEvalLinesWdg', send_data); 
                            }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (rowct, wo_code, ell_code)}
        return behavior

    def get_add_line(my, rowct, wo_code, ell_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                            bvr.src_el.innerHTML = '';
                            var rowct = Number('%s');
                            var wo_code = '%s';
                            var ell_code = '%s';
                            top_els = document.getElementsByClassName('printable_element_form_' + wo_code);
                            top_el = null;
                            for(var r = 0; r < top_els.length; r++){
                                if(top_els[r].getAttribute('element_code') == ell_code){
                                    top_el = top_els[r];
                                }
                            }
                            bctable = top_el.getElementsByClassName('bctable');
                            lastbctable = bctable[bctable.length - 1];
                            addportions = top_el.getElementsByClassName('new_barcode_line');
                            addportion = addportions[addportions.length - 1];
                            addportion.setAttribute('class','element_barcodes');
                            addportion.setAttribute('line',Number(rowct) + 1);
                            addportion.setAttribute('code','');
                            send_data = {'rowct': rowct + 1, 'wo_code': wo_code};
                            spt.api.load_panel(addportion, 'qc_reports.qc_reports.ElementEvalBarcodesWdg', send_data); 
                            newrow = lastbctable.insertRow(-1);
                            newrow.setAttribute('class','new_barcode_line');
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (rowct, wo_code, ell_code)}
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
        import time, datetime
        from tactic_client_lib import TacticServerStub
        from pyasm.common import Environment
        login = Environment.get_login()
        this_user = login.get_login()
        code = ''
        element_bcs = None
        rowct = 1
        server = TacticServerStub.get()
        wo_code = str(my.kwargs.get('wo_code'))
        if 'code' in my.kwargs.keys():
            code = my.kwargs.get('code')
            element_bcs = server.eval("@SOBJECT(twog/element_eval_barcodes['element_eval_code','%s'])" % code)
        elif 'rowct' in my.kwargs.keys():
            rowct = int(my.kwargs.get('rowct'))
        bctable = Table()
        bctable.add_attr('class','bctable')
        bctable.add_attr('border','1')
        if rowct == 1:
            bctable.add_row()
            bctable.add_cell("PART")
            bctable.add_cell("BARCODE")
            bctable.add_cell("PROGRAM START")
            bctable.add_cell("F")
            bctable.add_cell("PROGRAM END")
            bctable.add_cell("F")
            bctable.add_cell("LENGTH")
            bctable.add_cell("LABEL INFO")
            bctable.add_cell("SLATE INFO")
            plus_butt = bctable.add_cell(" ")
        if code not in [None,'']:
            #plus_butt.add_style('cursor: pointer;')
            #plus_butt.add_behavior(my.get_add_line())
            for el in element_bcs:
                brow = bctable.add_row()
                brow.add_attr('line',rowct)
                brow.add_attr('code',el.get('code'))
                brow.add_attr('class','element_barcodes')
                nw = bctable.add_cell('Part %s' % rowct)
                nw.add_attr('nowrap','nowrap')
                #bctable.add_cell('<input type="text" id="barcode-%s" class="barcode" value="%s" style="width: 100px;"/>' % (rowct, el.get('barcode')))
                bctable.add_cell(my.txtbox('barcode-%s' % rowct, el.get('barcode'),width='100px',js='no'))
                #bctable.add_cell('<input type="text" id="program_start-%s" class="program_start" value="%s" style="width: 150px;"/>' % (rowct, el.get('program_start')))
                bctable.add_cell(my.txtbox('program_start-%s' % rowct, el.get('program_start'),width='150px',js='yes'))
                #bctable.add_cell('<input type="text" id="f1-%s" class="f1" value="%s" style="width: 20px;"/>' % (rowct, el.get('f1')))
                bctable.add_cell(my.txtbox('f1-%s' % rowct, el.get('f1'),width='20px',js='no'))
                #bctable.add_cell('<input type="text" id="program_end-%s" class="program_end" value="%s" style="width: 150px;"/>' % (rowct, el.get('program_end')))
                bctable.add_cell(my.txtbox('program_end-%s' % rowct, el.get('program_end'),width='150px',js='yes'))
                #bctable.add_cell('<input type="text" id="f2-%s" class="f2" value="%s" style="width: 20px;"/>' % (rowct, el.get('f2')))
                bctable.add_cell(my.txtbox('f2-%s' % rowct, el.get('f2'),width='20px',js='no'))
                #bctable.add_cell('<input type="text" id="length-%s" class="length" value="%s" style="width: 100px;"/>' % (rowct, el.get('length')))
                bctable.add_cell(my.txtbox('length-%s' % rowct, el.get('length'),width='155px',js='yes'))
                #bctable.add_cell('<input type="text" id="label_info-%s" class="label_info" value="%s" style="width: 160px;"/>' % (rowct, el.get('label_info')))
                bctable.add_cell(my.txtbox('label_info-%s' % rowct, el.get('label_info'),width='190px',js='no'))
                #bctable.add_cell('<input type="text" id="slate_info-%s" class="slate_info" value="%s" style="width: 160px;"/>' % (rowct, el.get('slate_info')))
                bctable.add_cell(my.txtbox('slate_info-%s' % rowct, el.get('slate_info'),width='190px',js='no'))
                killer = bctable.add_cell('<b>X</b>')#This must delete the entry
                killer.add_style('cursor: pointer;')
                killer.add_behavior(my.get_kill_bvr(rowct, wo_code, el.get('code')))
                rowct = rowct + 1

        erow = bctable.add_row()
        erow.add_attr('line',rowct)
        erow.add_attr('code','')
        erow.add_attr('class','element_barcodes')
        nw2 = bctable.add_cell('Part %s' % rowct)
        nw2.add_attr('nowrap','nowrap')
        #bctable.add_cell('<input type="text" id="barcode-%s" class="barcode" value="" style="width: 100px;"/>' % (rowct))
        bctable.add_cell(my.txtbox('barcode-%s' % rowct,'',width='100px',js='no'))
        #bctable.add_cell('<input type="text" id="program_start-%s" class="program_start" value="" style="width: 150px;"/>' % (rowct))
        bctable.add_cell(my.txtbox('program_start-%s' % rowct,'',width='150px',js='yes'))
        #bctable.add_cell('<input type="text" id="f1-%s" class="f1" value="" style="width: 20px;"/>' % (rowct))
        bctable.add_cell(my.txtbox('f1-%s' % rowct,'',width='20px',js='yes'))
        #bctable.add_cell('<input type="text" id="program_end-%s" class="program_end" value="" style="width: 150px;"/>' % (rowct))
        bctable.add_cell(my.txtbox('program_end-%s' % rowct,'',width='150px',js='yes'))
        #bctable.add_cell('<input type="text" id="f2-%s" class="f2" value="" style="width: 20px;"/>' % (rowct))
        bctable.add_cell(my.txtbox('f2-%s' % rowct,'',width='20px',js='no'))
        #bctable.add_cell('<input type="text" id="length-%s" class="length" value="" style="width: 100px;"/>' % (rowct))
        bctable.add_cell(my.txtbox('length-%s' % rowct,'',width='155px',js='yes'))
        #bctable.add_cell('<input type="text" id="label_info-%s" class="label_info" value="" style="width: 160px;"/>' % (rowct))
        bctable.add_cell(my.txtbox('label_info-%s' % rowct,'',width='190px',js='no'))
        #bctable.add_cell('<input type="text" id="slate_info-%s" class="slate_info" value="" style="width: 160px;"/>' % (rowct))
        bctable.add_cell(my.txtbox('slate_info-%s' % rowct,'',width='190px',js='no'))
        addnew = bctable.add_cell('<b>+</b>')#This must add new entry
        addnew.add_style('cursor: pointer;')
        addnew.add_behavior(my.get_add_line(rowct,wo_code, code))
        erow2 = bctable.add_row()
        erow2.add_attr('class','new_barcode_line')
        return bctable
                

class ElementEvalLinesWdg(BaseTableElementWdg):
    def init(my):
        nothing = 'true'

    def get_kill_bvr(my, rowct, wo_code, ell_code, element_eval_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                            var rowct = Number('%s');
                            var wo_code = '%s';
                            var ell_code = '%s';
                            var element_eval_code = '%s';
                            if(confirm("Do you really want to delete this evaluation line?")){
                                server = TacticServerStub.get();
                                server.retire_sobject(server.build_search_key('twog/element_eval_lines',ell_code));
                                top_els = document.getElementsByClassName('printable_element_form_' + wo_code);
                                top_el = null;
                                for(var r = 0; r < top_els.length; r++){
                                    if(top_els[r].getAttribute('element_code') == element_eval_code){
                                        top_el = top_els[r];
                                    }
                                }
                                linestbl = top_el.getElementsByClassName('linestbl')[0];
                                element_lines = linestbl.getElementsByClassName('element_lines');
                                for(var r = 0; r < element_lines.length; r++){
                                    if(element_lines[r].getAttribute('line') == rowct){
                                        element_lines[r].innerHTML = '';
                                        element_lines[r].style.display = 'none';
                                    }
                                }
                                send_data = {'rowct': rowct, 'wo_code': wo_code, 'code': ell_code};
                                //spt.api.load_panel(linestbl, 'qc_reports.qc_reports.ElementEvalLinesWdg', send_data); 
                            }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (rowct, wo_code, ell_code, element_eval_code)}
        return behavior

    def get_add_line(my, rowct, wo_code, ell_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                            bvr.src_el.innerHTML = '';
                            var rowct = Number('%s');
                            var wo_code = '%s';
                            var ell_code = '%s';
                            top_els = document.getElementsByClassName('printable_element_form_' + wo_code);
                            top_el = null;
                            for(var r = 0; r < top_els.length; r++){
                                if(top_els[r].getAttribute('element_code') == ell_code){
                                    top_el = top_els[r];
                                }
                            }
                            linestbl = top_el.getElementsByClassName('linestbl');
                            lastlinestbl = linestbl[linestbl.length - 1];
                            addportions = top_el.getElementsByClassName('new_element_line');
                            addportion = addportions[addportions.length - 1];
                            addportion.setAttribute('class','element_lines');
                            addportion.setAttribute('line',Number(rowct) + 1);
                            addportion.setAttribute('code','');
                            send_data = {'rowct': rowct + 1, 'wo_code': wo_code, 'code': ell_code, 'reload': 'true'};
                            //send_data = {'rowct': rowct + 1, 'wo_code': wo_code};
                            spt.api.load_panel(addportion, 'qc_reports.qc_reports.ElementEvalLinesWdg', send_data); 
                            newrow = lastlinestbl.insertRow(-1);
                            newrow.setAttribute('class','new_element_line');
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (rowct, wo_code, ell_code)}
        return behavior

    def get_select_fillin(my, wo_code, rowct, ell_code):
        behavior = {'css_class': 'clickme', 'type': 'change', 'cbjs_action': '''        
                try{
                   wo_code = '%s';
                   ell_code = '%s';
                   rowct = '%s';
                   top_els = document.getElementsByClassName('printable_element_form_' + wo_code);
                   top_el = null;
                   for(var r = 0; r < top_els.length; r++){
                       if(top_els[r].getAttribute('element_code') == ell_code){
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
                       server = TacticServerStub.get(); 
                       server.insert('twog/qc_report_vars', {'type': 'element', 'description': newval});
                   }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (wo_code, ell_code, rowct)}
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

    def get_alter_text_bold(my):
        behavior = {'type': 'click_up', 'mouse_btn': 'LMB', 'modkeys': 'SHIFT', 'cbjs_action': '''        
                try{
                    if(bvr.src_el.style.fontWeight != 'bold'){
                        bvr.src_el.style.fontWeight = 'bold';
                    }else{
                        bvr.src_el.style.fontWeight = 'normal';
                    }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         '''}
        return behavior

    def get_alter_text_italic(my):
        behavior = {'type': 'click_up', 'mouse_btn': 'LMB', 'modkeys': 'CTRL', 'cbjs_action': '''        
                try{
                    if(bvr.src_el.style.fontStyle != 'italic'){
                        bvr.src_el.style.fontStyle = 'italic';
                    }else{
                        bvr.src_el.style.fontStyle = 'normal';
                    }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         '''}
        return behavior

    def txtbox(my, name, val, width='200px', js='no', style=''):
        txt = TextWdg(name)
        txt.add_attr('id',name)
        txt.add_style('width: %s;' % width)
        txt.set_value(val)
        if not style:
            style = ''
        if 'i' in style:
            txt.add_style('font-style: italic;')
        if 'b' in style:
            txt.add_style('font-weight: bold;')
        if js in ['Yes','yes']:
            txt.add_behavior(my.get_add_dots())
        if 'description' in name:
            txt.add_behavior(my.get_alter_text_bold())
            txt.add_behavior(my.get_alter_text_italic())
        return txt

    def get_display(my):
        import time, datetime
        from tactic_client_lib import TacticServerStub
        from pyasm.common import Environment
        from pyasm.prod.biz import ProdSetting
        login = Environment.get_login()
        this_user = login.get_login()
        code = ''
        element_lines = None
        rowct = 0
        server = TacticServerStub.get()
        #descriptions = server.eval("@SOBJECT(twog/qc_report_vars['type','element']['@ORDER_BY','description'])")
        type_codes = ['F','A','T','V']
        scales = ['1','2','3','FYI']
        in_safe = ['No', 'Yes']
        insrc = ['No', 'Yes', 'New', 'Approved', 'Fixed', 'Not Fixed']
        wo_code = str(my.kwargs.get('wo_code'))
        reloaded = False
        if 'reload' in my.kwargs.keys():
            if my.kwargs.get('reload') == 'true':
                reloaded = True
        if 'code' in my.kwargs.keys():
            code = my.kwargs.get('code')
            element_lines = server.eval("@SOBJECT(twog/element_eval_lines['element_eval_code','%s']['@ORDER_BY','timecode_in asc'])" % code)
            elm_top = []
            elm_bottom = []
            for elm in element_lines:
                if elm.get('ordering') in [None,'']:
                    elm_bottom.append(elm)
                else:
                    elm_top.append(elm)
            from operator import itemgetter
            new_top = sorted(elm_top, key=itemgetter('ordering')) 
            element_lines = []
            element_lines.extend(new_top)
            element_lines.extend(elm_bottom)
        if 'rowct' in my.kwargs.keys():
            rowct = int(my.kwargs.get('rowct'))
        linestbl = Table()
        linestbl.add_attr('class','linestbl')
        if rowct == 0 and not reloaded:
            linestbl.add_row()
            linestbl.add_cell("Timecode In")
            linestbl.add_cell("&nbsp;F")
            linestbl.add_cell("Description")
            linestbl.add_cell("In Safe")
            time_out_label = "Timecode Out"
            # Some clients want "Duration" instead
            duration_clients = ProdSetting.get_seq_by_key('qc_report_duration_clients')
            if my.kwargs.get('client_code') in duration_clients:
                time_out_label = "Duration"
            linestbl.add_cell(time_out_label)
            linestbl.add_cell("&nbsp;F")
            linestbl.add_cell("Code")
            linestbl.add_cell("Scale")
            linestbl.add_cell("Sector/Ch")
            linestbl.add_cell("In Source")
            plus_butt = linestbl.add_cell(" ")
        if code not in [None,''] and not reloaded:
            #plus_butt.add_style('cursor: pointer;')
            #plus_butt.add_behavior(my.get_add_line())
            for el in element_lines:
                seen_descs = []
                if el.get('code') != '':
                    row = linestbl.add_row()
                    row.add_attr('line',rowct)
                    row.add_attr('code',el.get('code'))
                    row.add_attr('class','element_lines')
                    #linestbl.add_cell('<input type="text" id="timecode_in-%s" name="timecode_in" value="%s" style="width: 75px;"/>' % (rowct, el.get('timecode_in')))
                    linestbl.add_cell(my.txtbox('timecode_in-%s' % rowct,el.get('timecode_in'),width='75px',js='yes'))
                    linestbl.add_cell('<input type="text" id="field_in-%s" name="field_in" value="%s" style="width: 20px;"/>' % (rowct, el.get('field_in')))
#                    desc_select = SelectWdg('description')
#                    desc_select.append_option('--Select--','')
#                    for d in descriptions:
#                        desc = d.get('description')
#                        desc_select.append_option(desc,desc)
#                        seen_descs.append(desc)
#                    if el.get('description') not in seen_descs:
#                        desc_select.append_option(el.get('description'), el.get('description'))
#                    desc_select.set_value(el.get('description'))
#                    desc_select.add_attr('id','description-%s' % rowct)
#                    desc_select.add_behavior(my.get_select_fillin(wo_code, rowct))
                    #mm1 = linestbl.add_cell(desc_select)
                    #mm1.add_attr('class','select_cell')
                    mm1 = linestbl.add_cell(my.txtbox('description-%s' % rowct,el.get('description'),width='450px',js='no',style=el.get('description_style')))
                    insafe_select = SelectWdg('in_safe')
                    insafe_select.append_option('-','')
                    for i in in_safe:
                        insafe_select.append_option(i,i)
                    insafe_select.set_value(el.get('in_safe'))
                    insafe_select.add_attr('id','in_safe-%s' % rowct)
                    mm2 = linestbl.add_cell(insafe_select)
                    mm2.add_attr('class','select_cell')
                    #linestbl.add_cell('<input type="text" id="timecode_out-%s" name="timecode_out" value="%s" style="width: 75px;"/>' % (rowct, el.get('timecode_out')))
                    linestbl.add_cell(my.txtbox('timecode_out-%s' % rowct,el.get('timecode_out'),width='75px',js='yes'))
                    linestbl.add_cell('<input type="text" id="field_out-%s" name="field_out" value="%s" style="width: 20px;"/>' % (rowct, el.get('field_out')))
                    type_code_select = SelectWdg('type_code') 
                    type_code_select.append_option('-','')
                    for tc in type_codes:
                        type_code_select.append_option(tc,tc)
                    type_code_select.set_value(el.get('type_code'))
                    type_code_select.add_attr('id','type_code-%s' % rowct)
                    mm3 = linestbl.add_cell(type_code_select)
                    mm3.add_attr('class','select_cell')
                    scale_select = SelectWdg('scale')
                    scale_select.append_option('-','')
                    for s in scales:
                        scale_select.append_option(s,s)
                    scale_select.set_value(el.get('scale'))
                    scale_select.add_attr('id','scale-%s' % rowct)
                    mm4 = linestbl.add_cell(scale_select)
                    mm4.add_attr('class','select_cell')
                    #linestbl.add_cell('<input type="text" id="sector_or_channel-%s" value="%s" style="width: 75px;"/>' % (rowct, el.get('sector_or_channel')))
                    linestbl.add_cell(my.txtbox('sector_or_channel-%s' % rowct,el.get('sector_or_channel'),width='60px',js='no'))
                    insrc_select = SelectWdg('in_source')
                    insrc_select.append_option('-','')
                    for i in insrc:
                        insrc_select.append_option(i,i)
                    insrc_select.set_value(el.get('in_source'))
                    insrc_select.add_attr('id','in_source-%s' % rowct)
                    mm5 = linestbl.add_cell(insrc_select)
                    mm5.add_attr('class','select_cell')
                    orderer = linestbl.add_cell(my.txtbox('ordering-%s' % rowct,el.get('ordering'),width='60px',js='no'))
                    killer = linestbl.add_cell('<b>X</b>')#This must delete the entry
                    killer.add_attr('id','killer-%s' % rowct)
                    killer.add_style('cursor: pointer;')
                    killer.add_behavior(my.get_kill_bvr(rowct, wo_code, el.get('code'), code))
                    rowct = rowct + 1

        erow = linestbl.add_row()
        erow.add_attr('line',rowct)
        erow.add_attr('code','')
        erow.add_attr('class','element_lines')
        #linestbl.add_cell('<input type="text" id="timecode_in-%s" name="timecode_in" value="" style="width: 75px;"/>' % (rowct))
        linestbl.add_cell(my.txtbox('timecode_in-%s' % rowct,'',width='75px',js='yes'))
        linestbl.add_cell('<input type="text" id="field_in-%s" name="field_in" value="" style="width: 20px;"/>' % (rowct))
#        desc_select = SelectWdg('description')
#        desc_select.append_option('--Select--','')
#        for d in descriptions:
#            desc = d.get('description')
#            desc_select.append_option(desc,desc)
#        desc_select.set_value('')
#        desc_select.add_attr('id','description-%s' % rowct)
#        desc_select.add_behavior(my.get_select_fillin(wo_code, rowct))
#        mm1 = linestbl.add_cell(desc_select)
#        mm1.add_attr('class','select_cell')
        mm1 = linestbl.add_cell(my.txtbox('description-%s' % rowct,'',width='450px',js='no'))
        insafe_select = SelectWdg('in_safe')
        insafe_select.append_option('-','')
        for i in in_safe:
            insafe_select.append_option(i,i)
        insafe_select.add_attr('id','in_safe-%s' % rowct)
        mm2 = linestbl.add_cell(insafe_select)
        mm2.add_attr('class','select_cell')
        #linestbl.add_cell('<input type="text" id="timecode_out-%s" name="timecode_out" value="" style="width: 75px;"/>' % (rowct))
        linestbl.add_cell(my.txtbox('timecode_out-%s' % rowct,'',width='75px',js='yes'))
        linestbl.add_cell('<input type="text" id="field_out-%s" name="field_out" value="" style="width: 20px;"/>' % (rowct))
        type_code_select = SelectWdg('type_code') 
        type_code_select.append_option('-','')
        for tc in type_codes:
            type_code_select.append_option(tc,tc)
        type_code_select.add_attr('id','type_code-%s' % rowct)
        mm3 = linestbl.add_cell(type_code_select)
        mm3.add_attr('class','select_cell')
        scale_select = SelectWdg('scale')
        scale_select.append_option('-','')
        for s in scales:
            scale_select.append_option(s,s)
        scale_select.add_attr('id','scale-%s' % rowct)
        mm4 = linestbl.add_cell(scale_select)
        mm4.add_attr('class','select_cell')
        #linestbl.add_cell('<input type="text" id="sector_or_channel-%s" value="" style="width: 75px;"/>' % rowct)
        linestbl.add_cell(my.txtbox('sector_or_channel-%s' % rowct,'',width='75px',js='no'))
        insrc_select = SelectWdg('in_source')
        insrc_select.append_option('-','')
        for i in insrc:
            insrc_select.append_option(i,i)
        insrc_select.add_attr('id','in_source-%s' % rowct)
        mm5 = linestbl.add_cell(insrc_select)
        mm5.add_attr('class','select_cell')
        addnew = linestbl.add_cell('<b>+</b>')#This must add new entry
        addnew.add_style('cursor: pointer;')
        addnew.add_behavior(my.get_add_line(rowct,wo_code, code))
        erow2 = linestbl.add_row()
        erow2.add_attr('class','new_element_line')
        return linestbl

class ElementEvalWdg(BaseTableElementWdg):

    def init(my):
        nothing = 'true'
        my.formats = ['Electronic/File', 'File - ProRes','File - MXF','File - MPEG','File - WAV','DBC', 'D5', 'HDCAM SR', 'NTSC', 'PAL']
        my.frame_rates = ['23.98fps','59.94i','50i','29.97fps','59.94p','DFTC','NDFTC','PAL/EBU','-']
        my.machines = ['VTR221','VTR222','VTR223','VTR224','VTR225','VTR231','VTR232','VTR233','VTR234','VTR235','VTR251','VTR252','VTR253','VTR254','VTR255','VTR261','VTR262','VTR263','VTR264','VTR265','VTR281','VTR282','VTR283','VTR284','VTR285','FCP01','FCP02','FCP03','FCP04','FCP05','FCP06','FCP07','FCP08','FCP09','FCP10','FCP11','FCP12','Amberfin','Clipster','Stradis']
        my.styles = ['Technical','Spot QC','Mastering']
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
        my.standards = ['625','525','720','1080 (4:4:4)','1080','PAL','NTSC','-']
        my.element = None
        my.element_lines = None
        my.key_tbl = Table()
        my.key_tbl.add_attr('border','1')
        my.key_tbl.add_row()
        long = my.key_tbl.add_cell('SECTOR KEY')
        long.add_attr('colspan','3')
        long.add_attr('align','center')
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
        txt.add_attr('id',name)
        txt.add_style('width: %s;' % width)
        txt.set_value(my.element.get(name))
        if js in ['Yes','yes']:
            txt.add_behavior(my.get_add_dots())
        return txt

    def fix_date(my, date):
        #This is needed due to the way Tactic deals with dates (using timezone info), post v4.0
        from pyasm.common import SPTDate
        return_date = ''
        date_obj = SPTDate.convert_to_local(date)
        if date_obj not in [None,'']:
            return_date = date_obj.strftime("%Y-%m-%d  %H:%M")
        return return_date

    def get_display(my):
        import time, datetime
        from tactic_client_lib import TacticServerStub
        from pyasm.common import Environment
        login = Environment.get_login()
        this_user = login.get_login()
        groups = Environment.get_group_names()
        show_save = False
        for g in groups:
            if 'qc' in g or 'edeliveries' in g or 'admin' in g:
                show_save = True
        this_timestamp = str(datetime.datetime.now()).split('.')[0]
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
        tstandard = my.kill_nothing(title.get('standard'))
        tframe_rate = my.kill_nothing(title.get('frame_rate'))
        tformat = my.kill_nothing(title.get('format'))
        
        my.element = {'code': '', 'description': '', 'timestamp': this_timestamp, 'login': this_user, 'operator': this_user, 'type': '', 'bay': '', 'machine_number': '', 'client_code': title.get('client_code'), 'client_name': title.get('client_name'), 'title': title.get('title'), 'episode': title.get('episode'), 'version': '', 'title_type': '', 'timecode': '', 'po_number': title.get('po_number'), 'style': '', 'title_code': work_order.get('title_code'), 'order_code': work_order.get('order_code'), 'work_order_code': code, 'conclusion': '', 'source_code': '', 'standard': my.kill_nothing(title.get('deliverable_standard')), 'aspect_ratio': my.kill_nothing(title.get('deliverable_aspect_ratio')), 'frame_rate': my.kill_nothing(title.get('deliverable_frame_rate')), 'format': my.kill_nothing(title.get('deliverable_format')), 'wo_name': work_order.get('process'), 'roll_up': '', 'bars_tone': '', 'black_silence_1': '', 'slate_silence': '', 'black_silence_2': '', 'video_mod_disclaimer': '', 'start_of_program': '', 'end_of_program': '','roll_up_f': '', 'bars_tone_f': '', 'black_silence_1_f': '', 'slate_silence_f': '', 'black_silence_2_f': '', 'video_mod_disclaimer_f': '', 'start_of_program_f': '', 'end_of_program_f': '', 'active_video_begins': '', 'active_video_ends': '', 'horizontal_blanking': '', 'vertical_blanking': '', 'video_average': '', 'video_peak': '', 'chroma_average': '', 'chroma_peak': '', 'video_sync': '', 'chroma_burst': '', 'setup': '', 'control_track': '', 'video_rf': '', 'front_porch': '', 'sync_duration': '', 'burst_duration': '', 'total_runtime': '', 'tv_feature_trailer': '', 'textless_at_tail': '', 'cc_subtitles': '', 'timecodes': '', 'vitc': '', 'ltc': '', 'record_vendor': '', 'record_date': '', 'language': '', 'comp_mne_sync': '', 'comp_mne_phase': '', 'missing_mne': '', 'average_dialogue': '', 'dec_a1': '', 'dec_a2': '', 'dec_a3': '', 'dec_a4': '', 'dec_b1': '', 'dec_b2': '', 'dec_b3': '', 'dec_b4': '', 'dec_c1': '', 'dec_c2': '', 'dec_c3': '', 'dec_c4': '', 'dec_d1': '', 'dec_d2': '', 'dec_d3': '', 'dec_d4': '', 'tape_pack': '', 'label': '', 'head_logo': '', 'tail_logo': '', 'notices': '', 'vendor_id': '', 'file_name': ''}
        my.element_lines = [{'code': '', 'description': '', 'timestamp': this_timestamp, 's_status': '', 'keywords': '', 'login': this_user, 'id': '', 'name': '', 'element_eval_code': '', 'order_code': work_order.get('order_code'), 'title_code': work_order.get('title_code'), 'work_order_code': code, 'timecode_in': '', 'field_in': '', 'timecode_out': '', 'field_out': '', 'media_type': '', 'type_code': '', 'scale': '', 'sector_or_channel': '', 'in_safe': '', 'in_source': '', 'source_code': ''}]
        if 'element_code' in my.kwargs.keys():
            element_code = str(my.kwargs.get('element_code'))
            my.element = server.eval("@SOBJECT(twog/element_eval['code','%s'])" % element_code)[0]
            my.element_lines = server.eval("@SOBJECT(twog/element_eval_lines['element_eval_code','%s'])" % element_code)
        
        wo_pevals = server.eval("@SOBJECT(twog/element_eval['work_order_code','%s']['code','!=','%s'])" % (code, element_code))
        title_pevals = server.eval("@SOBJECT(twog/element_eval['title_code','%s']['work_order_code','!=','%s']['code','!=','%s'])" % (work_order.get('title_code'), work_order.get('code'), element_code))
        others = Table()
        others.add_style('background-color: #528B8B; width: 100%s;' % '%')
        cols = ['#537072','#518A1A']
        colsct = 0
        if len(title_pevals) > 0:
            trrr = others.add_row()
            trrr.add_style('background-color: #50EDA1;')
            others.add_cell('<b>Other Element Evals for Title</b>')
            for t in title_pevals:
                click_row = others.add_row()
                click_row.add_attr('element_code',t.get('code'))
                click_row.add_attr('work_order_code',t.get('work_order_code'))
                click_row.set_style('cursor: pointer; background-color: %s;' % cols[colsct%2])
                click_row.add_behavior(my.get_click_row(t.get('work_order_code'), t.get('code')))
                others.add_cell('<b>WO:</b> %s, <b>CODE:</b> %s' % (t.get('wo_name'), t.get('work_order_code')))
                others.add_cell('<b>LANGUAGE:</b> %s' % (t.get('language')))
                others.add_cell('<b>OPERATOR:</b> %s' % t.get('operator'))
                others.add_cell('<b>STYLE:</b> %s' % t.get('style'))
                others.add_cell('<b>CONCLUSION:</b> %s' % t.get('conclusion'))
                others.add_cell('<b>DATETIME:</b> %s' % t.get('timestamp'))
                colsct = colsct + 1
        if len(wo_pevals) > 0:
            wrrr = others.add_row()
            wrrr.add_style('background-color: #50EDA1;')
            others.add_cell('<b>Other Element Evals for Work Order</b>')
            for w in wo_pevals:
                click_row = others.add_row()
                click_row.add_attr('element_code',w.get('code'))
                click_row.add_attr('work_order_code',w.get('work_order_code'))
                click_row.set_style('cursor: pointer; background-color: %s;' % cols[colsct%2])
                click_row.add_behavior(my.get_click_row(w.get('work_order_code'), w.get('code')))
                others.add_cell('<b>WO:</b> %s, <b>CODE:</b> %s' % (w.get('wo_name'), w.get('work_order_code')))
                others.add_cell('<b>LANGUAGE:</b> %s' % (w.get('language')))
                others.add_cell('<b>OPERATOR:</b> %s' % w.get('operator'))
                others.add_cell('<b>STYLE:</b> %s' % w.get('style'))
                others.add_cell('<b>CONCLUSION:</b> %s' % w.get('conclusion'))
                others.add_cell('<b>DATETIME:</b> %s' % w.get('timestamp'))
                colsct = colsct + 1

        widget.add_attr('class','big_ol_element_wdg_%s' % code)
        widget.add_attr('element_code',my.element.get('code'))
        widget.add_attr('id','big_ol_element_wdg_%s' % code)
        table = Table()
        table.add_attr('class','printable_element_form_%s' % code)
        table.add_attr('element_code',my.element.get('code'))
        table.add_attr('work_order_code',my.element.get('work_order_code'))
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
            acr.add_cell('<b>%s</b>' % mark)
        rtbl = Table()
        rtbl.add_row()
        rtbl.add_cell('&nbsp;&nbsp;&nbsp;&nbsp;')
        client_name = my.element.get('client_name').upper()
        if not client_name:
            client_name = "ELEMENT EVALUATION"
        big = rtbl.add_cell("<b>{0}</b>".format(client_name))
        big.add_attr('nowrap','nowrap')
        big.add_attr('align','center')
        big.add_attr('valign','center')
        big.add_style('font-size: 40px;')
        rtbl.add_cell('&nbsp;&nbsp;&nbsp;&nbsp;')
        rtbl.add_cell(acr)
        toptbl = Table()
        toptbl.add_row()
        toptbl.add_cell(img_tbl)
        toptbl.add_cell(rtbl)
        bay_sel = SelectWdg('bay_select')
        bay_sel.add_attr('id','bay')
        bay_sel.add_style('width: 135px;')
        bay_sel.append_option('--Select--','')
        for i in range(1,13):
            bay_sel.append_option('Bay %s' % i,'Bay %s' % i)
        if my.element.get('bay') not in [None,'']:
            bay_sel.set_value(my.element.get('bay'))

        style_sel = SelectWdg('style_select')
        style_sel.add_attr('id','style')
        style_sel.add_style('width: 135px;')
        style_sel.append_option('--Select--','')
        for s in my.styles:
            style_sel.append_option(s,s)
        if my.element.get('style') not in [None,'']:
            style_sel.set_value(my.element.get('style'))

        machine_sel = SelectWdg('machine_select')
        machine_sel.add_attr('id','machine_number')
        machine_sel.add_style('width: 135px;')
        machine_sel.append_option('--Select--','')
        for m in my.machines:
            machine_sel.append_option(m,m)
        if my.element.get('machine_number') not in [None,'']:
            machine_sel.set_value(my.element.get('machine_number'))

        format_sel = SelectWdg('format_select')
        format_sel.add_attr('id','format')
        format_sel.add_style('width: 153px;')
        format_sel.append_option('--Select--','')
        for f in my.formats: 
            format_sel.append_option(f,f)
        if my.element.get('format') not in [None,'']:
            format_sel.set_value(my.element.get('format'))

        frame_rate_sel = SelectWdg('frame_rate_select')
        frame_rate_sel.add_attr('id','frame_rate')
        frame_rate_sel.add_style('width: 153px;')
        frame_rate_sel.append_option('--Select--','')
        for f in my.frame_rates:
            frame_rate_sel.append_option(f,f)
        if my.element.get('frame_rate') not in [None,'']:
            frame_rate_sel.set_value(my.element.get('frame_rate'))

        standard_sel = SelectWdg('standard_select')
        standard_sel.add_attr('id','standard')
        standard_sel.add_style('width: 153px;')
        standard_sel.append_option('--Select--','')
        for s in my.standards:
            standard_sel.append_option(s,s)
        if my.element.get('standard') not in [None,'']:
            standard_sel.set_value(my.element.get('standard'))

        majtbl = Table()
        majtbl.add_attr('class','majtbl')
        majtbl.add_row()
        majtbl.add_cell('DATE')
        majtbl.add_cell('OPERATOR')
        majtbl.add_cell('STYLE')
        majtbl.add_cell('BAY')
        majtbl.add_cell('MACHINE #')
        majtbl.add_row()
       
        majtbl.add_cell(my.txtbox('timestamp',width='137px'))
        if my.element.get('operator') not in [None,'']:
            that_login = server.eval("@SOBJECT(sthpw/login['login','%s'])" % my.element.get('operator'))
            if that_login:
                that_login = that_login[0]
                that_login_name = '%s %s' % (that_login.get('first_name'), that_login.get('last_name'))
                my.element['operator'] = that_login_name
        majtbl.add_cell(my.txtbox('operator',width='150px'))
        mm1 = majtbl.add_cell(style_sel)
        mm1.add_attr('class','select_cell')

        mm2 = majtbl.add_cell(bay_sel)
        mm2.add_attr('class','select_cell')

        mm3 = majtbl.add_cell(machine_sel)
        mm3.add_attr('class','select_cell')
        tittbl = Table()
        tittbl.add_row()
        tittbl.add_cell('TITLE:')
        tittbl.add_cell(my.txtbox('title',width='400px'))
        tittbl.add_cell('&nbsp;&nbsp;&nbsp;FORMAT:')
        mm4 = tittbl.add_cell(format_sel)
        mm4.add_attr('class','select_cell')
        tittbl.add_row()
        tittbl.add_cell('SEASON:')
        tittbl.add_cell(my.txtbox('season',width='400px'))
        tittbl.add_cell('&nbsp;&nbsp;&nbsp;STANDARD:')
        mm5 = tittbl.add_cell(standard_sel)
        mm5.add_attr('class','select_cell')
        tittbl.add_row()
        tittbl.add_cell('EPISODE:')
        tittbl.add_cell(my.txtbox('episode',width='400px'))
        ffr = tittbl.add_cell('&nbsp;&nbsp;&nbsp;FRAME RATE:')
        ffr.add_attr('nowrap','nowrap')
        mm6 = tittbl.add_cell(frame_rate_sel)
        mm6.add_attr('class','select_cell')
        tittbl.add_row()
        tittbl.add_cell('VERSION:')
        tittbl.add_cell(my.txtbox('version',width='400px'))
        tittbl.add_cell('&nbsp;&nbsp;&nbsp;PO #:')
        tittbl.add_cell(my.txtbox('po_number',width='151px'))
        tittbl.add_row()
        mm7 = tittbl.add_cell('FILE NAME:')
        mm7.add_attr('nowrap','nowrap')
        mm8 = tittbl.add_cell(my.txtbox('file_name',width='635px'))
        mm8.add_attr('colspan','3')

        tt2 = Table()
        tt2.add_attr('width','85%s' % '%')
        tt2.add_row()
        tt2.add_cell(tittbl)

        pgf = Table()
        pgf.add_attr('class','pgf')
        head = Table()
        head.set_style('background-color: #4a4a4a; width: 100%s;' % '%')
        headr = head.add_row()
        pgc = head.add_cell('<font color="#FFFFFF"><b>PROGRAM FORMAT</b></font>')
        pgc.add_attr('width','500px')
        pgc.add_attr('align','left')
        spcs0 = head.add_cell('<font color="#FFFFFF"><b>F</b></font>')
        spcs0.add_attr('align','left')
        spcs0.add_attr('width','25px')
        pgc2 = head.add_cell('<font color="#FFFFFF"><b>VIDEO MEASUREMENTS</b></font>')
        pgc2.add_attr('align','left')
        pg1 = pgf.add_cell(head)
        pg1.add_attr('width','100%s' % '%')
        pg1.add_attr('colspan','3')
        pgf.add_row()
        pf = Table()
        pf.add_attr('border','1')
        pf.add_attr('nowrap','nowrap')
        pf.add_row()
        pf1 = pf.add_cell('Roll-up (blank)')
        pf1.add_attr('nowrap','nowrap')
        pf.add_cell(my.txtbox('roll_up',width='399px',js='yes'))
        pf.add_cell(my.txtbox('roll_up_f',width='20px'))

        pf.add_row()
        pf2 = pf.add_cell('Bars/Tone')
        pf2.add_attr('nowrap','nowrap')
        pf.add_cell(my.txtbox('bars_tone',width='399px',js='yes'))
        pf.add_cell(my.txtbox('bars_tone_f',width='20px'))
        pf.add_row()
        pf3 = pf.add_cell('Black/Silence')
        pf3.add_attr('nowrap','nowrap')
        pf.add_cell(my.txtbox('black_silence_1',width='399px',js='yes'))
        pf.add_cell(my.txtbox('black_silence_1_f',width='20px'))
        pf.add_row()
        pf4 = pf.add_cell('Slate/Silence')
        pf4.add_attr('nowrap','nowrap')
        pf.add_cell(my.txtbox('slate_silence',width='399px',js='yes'))
        pf.add_cell(my.txtbox('slate_silence_f',width='20px'))
        pf.add_row()
        pf5 = pf.add_cell('Black/Silence')
        pf5.add_attr('nowrap','nowrap')
        pf.add_cell(my.txtbox('black_silence_2',width='399px',js='yes'))
        pf.add_cell(my.txtbox('black_silence_2_f',width='20px'))
        pf.add_row()
        pf7 = pf.add_cell('Start of Program')
        pf7.add_attr('nowrap','nowrap')
        pf.add_cell(my.txtbox('start_of_program',width='399px',js='yes'))
        pf.add_cell(my.txtbox('start_of_program_f',width='20px'))
        pf.add_row()
        pf8 = pf.add_cell('End of Program')
        pf8.add_attr('nowrap','nowrap')
        pf.add_cell(my.txtbox('end_of_program',width='399px',js='yes'))
        pf.add_cell(my.txtbox('end_of_program_f',width='20px'))

        vm = Table()
        vm.add_attr('border','1')
        vm.add_attr('nowrap','nowrap')
        vm.add_row()
        vm1 = vm.add_cell('Active Video Begins')
        vm1.add_attr('nowrap','nowrap')
        vm.add_cell(my.txtbox('active_video_begins',width="400px"))

        gng = ['Good','No Good']
        gng2 = ['Good','Fair','Poor']
        vm.add_row()
        vm3 = vm.add_cell('Active Video Ends')
        vm3.add_attr('nowrap','nowrap')
        vm.add_cell(my.txtbox('active_video_ends',width="400px"))

        vm.add_row()
        vm5 = vm.add_cell('Horizontal Blanking')
        vm5.add_attr('nowrap','nowrap')
        vm.add_cell(my.txtbox('horizontal_blanking',width="400px"))
        vm.add_row()

        vm.add_row()
        vm11 = vm.add_cell('Luminance Peak')
        vm11.add_attr('nowrap','nowrap')
        vm.add_cell(my.txtbox('video_peak',width="400px"))
        vm.add_row()
        vm.add_row()
        vm15 = vm.add_cell('Chroma Peak')
        vm15.add_attr('nowrap','nowrap')
        vm.add_cell(my.txtbox('chroma_peak',width="400px"))
        vm.add_row()

        tm4 = vm.add_cell('Head Logo')
        tm4.add_attr('nowrap','nowrap')
        vm.add_cell(my.txtbox('head_logo',width="400px"))

        vm.add_row()
        tm55 = vm.add_cell('Tail Logo')
        tm55.add_attr('nowrap','nowrap')
        vm.add_cell(my.txtbox('tail_logo',width="400px"))

        pfc1 = pgf.add_cell(pf)
        pfc1.add_attr('valign','top')
        pgf.add_cell('&nbsp;')
        pgf.add_cell(vm)

        epro = Table()
        epro.add_attr('class','epro')
        head2 = Table()
        head2.set_style('background-color: #4a4a4a; width: 100%s;' % '%')
        headr2 = head2.add_row()
        pgc2 = head2.add_cell('<font color="#FFFFFF"><b>ELEMENT PROFILE</b></font>')
        pgc2.add_attr('align','left')
        pg1 = epro.add_cell(head2)
        pg1.add_attr('width','100%s' % '%')
        pg1.add_attr('colspan','3')
        epro.add_row()
        ef = Table()
        ef.add_attr('border','1')
        ef.add_row()
        ef1 = ef.add_cell('Total Runtime')
        ef1.add_attr('nowrap','nowrap')
        ef.add_cell(my.txtbox('total_runtime',width="400px",js='yes'))
        ef.add_row()
        ef2 = ef.add_cell('TV/Feature/Trailer')
        ef2.add_attr('nowrap','nowrap')
        ef.add_cell(my.txtbox('tv_feature_trailer',width="400px"))
        ef.add_row()
        ef2 = ef.add_cell('Video Aspect Ratio')
        ef2.add_attr('nowrap','nowrap')
        ar_select = SelectWdg('aspect_ratio_select')
        ar_select.add_attr('id','aspect_ratio')
        ar_select.add_style('width: 380px;')
        ar_select.append_option('--Select--','')
        for a in my.aspect_ratios:
            ar_select.append_option(a,a)
        if my.element.get('aspect_ratio') not in [None,'']:
            ar_select.set_value(my.element.get('aspect_ratio'))
        mm10 = ef.add_cell(ar_select)
        mm10.add_attr('class','select_cell')
        ef.add_row()
        ef2 = ef.add_cell('Textless @ Tail')
        ef2.add_attr('nowrap','nowrap')
        ef.add_cell(my.txtbox('textless_at_tail',width="400px"))
        ef.add_row()
        ef2 = ef.add_cell('Notices')
        ef2.add_attr('nowrap','nowrap')
        ef.add_cell(my.txtbox('notices',width="400px"))
        ef.add_row()
        ef.add_cell('Label')

        gng2 = ['Good','Fair','Poor','-']
        lab_sel = SelectWdg('label')
        lab_sel.add_attr('id','label')
        lab_sel.add_style('width: 380px;')
        lab_sel.append_option('--Select--','')
        for la in gng2:
            lab_sel.append_option(la, la)
        if my.element.get('label') not in [None,'']:
            lab_sel.set_value(my.element.get('label'))

        in1 = ef.add_cell(lab_sel)
        in1.add_attr('class','select_cell')

        tm = Table()
        tm.add_attr('border','1')
        tm.add_attr('nowrap','nowrap')
        tm.add_row()
        tm2 = tm.add_cell('Language')
        tm2.add_attr('nowrap','nowrap')
        tm.add_cell(my.txtbox('language',width="424px"))
        tm.add_row()
        ef2 = tm.add_cell('(CC)/Subtitles')
        ef2.add_attr('nowrap','nowrap')
        tm.add_cell(my.txtbox('cc_subtitles',width="424px"))
        tm.add_row()
        tm3 = tm.add_cell('VITC')
        tm3.add_attr('nowrap','nowrap')
        tm.add_cell(my.txtbox('vitc',width="424px"))

        tm.add_row()
        tm3 = tm.add_cell('Source Barcode')
        tm3.add_attr('nowrap','nowrap')
        tm.add_cell(my.txtbox('record_vendor',width="424px"))
        tm.add_row()
        tm33 = tm.add_cell('Element QC Barcode')
        tm33.add_attr('nowrap','nowrap')
        tm.add_cell(my.txtbox('vendor_id',width="424px"))
        tm.add_row()
        tm3 = tm.add_cell('Record Date')
        tm3.add_attr('nowrap','nowrap')

        from tactic.ui.widget import CalendarInputWdg
        rcrd = CalendarInputWdg("record_date")
        rcrd.set_option('show_activator', 'true')
        rcrd.set_option('show_time','false')
        rcrd.set_option('width', '380px')    
        rcrd.set_option('id', 'record_date')    
        rcrd.set_option('display_format','MM/DD/YYYY HH:MM')
        if my.element.get('record_date') not in [None,'']:
            rcrd.set_option('default', my.element.get('record_date'))
        else:
            rcrd.set_option('default', this_timestamp.split(' ')[0])
        rcrd.get_top().add_attr('id','record_date')
        rcrd.set_persist_on_submit()
        rcrd_date = tm.add_cell(rcrd)
        rcrd_date.add_attr('nowrap','nowrap')

        epro.add_cell(ef)
        epro.add_cell('&nbsp;')
        epro.add_cell(tm)

        ktbl = Table()
        ktbl.add_row()
        k1 = ktbl.add_cell('<i>Code Definitions: F=Film V=Video T=Telecine A=Audio</i>')
        k1.add_attr('align','left')
        k = ktbl.add_cell('&nbsp;&nbsp;&nbsp;')
        k.add_attr('align','right')
        k2 = ktbl.add_cell('<i>Severity Scale: 1=Minor 2=Marginal 3=Severe</i>')
        k2.add_attr('align','right')
        k22 = ktbl.add_cell('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
        k3 = ktbl.add_cell('<u>TC Shift</u>')
        k3.add_attr('id','tc_shifter')
        k3.add_attr('align','right')
        k3.add_style('cursor: pointer;')
        k3.add_behavior(my.launch_tc_shifter(code, my.element.get('code')))

        linestbl = ElementEvalLinesWdg(code=my.element.get('code'), wo_code=code,
                                       client_code=my.element.get('client_code'))
        audtbl = ElementEvalAudioWdg(code=my.element.get('code'),wo_code=code,channels=channels) 

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
        #table.add_cell(tittbl)
        table.add_cell(tt2)
        table.add_row()
        table.add_cell(pgf)
        table.add_row()
        table.add_cell(epro)
        table.add_row()
        aud2 = table.add_cell('<font color="#FFFFFF"><b>AUDIO CONFIGURATION - click to change number of channels</b></font>')
        aud2.add_attr('align','left')
        aud2.add_attr('id','audio_row')
        aud2.add_style('background-color: #4a4a4a;')
        aud2.add_style('cursor: pointer;')
        aud2.add_style('width: 100%s;' % '%')
        aud2.add_behavior(my.get_change_channels(code, my.element.get('code')))
        table.add_row()
        audio_table = table.add_cell(audtbl)
        audio_table.add_attr('id','audio_table')
        audio_table.add_attr('code',my.element.get('code'))
        audio_table.add_attr('wo_code',code)
        darkrow = table.add_row()
        darkrow.add_attr('id','darkrow')
        darkrow.set_style('background-color: #4a4a4a; width: 55%s;' % '%')
        table.add_cell('<b><font color="#FFFFFF">GENERAL COMMENTS</font></b>')
        table.add_row()
        table.add_cell('<textarea cols="194" rows="10" class="description" id="description">%s</textarea>' % my.element.get('description'))
        #print "PQ Description = %s" % my.element.get('description')

        printtbl = Table()
        printtbl.add_style('background-color: #528B8B; width: 100%s;' % '%');
        printtbl.add_row()
        p1 = printtbl.add_cell(' ')
        p1.add_style('width: 40%s;' % '%')
        p2 = printtbl.add_cell('<u><b>Print This Report</b></u>')
        p2.add_attr('nowrap','nowrap')
        p2.add_style('cursor: pointer;')
        p2.add_behavior(my.get_print_bvr(code, my.element.get('code'), 'element'))
        p3 = printtbl.add_cell(' ')
        p3.add_style('width: 40%s;' % '%')

        table.add_row()
        table.add_cell(fulllines)

        stbl = Table()
        stbl.add_row()
        s1 = stbl.add_cell(' ')
        s1.add_style('width: 40%s;' % '%')
        s2 = stbl.add_cell('<input type="button" value="Save"/>')
        s2.add_behavior(my.get_save_bvr(code, my.element.get('code')))
        s3 = stbl.add_cell(' ')
        s3.add_style('width: 40%s;' % '%')
        if my.element.get('code') not in [None,'']:
            cloner = stbl.add_cell('<input type="button" value="Clone"/>')
            cloner.add_attr('align','center')
            cloner.add_behavior(my.get_clone_report(code, my.element.get('code')))
            s4 = stbl.add_cell('<input type="button" value="Delete This Report"/>')
            s4.add_behavior(my.get_delete_report(code, my.element.get('code')))
        ttbl = Table()
        ttbl.add_style('background-color: #528B8B; width: 100%s;' % '%');
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

class TechEvalWdg(BaseTableElementWdg):

    def init(my):
        nothing = 'true'

    def get_stub(my):
        from tactic_client_lib import TacticServerStub
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
        import time, datetime
        from tactic_client_lib import TacticServerStub
        from pyasm.common import Environment
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
        code = my.kwargs.get('code');
        original_code = code
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
        tech = {'code': '', 'description': '', 'timestamp': this_timestamp, 'login': this_user, 'barcode': '', 'client_code': '', 'client_name': '', 'title': title.get('title'), 'title_code': title.get('code'), 'episode': '', 'type': '', 'trt': '', 'part': '', 'label_date': '', 'capture_or_layoff': '', 'date': this_timestamp, 'order_code': work_order.get('order_code'), 'source_deck': '', 'record_deck': '', 'aspect_ratio': '', 'format': '', 'standard': '', 'timecode': '', 'text': '', 'vitc_lines': '', 'horiz_blank': '', 'active_video_lines': '', 'title_safe': '', 'error_logger': '', 'audio_ch01': '', 'audio_ch02': '', 'audio_ch03': '', 'audio_ch04': '', 'audio_ch05': '', 'audio_ch06': '', 'audio_ch07': '', 'audio_ch08': '', 'audio_ch09': '', 'audio_ch10': '', 'audio_ch11': '', 'audio_ch12': '', 'peak_ch01': '', 'peak_ch02': '', 'peak_ch03': '', 'peak_ch04': '', 'peak_ch05': '', 'peak_ch06': '', 'peak_ch07': '', 'peak_ch08': '', 'peak_ch09': '', 'peak_ch10': '', 'peak_ch11': '', 'peak_ch12': '', 'in_phase_0102': '', 'in_phase_0304': '', 'in_phase_0506': '', 'in_phase_0708': '', 'in_phase_0910': '', 'in_phase_1112': '', 'first_cut': '', 'first_cut_field': '', 'last_cut': '', 'last_cut_field': '', 'tc_verify': '', 'error_logger_messages': '', 'general_comments': '', 'operator': this_user, 'source_code': '', 'work_order_code': work_order.get('code'), 'wo_name': work_order.get('process')}
        if 'tech_code' in my.kwargs.keys():
            tech_code = str(my.kwargs.get('tech_code'))
            if tech_code not in [None,'']:
                tech = my.server.eval("@SOBJECT(twog/tech_eval['code','%s'])" % tech_code)[0]
            else:
                tech_code = ''
        wo_evals = my.server.eval("@SOBJECT(twog/tech_eval['work_order_code','%s']['code','!=','%s'])" % (code, tech_code))
        title_evals = my.server.eval("@SOBJECT(twog/tech_eval['title_code','%s']['work_order_code','!=','%s']['code','!=','%s'])" % (work_order.get('title_code'), work_order.get('code'), tech_code))
        others = Table()
        others.add_style('background-color: #528B8B; width: 100%s;' % '%');
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
        widget = DivWdg()
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
        printtbl.add_style('background-color: #528B8B; width: 100%s;' % '%');
        printtbl.add_row()
        p1 = printtbl.add_cell(' ')
        p1.add_style('width: 40%s;' % '%')
        p2 = printtbl.add_cell('<u><b>Print This Report</b></u>')
        p2.add_attr('nowrap','nowrap')
        p2.add_style('cursor: pointer;')
        p2.add_behavior(my.get_print_bvr(code, tech.get('code'), 'tech'))
        p3 = printtbl.add_cell(' ')
        p3.add_style('width: 40%s;' % '%')

        from tactic.ui.widget import CalendarInputWdg
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

        from tactic.ui.widget import CalendarInputWdg
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
        ttbl.add_style('background-color: #528B8B; width: 100%s;' % '%');
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

class MetaDataReportWdg(BaseTableElementWdg):

    def init(my):
        nothing = 'true'
        my.ynd = ['Yes','No','-']
        my.yn = ['Yes','No']
        my.server = None
        my.languages = None

    def get_stub(my):
        from tactic_client_lib import TacticServerStub
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
                              var class_name = 'qc_reports.qc_reports.MetaDataReportWdg';
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
                              var class_name = 'qc_reports.qc_reports.MetaDataReportWdg';
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
                                  var class_name = 'qc_reports.qc_reports.MetaDataReportWdg';
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
                          var class_name = 'qc_reports.qc_reports.MetaDataReportWdg';
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
        import time, datetime
        from pyasm.common import Environment
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
        code = my.kwargs.get('code');
        original_code = code
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
        metadata = {'code': '', 'description': '', 'login': this_user, 'order_code': title.get('order_code'), 'title_code': title.get('code'), 'work_order_code': work_order.get('code'), 'title': title.get('title'), 'episode': title.get('episode'), 'content': '', 'source_type': '', 'source_codes': '', 'qc_operator': '', 'qc_date': this_timestamp, 'qc_notes': '', 'encoding_log_no_errors_f': '', 'encoding_log_no_errors_p': '', 'correct_codec_used_f': '', 'correct_codec_used_p': '', 'conclusion': '', 'fr_same_as_native_source_f': '', 'fr_same_as_native_source_p': '', 'hd_res_is_1920x1080_f': '', 'hd_res_is_1920x1080_p': '', 'field_dominance_is_none_f': '', 'field_dominance_is_none_p': '', 'tagged_as_progressive_f': '', 'tagged_as_progressive_p': '', 'clap_tag_removed_f': '', 'clap_tag_removed_p': '', 'pasp_is_correct_f': '', 'pasp_is_correct_p': '', 'gamma_tag_removed_f': '', 'gamma_tag_removed_p': '', 'no_fbimpaareleasedate_tagging_f': '', 'no_fbimpaareleasedate_tagging_p': '', 'proper_aspect_ratio_f': '', 'proper_aspect_ratio_p': '', 'websites_not_listed_f': '', 'websites_not_listed_p': '', 'cropping_values_correct_f': '', 'cropping_values_correct_p': '', 'no_promotional_bumpers_p': '', 'same_aspect_ratio_as_feature_p': '', 'suitable_for_general_audience_p': '', 'file_starts_at_5959_w_black_f': '', 'file_starts_at_1hr_w_fade_p': '', 'program_starts_at_1hr_f': '', 'program_begins_with_black_frame_p': '', 'program_ends_with_black_frame_f': '', 'program_ends_with_fade_p': '', 'video_notes': '', 'aconfig_trk1_language': '', 'aconfig_trk1_type': '', 'aconfig_trk2_language': '', 'aconfig_trk2_type': '', 'aconfig_trk3_language': '', 'aconfig_trk3_type': '', 'aconfig_trk4_language': '', 'aconfig_trk4_type': '', 'aconfig_trk5_language': '', 'aconfig_trk5_type': '', 'aconfig_trk6_language': '', 'aconfig_trk6_type': '', 'aconfig_trk7_language': '', 'aconfig_trk7_type': '', 'aconfig_trk8_language': '', 'aconfig_trk8_type': '', 'abundle_trk1_language': '', 'abundle_trk1_type': '', 'abundle_trk2_language': '', 'abundle_trk2_type': '', 'abundle_trk3_language': '', 'abundle_trk3_type': '', 'abundle_trk4_language': '', 'abundle_trk4_type': '', 'abundle_trk5_language': '', 'abundle_trk5_type': '', 'abundle_trk6_language': '', 'abundle_trk6_type': '', 'abundle_trk7_language': '', 'abundle_trk7_type': '', 'abundle_trk8_language': '', 'abundle_trk8_type': '', 'aconfig_trk1_language_p': '', 'aconfig_trk1_type_p': '', 'aconfig_trk2_language_p': '', 'aconfig_trk2_type_p': '', 'aconfig_trk3_language_p': '', 'aconfig_trk3_type_p': '', 'aconfig_trk4_language_p': '', 'aconfig_trk4_type_p': '', 'aconfig_trk5_language_p': '', 'aconfig_trk5_type_p': '', 'aconfig_trk6_language_p': '', 'aconfig_trk6_type_p': '', 'aconfig_trk7_language_p': '', 'aconfig_trk7_type_p': '', 'aconfig_trk8_language_p': '', 'aconfig_trk8_type_p': '', 'aconfig_verified_f': '', 'aconfig_verified_b': '', 'aconfig_verified_p': '', 'audio_in_sync_with_video_f': '', 'audio_in_sync_with_video_b': '', 'audio_in_sync_with_video_p': '', 'audio_tagged_correctly_f': '', 'audio_tagged_correctly_b': '', 'audio_tagged_correctly_p': '', 'no_audio_cut_off_f': '', 'no_audio_cut_off_b': '', 'no_audio_cut_off_p': '', 'trt_audio_is_trt_video_f': '', 'trt_audio_is_trt_video_b': '', 'trt_audio_is_trt_video_p': '', 'correct_audio_language_f': '', 'correct_audio_language_b': '', 'correct_audio_language_p': '', 'audio_notes': '', 'delivery_snapshot_feature': '', 'delivery_snapshot_trailer': '', 'delivery_snapshot_alt_audio': '', 'delivery_snapshot_subtitle': '', 'delivery_snapshot_cc': '', 'delivery_snapshot_vendor_notes': '', 'delivery_snapshot_poster_art': '', 'delivery_snapshot_dub_card': '', 'delivery_snapshot_other': '', 'forced_narrative_f': '', 'forced_narrative_p': '', 'subtitles_on_feature': '', 'subtitles_on_trailer': '', 'forced_narrative_not_overlapping_f': '', 'forced_narrative_not_overlapping_p': '', 'subtitles_on_feature_not_overlapping': '', 'subtitles_on_trailer_not_overlapping': '', 'dub_card_dimensions_match_feature': '', 'dub_card_fps_match_feature': '', 'dub_card_language_match_locale': '', 'dub_card_duration_4_to_5': '', 'dub_card_has_no_audio_tracks': '', 'dub_card_text_not_cutoff_with_cropping': '', 'cc_in_synch_with_video': '', 'subtitles_in_synch_with_video': '', 'subtitles_have_correct_language': '', 'assets_notes': '', 'thumb_is_jpeg': '', 'thumb_dpi_72_or_more': '', 'thumb_profile_is_rgb': '', 'thumb_same_aspect_ratio_as_video': '', 'thumb_only_active_pixels': '', 'thumb_horiz_at_least_640': '', 'thumb_for_each_chapter_stop': '', 'poster_is_jpeg': '', 'poster_dpi_72_or_more': '', 'poster_profile_is_rgb': '', 'poster_rez_at_least_1400x2100': '', 'poster_aspect_ratio_2x3': '', 'poster_key_art_and_title_only': '', 'poster_no_dvdcover_date_urlpromo_tagging': '', 'image_notes': '', 'trt_f': '', 'trt_p': ''}

        if 'metadata_code' in my.kwargs.keys():
            metadata_code = str(my.kwargs.get('metadata_code'))
            if metadata_code not in [None,'']:
                metadata = my.server.eval("@SOBJECT(twog/metadata_report['code','%s'])" % metadata_code)[0]
            else:
                metadata_code = ''
        wo_reports = my.server.eval("@SOBJECT(twog/metadata_report['work_order_code','%s']['code','!=','%s'])" % (code, metadata_code))
        title_reports = my.server.eval("@SOBJECT(twog/metadata_report['title_code','%s']['work_order_code','!=','%s']['code','!=','%s'])" % (work_order.get('title_code'), work_order.get('code'), metadata_code))
        others = Table()
        others.add_style('background-color: #528B8B; width: 100%s;' % '%');
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
            
        
        widget = DivWdg()
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

        from tactic.ui.widget import CalendarInputWdg
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

        st_fr = {'HD FEATURE': 'FRAME RATE IS THE SAME AS THE NATIVE SOURCE (23.976, 24, 25, 29.97)?','SD FEATURE NTSC': 'FRAME RATE IS THE SAME AS THE NATIVE SOURCE (23.976, 24, 29.97)?','SD FEATURE PAL': 'FRAME RATE IS THE SAME AS THE NATIVE SOURCE (23.976, 24, 25)?','HD TV': 'FRAME RATE IS THE SAME AS THE NATIVE SOURCE (23.976, 24, 25, 29.97)?','SD TV NTSC': 'FRAME RATE IS THE SAME AS THE NATIVE SOURCE (23.976, 24, 29.97)?','SD TV PAL': 'FRAME RATE IS THE SAME AS THE NATIVE SOURCE (23.976, 24, 25)?'};
        st_res = {'HD FEATURE': 'HD RESOLUTION IS 1920X1080 (SQUARE PIXEL ASPECT RATIO)?','SD FEATURE NTSC': 'SD NTSC RESOLUTION IS 720X480 OR 720X486?','SD FEATURE PAL': 'SD PAL RESOLUTION IS 720X576?','HD TV': 'HD RESOLUTION IS 1920X1080 (SQUARE PIXEL ASPECT RATIO)?','SD TV NTSC': 'SD NTSC RESOLUTION IS 720X480 OR 720X486?','SD TV PAL': 'SD PAL RESOLUTION IS 720X576?'};
        st_pasp = {'HD FEATURE': 'PASP IS CORRECT? (1:1)','SD FEATURE NTSC': 'PASP IS CORRECT? (4x3 = 0.889:1, 16x9 = 1.185:1)','SD FEATURE PAL': 'PASP IS CORRECT? (4x3 = 1.067:1, 16x9 = 1.422:1)','HD TV': 'PASP IS CORRECT? (1:1)','SD TV NTSC': 'PASP IS CORRECT? (4x3 = 0.889:1, 16x9 = 1.185:1)','SD TV PAL': 'PASP IS CORRECT? (4x3 = 1.067:1, 16x9 = 1.422:1)'};
        st_asterix = {'HD FEATURE': '&nbsp;','SD FEATURE NTSC': '<i>*SD CONTENT FROM 525 720x486 SOURCES = MIN CROP OF 4 FROM TOP AND 2 FROM BOTTOM</i>','SD FEATURE PAL': '&nbsp;','HD TV': '&nbsp;','SD TV NTSC': '<i>*SD CONTENT FROM 525 720x486 SOURCES = MIN CROP OF 4 FROM TOP AND 2 FROM BOTTOM</i>','SD TV PAL': '&nbsp;'};
        st_featepis = {'HD FEATURE': 'FEATURE','SD FEATURE NTSC': 'FEATURE','SD FEATURE PAL': 'FEATURE','HD TV': 'EPISODE','SD TV NTSC': 'EPISODE','SD TV PAL': 'EPISODE'};
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
        printtbl.add_style('background-color: #528B8B; width: 100%s;' % '%');
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
        ttbl.add_style('background-color: #528B8B; width: 100%s;' % '%');
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

class ReportTimecodeShifterWdg(BaseTableElementWdg):

    def init(my):
        nothing = 'true'
        my.server = None

    def shift_em(my, code, ell_code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        function make_2_digit(digis){
                            str_ret = digis.toString();
                            if(str_ret.length == 1){
                                str_ret = '0' + str_ret;
                            }
                            return str_ret;
                        }
                        try{
                          var wo_code = '%s';
                          var ell_code = '%s';
                          big_els = document.getElementsByClassName('big_ol_element_wdg_' + wo_code);
                          big_el = null;
                          for(var r = 0; r < big_els.length; r++){
                              if(big_els[r].getAttribute('element_code') == ell_code){
                                  big_el = big_els[r];
                              }
                          } 
                          el_lines = big_el.getElementsByClassName('element_lines');
                          shifter = document.getElementById('timecode_shifter');
                          start_at = shifter.getElementById('start_at').value;
                          add_amt = shifter.getElementById('add_amt').value;
                          add_s = add_amt.split(':');
                          if(add_s.length > 1){
                              add_hours = 0;
                              add_minutes = Number(add_s[0]);
                              add_seconds = Number(add_s[1]);
                              add_frames = -1;
                              if(add_s.length == 3){
                                  add_frames = Number(add_s[2]); 
                              }
                              for(var k = 0; k < el_lines.length; k++){
                                  line_code = el_lines[k].getAttribute('code');
                                  if(el_lines[k].style.display != 'none'){
                                      if(el_lines[k].getAttribute('code').indexOf('ELEMENT') != -1){
                                          inputs = el_lines[k].getElementsByClassName('spt_input');
                                          for(var r = 0; r < inputs.length; r++){
                                              if(inputs[r].id.indexOf('timecode') != -1){
                                                  line_tc = inputs[r].value;
                                                  if(line_tc != '' && line_tc != null){
                                                      if(line_tc > start_at){
                                                          new_hours = 0;
                                                          new_minutes = 0;
                                                          new_seconds = 0;
                                                          new_frames = 0;
                                                          tc_s = line_tc.split(':');
                                                          tc_hours = Number(tc_s[0]);    
                                                          tc_minutes = Number(tc_s[1]);    
                                                          tc_seconds = Number(tc_s[2]);    
                                                          tc_frames = Number(tc_s[3]);    
                                                          if(add_frames != -1){
                                                              new_frames = add_frames + tc_frames;
                                                              //alert('new_frames = ' + new_frames);
                                                              while(new_frames > 23){
                                                                  new_frames = new_frames - 24;
                                                                  tc_seconds = tc_seconds + 1;
                                                              }
                                                          }
                                                          new_seconds = tc_seconds + add_seconds;
                                                          while(new_seconds > 59){
                                                              new_seconds = new_seconds - 60;
                                                              tc_minutes = tc_minutes + 1;
                                                          }
                                                          new_minutes = tc_minutes + add_minutes;
                                                          while(new_minutes > 59){
                                                              new_minutes = new_minutes - 60;
                                                              tc_hours = tc_hours + 1;
                                                          }
                                                          new_hours = tc_hours + add_hours;
                                                          //alert("ID = " + inputs[r].id + " ORIG = " + line_tc + " NEW HOURS = " + new_hours + " NEW MINUTES = " + new_minutes + " NEW SECONDS = " + new_seconds + " NEW FRAMES = " + new_frames);
                                                          new_tc = make_2_digit(new_hours) + ':' + make_2_digit(new_minutes) + ':' + make_2_digit(new_seconds) + ':' + make_2_digit(new_frames);
                                                          inputs[r].value = new_tc;
                                                      }
                                                  }
                                                  
                                              }
                                          }
                                      }
                                  }
                              }
                          }
                           
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (code, ell_code)}
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
        wo_code = my.kwargs.get('wo_code')
        ell_code = my.kwargs.get('ell_code')
        widget = DivWdg()
        table = Table()
        table.add_attr('id','timecode_shifter')
        table.add_row()
        sa = table.add_cell('Start After:')
        sa.add_attr('nowrap','nowrap')
        table.add_cell(my.txtbox('start_at', '',width='75px',js='yes'))
        sb = table.add_cell('(Must exactly match the following format EX: 01:33:57:19)')
        sb.add_attr('nowrap','nowrap')
        table.add_row()
        table.add_cell('Add:') 
        table.add_cell(my.txtbox('add_amt', '',width='75px',js='yes'))
        sc = table.add_cell('(Minute:Second:Frame or Minute:Second)')
        sc.add_attr('nowrap','nowrap')
        table.add_row()
        butt = table.add_cell('<input type="button" value="Shift Timecodes"/>')
        butt.add_behavior(my.shift_em(wo_code,ell_code))
        widget.add(table)

        return widget
