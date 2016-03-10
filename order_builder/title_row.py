from tactic.ui.common import BaseRefreshWdg
from widget.button_small_new_wdg import ButtonSmallNewWdg

from pyasm.common import Environment
from pyasm.search import Search
from pyasm.web import Table
from widget.new_icon_wdg import CustomIconWdg

from alternative_elements.customcheckbox import CustomCheckboxWdg
from common_tools.common_functions import fix_date
from order_builder_utils import OBScripts, get_selected_color_behavior, get_upload_behavior, get_scratch_pipe_behavior
from qc_reports import QCReportLauncherWdg

from deliverable_count_wdg import DeliverableCountWdg
from nighttime_hotlist.nighttime_hotlist import BigBoardSelectWdg
from proj_row import ProjRow
from prereq_count_wdg import PreReqCountWdg
from sources_row import SourcesRow


class TitleRow(BaseRefreshWdg):

    def init(my):
        my.search_type = 'twog/title'
        my.title = 'Title'
        my.sk = ''
        my.code = ''
        my.search_id = ''
        my.user = ''
        my.order_sk = ''
        my.parent_sk = ''
        my.parent_sid = ''
        my.x_butt = "<img src='/context/icons/common/BtnKill.gif' title='Delete' name='Delete'/>"
        my.scratch_pipe = "<table border=0 cellspacing=0 cellpadding=2 style='font-size: 60%s; border-color: #FFFFFF; border-style: solid; border-width: 1px; cursor: pointer;'><tr><td align='center'><font color='#FFFFFF'>Pipeline</font></td></tr></table>" % '%'
        my.width = '1000px'
        my.height = '300px'
        my.disp_mode = 'Normal'
        my.small = False
        my.groups_str = ''
        my.is_master = False
        my.is_master_str = 'false'
        my.off_color = '#d9edcf'
        my.on_color = '#ff0000'
        my.stat_colors = {
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
            'Buddy Check In_Progress': '#1aade3',
            'Buddy Check In Progress': '#1aade3'
        }

    def get_display(my):
        my.sk = str(my.kwargs.get('sk'))
        my.code = my.sk.split('code=')[1]
        my.order_sk = str(my.kwargs.get('parent_sk'))
        order_code = my.order_sk.split('code=')[1]
        my.parent_sid = str(my.kwargs.get('parent_sid'))
        if 'display_mode' in my.kwargs.keys():
            my.disp_mode = str(my.kwargs.get('display_mode'))
        if my.disp_mode == 'Small':
            my.small = True
        if 'user' in my.kwargs.keys():
            my.user = my.kwargs.get('user')
        else:
            my.user = Environment.get_user_name()
        if 'groups_str' in my.kwargs.keys():
            my.groups_str = my.kwargs.get('groups_str')
        if my.groups_str in [None,'']:
            user_group_names = Environment.get_group_names()
            for mg in user_group_names:
                if my.groups_str == '':
                    my.groups_str = mg
                else:
                    my.groups_str = '%s,%s' % (my.groups_str, mg)
        user_is_scheduler = False
        if 'scheduling' in my.groups_str:
            user_is_scheduler = True
        if 'is_master' in my.kwargs.keys():
            my.is_master_str = my.kwargs.get('is_master')
            if my.is_master_str == 'true':
                my.is_master = True
        else:
            order_search = Search("twog/order")
            order_search.add_filter('code', order_code)
            order = order_search.get_sobject()
            order_classification = order.get_value('classification')
            if order_classification in ['master', 'Master']:
                my.is_master = True
                my.is_master_str = 'true'

        open_bottom = False
        if 'open_bottom' in my.kwargs.keys():
            ob_text = my.kwargs.get('open_bottom')
            if ob_text in [True, 'true', 't', '1', 1]:
                open_bottom = True
        my.parent_sk = my.order_sk
        obs = OBScripts(order_sk=my.order_sk, user=my.user, groups_str=my.groups_str, display_mode=my.disp_mode,
                        is_master=my.is_master)

        if 'main_obj' in my.kwargs.keys():
            main_obj = my.kwargs.get('main_obj')
        else:
            main_search = Search("twog/title")
            main_search.add_filter('code', my.code)
            main_obj = main_search.get_sobject()
        my.search_id = main_obj.get_value('id')
        proj_search = Search("twog/proj")
        proj_search.add_filter('title_code', my.code)
        proj_search.add_order_by('order_in_pipe')
        projs = proj_search.get_sobjects()
        table = Table()
        table.add_attr('cellpadding', '0')
        table.add_attr('cellspacing', '0')
        table.add_attr('class', 'TitleRow_%s' % my.code)
        table.add_style('border-collapse', 'separate')
        table.add_style('border-spacing', '25px 0px')
        table.add_style('border-bottom-right-radius', '10px')
        table.add_style('border-bottom-left-radius', '10px')
        table.add_style('border-top-right-radius', '10px')
        table.add_style('border-top-left-radius', '10px')
        table.add_style('color: #00056a;')
        table.add_style('background-color: %s;' % my.off_color)
        table.add_style('width: 100%;')
        table.add_row()
        epis = ''
        full_title_name = main_obj.get_value('title')
        if main_obj.get_value('episode'):
            epis = ' Episode: %s' % main_obj.get_value('episode')
            full_title_name = '%s: %s' % (full_title_name, main_obj.get_value('episode'))
        title_cell = table.add_cell('<b><u>Title: %s%s</u></b>' % (main_obj.get_value('title'), epis))
        title_cell.add_attr('nowrap', 'nowrap')
        title_cell.add_style('cursor: pointer;')
        title_cell.add_behavior(obs.get_panel_change_behavior(my.search_type, my.code, my.sk, my.order_sk, my.title, '',
                                                              'builder/refresh_from_save', '', my.parent_sk,
                                                              '%s: %s' % (main_obj.get_value('title'),
                                                                          main_obj.get_value('episode')),
                                                              user_is_scheduler))
        due_cell = table.add_cell('Due: %s' % fix_date(main_obj.get_value('due_date')).split(' ')[0])
        due_cell.add_attr('nowrap', 'nowrap')
        pipe_disp = main_obj.get_value('pipeline_code')
        if 'XsX' in pipe_disp:
            pipe_disp = 'Not Assigned'
        pipe_cell = table.add_cell('Pipeline: %s' % pipe_disp)
        pipe_cell.add_attr('nowrap', 'nowrap')
        long_cell1 = table.add_cell(' ')
        long_cell1.add_attr('align', 'right')
        long_cell1.add_style('width: 100%')
        if my.small:
            select_check = CustomCheckboxWdg(name='select_%s' % my.code, value_field=my.code, checked='false',
                                             dom_class='ob_selector', parent_table="TitleRow_%s" % my.code,
                                             normal_color=my.off_color, selected_color=my.on_color, code=my.code,
                                             ntype='title', search_key=my.sk,
                                             additional_js=get_selected_color_behavior(my.code,
                                                                                       'TitleRow',
                                                                                       my.on_color,
                                                                                       my.off_color))

            table.add_cell(select_check)
        elif user_is_scheduler:
            xb = table.add_cell(my.x_butt)
            xb.add_attr('align', 'right')
            xb.add_style('cursor: pointer;')
            xb.add_behavior(obs.get_killer_behavior(my.sk, my.parent_sk, 'OrderTable',
                                                    '%s: %s' % (main_obj.get_value('title'),
                                                                main_obj.get_value('episode'))))
        table.add_row()
        long_cell2 = table.add_cell('Code: %s' % my.code)
        long_cell2.add_style('width: 100%')
        status = main_obj.get_value('status')
        status = status.strip(' \t\n\r')
        stat_cell = table.add_cell('Status: %s' % status)
        stat_cell.add_attr('nowrap', 'nowrap')
        if status not in [None,'']:
            stat_cell.add_style('background-color: %s;' % my.stat_colors[status])
        stat_cell.add_style('width: 100%')
        long_cell22 = table.add_cell('Client Status: %s' % main_obj.get_value('client_status'))
        long_cell22.add_attr('nowrap', 'nowrap')
        long_cell22.add_style('width: 100%')
        if my.small:
            title_cell.add_style('font-size: 8px;')
            due_cell.add_style('font-size: 8px;')
            pipe_cell.add_style('font-size: 8px;')
            long_cell1.add_style('font-size: 8px;')
            long_cell2.add_style('font-size: 8px;')
            long_cell22.add_style('font-size: 8px;')
            stat_cell.add_style('font-size: 8px;')
        else:
            table.add_row()
            bottom_buttons = Table()
            bottom_buttons.add_row()
            deliverable_count = DeliverableCountWdg(title_code=my.code, order_sk=my.order_sk,
                                                    full_title=full_title_name)
            d_launcher = bottom_buttons.add_cell(deliverable_count)
            d_launcher.add_attr('class', 'deliverable_count_%s' % my.code)
            d_launcher.add_attr('valign', 'bottom')
            bottom_buttons.add_row()
            prereq_count = PreReqCountWdg(sob_code=my.code, sob_st='twog/title', sob_sk=my.sk,
                                          prereq_st='twog/title_prereq',
                                          sob_name='%s %s' % (main_obj.get_value('title'),
                                                              main_obj.get_value('episode')),
                                          pipeline=main_obj.get_value('pipeline_code'), order_sk=my.order_sk)
            prereq_launcher = bottom_buttons.add_cell(prereq_count)
            prereq_launcher.add_attr('class', 'prereq_count_%s' % my.code)
            prereq_launcher.add_attr('valign', 'bottom')

            if not my.is_master and user_is_scheduler:
                in_bigboard = 'Nope'
                if main_obj.get_value('bigboard') in [True, 'true', 't', 'T', 1]:
                    in_bigboard = 'Yep'
                bbo = BigBoardSelectWdg(search_type='twog/title', code=my.code, in_bigboard=in_bigboard)
                bboc = bottom_buttons.add_cell(bbo)
                bboc.add_attr('align', 'right')

                adder = ButtonSmallNewWdg(title="Add A Project", icon=CustomIconWdg.icons.get('ADD'))
                adder.add_behavior(get_multi_add_projs_behavior(my.order_sk, my.sk))
                add = bottom_buttons.add_cell(adder)
                add.add_attr('align', 'right')

            qc_launcher = QCReportLauncherWdg(code=my.code)
            qcl = bottom_buttons.add_cell(qc_launcher)
            qcl.add_attr('align', 'right')

            if user_is_scheduler:
                stop_button = ButtonSmallNewWdg(title='Deactivate Title - Remove from Operator Views',
                                                icon='/context/icons/custom/stopsmall.png')
                stop_button.add_behavior(get_deactivate_behavior(my.code))
                sb = bottom_buttons.add_cell(stop_button)
                sb.add_attr('id', 'stop_button_%s' % my.code)
                sb.add_attr('align', 'right')

                mastering_icon = '/context/icons/custom/mastering_gray.png'
                mastering_text = "Currently Doesn't Require QC Mastering. Change?"
                if main_obj.get('requires_mastering_qc') not in ['False', 'false', '0', None, False]:
                    mastering_icon = '/context/icons/custom/mastering_lilac.png'
                    mastering_text = "Currently Requires QC Mastering. Change?"
                mastering_button = ButtonSmallNewWdg(title=mastering_text, icon=mastering_icon)
                mastering_button.add_behavior(get_set_mastering(main_obj.get_value('code'), my.order_sk))
                mb = bottom_buttons.add_cell(mastering_button)
                mb.add_attr('id', 'mastering_button_%s' % my.code)
                mb.add_attr('align', 'right')

                face_icon = CustomIconWdg.icons.get('GRAY_BOMB')
                face_text = "All is Ok - Set External Rejection?"
                if main_obj.get('is_external_rejection') == 'true':
                    face_icon = CustomIconWdg.icons.get('RED_BOMB')
                    face_text = "This is an External Rejection!!!"

                panic_button = ButtonSmallNewWdg(title=face_text, icon=face_icon)
                panic_button.add_behavior(get_set_external_rejection(main_obj.get_value('code'), my.order_sk))
                pb = bottom_buttons.add_cell(panic_button)
                pb.add_attr('id', 'panic_button_%s' % my.code)
                pb.add_attr('align', 'right')

                redo_icon = '/context/icons/custom/history_gray.png'
                redo_text = "This is not set as a Redo Title"
                if main_obj.get('redo') not in ['False', 'false', '0', None, False]:
                    redo_icon = '/context/icons/custom/history.png'
                    redo_text = "Currently marked as a Redo Title. Change?"

                redo_button = ButtonSmallNewWdg(title=redo_text, icon=redo_icon)
                redo_button.add_behavior(get_set_redo(main_obj.get_value('code'), my.order_sk))
                rb = bottom_buttons.add_cell(redo_button)
                rb.add_attr('id', 'redo_button_%s' % my.code)
                rb.add_attr('align', 'right')

                if main_obj.get('repurpose'):
                    repurpose_button_text = 'Title is set as a &#34;Repurpose&#34;, do you want to remove this?'
                else:
                    repurpose_button_text = 'Set title as a &#34;Repurpose&#34;?'

                repurpose_button = ButtonSmallNewWdg(title=repurpose_button_text,
                                                     icon=CustomIconWdg.icons.get('REPURPOSE'))
                repurpose_button.add_behavior(set_repurpose(main_obj.get_value('code'), my.order_sk,
                                                            main_obj.get_value('repurpose')))
                repurpose_button_cell = bottom_buttons.add_cell(repurpose_button)
                repurpose_button_cell.add_attr('id', 'repurpose_button_{0}'.format(my.code))
                repurpose_button_cell.add_attr('align', 'right')

                prio_reset = ButtonSmallNewWdg(title="Reset Dept Priorities", icon=CustomIconWdg.icons.get('UNDO'))
                prio_reset.add_behavior(get_reset_dept_prios(main_obj.get_value('code')))
                pr = bottom_buttons.add_cell(prio_reset)
                pr.add_attr('align', 'right')

                sts_launcher = ButtonSmallNewWdg(title="Set Status Triggers", icon=CustomIconWdg.icons.get('LINK'))
                sts_launcher.add_behavior(get_launch_title_proj_sts_behavior(main_obj.get_value('code')))
                stsl = bottom_buttons.add_cell(sts_launcher)
                stsl.add_attr('align', 'right')

            source_inspector = ButtonSmallNewWdg(title="Inspect Sources", icon=CustomIconWdg.icons.get('SOURCE_PORTAL'))
            source_inspector.add_behavior(get_source_inspector_behavior(my.sk,
                                                                        '%s: %s' % (main_obj.get_value('title'),
                                                                                    main_obj.get_value('episode'))))
            si = bottom_buttons.add_cell(source_inspector)
            si.add_attr('align', 'right')

            upload = ButtonSmallNewWdg(title="Upload", icon=CustomIconWdg.icons.get('PUBLISH'))
            upload.add_behavior(get_upload_behavior(my.sk))
            up = bottom_buttons.add_cell(upload)
            up.add_attr('align', 'right')

            note_adder = ButtonSmallNewWdg(title="Add Note", icon=CustomIconWdg.icons.get('NOTE_ADD'))
            note_adder.add_behavior(obs.get_launch_note_behavior(my.sk, main_obj.get_value('title')))
            nadd = bottom_buttons.add_cell(note_adder)
            nadd.add_attr('align', 'right')
            nadd.add_style('cursor: pointer;')

            if user_is_scheduler:
                pipe_button = ButtonSmallNewWdg(title="Assign Pipeline", icon=CustomIconWdg.icons.get('PIPELINE'))
                pipe_button.add_behavior(get_scratch_pipe_behavior('twog/title', my.search_id, my.parent_sid,
                                                                   my.width, my.height,
                                                                   main_obj.get_value('pipeline_code'),
                                                                   main_obj.get_search_key(), 'TitleRow',
                                                                   '%s: %s' % (main_obj.get_value('title'),
                                                                               main_obj.get_value('episode')),
                                                                   my.order_sk))
                bottom_buttons.add_cell(pipe_button)

            if my.is_master and user_is_scheduler:
                templer = ButtonSmallNewWdg(title="Template All", icon=CustomIconWdg.icons.get('TEMPLATE_DOWN'))
                templer.add_behavior(get_template_all_behavior(my.order_sk, my.code, my.is_master_str))
                tem = bottom_buttons.add_cell(templer)
                tem.add_attr('align', 'right')
                tem.add_style('cursor: pointer;')

            long_cell3 = table.add_cell(bottom_buttons)
            long_cell3.add_attr('align', 'right')
            long_cell3.add_attr('valign', 'bottom')
            long_cell3.add_attr('colspan', '3')
            long_cell3.add_style('width: 100%')

            sources = SourcesRow(title_code=my.code, title_sk=my.sk, order_sk=my.order_sk)
            src_row = table.add_row()
            src_row.add_attr('class', 'sources_row')
            src_cell = table.add_cell(sources)
            src_cell.add_attr('colspan', '6')
            src_cell.add_attr('class', 'sources_%s' % my.sk)
            src_cell.add_attr('order_sk', my.order_sk)

        if main_obj.get_value('is_external_rejection') == 'true':
            table.add_row()
            explanation_cell = table.add_cell('<u><b>External Rejection Reason:</b></u> %s' % main_obj.get('external_rejection_reason'))
            explanation_cell.add_attr('colspan', '5')

        bottom = Table()
        bottom.add_attr('width', '100%')
        bottom.add_attr('cellpadding', '0')
        bottom.add_attr('cellspacing', '0')
        for proj in projs:
            proj_sk = proj.get_search_key()
            proj_row = bottom.add_row()
            proj_row.add_attr('class', 'row_%s' % proj_sk)
            proj_obj = ProjRow(sk=proj_sk, parent_sk=my.sk, order_sk=my.order_sk, parent_sid=my.search_id,
                               groups_str=my.groups_str, user=my.user, display_mode=my.disp_mode,
                               is_master=my.is_master_str, main_obj=proj)
            proj_cell = bottom.add_cell(proj_obj)
            proj_cell.add_attr('width', '100%')
            proj_cell.add_attr('sk', proj_sk)
            proj_cell.add_attr('order_sk', my.order_sk)
            proj_cell.add_attr('parent_sk', my.sk)
            proj_cell.add_attr('parent_sid', my.search_id)
            proj_cell.add_attr('call_me', proj.get_value('process'))
            proj_cell.add_attr('my_class', 'ProjRow')
            proj_cell.add_attr('display_mode', my.disp_mode)
            proj_cell.add_attr('class', 'cell_%s' % proj_sk)
        tab2ret = Table()
        tab2ret.add_attr('width', '100%')
        top_row = tab2ret.add_row()
        top_row.add_attr('class', 'top_%s' % my.sk)
        tab2ret.add_cell(table)
        bot_row = tab2ret.add_row()
        bot_row.add_attr('class', 'bot_%s' % my.sk)
        if not open_bottom:
            bot_row.add_style('display: none;')
        else:
            bot_row.add_style('display: table-row;')
        bot = tab2ret.add_cell(bottom)
        bot.add_style('padding-left: 40px;')

        return tab2ret


