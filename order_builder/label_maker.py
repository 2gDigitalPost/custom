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
            'D5': os.path.join(current_directory, 'templates/D5_label.html'),
            'LTO': os.path.join(current_directory, 'templates/LTO_label.html')
        }

        # This is needed to present the keys in template_files in order
        # Since the platform is using Python 2.6, Ordered dictionaries are not available by default
        my.template_file_types = ('HDCAM', 'HDCAM_FILM_FOX', 'HDCAM_TV_FOX', 'HDCAM DIGIBETA', 'DVD', 'D5', 'LTO')
    
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
        audio_layouts = (1, 7, 2, 8, 3, 9, 4, 10, 5, 11, 6, 12)

        for audio_layout in audio_layouts:
            audio_layout_str = make_zero_padded(str(audio_layout), 2)
            audio_data = source.get('audio_ch_{0}'.format(audio_layout))

            if audio_data:
                audio_lines += '<div>CH{0}: {1}</div>'.format(audio_layout_str, audio_data)

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

        if barcode:
            for file_type, file_location in my.template_files.items():
                label_page_template = Template(filename=file_location)

                context = {
                    'BARCODE': barcode,
                    'CLIENT': client_name,
                    'DATE': str(date),
                    'FRAME_RATE': source.get('frame_rate'),
                    'STANDARD': source.get('standard'),
                    'STRAT2G_PART': source.get('part'),
                    'TOTAL_RUN_TIME': source.get('total_run_time'),
                    'VERSION': source.get('version')
                }

                if file_type == 'HDCAM':
                    context.update({
                        'WHOLETITLE': whole_title,
                        'TOTAL_RUN_TIME': source.get('total_run_time'),
                        'MTMINFOCHUNK_SMALL': '<br/>'.join(misc_info).replace('replace', 'small'),
                        'AUDIO_CHANNELS_SMALL': audio_lines,
                        'MTMINFOCHUNK_MEDIUM': '<br/>'.join(misc_info).replace('replace', 'medium'),
                        'AUDIO_CHANNELS': audio_lines,
                        'MTMINFOCHUNK_LARGE': '<br/>'.join(misc_info).replace('replace', 'large'),
                        'AUDIO_CHANNELS_LARGE': audio_lines
                    })
                elif file_type == 'LTO':
                    context.update({
                        'WHOLETITLE': whole_title,
                        'TOTAL_RUN_TIME': source.get('total_run_time'),
                        'MTMINFOCHUNK_SMALL': '<br/>'.join(misc_info),
                        'AUDIO_CHANNELS_SMALL': audio_lines,
                        'MTMINFOCHUNK_MEDIUM': '<br/>'.join(misc_info).replace('replace', 'medium'),
                        'AUDIO_CHANNELS': audio_lines,
                        'MTMINFOCHUNK_LARGE': '<br/>'.join(misc_info).replace('replace', 'large'),
                        'AUDIO_CHANNELS_LARGE': audio_lines
                    })
                elif file_type == 'DVD':
                    context.update({
                        'TITLE': source.get('title'),
                        'TYPE': source.get('source_type'),
                        'DESCRIPTION': source.get('description'),
                        'AUDIO_CH01': source.get('audio_ch_1'),
                        'AUDIO_CH02': source.get('audio_ch_2'),
                        'AUDIO_CH03': source.get('audio_ch_3'),
                        'AUDIO_CH04': source.get('audio_ch_4'),
                        'AUDIO_CH05': source.get('audio_ch_5'),
                        'AUDIO_CH06': source.get('audio_ch_6'),
                        'SOURCE_TYPE': source.get('source_type'),
                        'GENERATION': source.get('generation'),
                    })
                elif file_type == 'HDCAM DIGIBETA':
                    context.update({
                        'TOTAL_RUN_TIME': source.get('total_run_time'),
                        'TITLE': source.get('title'),
                        'DESCRIPTION': source.get('description'),
                        'ASPECT_RATIO': source.get('aspect_ratio'),
                        'CH01': source.get('audio_ch_1'),
                        'CH02': source.get('audio_ch_2'),
                        'CH03': source.get('audio_ch_3'),
                        'CH04': source.get('audio_ch_4'),
                    })
                elif file_type == 'D5':
                    context.update({
                        'TOTAL_RUN_TIME': source.get('total_run_time'),
                        'TITLE': source.get('title'),
                        'DESCRIPTION': source.get('description'),
                        'ASPECT_RATIO': source.get('aspect_ratio'),
                        'CH01': source.get('audio_ch_1'),
                        'CH02': source.get('audio_ch_2'),
                        'CH03': source.get('audio_ch_3'),
                        'CH04': source.get('audio_ch_4'),
                        'TEXTLESS': source.get('textless'),
                        'COLOR_SPACE': source.get('color_space'),
                        'MTMINFOCHUNK_SMALL': '<br/>'.join(misc_info).replace('replace', 'small'),
                        'AUDIO_CHANNELS': audio_lines,
                        'MTMINFOCHUNK_MEDIUM': '<br/>'.join(misc_info).replace('replace', 'medium'),
                        'WHOLETITLE': whole_title,
                    })
                elif file_type == 'HDCAM_FILM_FOX':
                    context.update({
                        'TOTAL_RUN_TIME': source.get('total_run_time'),
                        'TITLE': source.get('title'),
                        'DESCRIPTION': source.get('description'),
                        'ASPECT_RATIO': source.get('aspect_ratio'),
                        'CH01': source.get('audio_ch_1'),
                        'CH02': source.get('audio_ch_2'),
                        'CH03': source.get('audio_ch_3'),
                        'CH04': source.get('audio_ch_4'),
                        'CH07': source.get('audio_ch_7'),
                        'CH08': source.get('audio_ch_8'),
                        'CH09': source.get('audio_ch_9'),
                        'CH10': source.get('audio_ch_10'),
                        'CH05': source.get('audio_ch_5'),
                        'CH11': source.get('audio_ch_11'),
                        'CH06': source.get('audio_ch_6'),
                        'CH12': source.get('audio_ch_12'),
                        'PO_NUMBER': source.get('po_number'),
                        'CLIENT_ASSET_ID': source.get('client_asset_id'),
                        'FORMAT': source.get('format'),
                        'TEXTLESS': source.get('textless'),
                        'CAPTIONING': captioning,
                        'SUBTITLES': subtitles,
                        'ADDITIONAL_LABEL_INFO': source.get('additional_label_info')
                    })
                elif file_type == 'HDCAM_TV_FOX':
                    context.update({
                        'TOTAL_RUN_TIME': source.get('total_run_time'),
                        'TITLE': source.get('title'),
                        'DESCRIPTION': source.get('description'),
                        'ASPECT_RATIO': source.get('aspect_ratio'),
                        'CH01': source.get('audio_ch_1'),
                        'CH02': source.get('audio_ch_2'),
                        'CH03': source.get('audio_ch_3'),
                        'CH04': source.get('audio_ch_4'),
                        'CH07': source.get('audio_ch_7'),
                        'CH08': source.get('audio_ch_8'),
                        'CH09': source.get('audio_ch_9'),
                        'CH10': source.get('audio_ch_10'),
                        'CH05': source.get('audio_ch_5'),
                        'CH11': source.get('audio_ch_11'),
                        'CH06': source.get('audio_ch_6'),
                        'CH12': source.get('audio_ch_12'),
                        'EPISODE': source.get('episode'),
                        'PO_NUMBER': source.get('po_number'),
                        'CLIENT_ASSET_ID': source.get('client_asset_id'),
                        'FORMAT': source.get('format'),
                        'TEXTLESS': source.get('textless'),
                        'CAPTIONING': captioning,
                        'SUBTITLES': subtitles,
                        'ADDITIONAL_LABEL_INFO': source.get('additional_label_info')
                    })

                result = label_page_template.render(**context)

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

    for (var r = 0; r < sels.length; r++) {
        if (sels[r].name == 'label_type') {
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
