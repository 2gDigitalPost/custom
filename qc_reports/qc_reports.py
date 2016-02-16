__all__ = ["QCReportLauncherWdg", "QCReportClonerWdg", "QCReportSelectorWdg", "PrintQCReportWdg",
           "ElementEvalBarcodesWdg", "ReportTimecodeShifterWdg"]

import os

from tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseTableElementWdg

from pyasm.command import *
from pyasm.common import Environment
from pyasm.web import Table, DivWdg
from pyasm.widget import TextWdg, CheckboxWdg


class QCReportLauncherWdg(BaseTableElementWdg):

    def init(my):
        nothing = 'true'
        my.server = None

    def get_launch_behavior(my, code):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                          var code = '%s';
                          var class_name = 'qc_reports.QCReportSelectorWdg';
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
                                    var class_name = 'qc_reports.prequal_eval_wdg.PreQualEvalWdg';
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
                                            new_md = server.insert('twog/metadata_report', {
                                                'title': title.title,
                                                'episode': kill_nothing(title.episode),
                                                'title_code': title.code,
                                                'client_code': kill_nothing(title.client_code),
                                                'client_name': kill_nothing(title.client_name),
                                                'order_code': title.order_code,
                                                'wo_name': wo.process,
                                                'work_order_code': wo.code,
                                                'login': login_name,
                                                'description': the_report.description,
                                                'content': the_report.content,
                                                'source_type': the_report.source_type,
                                                'source_codes': source_codes,
                                                'qc_operator': login_name,
                                                'qc_date': today,
                                                'qc_notes': the_report.qc_notes,
                                                'encoding_log_no_errors_f': the_report.encoding_log_no_errors_f,
                                                'encoding_log_no_errors_p': the_report.encoding_log_no_errors_p,
                                                'correct_codec_used_f': the_report.correct_codec_used_f,
                                                'correct_codec_used_p': the_report.correct_codec_used_p,
                                                'fr_same_as_native_source_f': the_report.fr_same_as_native_source_f,
                                                'fr_same_as_native_source_p': the_report.fr_same_as_native_source_p,
                                                'hd_res_is_1920x1080_f': the_report.hd_res_is_1920x1080_f,
                                                'hd_res_is_1920x1080_p': the_report.hd_res_is_1920x1080_p,
                                                'field_dominance_is_none_f': the_report.field_dominance_is_none_f,
                                                'field_dominance_is_none_p': the_report.field_dominance_is_none_p,
                                                'tagged_as_progressive_f': the_report.tagged_as_progressive_f,
                                                'tagged_as_progressive_p': the_report.tagged_as_progressive_p,
                                                'clap_tag_removed_f': the_report.clap_tag_removed_f,
                                                'clap_tag_removed_p': the_report.clap_tag_removed_p,
                                                'pasp_is_correct_f': the_report.pasp_is_correct_f,
                                                'pasp_is_correct_p': the_report.pasp_is_correct_p,
                                                'gamma_tag_removed_f': the_report.gamme_tag_removed_f,
                                                'gamma_tag_removed_p': the_report.gamme_tag_removed_p,
                                                'no_fbimpaareleasedate_tagging_f': the_report.no_fbimpaareleasedate_tagging_f,
                                                'no_fbimpaareleasedate_tagging_p': the_report.no_fbimpaareleasedate_tagging_p,
                                                'proper_aspect_ratio_f': the_report.proper_aspect_ratio_f,
                                                'proper_aspect_ratio_p': the_report.proper_aspect_ratio_p,
                                                'websites_not_listed_f': the_report.websites_not_listed_f,
                                                'websites_not_listed_p': the_report.websites_not_listed_p,
                                                'cropping_values_correct_f': the_report.cropping_values_correct_f,
                                                'cropping_values_correct_p': the_report.cropping_values_correct_p,
                                                'no_promotional_bumpers_p': the_report.no_promotional_bumpers_p,
                                                'same_aspect_ratio_as_feature_p': the_report.same_aspect_ratio_as_feature_p,
                                                'suitable_for_general_audience_p': the_report.suitable_for_general_audience_p,
                                                'file_starts_at_5959_w_black_f': the_report.file_starts_at_5959_w_black_f,
                                                'file_starts_at_1hr_w_fade_p': the_report.file_starts_at_1hr_w_fade_p,
                                                'program_starts_at_1hr_f': the_report.program_starts_at_1hr_f,
                                                'program_begins_with_black_frame_p': the_report.program_begins_with_black_frame_p,
                                                'program_ends_with_black_frame_f': the_report.program_ends_with_black_frame_f,
                                                'program_ends_with_fade_p': the_report.program_ends_with_fade_p,
                                                'video_notes': the_report.video_notes,
                                                'aconfig_trk1_language': the_report.aconfig_trk1_language,
                                                'aconfig_trk1_type': the_report.aconfig_trk1_type,
                                                'aconfig_trk2_language': the_report.aconfig_trk2_language,
                                                'aconfig_trk2_type': the_report.aconfig_trk2_type,
                                                'aconfig_trk3_language': the_report.aconfig_trk3_language,
                                                'aconfig_trk3_type': the_report.aconfig_trk3_type,
                                                'aconfig_trk4_language': the_report.aconfig_trk4_language,
                                                'aconfig_trk4_type': the_report.aconfig_trk4_type,
                                                'aconfig_trk5_language': the_report.aconfig_trk5_language,
                                                'aconfig_trk5_type': the_report.aconfig_trk5_type,
                                                'aconfig_trk6_language': the_report.aconfig_trk6_language,
                                                'aconfig_trk6_type': the_report.aconfig_trk6_type,
                                                'aconfig_trk7_language': the_report.aconfig_trk7_language,
                                                'aconfig_trk7_type': the_report.aconfig_trk7_type,
                                                'aconfig_trk8_language': the_report.aconfig_trk8_language,
                                                'aconfig_trk8_type': the_report.aconfig_trk8_type,
                                                'abundle_trk1_language': the_report.abundle_trk1_language,
                                                'abundle_trk1_type': the_report.abundle_trk1_type,
                                                'abundle_trk2_language': the_report.abundle_trk2_language,
                                                'abundle_trk2_type': the_report.abundle_trk2_type,
                                                'abundle_trk3_language': the_report.abundle_trk3_language,
                                                'abundle_trk3_type': the_report.abundle_trk3_type,
                                                'abundle_trk4_language': the_report.abundle_trk4_language,
                                                'abundle_trk4_type': the_report.abundle_trk4_type,
                                                'abundle_trk5_language': the_report.abundle_trk5_language,
                                                'abundle_trk5_type': the_report.abundle_trk5_type,
                                                'abundle_trk6_language': the_report.abundle_trk6_language,
                                                'abundle_trk6_type': the_report.abundle_trk6_type,
                                                'abundle_trk7_language': the_report.abundle_trk7_language,
                                                'abundle_trk7_type': the_report.abundle_trk7_type,
                                                'abundle_trk8_language': the_report.abundle_trk8_language,
                                                'abundle_trk8_type': the_report.abundle_trk8_type,
                                                'aconfig_trk1_language_p': the_report.aconfig_trk1_language_p,
                                                'aconfig_trk1_type_p': the_report.aconfig_trk1_type_p,
                                                'aconfig_trk2_language_p': the_report.aconfig_trk2_language_p,
                                                'aconfig_trk2_type_p': the_report.aconfig_trk2_type_p,
                                                'aconfig_trk3_language_p': the_report.aconfig_trk3_language_p,
                                                'aconfig_trk3_type_p': the_report.aconfig_trk3_type_p,
                                                'aconfig_trk4_language_p': the_report.aconfig_trk4_language_p,
                                                'aconfig_trk4_type_p': the_report.aconfig_trk4_type_p,
                                                'aconfig_trk5_language_p': the_report.aconfig_trk5_language_p,
                                                'aconfig_trk5_type_p': the_report.aconfig_trk5_type_p,
                                                'aconfig_trk6_language_p': the_report.aconfig_trk6_language_p,
                                                'aconfig_trk6_type_p': the_report.aconfig_trk6_type_p,
                                                'aconfig_trk7_language_p': the_report.aconfig_trk7_language_p,
                                                'aconfig_trk7_type_p': the_report.aconfig_trk7_type_p,
                                                'aconfig_trk8_language_p': the_report.aconfig_trk8_language_p,
                                                'aconfig_trk8_type_p': the_report.aconfig_trk8_type_p,
                                                'aconfig_verified_f': the_report.aconfig_verified_f,
                                                'aconfig_verified_b': the_report.aconfig_verified_b,
                                                'aconfig_verified_p': the_report.aconfig_verified_p,
                                                'audio_in_sync_with_video_f': the_report.audio_in_sync_with_video_f,
                                                'audio_in_sync_with_video_b': the_report.audio_in_sync_with_video_b,
                                                'audio_in_sync_with_video_p': the_report.audio_in_sync_with_video_p,
                                                'audio_tagged_correctly_f': the_report.audio_tagged_correctly_f,
                                                'audio_tagged_correctly_b': the_report.audio_tagged_correctly_b,
                                                'audio_tagged_correctly_p': the_report.audio_tagged_correctly_p,
                                                'no_audio_cut_off_f': the_report.no_audio_cut_off_f,
                                                'no_audio_cut_off_b': the_report.no_audio_cut_off_b,
                                                'no_audio_cut_off_p': the_report.no_audio_cut_off_p,
                                                'trt_audio_is_trt_video_f': the_report.trt_audio_is_trt_video_f,
                                                'trt_audio_is_trt_video_b': the_report.trt_audio_is_trt_video_b,
                                                'trt_audio_is_trt_video_p': the_report.trt_audio_is_trt_video_p,
                                                'correct_audio_language_f': the_report.correct_audio_language_f,
                                                'correct_audio_language_b': the_report.correct_audio_language_b,
                                                'correct_audio_language_p': the_report.correct_audio_language_p,
                                                'audio_notes': the_report.audio_notes,
                                                'delivery_snapshot_feature': the_report.delivery_snapshot_feature,
                                                'delivery_snapshot_alt_audio': the_report.delivery_snapshot_alt_audio,
                                                'delivery_snapshot_subtitle': the_report.delivery_snapshot_subtitle,
                                                'delivery_snapshot_cc': the_report.delivery_snapshot_cc,
                                                'delivery_snapshot_vendor_notes': the_report.delivery_snapshot_vendor_notes,
                                                'delivery_snapshot_poster_art': the_report.delivery_snapshot_poster_art,
                                                'delivery_snapshot_dub_card': the_report.delivery_snapshot_dub_card,
                                                'delivery_snapshot_other': the_report.delivery_snapshot_other,
                                                'forced_narrative_f': the_report.forced_narrative_f,
                                                'forced_narrative_p': the_report.forced_narrative_p,
                                                'subtitles_on_feature': the_report.subtitles_on_feature,
                                                'subtitles_on_trailer': the_report.subtitles_on_trailer,
                                                'forced_narrative_not_overlapping_f': the_report.forced_narrative_not_overlapping_f,
                                                'forced_narrative_not_overlapping_p': the_report.forced_narrative_not_overlapping_p,
                                                'subtitles_on_feature_not_overlapping': the_report.subtitles_on_feature_not_overlapping,
                                                'subtitles_on_trailer_not_overlapping': the_report.subtitles_on_trailer_not_overlapping,
                                                'dub_card_dimensions_match_feature': the_report.dub_card_dimensions_match_feature,
                                                'dub_card_fps_match_feature': the_report.dub_card_fps_match_feature,
                                                'dub_card_language_match_locale': the_report.dub_card_language_match_locale,
                                                'dub_card_duration_4_to_5': the_report.dub_card_duration_4_to_5,
                                                'dub_card_has_no_audio_tracks': the_report.dub_card_has_no_audio_tracks,
                                                'dub_card_text_not_cutoff_with_cropping': the_report.dub_card_text_not_cutoff_with_cropping,
                                                'cc_in_sync_with_video': the_report.cc_in_sync_with_video,
                                                'subtitles_in_sync_with_video': the_report.subtitles_in_sync_with_video,
                                                'subtitles_have_correct_language': the_report.subtitles_have_correct_language,
                                                'assets_notes': the_report.assets_notes,
                                                'thumb_is_jpeg': the_report.thumb_is_jpeg,
                                                'thumb_dpi_72_or_more': the_report.thumb_dpi_72_or_more,
                                                'thumb_profile_is_rgb': the_report.thumb_profile_is_rgb,
                                                'thumb_same_aspect_ratio_as_video': the_report.thumb_same_aspect_ratio_as_video,
                                                'thumb_only_active_pixels': the_report.thumb_only_active_pixels,
                                                'thumb_horiz_at_least_640': the_report.thumb_horiz_at_least_640,
                                                'thumb_for_each_chapter_stop': the_report.thumb_for_each_chapter_stop,
                                                'poster_is_jpeg': the_report.poster_is_jpeg,
                                                'poster_dpi_72_or_more': the_report.poster_dpi_72_or_more,
                                                'poster_profile_is_rgb': the_report.poster_profile_is_rgb,
                                                'poster_rez_at_least_1400x2100': the_report.poster_rez_at_least_1400x2100,
                                                'poster_aspect_ratio_2x3': the_report.poster_aspect_ratio_2x3,
                                                'poster_key_art_and_title_only': the_report.poster_key_art_and_title_only,
                                                'poster_no_dvdcover_date_urlpromo_tagging': the_report.poster_no_dvdcover_date_urlpromo_tagging,
                                                'image_notes': the_report.image_notes,
                                                'delivery_snapshot_trailer': the_report.delivery_snapshot_trailer,
                                                'trt_f': the_report.trt_f,
                                                'trt_p': the_report.trt_p});
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
                                            ele_dict = {
                                                'description': kill_nothing(the_report.description),
                                                'login': login_name,
                                                'operator': login_name,
                                                'type': kill_nothing(the_report.type),
                                                'bay': kill_nothing(the_report.bay),
                                                'machine_number': kill_nothing(the_report.machine_number),
                                                'client_code': kill_nothing(title.client_code),
                                                'client_name': kill_nothing(title.client_name),
                                                'title': kill_nothing(title.title),
                                                'episode': kill_nothing(title.episode),
                                                'version': kill_nothing(the_report.version),
                                                'title_type': kill_nothing(the_report.title_type),
                                                'format': kill_nothing(the_report.format),
                                                'standard': kill_nothing(the_report.standard),
                                                'timecode': kill_nothing(the_report.timecode),
                                                'po_number': kill_nothing(title.po_number),
                                                'style': kill_nothing(the_report.style),
                                                'order_code': kill_nothing(title.order_code),
                                                'title_code': kill_nothing(title.code),
                                                'work_order_code': kill_nothing(wo.code),
                                                'conclusion': kill_nothing(the_report.conclusion),
                                                'source_code': kill_nothing(source_codes),
                                                'wo_name': kill_nothing(wo.process),
                                                'aspect_ratio': kill_nothing(the_report.aspect_ratio),
                                                'frame_rate': kill_nothing(the_report.frame_rate),
                                                'roll_up': kill_nothing(the_report.roll_up),
                                                'bars_tone': kill_nothing(the_report.bars_tone),
                                                'black_silence_1': kill_nothing(the_report.black_silence_1),
                                                'slate_silence': kill_nothing(the_report.slate_silence),
                                                'black_silence_2': kill_nothing(the_report.black_silence_2),
                                                'video_mod_disclaimer': kill_nothing(the_report.video_mod_disclaimer),
                                                'start_of_program': kill_nothing(the_report.start_of_program),
                                                'end_of_program': kill_nothing(the_report.end_of_program),
                                                'active_video_begins': kill_nothing(the_report.active_video_begins),
                                                'active_video_ends': kill_nothing(the_report.active_video_ends),
                                                'horizontal_blanking': kill_nothing(the_report.horizontal_blanking),
                                                'vertical_blanking': kill_nothing(the_report.vertical_blanking),
                                                'video_average': kill_nothing(the_report.video_average),
                                                'video_peak': kill_nothing(the_report.video_peak),
                                                'chroma_average': kill_nothing(the_report.chroma_average),
                                                'chroma_peak': kill_nothing(the_report.chroma_peak),
                                                'video_sync': kill_nothing(the_report.video_sync),
                                                'chroma_burst': kill_nothing(the_report.chroma_burst),
                                                'setup': kill_nothing(the_report.setup),
                                                'control_track': kill_nothing(the_report.control_track),
                                                'video_rf': kill_nothing(the_report.video_rf),
                                                'front_porch': kill_nothing(the_report.front_porch),
                                                'sync_duration': kill_nothing(the_report.sync_duration),
                                                'burst_duration': kill_nothing(the_report.burst_duration),
                                                'total_runtime': kill_nothing(the_report.total_runtime),
                                                'tv_feature_trailer': kill_nothing(the_report.tv_feature_trailer),
                                                'video_aspect_ratio': kill_nothing(the_report.video_aspect_ratio),
                                                'textless_at_tail': kill_nothing(the_report.textless_at_tail),
                                                'cc_subtitles': kill_nothing(the_report.cc_subtitles),
                                                'timecodes': kill_nothing(the_report.timecodes),
                                                'vitc': kill_nothing(the_report.vitc),
                                                'ltc': kill_nothing(the_report.ltc),
                                                'record_vendor': kill_nothing(the_report.record_vendor),
                                                'record_date': kill_nothing(the_report.record_date),
                                                'language': kill_nothing(the_report.language),
                                                'comp_mne_sync': kill_nothing(the_report.comp_mne_sync),
                                                'comp_mne_phase': kill_nothing(the_report.comp_mne_phase),
                                                'missing_mne': kill_nothing(the_report.missing_mne),
                                                'average_dialogue': kill_nothing(the_report.average_dialogue),
                                                'dec_a1': kill_nothing(the_report.dec_a1),
                                                'dec_a2': kill_nothing(the_report.dec_a2),
                                                'dec_a3': kill_nothing(the_report.dec_a3),
                                                'dec_a4': kill_nothing(the_report.dec_a4),
                                                'dec_b1': kill_nothing(the_report.dec_b1),
                                                'dec_b2': kill_nothing(the_report.dec_b2),
                                                'dec_b3': kill_nothing(the_report.dec_b3),
                                                'dec_b4': kill_nothing(the_report.dec_b4),
                                                'dec_c1': kill_nothing(the_report.dec_c1),
                                                'dec_c2': kill_nothing(the_report.dec_c2),
                                                'dec_c3': kill_nothing(the_report.dec_c3),
                                                'dec_c4': kill_nothing(the_report.dec_c4),
                                                'dec_d1': kill_nothing(the_report.dec_d1),
                                                'dec_d2': kill_nothing(the_report.dec_d2),
                                                'dec_d3': kill_nothing(the_report.dec_d3),
                                                'dec_d4': kill_nothing(the_report.dec_d4),
                                                'tape_pack': kill_nothing(the_report.tape_pack),
                                                'label': kill_nothing(the_report.label),
                                                'head_logo': kill_nothing(the_report.head_logo),
                                                'tail_logo': kill_nothing(the_report.tail_logo),
                                                'notices': kill_nothing(the_report.notices),
                                                'vendor_id': kill_nothing(the_report.vendor_id),
                                                'roll_up_f': kill_nothing(the_report.roll_up_f),
                                                'bars_tone_f': kill_nothing(the_report.bars_tone_f),
                                                'black_silence_1_f': kill_nothing(the_report.black_silence_1_f),
                                                'black_silence_2_f': kill_nothing(the_report.black_silence_2_f),
                                                'slate_silence_f': kill_nothing(the_report.slate_silence_f),
                                                'video_mod_disclaimer_f': kill_nothing(the_report.video_mod_disclaimer_f),
                                                'start_of_program_f': kill_nothing(the_report.start_of_program_f),
                                                'end_of_program_f': kill_nothing(the_report.end_of_program_f)
                                            }
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
                                    var class_name = 'qc_reports.element_eval_wdg.ElementEvalWdg';
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
                          spt.api.load_panel(loader_el, 'qc_reports.QCReportClonerWdg', {'type': type, 'wo_code': wo_code, 'report_code': report_code, 'new_titles': title_codes});
                          spt.app_busy.hide();
                          
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (report_code)}
        return behavior

    def get_display(my):
        login = Environment.get_login()
        this_user = login.get_login()
        wo_code = my.kwargs.get('wo_code')
        report_code = my.kwargs.get('report_code')
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

            all_titles = [this_title]
            table = Table()
            table.add_style('width: 100%s;' % '%')
            # Need Select All Checkbox Here
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
            # Need Title/Order Adder Here
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

                qc_wos = server.eval("@SOBJECT(sthpw/task['title_code','%s']['search_type','twog/proj?project=twog']['assigned_login_group','in','qc|qc supervisor'])" % title_code)
                for qcwo in qc_wos:
                    qcwocode = qcwo.get('lookup_code')
                    # Used to restrict such that you could not clone to the same Work Order
                    wotbl.add_row()
                    check = CheckboxWdg('clonecheck_%s' % qcwocode)

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
            loader_tbl.add_style('width: 100%;')
            widget.add(loader_tbl)
            tbl2 = Table()
            tbl2.add_style('width: 100%;')
            tbl2.add_row()
            t1 = tbl2.add_cell(' ')
            t1.add_attr('width','47%')
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
                # Need Select All Checkbox Here
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

                qc_wos_expr = "@SOBJECT(sthpw/task['title_code','%s']['search_type','twog/proj?project=twog']['assigned_login_group','in','qc|qc supervisor'])" % title_code
                qc_wos = server.eval(qc_wos_expr)
                for qcwo in qc_wos:
                    qcwocode = qcwo.get('lookup_code')
                    if qcwocode != wo_code:
                        wotbl.add_row()
                        check = CheckboxWdg('clonecheck_%s' % qcwocode)
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
        module = 'qc_reports'

        if type == 'ElementEvalWdg':
            module = 'element_eval_wdg'
        elif type == 'TechEvalWdg':
            module = 'tech_eval_wdg'
        elif type == 'MetaDataReportWdg':
            module = 'metadata_report_wdg'
        elif type == 'PreQualEvalWdg':
            module = 'prequal_eval_wdg'

        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                          var code = '%s';
                          var module = '%s';
                          var type = '%s';
                          var name = '%s';
                          var class_name = 'qc_reports.' + module + '.' + type;
                          kwargs = {'code': code}
                          spt.popup.close(spt.popup.get_popup(bvr.src_el));
                          //spt.panel.load_popup(name + ' for ' + code, class_name, kwargs);
                          spt.tab.add_new(type + '_qc_report_for_' + code, name + ' for ' + code, class_name, kwargs);
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         ''' % (code, module, type, name)}

        return behavior

    def get_display(my):
        code = my.kwargs.get('code')
        widget = DivWdg()
        table = Table()
        types = {
            'PreQual Evaluation': 'PreQualEvalWdg',
            'Element Evaluation': 'ElementEvalWdg',
            'Technical Evaluation': 'TechEvalWdg',
            'MetaData Report': 'MetaDataReportWdg'
        }
        colors = {
            'PreQual Evaluation': '#a2b2d2',
            'Element Evaluation': '#d5c9dd',
            'Technical Evaluation': '#aa8e98',
            'MetaData Report': '#c6e2d9'
        }
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


class PrintQCReportWdg(Command):

    def __init__(my, **kwargs):
        super(PrintQCReportWdg, my).__init__(**kwargs)
        my.html = unicode(kwargs.get('html'))
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
                            spt.api.load_panel(addportion, 'qc_reports.ElementEvalBarcodesWdg', send_data);
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
            for el in element_bcs:
                brow = bctable.add_row()
                brow.add_attr('line',rowct)
                brow.add_attr('code',el.get('code'))
                brow.add_attr('class','element_barcodes')
                nw = bctable.add_cell('Part %s' % rowct)
                nw.add_attr('nowrap','nowrap')
                bctable.add_cell(my.txtbox('barcode-%s' % rowct, el.get('barcode'),width='100px',js='no'))
                bctable.add_cell(my.txtbox('program_start-%s' % rowct, el.get('program_start'),width='150px',js='yes'))
                bctable.add_cell(my.txtbox('f1-%s' % rowct, el.get('f1'),width='20px',js='no'))
                bctable.add_cell(my.txtbox('program_end-%s' % rowct, el.get('program_end'),width='150px',js='yes'))
                bctable.add_cell(my.txtbox('f2-%s' % rowct, el.get('f2'),width='20px',js='no'))
                bctable.add_cell(my.txtbox('length-%s' % rowct, el.get('length'),width='155px',js='yes'))
                bctable.add_cell(my.txtbox('label_info-%s' % rowct, el.get('label_info'),width='190px',js='no'))
                bctable.add_cell(my.txtbox('slate_info-%s' % rowct, el.get('slate_info'),width='190px',js='no'))
                killer = bctable.add_cell('<b>X</b>')#This must delete the entry
                killer.add_style('cursor: pointer;')
                killer.add_behavior(my.get_kill_bvr(rowct, wo_code, el.get('code')))
                rowct += 1

        erow = bctable.add_row()
        erow.add_attr('line',rowct)
        erow.add_attr('code','')
        erow.add_attr('class','element_barcodes')
        nw2 = bctable.add_cell('Part %s' % rowct)
        nw2.add_attr('nowrap','nowrap')
        bctable.add_cell(my.txtbox('barcode-%s' % rowct,'',width='100px',js='no'))
        bctable.add_cell(my.txtbox('program_start-%s' % rowct,'',width='150px',js='yes'))
        bctable.add_cell(my.txtbox('f1-%s' % rowct,'',width='20px',js='yes'))
        bctable.add_cell(my.txtbox('program_end-%s' % rowct,'',width='150px',js='yes'))
        bctable.add_cell(my.txtbox('f2-%s' % rowct,'',width='20px',js='no'))
        bctable.add_cell(my.txtbox('length-%s' % rowct,'',width='155px',js='yes'))
        bctable.add_cell(my.txtbox('label_info-%s' % rowct,'',width='190px',js='no'))
        bctable.add_cell(my.txtbox('slate_info-%s' % rowct,'',width='190px',js='no'))
        addnew = bctable.add_cell('<b>+</b>')  # This must add new entry
        addnew.add_style('cursor: pointer;')
        addnew.add_behavior(my.get_add_line(rowct,wo_code, code))
        erow2 = bctable.add_row()
        erow2.add_attr('class','new_barcode_line')
        return bctable


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

    def txtbox(my, name, val, width='200px', js=False):
        txt = TextWdg(name)
        txt.add_attr('id',name)
        txt.add_style('width: %s;' % width)
        txt.set_value(val)

        if js:
            txt.add_behavior(my.get_add_dots())

        return txt

    def get_display(my):
        wo_code = my.kwargs.get('wo_code')
        ell_code = my.kwargs.get('ell_code')
        widget = DivWdg()
        table = Table()
        table.add_attr('id', 'timecode_shifter')
        table.add_row()
        sa = table.add_cell('Start After:')
        sa.add_attr('nowrap', 'nowrap')
        table.add_cell(my.txtbox('start_at', '', width='75px', js=True))
        sb = table.add_cell('(Must exactly match the following format EX: 01:33:57:19)')
        sb.add_attr('nowrap', 'nowrap')
        table.add_row()
        table.add_cell('Add:')
        table.add_cell(my.txtbox('add_amt', '', width='75px', js=True))
        sc = table.add_cell('(Minute:Second:Frame or Minute:Second)')
        sc.add_attr('nowrap', 'nowrap')
        table.add_row()
        butt = table.add_cell('<input type="button" value="Shift Timecodes"/>')
        butt.add_behavior(my.shift_em(wo_code, ell_code))
        widget.add(table)

        return widget