def get_multi_add_projs_behavior(order_sk, title_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    title_sk = '%s';
    order_sk = '%s';
    kwargs = {'parent_sk': title_sk, 'order_sk': order_sk, 'search_type': 'twog/proj'};
    spt.panel.load_popup('Add Proj(s)', 'order_builder.MultiManualAdderWdg', kwargs);
}
catch(err){
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (title_sk, order_sk)}
    return behavior


def get_deactivate_behavior(title_code):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
    title_code = '%s';
    if(confirm('Are you sure you want to deactivate this title and remove it from operator views?')){
        server = TacticServerStub.get();
        tasks = server.eval("@SOBJECT(sthpw/task['title_code','" + title_code + "'])");
        for(var r = 0; r < tasks.length; r++) {
            server.update(tasks[r].__search_key__, {'active': 0});
        }

        alert('Done Deactivating the title. If you want to activate it again and put it on the Operator Views, put the order in "Bid", then "In Production"');
    }
}
catch(err){
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (title_code)}
    return behavior


def get_set_mastering(title_code, order_sk):
    """
    Toggles the QC Mastering requirement on an order

    :param title_code:
    :param order_sk:
    :return:
    """
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try{
    var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
    server = TacticServerStub.get();
    title_code = '%s';
    order_sk = '%s';
    title_sk = server.build_search_key('twog/title',title_code);
    mastering_button = top_el.getElementById('mastering_button_' + title_code).getElementsByClassName("spt_button_icon")[0];
    inner = mastering_button.innerHTML;
    is_currently_on = false;
    confirm_text = "Are you sure you want to set 'QC Mastering Requirement'?";
    if(inner.indexOf('mastering_lilac.png') != -1) {
        is_currently_on = true;
        confirm_text = "Are you sure you want to remove the 'QC Mastering Requirement'?";
    }
    if(confirm(confirm_text)) {
        if(!is_currently_on) {
            spt.app_busy.show("Setting 'QC Mastering Requirement'...");
            server.update(title_sk, {'requires_mastering_qc': true});
        } else {
            //Then it is an external rejection, but we will set it to NOT be one
            spt.app_busy.show("Removing 'QC Mastering Requirement'...");
            server.update(title_sk, {'requires_mastering_qc': false});
        }

        order_sk = top_el.getAttribute('order_sk');
        display_mode = top_el.getAttribute('display_mode');
        user = top_el.getAttribute('user');
        groups_str = top_el.get('groups_str');
        is_master_str = top_el.getAttribute('is_master_str');
        allowed_titles = top_el.getAttribute('allowed_titles');
        title_el = top_el.getElementsByClassName('cell_' + title_sk)[0];
        found_parent_sk = title_el.get('parent_sk');
        found_parent_sid = title_el.get('parent_sid');
        send_data =  {sk: title_sk, parent_sid: found_parent_sid, parent_sk: found_parent_sk, order_sk: order_sk, display_mode: display_mode, user: user, groups_str: groups_str, allowed_titles: allowed_titles, is_master: is_master_str};
        spt.api.load_panel(title_el, 'order_builder.TitleRow', send_data);
        spt.app_busy.hide();
    }
}
catch(err){
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (title_code, order_sk)}
    return behavior


