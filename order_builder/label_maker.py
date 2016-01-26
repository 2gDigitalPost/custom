__all__ = ["LabelLauncherWdg", "LabelWdg"]

import os, datetime

from client.tactic_client_lib import TacticServerStub

from pyasm.web import Table, DivWdg
from pyasm.widget import SelectWdg
from tactic.ui.common import BaseTableElementWdg
from tactic.ui.common import BaseRefreshWdg

from mako.template import Template
from common_tools.utils import make_zero_padded


class LabelLauncherWdg(BaseTableElementWdg):

    def init(my):
        my.server = TacticServerStub.get()

    def get_launch_behavior(my):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''        
                        try{
                          var server = TacticServerStub.get();
                          var code = bvr.src_el.get('code');
                          var title = bvr.src_el.get('title');
                          var class_name = 'order_builder.LabelWdg';
                          kwargs = {
                                           'code': code
                                   };
                          spt.panel.load_popup('Print Label for ' + title, class_name, kwargs);
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
         '''}
        return behavior

    def get_display(my):
        sobject = my.get_current_sobject()
        code = sobject.get_code()
        title = sobject.get_value('title')
        widget = DivWdg()
        table = Table()
        table.add_attr('width', '50px')
        table.add_row()
        cell1 = table.add_cell(
                '<img border="0" style="vertical-align: middle" title="" src="/context/icons/silk/printer.png">'
        )
        launch_behavior = my.get_launch_behavior()
        cell1.add_attr('code', code)
        cell1.add_attr('title', title)
        cell1.add_style('cursor', 'pointer')
        cell1.add_behavior(launch_behavior)
        widget.add(table)

        return widget


class LabelWdg(BaseRefreshWdg):

    def init(my):
        my.server = TacticServerStub.get()

        current_directory = os.path.dirname(__file__)
        my.template_files = {
            'HDCAM': os.path.join(current_directory, 'templates/HDCAM_label.html'),
            'HDCAM_FILM_FOX': os.path.join(current_directory, 'templates/HDCAM_FILM_FOX_label.html'),
            'HDCAM_TV_FOX': os.path.join(current_directory, 'templates/HDCAM_TV_FOX_label.html'),
            'HDCAM DIGIBETA': os.path.join(current_directory, 'templates/HDCAM_Digibeta_label.html'),
            'DVD': os.path.join(current_directory, 'templates/DVD_Label.html'),
            'D5': os.path.join(current_directory, 'templates/D5_label.html')
        }

        # This is needed to present the keys in template_files in order
        # Since the platform is using Python 2.6, Ordered dictionaries are not available by default
        my.template_file_types = ('HDCAM', 'HDCAM_FILM_FOX', 'HDCAM_TV_FOX', 'HDCAM DIGIBETA', 'DVD', 'D5')
    
    def get_display(my):
        code = str(my.kwargs.get('code'))
        source = my.server.eval("@SOBJECT(twog/source['code','%s'])" % code)[0]
        client_name = ''

        if source.get('client_code'):
            client_names = my.server.eval("@GET(twog/client['code','%s'].name)" % source.get('client_code'))
            if len(client_names) > 0:
                client_name = client_names[0]

        whole_title = source.get('title')
        if source.get('episode'):
            whole_title = '%s: %s' % (whole_title, source.get('episode')) 

        chunk_lines = whole_title
        if len(whole_title) > 20:
            chunks = whole_title.split(' ')
            len_chunks = len(chunks)
            chunk_sum = 0
            last_bit = ''
            chunk_lines = ''
            for chunk in chunks:
                clen = len(chunk)
                chunk_sum = clen + chunk_sum + 1
                if chunk_sum > 20:
                    chunk_sum = 0
                    chunk_lines = '%s %s<br/>' % (chunk_lines, last_bit)
                else:
                    if chunk_lines == '':
                        chunk_lines = last_bit
                    else:
                        chunk_lines = '%s %s' % (chunk_lines, last_bit)
                last_bit = chunk

            end_part = chunks[len_chunks - 1]
            len_end = len(end_part)
            if len_end + chunk_sum > 20:
                chunk_lines = '%s<br/>%s' % (chunk_lines, end_part)
            else:
                chunk_lines = '%s %s' % (chunk_lines, end_part)
        whole_title = chunk_lines
            
        barcode = source.get('barcode')
        captioning = source.get('captioning') or 'N/A'
        subtitles = source.get('subtitles') or 'N/A'

        table = Table()
        table.add_attr('class', 'print_label_wdg')
        table.add_row()
        select = SelectWdg('label_type')

        for file_type in my.template_file_types:
            select.append_option(file_type, file_type)

        selly = table.add_cell(select)
        selly.add_attr('align', 'center')
        table.add_row()
        date = str(datetime.datetime.now()).split(' ')[0]

        audio_lines = ''
        audio_layout = ((1, 7), (2, 8), (3, 9), (4, 10), (5, 11), (6, 12))

        for layout in audio_layout:
            this_line = ''

            left_digit = layout[0]
            left_digit_str = make_zero_padded(str(left_digit), 2)
            left_line = ''
            found_left = False

            if source.get('audio_ch_%s' % left_digit) not in [None, '']:
                left_line = '<div id="chleftreplace">CH%s: %s</div>' % (left_digit_str, source.get('audio_ch_%s' % left_digit))
                found_left = True

            right_digit = layout[1]
            right_digit_str = make_zero_padded(str(right_digit), 2)
            right_line = ''
            found_right = False

            if source.get('audio_ch_%s' % right_digit) not in [None, '']:
                right_line = '<div id="chrightreplace">CH%s: %s</div>' % (right_digit_str, source.get('audio_ch_%s' % right_digit))
                found_right = True

            if found_left and not found_right:
                this_line = '%s<div id="chrightreplace">&nbsp;</div>\n' % left_line
            if found_left and found_right:
                this_line = '%s%s\n' % (left_line, right_line)
            if not found_left and found_right:
                this_line = '<div id="chleftreplace">&nbsp;</div>%s\n' % right_line
            if this_line != '':
                audio_lines = '%s' % this_line

        misc_info = []

        if source.get('description'):
            misc_info.append('<span class="replace"><i>{0}</i></span>'.format(source.get('description')))
        if source.get('aspect_ratio'):
            misc_info.append('<span class="replace">Aspect Ratio: {0}</span>'.format(source.get('aspect_ratio')))
        if source.get('captioning'):
            misc_info.append('<span class="replace">Captioning: {0}</span>'.format(source.get('captioning')))
        if source.get('textless'):
            misc_info.append('<span class="replace">Textless: {0}</span>'.format(source.get('textless')))
        if source.get('po_number'):
            misc_info.append('<span class="replace">PO #: {0}</span>'.format(source.get('po_number')))

        mtminfo = ''
        if source.get('description'):
            mtminfo = '''%s<span id="replace"><i>%s</i></span><br/>''' % (mtminfo, source.get('description'))
        if source.get('aspect_ratio'):
            mtminfo = '''%s<span id="replace">Aspect Ratio: %s</span><br/>''' % (mtminfo, source.get('aspect_ratio'))
        if source.get('captioning'):
            mtminfo = '''%s<span id="replace">Captioning: %s</span><br/>''' % (mtminfo, source.get('captioning'))
        if source.get('textless'):
            mtminfo = '''%s<span id="replace">Textless: %s</span><br/>''' % (mtminfo, source.get('textless'))
        if source.get('po_number'):
            mtminfo = '''%s<span id="replace">PO #: %s</span><br/>''' % (mtminfo, source.get('po_number'))

        if barcode:
            for file_type in my.template_file_types:
                if file_type == 'HDCAM':
                    label_page_template = Template(filename=my.template_files[file_type])

                    context = {
                        'WHOLETITLE': whole_title,
                        'VERSION': source.get('version'),
                        'BARCODE': barcode,
                        'DATE': str(date),
                        'STANDARD': source.get('standard'),
                        'FRAME_RATE': source.get('frame_rate'),
                        'STRAT2G_PART': source.get('part'),
                        'TRT': source.get('total_run_time'),
                        'CLIENT': client_name,
                        'MTMINFOCHUNK_SMALL': '<br/>'.join(misc_info).replace('replace', 'small'),
                        'AUDIO_CHANNELS_SMALL': audio_lines.replace('replace', 'small'),
                        'MTMINFOCHUNK_MEDIUM': '<br/>'.join(misc_info).replace('replace', 'medium'),
                        'AUDIO_CHANNELS': audio_lines.replace('replace', ''),
                        'MTMINFOCHUNK_LARGE': '<br/>'.join(misc_info).replace('replace', 'large'),
                        'AUDIO_CHANNELS_LARGE': audio_lines.replace('replace', '_large')
                    }

                    result = label_page_template.render(**context)
                else:
                    result = ''
                    template_file = open(my.template_files[file_type], 'r')
                    for line in template_file:
                        if not line.strip():
                            continue
                        else:
                            line = line.rstrip('\r\n')
                            line = line.replace('[WHOLETITLE]', whole_title)
                            line = line.replace('[TITLE]', source.get('title'))
                            line = line.replace('[EPISODE]', source.get('episode'))
                            line = line.replace('[BARCODE]', barcode)
                            line = line.replace('[TOTAL_RUN_TIME]', source.get('total_run_time'))
                            line = line.replace('[TRT]', source.get('total_run_time'))
                            line = line.replace('[VERSION]', source.get('version'))
                            line = line.replace('[ASPECT_RATIO]', source.get('aspect_ratio'))
                            line = line.replace('[COLOR_SPACE]', source.get('color_space'))
                            line = line.replace('[STRAT2G_PART]', source.get('part'))
                            if '[AUDIO_CHANNELS' in line:
                                replacer = ''
                                full_tag = '[AUDIO_CHANNELS]'
                                if 'SMALL' in line:
                                    replacer = '_small'
                                    full_tag = '[AUDIO_CHANNELS_SMALL]'
                                if 'LARGE' in line:
                                    replacer = '_large'
                                    full_tag = '[AUDIO_CHANNELS_LARGE]'
                                line = line.replace(full_tag, audio_lines.replace('replace', replacer))
                            if '[MTMINFOCHUNK_' in line:
                                replacer = 'medium'
                                full_tag = '[MTMINFOCHUNK_MEDIUM]'
                                if 'SMALL' in line:
                                    replacer = 'small'
                                    full_tag = '[MTMINFOCHUNK_SMALL]'
                                elif 'LARGE' in line:
                                    replacer = 'large'
                                    full_tag = '[MTMINFOCHUNK_LARGE]'
                                line = line.replace(full_tag, mtminfo.replace('replace', replacer))
                            line = line.replace('[AUDIO_CH01]', source.get('audio_ch_1'))
                            line = line.replace('[AUDIO_CH02]', source.get('audio_ch_2'))
                            line = line.replace('[AUDIO_CH03]', source.get('audio_ch_3'))
                            line = line.replace('[AUDIO_CH04]', source.get('audio_ch_4'))
                            line = line.replace('[AUDIO_CH05]', source.get('audio_ch_5'))
                            line = line.replace('[AUDIO_CH06]', source.get('audio_ch_6'))
                            line = line.replace('[AUDIO_CH07]', source.get('audio_ch_7'))
                            line = line.replace('[AUDIO_CH08]', source.get('audio_ch_8'))
                            line = line.replace('[AUDIO_CH09]', source.get('audio_ch_9'))
                            line = line.replace('[AUDIO_CH10]', source.get('audio_ch_10'))
                            line = line.replace('[AUDIO_CH11]', source.get('audio_ch_11'))
                            line = line.replace('[AUDIO_CH12]', source.get('audio_ch_12'))
                            line = line.replace('[CH01]', source.get('audio_ch_1'))
                            line = line.replace('[CH02]', source.get('audio_ch_2'))
                            line = line.replace('[CH03]', source.get('audio_ch_3'))
                            line = line.replace('[CH04]', source.get('audio_ch_4'))
                            line = line.replace('[CH05]', source.get('audio_ch_5'))
                            line = line.replace('[CH06]', source.get('audio_ch_6'))
                            line = line.replace('[CH07]', source.get('audio_ch_7'))
                            line = line.replace('[CH08]', source.get('audio_ch_8'))
                            line = line.replace('[CH09]', source.get('audio_ch_9'))
                            line = line.replace('[CH10]', source.get('audio_ch_10'))
                            line = line.replace('[CH11]', source.get('audio_ch_11'))
                            line = line.replace('[CH12]', source.get('audio_ch_12'))
                            line = line.replace('[STANDARD]', source.get('standard'))
                            line = line.replace('[CLIENT]', client_name)
                            line = line.replace('[FRAME_RATE]', source.get('frame_rate'))
                            line = line.replace('[SOURCE_TYPE]', source.get('source_type'))
                            line = line.replace('[TYPE]', source.get('source_type'))
                            line = line.replace('[GENERATION]', source.get('generation'))
                            line = line.replace('[DESCRIPTION]', source.get('description'))
                            line = line.replace('[TEXTLESS]', source.get('textless'))
                            line = line.replace('[PO_NUMBER]', source.get('po_number'))
                            line = line.replace('[CLIENT_ASSET_ID]', source.get('client_asset_id'))
                            line = line.replace('[FORMAT]', source.get('format'))
                            line = line.replace('[CAPTIONING]', captioning)
                            line = line.replace('[SUBTITLES]', subtitles)
                            line = line.replace('[ADDITIONAL_LABEL_INFO]', source.get('additional_label_info'))
                            line = line.replace('[DATE]', str(date))
                            result = '%s%s' % (result, line)

                    template_file.close()

                new_bc_file = '/var/www/html/source_labels/printed_labels/%s_%s.html' % (barcode, file_type)

                if os.path.exists(new_bc_file):
                    os.system('rm -rf %s' % new_bc_file)

                new_file = open(new_bc_file, 'w')
                new_file.write(result)
                new_file.close()

            t1 = table.add_cell('')
            t1.add_style('width', '100%')

            input_button_string = '<input type="button" value="Get Label Page For {0} :({1})"/>'.format(
                source.get('title'), barcode
            )
            launch_button = table.add_cell(input_button_string)
            launch_button.add_behavior(my.get_open_barcode_label_page(barcode))

            t2 = table.add_cell('')
            t2.add_style('width', '100%')
        else:
            table.add_cell('This Source does not have a barcode')

        return table

    @staticmethod
    def get_open_barcode_label_page(barcode):
        behavior = {
            'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    var barcode = '%s';
    var top_el = spt.api.get_parent(bvr.src_el, '.print_label_wdg');
    var sels = top_el.getElementsByTagName('select');
    var type_sel = '';

    for(var r = 0; r < sels.length; r++){
        if(sels[r].name == 'label_type'){
            type_sel = sels[r];
        }
    }

    var type = type_sel.value;
    var url = '/source_labels/printed_labels/' + barcode + '_' + type + '.html';
    new_win = window.open(url, '_blank',
                          'toolbar=1, location=1, directories=1, status=1, menubar=1, scrollbars=0, resizable=0');
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
         ''' % barcode
        }
        return behavior