def set_repurpose(title_code, order_sk, is_repurpose):
    """
    Toggles 'repurpose' on an order (repurposed titles are moved to the top of the priority queue)

    :param title_code: The title code
    :param order_sk: The order's search key
    :return: Javascript behavior
    """
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
    var server = TacticServerStub.get();
    var title_code = '%s';
    var order_sk = '%s';
    var is_currently_repurpose = '%s';
    var title_sk = server.build_search_key('twog/title', title_code);
    var repurpose_button = top_el.getElementById('repurpose_button_' + title_code).getElementsByClassName("spt_button_icon")[0];

    var is_currently_on;
    var confirm_text;

    if(is_currently_repurpose == 'True') {
        is_currently_on = true;
        confirm_text = "Are you sure you want to unset this title as a 'repurpose'?";
    } else {
        is_currently_on = false;
        confirm_text = "Are you sure you want to set this title as a 'repurpose'?";
    }

    if(confirm(confirm_text)) {
        if(!is_currently_on) {
            spt.app_busy.show("Setting 'Repurpose'...");
            server.update(title_sk, {'repurpose': true});
        } else {
            spt.app_busy.show("Removing 'Repurpose'...");
            server.update(title_sk, {'repurpose': false});
        }

        order_sk = top_el.getAttribute('order_sk');
        var display_mode = top_el.getAttribute('display_mode');
        var user = top_el.getAttribute('user');
        var groups_str = top_el.get('groups_str');
        var is_master_str = top_el.getAttribute('is_master_str');
        var allowed_titles = top_el.getAttribute('allowed_titles');
        var title_el = top_el.getElementsByClassName('cell_' + title_sk)[0];
        var found_parent_sk = title_el.get('parent_sk');
        var found_parent_sid = title_el.get('parent_sid');
        var send_data =  {sk: title_sk, parent_sid: found_parent_sid, parent_sk: found_parent_sk, order_sk: order_sk, display_mode: display_mode, user: user, groups_str: groups_str, allowed_titles: allowed_titles, is_master: is_master_str};
        spt.api.load_panel(title_el, 'order_builder.TitleRow', send_data);
        spt.app_busy.hide();
    }
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (title_code, order_sk, is_repurpose)}
    return behavior


def get_set_external_rejection(title_code, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');

    server = TacticServerStub.get();
    title_code = '%s';
    order_sk = '%s';
    title_sk = server.build_search_key('twog/title',title_code);
    panic_button = top_el.getElementById('panic_button_' + title_code).getElementsByClassName("spt_button_icon")[0];
    inner = panic_button.innerHTML;
    is_currently_on = false;
    confirm_text = "Are you sure you want to set this Title as Externally Rejected?";
    if(inner.indexOf('red_bomb.png') != -1) {
        is_currently_on = true;
        confirm_text = "Are you sure you want to make this Title NOT Externally Rejected?";
    }
    if(confirm(confirm_text)) {
        if(!is_currently_on) {
            //Then it is currently not an external rejection, but we will set it to be one
            //We need to open a class for them to enter text. After submit in the next class, it will set the 'is_external_rejection' to true
            //server.update(title_sk, {'is_external_rejection': 'true'});
            spt.panel.load_popup('Please tell us why this was rejected externally.', 'order_builder.order_builder.ExternalRejectionReasonWdg', {'title_sk': title_sk, 'order_sk': order_sk});
        } else {
            //Then it is an external rejection, but we will set it to NOT be one
            spt.app_busy.show("Removing External Rejection desgination...");
            server.update(title_sk, {'is_external_rejection': 'false'});
            alert("You may want to check out the Due and Expected Delivery Dates, as they changed when the title was set to be an external rejection. Also, the Title has been taken off the bigboard.");
            order_sk = top_el.getAttribute('order_sk');
            display_mode = top_el.getAttribute('display_mode');
            user = top_el.getAttribute('user');
            groups_str = top_el.get('groups_str');
            is_master_str = top_el.getAttribute('is_master_str');
            allowed_titles = top_el.getAttribute('allowed_titles');
            title_el = top_el.getElementsByClassName('cell_' + title_sk)[0];
            found_parent_sk = title_el.get('parent_sk');
            found_parent_sid = title_el.get('parent_sid');
            send_data =  {sk: title_sk, parent_sid: found_parent_sid, parent_sk: found_parent_sk, order_sk: order_sk, display_mode: display_mode, user: user, groups_str: groups_str, allowed_titles: allowed_titles, is_master: is_master_str};
            spt.api.load_panel(title_el, 'order_builder.TitleRow', send_data);
            spt.app_busy.hide();
        }
    }
}
catch(err){
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (title_code, order_sk)}
    return behavior


def get_set_redo(title_code, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try{
    var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');

    server = TacticServerStub.get();
    title_code = '%s';
    order_sk = '%s';
    title_sk = server.build_search_key('twog/title',title_code);
    redo_button = top_el.getElementById('redo_button_' + title_code).getElementsByClassName("spt_button_icon")[0];
    inner = redo_button.innerHTML;
    is_currently_on = false;
    confirm_text = "Are you sure you want to mark this Title as a Redo?";
    if(inner.indexOf('history.png') != -1) {
        is_currently_on = true;
        confirm_text = "Are you sure you want to make this Title NOT a Redo?";
    }
    if(confirm(confirm_text)) {
        if(!is_currently_on) {
            //Then it is currently not an external rejection, but we will set it to be one
            //We need to open a class for them to enter text. After submit in the next class, it will set the 'is_external_rejection' to true
            //server.update(title_sk, {'redo': 'true'});
            spt.panel.load_popup('Please enter the requested information.', 'order_builder.order_builder.TitleRedoWdg', {'title_sk': title_sk, 'order_sk': order_sk});
        } else {
            //Then it is an external rejection, but we will set it to NOT be one
            spt.app_busy.show("Removing Redo Designation...");
            server.update(title_sk, {'redo': 'false'});
            order_sk = top_el.getAttribute('order_sk');
            display_mode = top_el.getAttribute('display_mode');
            user = top_el.getAttribute('user');
            groups_str = top_el.get('groups_str');
            is_master_str = top_el.getAttribute('is_master_str');
            allowed_titles = top_el.getAttribute('allowed_titles');
            title_el = top_el.getElementsByClassName('cell_' + title_sk)[0];
            found_parent_sk = title_el.get('parent_sk');
            found_parent_sid = title_el.get('parent_sid');
            send_data =  {sk: title_sk, parent_sid: found_parent_sid, parent_sk: found_parent_sk, order_sk: order_sk, display_mode: display_mode, user: user, groups_str: groups_str, allowed_titles: allowed_titles, is_master: is_master_str};
            spt.api.load_panel(title_el, 'order_builder.TitleRow', send_data);
            spt.app_busy.hide();
        }
    }
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (title_code, order_sk)}
    return behavior


def get_reset_dept_prios(title_code):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try{
    title_code = '%s';
    if(confirm("Are you sure you want to set all Department Priorities under this Title to the Title's Main Priority?")) {
        server = TacticServerStub.get();
        title = server.eval("@SOBJECT(twog/title['code','" + title_code + "'])")[0];
        adps = title.active_dept_priorities;
        depts = ['audio','compression','edeliveries','edit','machine room','media vault','qc','vault'];
        data = {};
        for(var r = 0; r < depts.length; r++){
            if(adps.indexOf(depts[r]) == -1){
                data[depts[r].replace(' ','_') + '_priority'] = title.priority;
            }
        }
        if(data != {}){
            server.update(title.__search_key__, data);
        }
    }
}
catch(err){
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (title_code)}
    return behavior


def get_launch_title_proj_sts_behavior(title_code):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    title_code = '%s';
    kwargs = {'title_code': title_code};
    spt.panel.load_popup('Set Status Triggers On ' + title_code, 'order_builder.order_builder.TitleProjStatusTriggerWdg', kwargs);
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (title_code)}
    return behavior


def get_source_inspector_behavior(search_key, name):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    search_key = '%s';
    name = '%s';
    kwargs = {'search_key': search_key};
    spt.panel.load_popup('Source Inspector for ' + name, 'order_builder.TitleSourceInspectorWdg', kwargs);
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (search_key, name)}
    return behavior


def get_template_all_behavior(order_sk, title_code, is_master_str):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    if(confirm('Are you sure you want to template this Title pipeline now? Are you finished building the pipeline with all its bits and pieces?')) {
        spt.app_busy.show("Allllrighty then. We're Templating it now...");
        var server = TacticServerStub.get();
        var order_sk = '%s';
        var title_code = '%s';
        var is_master_str = '%s';
        var title_sk = server.build_search_key('twog/title', title_code);
        var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
        var allowed_titles = top_el.getAttribute('allowed_titles');
        if(allowed_titles == 'NOTHING|NOTHING') {
            allowed_titles = '';
        }
        projs = server.eval("@SOBJECT(twog/proj['title_code','" + title_code + "'])");
        bad_projs = [];
        bad_wos = [];
        partially_rejected = false;
        for(var r = 0; r < projs.length; r++){
            // DO PROJ STUFF HERE, BUILD LIST OF BAD PROJS (cant template)
            proj_templ_code = projs[r].proj_templ_code;
            proj_others = server.eval("@SOBJECT(twog/proj['templ_me','true']['proj_templ_code','" + proj_templ_code + "']['code','!=','" + projs[r].code + "'])");
            if(proj_others.length == 0){
                // IF PROJ WAS GOOD, DO PROJ'S WO'S
                server.update(projs[r].__search_key__, {'templ_me': 'true', 'specs': projs[r].specs + ' '});
                wos = server.eval("@SOBJECT(twog/work_order['proj_code','" + projs[r].code + "'])")
                for(var v = 0; v < wos.length; v++){
                    work_order_templ_code = wos[v].work_order_templ_code;
                    wo_others = server.eval("@SOBJECT(twog/work_order['templ_me','true']['work_order_templ_code','" + work_order_templ_code + "']['code','!=','" + wos[v].code + "'])");
                    if(wo_others.length == 0){
                        server.update(wos[v].__search_key__, {'templ_me': 'true', 'instructions': wos[v].instructions + ' '});
                        // now do the equipment_used
                        all_wot_eqts = server.eval("@SOBJECT(twog/equipment_used_templ['work_order_templ_code','" + work_order_templ_code + "'])");
                        equip = server.eval("@SOBJECT(twog/equipment_used['work_order_code','" + wos[v].code + "'])")
                        for(var w = 0; w < all_wot_eqts.length; w++){
                            eqt_code = all_wot_eqts[w].code;
                            at_least_one = false;
                            for(var b = 0; b < equip.length; b++){
                                if(equip[b].equipment_used_templ_code == eqt_code){
                                    at_least_one = true;
                                }
                            }
                            if(!at_least_one){
                                server.delete_sobject(all_wot_eqts[w].__search_key__);
                            }
                        }
                        equip = server.eval("@SOBJECT(twog/equipment_used['work_order_code','" + wos[v].code + "'])")
                        for(var t = 0; t < equip.length; t++) {
                            eq_code = equip[t].code;
                            eq_templ_code = equip[t].equipment_used_templ_code;
                            if(eq_templ_code != '' && eq_templ_code != null){
                                eqt_sk = server.build_search_key('twog/equipment_used_templ', eq_templ_code);
                                server.update(eqt_sk, {'work_order_templ_code': work_order_templ_code, 'name': equip[t].name, 'description': equip[t].description, 'client_code': equip[t].client_code, 'equipment_code': equip[t].equipment_code, 'expected_cost': equip[t].expected_cost, 'expected_duration': equip[t].expected_duration, 'expected_quantity': equip[t].expected_quantity, 'units': equip[t].units})
                            } else {
                                templ = server.insert('twog/equipment_used_templ',{'work_order_templ_code': work_order_templ_code, 'name': equip[t].name, 'description': equip[t].description, 'client_code': equip[t].client_code, 'equipment_code': equip[t].equipment_code, 'expected_cost': equip[t].expected_cost, 'expected_duration': equip[t].expected_duration, 'expected_quantity': equip[t].expected_quantity, 'units': equip[t].units})
                                server.update(equip[t].__search_key__, {'equipment_used_templ_code': templ.code})
                            }
                       }
                    } else {
                        bad_wos.push(wos[v].code + ': ' + wos[v].process);
                        partially_rejected = true;
                    }
                }
            } else {
                bad_projs.push(projs[r].code + ': ' + projs[r].process);
                partially_rejected = true;
            }
        }
        spt.app_busy.hide();
        if(partially_rejected) {
            alert('Cannot template the following projects, please notify the Admin' + bad_projs);
            alert('Cannot template the following work_orders, please notify the Admin' + bad_wos);
        } else {
            //reload
            order_sk = top_el.getAttribute('order_sk');
            display_mode = top_el.getAttribute('display_mode');
            user = top_el.getAttribute('user');
            groups_str = top_el.get('groups_str');
            allowed_titles = top_el.getAttribute('allowed_titles');
            parent_el = top_el.getElementsByClassName('cell_' + order_sk)[0];
            found_parent_sk = parent_el.get('parent_sk');
            found_parent_sid = parent_el.get('parent_sid');
            is_master = 'true';
            send_data = {sk: order_sk, user: user, groups_str: groups_str, allowed_titles: allowed_titles, parent_sid: found_parent_sid, parent_sk: found_parent_sk, order_sk: order_sk, display_mode: display_mode, is_master: is_master};
            parent_pyclass = 'OrderTable';
            send_data['allowed_titles'] = allowed_titles;
            spt.api.load_panel(parent_el, 'order_builder.' + parent_pyclass, send_data);
            spt.app_busy.hide();
        }
    }
}
catch(err){
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (order_sk, title_code, is_master_str)}
    return behavior
