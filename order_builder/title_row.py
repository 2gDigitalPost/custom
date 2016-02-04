from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget.button_new_wdg import ButtonSmallNewWdg

from pyasm.common import Environment
from pyasm.search import Search
from pyasm.web import Table
from pyasm.widget import IconWdg, TextWdg

from alternative_elements.customcheckbox import CustomCheckboxWdg
from common_tools.common_functions import fix_date
from order_builder_utils import OBScripts
from qc_reports import QCReportLauncherWdg

from nighttime_hotlist.nighttime_hotlist import BigBoardSelectWdg, BigBoardSingleWOSelectWdg, IndieBigBoardSelectWdg
from work_order_printer import WorkOrderPrintLauncherWdg


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
            'Amberfin01_In_Progress':'#D8F1A8',
            'Amberfin01 In Progress':'#D8F1A8',
            'Amberfin02_In_Progress':'#F3D291',
            'Amberfin02 In Progress':'#F3D291',
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
            main_search.add_filter('code',my.code)
            main_obj = main_search.get_sobject()
        my.search_id = main_obj.get_value('id')
        proj_search = Search("twog/proj")
        proj_search.add_filter('title_code',my.code)
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
        title_cell.add_attr('nowrap','nowrap')
        title_cell.add_style('cursor: pointer;')
        title_cell.add_behavior(obs.get_panel_change_behavior(my.search_type, my.code, my.sk, my.order_sk, my.title, '', 'builder/refresh_from_save', '', my.parent_sk, '%s: %s' % (main_obj.get_value('title'),main_obj.get_value('episode')), user_is_scheduler))
        due_cell = table.add_cell('Due: %s' % fix_date(main_obj.get_value('due_date')).split(' ')[0])
        due_cell.add_attr('nowrap','nowrap')
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
                                             additional_js=obs.get_selected_color_behavior(my.code,
                                                                                           'TitleRow',
                                                                                           my.on_color,
                                                                                           my.off_color))

            table.add_cell(select_check)
        elif user_is_scheduler:
            xb = table.add_cell(my.x_butt)
            xb.add_attr('align','right')
            xb.add_style('cursor: pointer;')
            xb.add_behavior(obs.get_killer_behavior(my.sk, my.parent_sk, 'OrderTable', '%s: %s' % (main_obj.get_value('title'),main_obj.get_value('episode'))))
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
            d_launcher.add_attr('class','deliverable_count_%s' % my.code)
            d_launcher.add_attr('valign','bottom')
            bottom_buttons.add_row()
            prereq_count = PreReqCountWdg(sob_code=my.code, sob_st='twog/title', sob_sk=my.sk,
                                          prereq_st='twog/title_prereq',
                                          sob_name='%s %s' % (main_obj.get_value('title'),
                                                              main_obj.get_value('episode')),
                                          pipeline=main_obj.get_value('pipeline_code'), order_sk=my.order_sk)
            prereq_launcher = bottom_buttons.add_cell(prereq_count)
            prereq_launcher.add_attr('class','prereq_count_%s' % my.code)
            prereq_launcher.add_attr('valign','bottom')

            if not my.is_master and user_is_scheduler:
                in_bigboard = 'Nope'
                if main_obj.get_value('bigboard') in [True, 'true', 't', 'T', 1]:
                    in_bigboard = 'Yep'
                bbo = BigBoardSelectWdg(search_type='twog/title', code=my.code, in_bigboard=in_bigboard)
                bboc = bottom_buttons.add_cell(bbo)
                bboc.add_attr('align', 'right')

                adder = ButtonSmallNewWdg(title="Add A Project", icon=IconWdg.ADD)
                adder.add_behavior(obs.get_multi_add_projs_behavior(my.sk))
                add = bottom_buttons.add_cell(adder)
                add.add_attr('align', 'right')

            qc_launcher = QCReportLauncherWdg(code=my.code)
            qcl = bottom_buttons.add_cell(qc_launcher)
            qcl.add_attr('align', 'right')

            if user_is_scheduler:
                stop_button = ButtonSmallNewWdg(title='Deactivate Title - Remove from Operator Views', icon='/context/icons/custom/stopsmall.png')
                stop_button.add_behavior(obs.get_deactivate_behavior(my.code))
                sb = bottom_buttons.add_cell(stop_button)
                sb.add_attr('id','stop_button_%s' % my.code)
                sb.add_attr('align','right')

                mastering_icon = '/context/icons/custom/mastering_gray.png'
                mastering_text = "Currently Doesn't Require QC Mastering. Change?"
                if main_obj.get('requires_mastering_qc') not in ['False', 'false', '0', None, False]:
                    mastering_icon = '/context/icons/custom/mastering_lilac.png'
                    mastering_text = "Currently Requires QC Mastering. Change?"
                mastering_button = ButtonSmallNewWdg(title=mastering_text, icon=mastering_icon)
                mastering_button.add_behavior(obs.get_set_mastering(main_obj.get_value('code'), my.order_sk))
                mb = bottom_buttons.add_cell(mastering_button)
                mb.add_attr('id', 'mastering_button_%s' % my.code)
                mb.add_attr('align', 'right')

                face_icon = IconWdg.GRAY_BOMB
                face_text = "All is Ok - Set External Rejection?"
                if main_obj.get('is_external_rejection') == 'true':
                    face_icon = IconWdg.RED_BOMB
                    face_text = "This is an External Rejection!!!"

                panic_button = ButtonSmallNewWdg(title=face_text, icon=face_icon)
                panic_button.add_behavior(obs.get_set_external_rejection(main_obj.get_value('code'), my.order_sk))
                pb = bottom_buttons.add_cell(panic_button)
                pb.add_attr('id', 'panic_button_%s' % my.code)
                pb.add_attr('align', 'right')

                redo_icon = '/context/icons/custom/history_gray.png'
                redo_text = "This is not set as a Redo Title"
                if main_obj.get('redo') not in ['False', 'false', '0', None, False]:
                    redo_icon = '/context/icons/custom/history.png'
                    redo_text = "Currently marked as a Redo Title. Change?"

                redo_button = ButtonSmallNewWdg(title=redo_text, icon=redo_icon)
                redo_button.add_behavior(obs.get_set_redo(main_obj.get_value('code'), my.order_sk))
                rb = bottom_buttons.add_cell(redo_button)
                rb.add_attr('id','redo_button_%s' % my.code)
                rb.add_attr('align','right')

                prio_reset = ButtonSmallNewWdg(title="Reset Dept Priorities", icon=IconWdg.UNDO)
                prio_reset.add_behavior(obs.get_reset_dept_prios(main_obj.get_value('code')))
                pr = bottom_buttons.add_cell(prio_reset)
                pr.add_attr('align','right')

                sts_launcher = ButtonSmallNewWdg(title="Set Status Triggers", icon=IconWdg.LINK)
                sts_launcher.add_behavior(obs.get_launch_title_proj_sts_behavior(main_obj.get_value('code')))
                stsl = bottom_buttons.add_cell(sts_launcher)
                stsl.add_attr('align','right')

            source_inspector = ButtonSmallNewWdg(title="Inspect Sources", icon=IconWdg.SOURCE_PORTAL)
            source_inspector.add_behavior(obs.get_source_inspector_behavior(my.sk, '%s: %s' % (main_obj.get_value('title'), main_obj.get_value('episode'))))
            si = bottom_buttons.add_cell(source_inspector)
            si.add_attr('align', 'right')

            upload = ButtonSmallNewWdg(title="Upload", icon=IconWdg.PUBLISH)
            upload.add_behavior(obs.get_upload_behavior(my.sk))
            up = bottom_buttons.add_cell(upload)
            up.add_attr('align', 'right')

            note_adder = ButtonSmallNewWdg(title="Add Note", icon=IconWdg.NOTE_ADD)
            note_adder.add_behavior(obs.get_launch_note_behavior(my.sk, main_obj.get_value('title')))
            nadd = bottom_buttons.add_cell(note_adder)
            nadd.add_attr('align', 'right')
            nadd.add_style('cursor: pointer;')

            if user_is_scheduler:
                pipe_button = ButtonSmallNewWdg(title="Assign Pipeline", icon=IconWdg.PIPELINE)
                pipe_button.add_behavior(obs.get_scratch_pipe_behavior('twog/title', my.search_id, my.parent_sid,
                                                                       my.width, my.height,
                                                                       main_obj.get_value('pipeline_code'),
                                                                       main_obj.get_search_key(),
                                                                       'TitleRow','%s: %s' % (main_obj.get_value('title'),main_obj.get_value('episode'))))
                scratch = bottom_buttons.add_cell(pipe_button)

            if my.is_master and user_is_scheduler:
                templer = ButtonSmallNewWdg(title="Template All", icon=IconWdg.TEMPLATE_DOWN)
                templer.add_behavior(obs.get_template_all_behavior(my.code))
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
        bottom.add_attr('width','100%')
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


class DeliverableCountWdg(BaseRefreshWdg):

    def init(my):
        my.title_code = ''
        my.order_sk = ''

    def get_display(my):
#        deliverable_count_time = time.time()
        my.order_sk = str(my.kwargs.get('order_sk'))
        my.title_code = str(my.kwargs.get('title_code'))
        full_title = str(my.kwargs.get('full_title'))
        delivs_search = Search("twog/work_order_deliverables")
        delivs_search.add_filter('title_code',my.title_code)
        delivs = delivs_search.get_sobjects()
        linked = []
        for d in delivs:
            linked.append(d.get_value('satisfied'))
        satisfied = 0
        unsatisfied = 0
        for link in linked:
            if link == True:
                satisfied = satisfied + 1
            else:
                unsatisfied = unsatisfied + 1
        obs = OBScripts(order_sk=my.order_sk)
        table = Table()
        table.add_row()
        deliverable_launcher = table.add_cell('<u>Delivs: (%s/%s)</u>' % (satisfied, satisfied + unsatisfied))
        deliverable_launcher.add_attr('nowrap','nowrap')
        deliverable_launcher.add_attr('valign','bottom')
        deliverable_launcher.add_style('font-size: 80%s;' % '%')
        deliverable_launcher.add_style('font-color: #2e2e2e;')
        deliverable_launcher.add_style('cursor: pointer;')
        deliverable_launcher.add_behavior(obs.get_launch_deliverables_behavior(my.title_code, full_title))
        #--print "LEAVING DELIVERABLE COUNT WDG"
#        print "DELIVERABLE COUNT TIME = %s" % (time.time() - deliverable_count_time)
        return table



class PreReqCountWdg(BaseRefreshWdg):

    def init(my):
        my.sob_sk = ''
        my.sob_code = ''
        my.sob_st = ''
        my.sob_name = ''
        my.prereq_st = ''
        my.pipeline = ''
        my.order_sk = ''

    def get_display(my):
#        prereq_count_time = time.time()
        my.sob_code = str(my.kwargs.get('sob_code'))
        my.sob_sk = str(my.kwargs.get('sob_sk'))
        my.sob_st = str(my.kwargs.get('sob_st'))
        my.prereq_st = str(my.kwargs.get('prereq_st'))
        my.sob_name = str(my.kwargs.get('sob_name'))
        my.pipeline = str(my.kwargs.get('pipeline'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        code_type = 'title_code'
        if my.sob_st == 'twog/work_order':
            code_type = 'work_order_code'
        all_search = Search(my.prereq_st)
        all_search.add_filter(code_type,my.sob_code)
        all_pres = all_search.get_sobjects()

        satisfied = 0
        unsatisfied = 0
        for ap in all_pres:
            if ap.get_value('satisfied') == True:
                satisfied = satisfied + 1
            else:
                unsatisfied = unsatisfied + 1

        obs = OBScripts(order_sk=my.order_sk)
        table = Table()
        table.add_row()
        fcolor = '#FF0000'
        if satisfied + unsatisfied > 0:
            if (satisfied/(satisfied + unsatisfied)) == 1:
                fcolor = '#458b00'
        prereq_launcher = table.add_cell('<font color="%s"><u>Checklist: (%s/%s)</u></font>' % (fcolor, satisfied, satisfied + unsatisfied))
        prereq_launcher.add_attr('nowrap','nowrap')
        prereq_launcher.add_attr('valign','bottom')
        prereq_launcher.add_style('font-size: 80%s;' % '%')
        prereq_launcher.add_style('font-color: #2e2e2e;')
        prereq_launcher.add_style('cursor: pointer;')
        prereq_launcher.add_behavior(obs.get_launch_prereq_behavior(my.sob_code, my.sob_st, my.sob_sk, my.sob_name, my.pipeline))
#        print "PREREQ COUNT TIME = %s" % (time.time() - prereq_count_time)
        return table


class ProjRow(BaseRefreshWdg):

    def init(my):
        from client.tactic_client_lib import TacticServerStub
        my.server = TacticServerStub.get()
        my.search_type = 'twog/proj'
        my.title = "Project"
        my.sk = ''
        my.code = ''
        my.search_id = ''
        my.parent_sk = ''
        my.parent_sid = ''
        my.order_sk = ''
        my.x_butt = "<img src='/context/icons/common/BtnKill.gif' title='Delete' name='Delete'/>"
        my.scratch_pipe = "<table border=0 cellspacing=0 cellpadding=2 style='font-size: 60%s; border-color: #FFFFFF; border-style: solid; border-width: 1px; cursor: pointer;'><tr><td align='center'><font color='#FFFFFF'>Pipeline</font></td></tr></table>" % '%'
        my.width = '1000px'
        my.height = '300px'
        my.small = False
        my.disp_mode = 'Small'
        my.groups_str = ''
        my.user = ''
        my.is_master = False
        my.is_master_str = 'false'
        my.on_color = '#ff0000'
        my.off_color = '#d9ed8b'
        my.stat_colors = {'Assignment': '#fcaf88', 'Pending': '#d7d7d7', 'In Progress': '#f5f3a4', 'In_Progress': '#f5f3a4', 'In Production': '#f5f3a4', 'In_Production': '#f5f3a4', 'In production': '#f5f3a4', 'In_production': '#f5f3a4', 'Waiting': '#ffd97f', 'Need Assistance': '#fc88fb', 'Need_Assistance': '#fc88fb', 'Review': '#888bfc', 'Approved': '#d4b5e7', 'On Hold': '#e8b2b8', 'On_Hold': '#e8b2b8', 'Client Response': '#ddd5b8', 'Completed': '#b7e0a5', 'Ready': '#b2cee8', 'Internal Rejection': '#ff0000', 'External Rejection': '#ff0000', 'Rejected': '#ff0000', 'Failed QC': '#ff0000', 'Fix Needed': '#c466a1', 'Need Buddy Check': '#e3701a', 'DR In_Progress': '#d6e0a4', 'DR In Progress': '#d6e0a4','Amberfin01_In_Progress':'#D8F1A8', 'Amberfin01 In Progress':'#D8F1A8', 'Amberfin02_In_Progress':'#F3D291',  'Amberfin02 In Progress':'#F3D291','BATON In_Progress': '#c6e0a4', 'BATON In Progress': '#c6e0a4','Export In_Progress': '#796999', 'Export In Progress': '#796999','Buddy Check In_Progress': '#1aade3','Buddy Check In Progress': '#1aade3'}


    def get_parent_context_file_link(my,search_id,process_name,parent_st):
        what_to_ret = ''
        base = '/volumes'
        expr = "@SOBJECT(sthpw/snapshot['search_id','%s']['search_type','%s']['process','%s']['is_current','true'])" % (search_id, parent_st, process_name)
        those_snaps = my.server.eval(expr)
        if len(those_snaps) > 0:
            that_snap = those_snaps[0]
            rel_paths = my.server.get_all_paths_from_snapshot(that_snap.get('code'), mode='relative')
            if len(rel_paths) > 0:
                rel_path = rel_paths[0]
                splits = rel_path.split('/')
                if len(splits) < 2:
                    splits = rel_path.split('\\')
                file_only = splits[len(splits) - 1]
                what_to_ret = '<a href="%s/%s">%s</a>' % (base,rel_path, file_only)
        return what_to_ret

    def get_display(my):
#        proj_row_time = time.time()
        my.sk = str(my.kwargs.get('sk'))
        my.code = my.sk.split('code=')[1]
        my.parent_sk = str(my.kwargs.get('parent_sk'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        order_code = my.order_sk.split('code=')[1]
        my.parent_sid = str(my.kwargs.get('parent_sid'))
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

        if 'display_mode' in my.kwargs.keys():
            my.disp_mode = str(my.kwargs.get('display_mode'))
        if my.disp_mode == 'Small':
            my.small = True
        if 'is_master' in my.kwargs.keys():
            my.is_master_str = my.kwargs.get('is_master')
            if my.is_master_str == 'true':
                my.is_master = True
        else:
            order_search = Search("twog/order")
            order_search.add_filter('code',order_code)
            order = order_search.get_sobject()
            order_classification = order.get_value('classification')
            if order_classification in ['master','Master']:
                my.is_master = True
                my.is_master_str = 'true'
        open_bottom = False
        if 'open_bottom' in my.kwargs.keys():
            ob_text = my.kwargs.get('open_bottom')
            if ob_text in [True,'true','t','1',1]:
                open_bottom = True
        obs = OBScripts(order_sk=my.order_sk, user=my.user, groups_str=my.groups_str, display_mode=my.disp_mode, is_master=my.is_master)
        main_obj = None
        if 'main_obj' in my.kwargs.keys():
            main_obj = my.kwargs.get('main_obj')
        else:
            main_search = Search("twog/proj")
            main_search.add_filter('code',my.code)
            main_obj = main_search.get_sobject()
        pipe_disp = main_obj.get_value('pipeline_code')
        if pipe_disp in [None,'','twog/proj','NOTHINGXsXNOTHING']:
            pipe_disp = "Not Assigned"
            tp_search = Search("twog/title")
            tp_search.add_filter('code',main_obj.get_value('title_code'))
            titl = tp_search.get_sobject()
            title_pipe = titl.get_value('pipeline_code')
            cp_search = Search("twog/client_pipes")
            cp_search.add_filter('process_name',main_obj.get_value('process'))
            cp_search.add_filter('pipeline_code',title_pipe)
            client_pipes = cp_search.get_sobjects()
            if len(client_pipes) > 0:
                client_pipe = client_pipes[0]
                my.server.update(main_obj.get_search_key(), {'pipeline_code': client_pipe.get_value('pipe_to_assign')})
                pipe_disp = client_pipe.get_value('pipe_to_assign')
        my.search_id = main_obj.get_value('id')
        due_date = ''
        task_search = Search("sthpw/task")
        task_search.add_filter('code',main_obj.get_value('task_code'))
        task = task_search.get_sobjects()
        task_sk = ''
        status = ''
        active_bool = False
        active_status = ''
        if len(task) > 0:
            due_date = task[0].get_value('bid_end_date')
            status = task[0].get_value('status')
            task_sk = task[0].get_search_key()
            active_bool = task[0].get_value('active')
            if active_bool in [True,'true','t',1,'1']:
                active_status = '<font color="#0ff000">Active</font>'
            else:
                active_status = '<font color="#ff0000">Inactive</font>'
        wo_search = Search("twog/work_order")
        wo_search.add_filter('proj_code',my.code)
        wo_search.add_order_by('order_in_pipe')
        wos = wo_search.get_sobjects()
        table = Table()
        table.add_attr('class','ProjRow_%s' % my.code)
        table.add_attr('id',main_obj.get_value('code'))
        table.add_attr('cellpadding','0')
        table.add_attr('cellspacing','0')
        table.add_style('border-collapse', 'separate')
        table.add_style('border-spacing', '25px 0px')
        table.add_style('color: #1d216a;')
        table.add_style('background-color: %s;' % my.off_color)
        table.add_style('width: 100%s;' % '%')
        table.add_style('border-bottom-right-radius', '10px')
        table.add_style('border-bottom-left-radius', '10px')
        table.add_style('border-top-right-radius', '10px')
        table.add_style('border-top-left-radius', '10px')
        table.add_row()
        proj_cell = table.add_cell('<b><u>Project: %s</u></b>' % main_obj.get_value('process'))
        proj_cell.add_attr('nowrap','nowrap')
        proj_cell.add_style('cursor: pointer;')
        proj_cell.add_behavior(obs.get_panel_change_behavior(my.search_type, my.code, my.sk, my.order_sk, my.title, main_obj.get_value('proj_templ_code'), 'builder/refresh_from_save',main_obj.get_value('task_code'),my.parent_sk,main_obj.get_value('process'), user_is_scheduler))
        stat_tbl = Table()
        stat_tbl.add_row()
        stat_cell = stat_tbl.add_cell('Status: %s' % status)
        stat_cell.add_attr('nowrap','nowrap')
        if status not in [None,'']:
            stat_cell.add_style('background-color: %s;' % my.stat_colors[status])
        s2 = stat_tbl.add_cell(' ')
        s2.add_attr('width','100%s' % '%')
        table.add_cell(stat_tbl)
        due_cell = table.add_cell('Due: %s' % fix_date(due_date).split(' ')[0])
        due_cell.add_attr('nowrap','nowrap')
        top_buttons = Table()
        top_buttons.add_row()
        if my.small:
            #select_check = CheckboxWdg('select_%s' % (my.code))
            select_check = CustomCheckboxWdg(name='select_%s' % my.code,value_field=my.code,checked='false',dom_class='ob_selector',parent_table="ProjRow_%s" % my.code,normal_color=my.off_color,selected_color=my.on_color,code=my.code,ntype='proj',search_key=my.sk,task_sk=task_sk,additional_js=obs.get_selected_color_behavior(my.code, 'ProjRow', my.on_color, my.off_color))
            #select_check.set_persistence()
            #select_check.set_value(False)
            #select_check.add_attr('code',my.code)
            #select_check.add_attr('ntype','proj')
            #select_check.add_attr('parent_table','ProjRow_%s' % my.code)
            #select_check.add_attr('normal_color',my.off_color)
            #select_check.add_attr('selected_color',my.on_color)
            #select_check.add_attr('search_key',my.sk)
            #select_check.add_attr('task_sk',task_sk)
            #select_check.add_behavior(obs.get_selected_color_behavior(my.code, 'ProjRow', my.on_color, my.off_color))
            cb = top_buttons.add_cell(select_check)
        elif user_is_scheduler:
            xb = top_buttons.add_cell(my.x_butt)
            xb.add_attr('align','right')
            xb.add_style('cursor: pointer;')
            xb.add_behavior(obs.get_killer_behavior(my.sk, my.parent_sk, 'TitleRow', main_obj.get_value('process')))
        long_cell1 = table.add_cell(top_buttons)
        long_cell1.add_attr('align','right')
        long_cell1.add_style('width: 100%s' % '%')
        table.add_row()
        code_cell = table.add_cell('Code: %s' % my.code)
        active_cell = table.add_cell(active_status)
        active_cell.add_attr('align','right')
        active_cell.add_attr('colspan','3')
        active_cell.add_style('width: 100%%;')
        table.add_row()

        title_fullname = main_obj.get_value('title')
        if main_obj.get_value('episode') not in [None,'']:
            title_fullname = '%s: %s' % (title_fullname, main_obj.get_value('episode'))

        pipe_cell = table.add_cell('Pipeline: %s&nbsp;&nbsp;&nbsp;&nbsp;Title: %s' % (pipe_disp, title_fullname))
        pipe_cell.add_attr('nowrap','nowrap')
        long_cell2 = table.add_cell('Priority: ')
        long_cell2.add_attr('align','right')
        long_cell2.add_style('width: 100%s' % '%')
        prio_wdg = TextWdg('barcode_switcher')
        prio_wdg.add_attr('old_prio',main_obj.get_value('priority'))
        prio_wdg.set_value(main_obj.get_value('priority'))
        if user_is_scheduler:
            prio_wdg.add_behavior(obs.get_alter_prio_behavior(main_obj.get_search_key()))
        else:
            prio_wdg.add_attr('disabled','disabled')
            prio_wdg.add_attr('readonly','readonly')
        long_cell21 = table.add_cell(prio_wdg)
        long_cell21.add_attr('align','left')
        long_cell21.add_style('width: 100%s' % '%')
        if my.small:
            proj_cell.add_style('font-size: 8px;')
            stat_cell.add_style('font-size: 8px;')
            due_cell.add_style('font-size: 8px;')
            long_cell1.add_style('font-size: 8px;')
            code_cell.add_style('font-size: 8px;')
            pipe_cell.add_style('font-size: 8px;')
            long_cell2.add_style('font-size: 8px;')
            long_cell21.add_style('font-size: 8px;')
        else:
            bottom_buttons = Table()
            bottom_buttons.add_row()
            lynk = my.get_parent_context_file_link(my.parent_sid, main_obj.get_value('process'), 'twog/title?project=twog')
            bottom_buttons.add_cell(lynk)

            if not my.is_master:
                if main_obj.get_value('creation_type') == 'hackup':# and my.user in ['admin','philip.rowe']:
                    hack_edit = ButtonSmallNewWdg(title="Edit Connections", icon=IconWdg.HACKUP)
                    hack_edit.add_behavior(obs.get_edit_hackup_connections(my.code, main_obj.get_value('process')))
                    he = bottom_buttons.add_cell(hack_edit)
                    he.add_attr('align','right')
                    he.add_attr('valign','bottom')
                if user_is_scheduler:
                    adder = ButtonSmallNewWdg(title="Add A Work Order", icon=IconWdg.ADD)
                    adder.add_behavior(obs.get_multi_add_wos_behavior(my.sk))
                    add = bottom_buttons.add_cell(adder)
                    add.add_attr('align','right')
                    priority = ButtonSmallNewWdg(title="Change Priority", icon=IconWdg.PRIORITY)
                    priority.add_behavior(obs.get_change_priority_behavior(main_obj.get_value('code'), main_obj.get_value('process')))
                    prio = bottom_buttons.add_cell(priority)
                    prio.add_attr('align','right')
                    duedate = ButtonSmallNewWdg(title="Change Due Date", icon=IconWdg.CALENDAR)
                    duedate.add_behavior(obs.get_change_due_date_behavior(main_obj.get_value('code'), main_obj.get_value('process')))
                    due = bottom_buttons.add_cell(duedate)
                    due.add_attr('align','right')

            upload = ButtonSmallNewWdg(title="Upload", icon=IconWdg.PUBLISH)
            upload.add_behavior(obs.get_upload_behavior(my.sk))
            up = bottom_buttons.add_cell(upload)
            up.add_attr('align','right')
            note_adder = ButtonSmallNewWdg(title="Add Note", icon=IconWdg.NOTE_ADD)
            note_adder.add_behavior(obs.get_launch_note_behavior(my.sk, main_obj.get_value('process')))
            nadd = bottom_buttons.add_cell(note_adder)
            nadd.add_attr('align','right')
            nadd.add_style('cursor: pointer;')

            if user_is_scheduler:
                pipe_button = ButtonSmallNewWdg(title="Assign Pipeline", icon=IconWdg.PIPELINE)
                pipe_button.add_behavior(obs.get_scratch_pipe_behavior('twog/proj',my.search_id,my.parent_sid,my.width,my.height, main_obj.get_value('pipeline_code'),main_obj.get_search_key(),'ProjRow',main_obj.get_value('process')))
                scratch = bottom_buttons.add_cell(pipe_button)

            templ_icon = None
            templ_title = ''
            if my.is_master:
                if main_obj.get_value('templ_me') == True:
                    templ_icon = IconWdg.CHECK
                    templ_title = "This is the Templating Project"
                else:
                   templ_icon = IconWdg.TEMPLATE
                   templ_title = "Use This as Template for Parent Pipeline"
                templ_button = ButtonSmallNewWdg(title="Template Me", icon=templ_icon)
                if main_obj.get_value('templ_me') == False:
                    templ_button.add_behavior(obs.get_templ_proj_behavior(main_obj.get_value('templ_me'),main_obj.get_value('proj_templ_code'),main_obj.get_search_key()))
                templ_butt = bottom_buttons.add_cell(templ_button)
                templ_butt.add_attr('class','templ_butt_%s' % my.sk)

            long_cell3 = table.add_cell(bottom_buttons)
            long_cell3.add_attr('align','right')
            long_cell3.add_attr('valign','bottom')
            long_cell3.add_style('width: 100%s' % '%')
        bottom = Table()
        bottom.add_attr('width','100%s' % '%')
        bottom.add_attr('cellpadding','0')
        bottom.add_attr('cellspacing','0')
        for wo in wos:
            wo_sk = wo.get_search_key()
            wo_row = bottom.add_row()
            wo_row.add_attr('class', 'row_%s' % wo_sk)
            wo_obj = WorkOrderRow(sk=wo_sk, parent_sk=my.sk, order_sk=my.order_sk, parent_sid=my.search_id, groups_str=my.groups_str, user=my.user, display_mode=my.disp_mode, is_master=my.is_master_str,main_obj=wo,parent_obj=main_obj)
            wo_cell = bottom.add_cell(wo_obj)
            wo_cell.add_attr('width','100%s' % '%')
            wo_cell.add_attr('sk', wo_sk)
            wo_cell.add_attr('order_sk', my.order_sk)
            wo_cell.add_attr('parent_sk', my.sk)
            wo_cell.add_attr('parent_sid', my.search_id)
            wo_cell.add_attr('display_mode', my.disp_mode)
            wo_cell.add_attr('groups_str', my.groups_str)
            wo_cell.add_attr('user', my.user)
            wo_cell.add_attr('call_me', wo.get_value('process'))
            wo_cell.add_attr('my_class','WorkOrderRow')
            wo_cell.add_attr('class','cell_%s' % wo_sk)
        tab2ret = Table()
        top_row = tab2ret.add_row()
        top_row.add_attr('class','top_%s' % my.sk)
        tab2ret.add_attr('width','100%s' % '%')
        tab2ret.add_cell(table)
        bot_row = tab2ret.add_row()
        bot_row.add_attr('class','bot_%s' % my.sk)
        if not open_bottom:
            bot_row.add_style('display: none;')
        else:
            bot_row.add_style('display: table-row;')
        bot = tab2ret.add_cell(bottom)
        bot.add_style('padding-left: 40px;')
        return tab2ret

class SourcesRow(BaseRefreshWdg):

    def init(my):
        my.server = None
        my.title_sk = ''
        my.title_code = ''
        my.order_sk = ''

    def get_display(my):
#        sources_row_time = time.time()
        my.title_code = str(my.kwargs.get('title_code'))
        my.title_sk = str(my.kwargs.get('title_sk'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        obs = OBScripts(order_sk=my.order_sk)
        origin_search = Search("twog/title_origin")
        origin_search.add_filter('title_code',my.title_code)
        origins = origin_search.get_sobjects()

        groups_str = ''
        user_group_names = Environment.get_group_names()
        for mg in user_group_names:
            if groups_str == '':
                groups_str = mg
            else:
                groups_str = '%s,%s' % (groups_str, mg)
        user_is_scheduler = False
        if 'scheduling' in groups_str:
            user_is_scheduler = True

        table = Table()
        table.add_attr('width','100%s' % '%')
        table.add_attr('bgcolor','#cbe49e')
        table.add_style('border-bottom-right-radius', '10px')
        table.add_style('border-bottom-left-radius', '10px')
        table.add_style('border-top-right-radius', '10px')
        table.add_style('border-top-left-radius', '10px')
        table.add_row()
        source_limit = 7
        count = 0
        if len(origins) > 0:
            table.add_row()
            mr_title = table.add_cell('<b><u><i>Sources</i></u></b>')
            mr_title.add_style('font-size: 90%s;' % '%')
        seen = []
        for origin in origins:
            source_code = origin.get_value('source_code')
            if source_code not in seen:
                seen.append(source_code)
                source_search = Search("twog/source")
                source_search.add_filter('code',source_code)
                source = source_search.get_sobject()
                if count % source_limit == 0:
                    table.add_row()
                celly = None
                if not source.get_value('high_security'):
                    celly = table.add_cell('<font color="#3e3e3e"><b><u>(%s): %s</u></b></font>' % (source.get_value('barcode'),source.get_value('title')))
                else:
                    celly = table.add_cell('<font color="#ff0000"><b><u>!!!(%s): %s!!!</u></b></font>' % (source.get_value('barcode'),source.get_value('title')))
                celly.add_attr('nowrap','nowrap')
                celly.add_style('cursor: pointer;')
                celly.add_style('font-size: 80%s;' % '%')
                celly.add_behavior(obs.get_launch_source_behavior(my.title_code,my.title_sk,source.get_value('code'),source.get_search_key()))
                spacer = table.add_cell(' &nbsp;&nbsp; ')
                count = count + 1
            else:
                from client.tactic_client_lib import TacticServerStub
                my.server = TacticServerStub.get()
                my.server.retire_sobject(origin.get_search_key())
        table2 = Table()
        if user_is_scheduler:
            table2.add_row()
            barcode_text_wdg = TextWdg('barcode_insert')
            barcode_text_wdg.add_behavior(obs.get_barcode_insert_behavior(my.title_code,my.title_sk))
            bct = table2.add_cell(barcode_text_wdg)
            bct.add_attr('align','right')
            bct.add_attr('width','100%s' % '%')
        two_gether = Table()
        two_gether.add_row()
        srcs = two_gether.add_cell(table)
        srcs.add_attr('width','100%s' % '%')
        srcs.add_attr('valign','top')
        if user_is_scheduler:
            bcentry = two_gether.add_cell(table2)
            bcentry.add_attr('valign','top')

#        print "SOURCES ROW TIME = %s" % (time.time() - sources_row_time)
        return two_gether

class WorkOrderRow(BaseRefreshWdg):

    def init(my):
        from client.tactic_client_lib import TacticServerStub
        my.server = TacticServerStub.get()
        my.search_type = 'twog/work_order'
        my.title = "Work Order"
        my.sk = ''
        my.search_id = ''
        my.code = ''
        my.user = ''
        my.groups_str = ''
        my.parent_sk = ''
        my.parent_sid = ''
        my.order_sk = ''
        my.x_butt = "<img src='/context/icons/common/BtnKill.gif' title='Delete' name='Delete'/>"
        my.add_eu = "<table border=0 cellspacing=0 cellpadding=2 style='font-size: 60%s; border-color: #FFFFFF; border-style: solid; border-width: 1px; cursor: pointer;'><tr><td align='center'><font color='#FFFFFF'>Add Equipment</font></td></tr></table>" % '%'
        my.width = '1000px'
        my.height = '300px'
        my.disp_mode = 'Small'
        my.small = False
        my.is_master = False
        my.is_master_str = 'false'
        my.on_color = '#ff0000'
        my.off_color = '#c6eda0'
        my.stat_colors = {'Assignment': '#fcaf88', 'Pending': '#d7d7d7', 'In Progress': '#f5f3a4', 'In_Progress': '#f5f3a4', 'In Production': '#f5f3a4', 'In_Production': '#f5f3a4', 'In production': '#f5f3a4', 'In_production': '#f5f3a4', 'Waiting': '#ffd97f', 'Need Assistance': '#fc88fb', 'Need_Assistance': '#fc88fb', 'Review': '#888bfc', 'Approved': '#d4b5e7', 'On Hold': '#e8b2b8', 'On_Hold': '#e8b2b8', 'Client Response': '#ddd5b8', 'Completed': '#b7e0a5', 'Ready': '#b2cee8', 'Internal Rejection': '#ff0000', 'External Rejection': '#ff0000', 'Rejected': '#ff0000', 'Failed QC': '#ff0000', 'Fix Needed': '#c466a1', 'Need Buddy Check': '#e3701a', 'DR In_Progress': '#d6e0a4', 'DR In Progress': '#d6e0a4','Amberfin01_In_Progress':'#D8F1A8', 'Amberfin01 In Progress':'#D8F1A8', 'Amberfin02_In_Progress':'#F3D291',  'Amberfin02 In Progress':'#F3D291','BATON In_Progress': '#c6e0a4', 'BATON In Progress': '#c6e0a4','Export In_Progress': '#796999', 'Export In Progress': '#796999','Buddy Check In_Progress': '#1aade3','Buddy Check In Progress': '#1aade3'}

    def get_parent_context_file_link(my,search_id,process_name,parent_st):
        what_to_ret = ''
        base = '/volumes'
        expr = "@SOBJECT(sthpw/snapshot['search_id','%s']['search_type','%s']['process','%s']['is_current','true'])" % (search_id, parent_st, process_name)
        those_snaps = my.server.eval(expr)
        if len(those_snaps) > 0:
            that_snap = those_snaps[0]
            rel_paths = my.server.get_all_paths_from_snapshot(that_snap.get('code'), mode='relative')
            if len(rel_paths) > 0:
                rel_path = rel_paths[0]
                splits = rel_path.split('/')
                if len(splits) < 2:
                    splits = rel_path.split('\\')
                file_only = splits[len(splits) - 1]
                what_to_ret = '<a href="%s/%s">%s</a>' % (base,rel_path, file_only)
        return what_to_ret

    def get_display(my):
#        wo_row_time = time.time()
        my.sk = str(my.kwargs.get('sk'))
        my.code = my.sk.split('code=')[1]
        my.parent_sk = str(my.kwargs.get('parent_sk'))
        my.parent_sid = str(my.kwargs.get('parent_sid'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        order_code = my.order_sk.split('code=')[1]
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

        if 'display_mode' in my.kwargs.keys():
            my.disp_mode = str(my.kwargs.get('display_mode'))
        if my.disp_mode == 'Small':
            my.small = True
        if 'is_master' in my.kwargs.keys():
            my.is_master_str = my.kwargs.get('is_master')
            if my.is_master_str in [True,'true','t',1]:
                my.is_master = True
                my.is_master_str = 'true'
        else:
            order_search = Search("twog/order")
            order_search.add_filter('code',order_code)
            order = order_search.get_sobject()
            order_classification = order.get_value('classification')
            if order_classification in ['master','Master']:
                my.is_master = True
                my.is_master_str = 'false'
        open_bottom = False
        if 'open_bottom' in my.kwargs.keys():
            ob_text = my.kwargs.get('open_bottom')
            if ob_text in [True,'true','t','1',1]:
                open_bottom = True

        obs = OBScripts(order_sk=my.order_sk, user=my.user, groups_str=my.groups_str, is_master=my.is_master)
        main_obj = None
        if 'main_obj' in my.kwargs.keys():
            main_obj = my.kwargs.get('main_obj')
        else:
            main_search = Search("twog/work_order")
            main_search.add_filter('code',my.code)
            main_obj = main_search.get_sobject()
        parent_obj = None
        if 'parent_obj' in my.kwargs.keys():
            parent_obj = my.kwargs.get('parent_obj')
        else:
            parent_search = Search("twog/proj")
            parent_search.add_filter('code',main_obj.get_value('proj_code'))
            parent_obj = parent_search.get_sobject()

#        eq_search_time = time.time()
        eu_search = Search("twog/equipment_used")
        eu_search.add_filter('work_order_code',my.code)
        eus = eu_search.get_sobjects()
#        print "EQ SEARCH TIME = %s" % (time.time() - eq_search_time)

#        task_search_time = time.time()
        task_search = Search("sthpw/task")
        task_search.add_filter('code',main_obj.get_value('task_code'))
        task = task_search.get_sobjects()
#        print "TASK SEARCH TIME = %s" % (time.time() - task_search_time)

        my.search_id = main_obj.get_value('id')
        due_date = ''
        start_date = ''
        end_date = ''
        status = ''
        assigned = ''
        priority = ''
        task_sk = ''
        active_bool = False
        active_status = ''
        task_exists = False
        if len(task) > 0:
            task = task[0]
            task_exists = True
            due_date = task.get_value('bid_end_date')
            start_date = task.get_value('actual_start_date')
            end_date = task.get_value('actual_end_date')
            status = task.get_value('status')
            assigned = task.get_value('assigned')
            priority = task.get_value('priority')
            task_sk = task.get_search_key()
            active_bool = task.get_value('active')
            if active_bool in [True,'true','t',1,'1']:
                active_status = '<font color="#0ff000">Active</font>'
            else:
                active_status = '<font color="#ff0000">Inactive</font>'
        bgcol = my.off_color
        if main_obj.get_value('work_group') in [None,''] or main_obj.get_value('estimated_work_hours') in [None,'']:
            bgcol = '#FFFFFF'
        if assigned not in [None,'']:
            assigned_s = Search('sthpw/login')
            assigned_s.add_filter('location','internal')
            assigned_s.add_filter('login',assigned)
            assigned_o = assigned_s.get_sobject()
            assigned = ''
            if assigned_o:
                assigned = '%s %s' % (assigned_o.get_value('first_name'), assigned_o.get_value('last_name'))

        table = Table()
        table.add_attr('id', main_obj.get_value('code'))
        table.add_attr('cellpadding','0')
        table.add_attr('cellspacing','0')
        table.add_attr('class','WorkOrderRow_%s' % my.code)
        table.add_attr('width','100%s' % '%')
        table.add_style('border-collapse', 'separate')
        table.add_style('border-spacing', '25px 0px')
        table.add_style('color: #373a6a;')
        table.add_style('background-color: %s;' % bgcol)
        table.add_style('width: 100%s;' % '%')
        table.add_style('border-bottom-right-radius', '10px')
        table.add_style('border-bottom-left-radius', '10px')
        table.add_style('border-top-right-radius', '10px')
        table.add_style('border-top-left-radius', '10px')
        row1 = table.add_row()
        row1.add_attr('width','100%s' % '%')
        row1.add_style('width: 100%s;' % '%')
        wo_cell = table.add_cell('<b><u>Work Order: %s</u></b>' % main_obj.get_value('process'))
        wo_cell.add_attr('nowrap','nowrap')
        wo_cell.add_style('cursor: pointer;')
        wo_cell.add_behavior(obs.get_panel_change_behavior(my.search_type, my.code, my.sk, my.order_sk, my.title, main_obj.get_value('work_order_templ_code'), 'builder/refresh_from_save',main_obj.get_value('task_code'),my.parent_sk,main_obj.get_value('process'), user_is_scheduler))
        stat_cell = table.add_cell('Status: %s' % status)
        stat_cell.add_attr('nowrap','nowrap')
        if status not in [None,'']:
            stat_cell.add_style('background-color: %s;' % my.stat_colors[status])
        priority_cell = table.add_cell('Priority: %s' % priority)
        priority_cell.add_attr('nowrap','nowrap')
        assigned_cell = table.add_cell('Assigned to: %s' % assigned)
        assigned_cell.add_attr('nowrap','nowrap')
        due_cell = table.add_cell('Due: %s' % fix_date(due_date))
        due_cell.add_attr('nowrap','nowrap')
        top_buttons = Table()
        top_buttons.add_row()
        if my.small:
            #select_check = CheckboxWdg('select_%s' % (my.code))
            select_check = CustomCheckboxWdg(name='select_%s' % my.code,value_field=my.code,checked='false',dom_class='ob_selector',parent_table="WorkOrderRow_%s" % my.code,process=main_obj.get_value('process'),work_group=main_obj.get_value('work_group'),proj_code=main_obj.get_value('proj_code'),title_code=main_obj.get_value('title_code'),order_code=order_code,task_code=main_obj.get_value('task_code'),normal_color=my.off_color,selected_color=my.on_color,code=my.code,ntype='work_order',search_key=my.sk,task_sk=task_sk,additional_js=obs.get_selected_color_behavior(my.code, 'WorkOrderRow', my.on_color, my.off_color))
            #select_check.set_persistence()
            #select_check.set_value(False)
            #select_check.add_attr('code',my.code)
            #select_check.add_attr('ntype','work_order')
            #select_check.add_attr('work_group',main_obj.get_value('work_group'))
            #select_check.add_attr('process',main_obj.get_value('process'))
            #select_check.add_attr('proj_code',parent_obj.get_value('code'))
            #select_check.add_attr('title_code',parent_obj.get_value('title_code'))
            #select_check.add_attr('order_code',order_code)
            #select_check.add_attr('task_code',main_obj.get_value('task_code'))
            #select_check.add_attr('parent_table','WorkOrderRow_%s' % my.code)
            #select_check.add_attr('normal_color',my.off_color)
            #select_check.add_attr('selected_color',my.on_color)
            #select_check.add_attr('search_key',my.sk)
            #select_check.add_attr('task_sk',task_sk)
            #select_check.add_behavior(obs.get_selected_color_behavior(my.code, 'WorkOrderRow', my.on_color, my.off_color))
            cb = top_buttons.add_cell(select_check)
        elif user_is_scheduler:
            xb = top_buttons.add_cell(my.x_butt)
            xb.add_attr('align','right')
            xb.add_style('cursor: pointer;')
            xb.add_behavior(obs.get_killer_behavior(my.sk, my.parent_sk, 'ProjRow', main_obj.get_value('process')))
        long_cell1 = table.add_cell(top_buttons)
        long_cell1.add_attr('align','right')
        long_cell1.add_attr('colspan','1')
        long_cell1.add_style('width: 100%s' % '%')
        table.add_row()
        ccel = table.add_cell('Code: %s' % my.code)
        ccel.add_attr('nowrap','nowrap')
        start_cell = table.add_cell('Start: %s' % fix_date(start_date))
        start_cell.add_attr('nowrap','nowrap')
        end_cell = table.add_cell('End: %s' % fix_date(end_date))
        end_cell.add_attr('nowrap','nowrap')
        active_cell = table.add_cell(active_status)
        active_cell.add_attr('align','right')
        active_cell.add_attr('colspan','3')
        active_cell.add_style("width: 100%%;")
        if my.small:
            wo_cell.add_style('font-size: 8px;')
            stat_cell.add_style('font-size: 8px;')
            priority_cell.add_style('font-size: 8px;')
            assigned_cell.add_style('font-size: 8px;')
            due_cell.add_style('font-size: 8px;')
            long_cell1.add_style('font-size: 8px;')
            ccel.add_style('font-size: 8px;')
            start_cell.add_style('font-size: 8px;')
            end_cell.add_style('font-size: 8px;')
            active_cell.add_style('font-size: 8px;')
        else:
            table.add_row()
            bottom_buttons = Table()
            bottom_buttons.add_row()
            bbl = Table()
            bbl.add_row()
            ins = bbl.add_cell(main_obj.get_value('instructions').replace('<','&lt;').replace('>','&gt;'))
            ins.add_attr('align','left')
            ins.add_attr('colspan','5')
            ins.add_attr('width','100%s' % '%')
            empt = bbl.add_cell(' ')
            empt.add_attr('width', '100%s' % '%')
            bbr = Table()
            bbr.add_row()
            prereq_count = PreReqCountWdg(sob_code=my.code, sob_st='twog/work_order', sob_sk=my.sk, prereq_st='twog/work_order_prereq', sob_name=main_obj.get_value('process'), pipeline='nothing', order_sk=my.order_sk)
            prereq_launcher = bbr.add_cell(prereq_count)
            prereq_launcher.add_attr('class','prereq_count_%s' % my.code)
            prereq_launcher.add_attr('valign','bottom')
            prereq_launcher.add_attr('colspan','2')

            if main_obj.get_value('creation_type') == 'hackup' and user_is_scheduler:# and my.user in ['admin','philip.rowe']:
                hack_edit = ButtonSmallNewWdg(title="Edit Connections", icon=IconWdg.HACKUP)
                hack_edit.add_behavior(obs.get_edit_hackup_connections(my.code, main_obj.get_value('process')))
                he = bbr.add_cell(hack_edit)
                he.add_attr('align','right')
                he.add_attr('valign','bottom')
            else:
                blah = bbr.add_cell('')

            if user_is_scheduler:
                error_edit = ButtonSmallNewWdg(title="Report Error", icon=IconWdg.REPORT_ERROR)
                error_edit.add_behavior(obs.get_add_wo_error_behavior(my.code))
                uno = bbr.add_cell('&nbsp;')
                er = bbr.add_cell(error_edit)
                er.add_attr('align','right')
                er.add_attr('valign','bottom')
                er.add_attr('colspan','3')
                er.add_attr('width','100%s' % '%')


            bbr.add_row()

            if not my.is_master and user_is_scheduler and task_exists:
#                indie_button_time = time.time()
                indie_button = IndieBigBoardSelectWdg(search_key=task.get_search_key(),indie_bigboard=task.get_value('indie_bigboard'),title_code=parent_obj.get_value('title_code'),lookup_code=my.code)
                indie = bbr.add_cell(indie_button)
                indie.add_attr('align','right')
                indie.add_attr('valign','bottom')
#                print "INDIE BUTTON TIME = %s" % (time.time() - indie_button_time)

#                bb_time = time.time()
                big_button = BigBoardSingleWOSelectWdg(search_key=task.get_search_key(),bigboard=task.get_value('bigboard'),title_code=parent_obj.get_value('title_code'),lookup_code=my.code)
                bbw = bbr.add_cell(big_button)
                bbw.add_attr('align','right')
                bbw.add_attr('valign','bottom')
#                print "BB TIME = %s" % (time.time() - bb_time)

            print_button = WorkOrderPrintLauncherWdg(work_order_code=my.code)
            prnt = bbr.add_cell(print_button)
            prnt.add_attr('align','right')
            prnt.add_attr('valign','bottom')

            upload = ButtonSmallNewWdg(title="Upload", icon=IconWdg.PUBLISH)
            upload.add_behavior(obs.get_upload_behavior(my.sk))
            up = bbr.add_cell(upload)
            up.add_attr('align','right')
            up.add_attr('valign','bottom')

            note_adder = ButtonSmallNewWdg(title="Add Note", icon=IconWdg.NOTE_ADD)
            note_adder.add_behavior(obs.get_launch_note_behavior(my.parent_sk, parent_obj.get_value('process')))
            nadd = bbr.add_cell(note_adder)
            nadd.add_attr('align','right')
            nadd.add_attr('valign','bottom')
            nadd.add_style('cursor: pointer;')

            if user_is_scheduler:
                add_eq_used_butt = ButtonSmallNewWdg(title="Add Equipment", icon=IconWdg.EQUIPMENT_ADD)
                add_eq_used_butt.add_behavior(obs.get_eu_add_behavior(main_obj.get_value('process'),main_obj.get_search_key(), main_obj.get_value('code')))
                eu_adder = bbr.add_cell(add_eq_used_butt)
                eu_adder.add_attr('width','100%s' % '%')
                eu_adder.add_attr('align', 'right')
                eu_adder.add_attr('valign', 'bottom')
                eu_adder.add_style('cursor: pointer;')

                source_portal = ButtonSmallNewWdg(title="Passed in Result(s) or Source(s)", icon=IconWdg.SOURCE_PORTAL)
                source_portal.add_behavior(obs.get_launch_source_portal_behavior(main_obj.get_value('process'), main_obj.get_search_key(), main_obj.get_value('code'), parent_obj.get_value('pipeline_code'), my.is_master_str))
                sp = bbr.add_cell(source_portal)
                sp.add_attr('align','right')
                sp.add_attr('valign','bottom')

                file_add = ButtonSmallNewWdg(title="Intermediate File(s) or Permanent Element(s)", icon=IconWdg.FILE_ADD)
                file_add.add_behavior(obs.get_launch_out_files_behavior(main_obj.get_value('process'), main_obj.get_search_key(), main_obj.get_value('code')))
                fa = bbr.add_cell(file_add)
                fa.add_attr('align','right')
                fa.add_attr('valign','bottom')

            templ_icon = None
            templ_title = ''
            if my.is_master:
                if main_obj.get_value('templ_me') == True:
                    templ_icon = IconWdg.CHECK
                    templ_title = "This is the Templating Work Order"
                else:
                    templ_icon = IconWdg.TEMPLATE
                    templ_title = "Use This as Template for Parent Pipeline"
                templ_button = ButtonSmallNewWdg(title=templ_title, icon=templ_icon)
                if main_obj.get_value('templ_me') == False:
                    templ_button.add_behavior(obs.get_templ_wo_behavior(main_obj.get_value('templ_me'),main_obj.get_value('work_order_templ_code'),main_obj.get_search_key()))
                templ_butt = bbr.add_cell(templ_button)
                templ_butt.add_attr('class','templ_butt_%s' % my.sk)
                templ_butt.add_attr('width','100%s' % '%')
                templ_butt.add_attr('align', 'right')
                templ_butt.add_attr('valign', 'bottom')
            bl = bottom_buttons.add_cell(bbl)
            bl.add_attr('valign','bottom')
            bl.add_attr('align','left')
            bl.add_attr('width','100%s' % '%')
            br = bottom_buttons.add_cell(bbr)
            br.add_attr('valign','bottom')

            bbs = table.add_cell(bottom_buttons)
            bbs.add_attr('width','100%s' % '%')
            bbs.add_attr('align','left')
            bbs.add_attr('valign','bottom')

            if user_is_scheduler:
                src_row = table.add_row()
                src_row.add_attr('class','wo_sources_row')
                wos = WorkOrderSourcesRow(work_order_code=my.code, work_order_sk=my.sk, order_sk=my.order_sk)
                wos_cell = table.add_cell(wos)
                wos_cell.add_attr('colspan','4')
                wos_cell.add_attr('class','wo_sources_%s' % my.sk)

        bottom = Table()
        bottom.add_attr('width','100%s' % '%')
        bottom.add_attr('cellpadding','0')
        bottom.add_attr('cellspacing','0')
        for eu in eus:
            eu_sk = eu.get_search_key()
            if eu.get_value('client_code') in [None,'']:
                my.server.update(eu_sk, {'client_code': main_obj.get_value('client_code')}, triggers=False)
            eu_row = bottom.add_row()
            eu_row.add_attr('class', 'EquipmentUsedRowRow row_%s' % eu_sk)
            eu_obj = EquipmentUsedRow(sk=eu_sk, parent_sk=my.sk, order_sk=my.order_sk, parent_sid=my.search_id, groups_str=my.groups_str, user=my.user, display_mode=my.disp_mode, is_master=my.is_master_str,main_obj=eu)
            eu_cell = bottom.add_cell(eu_obj)
            eu_cell.add_attr('width','100%s' % '%')
            eu_cell.add_attr('sk', eu_sk)
            eu_cell.add_attr('order_sk', my.order_sk)
            eu_cell.add_attr('parent_sk', my.sk )
            eu_cell.add_attr('parent_sid', my.search_id )
            eu_cell.add_attr('call_me', eu.get_value('name'))
            eu_cell.add_attr('wot_code', main_obj.get_value('work_order_templ_code'))
            eu_cell.add_attr('my_class','EquipmentUsedRow')
            eu_cell.add_attr('class','cell_%s' % eu_sk)
        tab2ret = Table()
        tab2ret.add_attr('width','100%s' % '%')
        top_row = tab2ret.add_row()
        top_row.add_attr('class','top_%s' % my.sk)
        tab2ret.add_cell(table)
        bot_row = tab2ret.add_row()
        if not open_bottom:
            bot_row.add_style('display: none;')
        else:
            bot_row.add_style('display: table-row;')
        bot_row.add_attr('class','bot_%s' % my.sk)
        bot = tab2ret.add_cell(bottom)
        bot.add_style('padding-left: 40px;')
#        print "WO ROW TIME = %s" % (time.time() - wo_row_time)
        return tab2ret


class WorkOrderSourcesRow(BaseRefreshWdg):

    def init(my):
        from client.tactic_client_lib import TacticServerStub
        my.server = TacticServerStub.get()
        my.work_order_sk = ''
        my.work_order_code = ''
        my.order_sk = ''

    def get_snapshot_file_link(my,snapshot_code):
        what_to_ret = ''
        base = '/volumes'
        rel_paths = my.server.get_all_paths_from_snapshot(snapshot_code, mode='relative')
        ctx_expr = "@GET(sthpw/snapshot['code','%s'].context)" % snapshot_code
        ctx = my.server.eval(ctx_expr)[0];
        if len(rel_paths) > 0:
            rel_path = rel_paths[0]
            splits = rel_path.split('/')
            if len(splits) < 2:
                splits = rel_path.split('\\')
            file_only = splits[len(splits) - 1]
            what_to_ret = '<a href="%s/%s">%s: %s</a>' % (base,rel_path, ctx, file_only)
        return what_to_ret

    def get_display(my):
#        wo_sources_time = time.time()
        my.work_order_code = str(my.kwargs.get('work_order_code'))
        my.work_order_sk = str(my.kwargs.get('work_order_sk'))
        my.work_order_sk = my.server.build_search_key('twog/work_order', my.work_order_code)
        my.order_sk = str(my.kwargs.get('order_sk'))
        obs = OBScripts(order_sk=my.order_sk)
        wsource_search = Search("twog/work_order_sources")
        wsource_search.add_filter('work_order_code',my.work_order_code)
        wo_sources = wsource_search.get_sobjects()
        table = Table()
        table.add_attr('width','100%s' % '%')
        table.add_attr('bgcolor','#c6c6e4')
        table.add_style('border-bottom-left-radius', '10px')
        table.add_style('border-top-left-radius', '10px')
        table.add_row()
        source_limit = 4
        pass_search = Search("twog/work_order_passin")
        pass_search.add_filter('work_order_code',my.work_order_code)
        passins = pass_search.get_sobjects()
        sources = []
        inter_passins = []
        for passin in passins:
            if passin.get_value('deliverable_source_code') not in [None,'']:
                source_search = Search("twog/source")
                source_search.add_filter('code',passin.get_value('deliverable_source_code'))
                that_src = source_search.get_sobject()
                sources.append(that_src)
            elif passin.get_value('intermediate_file_code') not in [None,'']:
                inter_search = Search("twog/intermediate_file")
                inter_search.add_filter('code',passin.get_value('intermediate_file_code'))
                inter_file = inter_search.get_sobject()
                inter_passins.append(inter_file)

        seen = []
        for wo_source in wo_sources:
            source_code = wo_source.get_value('source_code')
            if source_code not in seen:
                seen.append(source_code)
                source_search = Search("twog/source")
                source_search.add_filter("code",source_code)
                source = source_search.get_sobject()
                sources.append(source)

        if len(sources) > 0:
            table.add_row()
            mr_title = table.add_cell('<b><u><i>Sources</i></u></b>')
            mr_title.add_style('font-size: 90%s;' % '%')

        count = 0
        for source in sources:
            inner_table = Table()
            inner_table.add_row()
            celly = None
            if not source.get_value('high_security'):
                celly = inner_table.add_cell('<font color="#3e3e3e"><b><u>(%s): %s</u></b></font>' % (source.get_value('barcode'),source.get_value('title')))
            else:
                celly = inner_table.add_cell('<font color="#ff0000"><b><u>!!!(%s): %s!!!</u></b></font>' % (source.get_value('barcode'),source.get_value('title')))
            celly.add_attr('nowrap','nowrap')
            celly.add_style('cursor: pointer;')
            celly.add_style('font-size: 80%s;' % '%')
            celly.add_behavior(obs.get_launch_wo_source_behavior(my.work_order_code, my.work_order_sk, source.get_value('code')))
            if count % source_limit == 0:
                table.add_row()
            inner_cell = table.add_cell(inner_table)
            inner_cell.add_attr('valign','top')
            spacer = table.add_cell(' &nbsp;&nbsp; ')
            count = count + 1

        inter_pass_table = Table()
        inter_pass_table.add_attr('width','100%s' % '%')
        inter_pass_table.add_attr('bgcolor','#c6c6e4')
        if len(inter_passins) > 0:
            inter_pass_table.add_row()
            mr_title = inter_pass_table.add_cell('<b><u><i>Intermediate Sources</i></u></b>')
            mr_title.add_attr('nowrap','nowrap')
            mr_title.add_style('font-size: 90%s;' % '%')
            if len(sources) < 1:
                inter_pass_table.add_style('border-top-left-radius', '10px')
                inter_pass_table.add_style('border-bottom-left-radius', '10px')
        count = 0
        for intermediate in inter_passins:
            inner_table = Table()
            inner_table.add_row()
            celly = inner_table.add_cell('<font color="#3e3e3e"><b><u>%s</u></b></font>' % (intermediate.get_value('title')))
            celly.add_attr('nowrap','nowrap')
            celly.add_style('cursor: pointer;')
            celly.add_style('font-size: 80%s;' % '%')
            celly.add_behavior(obs.get_launch_wo_inter_behavior(my.work_order_code,my.work_order_sk,intermediate.get_value('code')))
            if count % source_limit == 0:
                inter_pass_table.add_row()
            inner_cell = inter_pass_table.add_cell(inner_table)
            inner_cell.add_attr('valign','top')
            spacer = inter_pass_table.add_cell(' &nbsp;&nbsp; ')
            count = count + 1


        # Need to enter Interims and Delivs Here
        inter_table = Table()
        inter_table.add_attr('width','100%s' % '%')
        inter_table.add_attr('bgcolor','#acbe49e')
        wointer_search = Search("twog/work_order_intermediate")
        wointer_search.add_filter('work_order_code',my.work_order_code)
        wointers = wointer_search.get_sobjects()
        if len(wointers) > 0:
            inter_table.add_row()
            mr_title = inter_table.add_cell('<b><u><i>Intermediate Results</i></u></b>')
            mr_title.add_attr('nowrap', 'nowrap')
            mr_title.add_style('font-size: 90%s;' % '%')
            if len(sources) < 1 and len(inter_passins) < 1:
                inter_table.add_style('border-top-left-radius', '10px')
                inter_table.add_style('border-bottom-left-radius', '10px')
        count = 0
        for wointer in wointers:
            inter_code = wointer.get_value('intermediate_file_code')
            if inter_code not in seen:
                seen.append(inter_code)
                inter_search = Search("twog/intermediate_file")
                inter_search.add_filter('code',inter_code)
                intermediate = inter_search.get_sobject()
                inner_table = Table()
                inner_table.add_row()
                celly = inner_table.add_cell('<font color="#3e3e3e"><b><u>%s</u></b></font>' % (intermediate.get_value('title')))
                celly.add_attr('nowrap','nowrap')
                celly.add_style('cursor: pointer;')
                celly.add_style('font-size: 80%s;' % '%')
                celly.add_behavior(obs.get_launch_wo_inter_behavior(my.work_order_code,my.work_order_sk,inter_code))
                if count % source_limit == 0:
                    inter_table.add_row()
                inner_cell = inter_table.add_cell(inner_table)
                inner_cell.add_attr('valign','top')
                spacer = inter_table.add_cell(' &nbsp;&nbsp; ')
                count = count + 1

        # Need deliverables listed here
        deliv_table = Table()
        deliv_table.add_attr('width','100%s' % '%')
        deliv_table.add_attr('bgcolor','#acbe49e')
        deliv_table.add_style('border-bottom-right-radius', '10px')
        deliv_table.add_style('border-top-right-radius', '10px')
        d_search = Search("twog/work_order_deliverables")
        d_search.add_filter('work_order_code',my.work_order_code)
        wodelivs = d_search.get_sobjects()
        if len(wodelivs) > 0:
            deliv_table.add_row()
            mr_title = deliv_table.add_cell('<b><u><i>Permanent Results</i></u></b>')
            mr_title.add_attr('nowrap','nowrap')
            mr_title.add_style('font-size: 90%s;' % '%')
            if len(sources) < 1 and len(inter_passins) < 1 and len(wointers) < 1:
                deliv_table.add_style('border-top-left-radius', '10px')
                deliv_table.add_style('border-bottom-left-radius', '10px')
        count = 0
        for wodeliv in wodelivs:
            deliv_code = wodeliv.get_value('deliverable_source_code')
            if deliv_code not in seen:
                seen.append(deliv_code)
                s_search = Search("twog/source")
                s_search.add_filter('code',deliv_code)
                deliverable = s_search.get_sobjects()
                if len(deliverable) > 0:
                    deliverable = deliverable[0]
                    inner_table = Table()
                    inner_table.add_row()
                    celly = None
                    if not deliverable.get_value('high_security'):
                        celly = inner_table.add_cell('<font color="#3e3e3e"><b><u>(%s): %s</u></b></font>' % (deliverable.get_value('barcode'), deliverable.get_value('title')))
                    else:
                        celly = inner_table.add_cell('<font color="#ff0000"><b><u>!!!(%s): %s!!!</u></b></font>' % (deliverable.get_value('barcode'), deliverable.get_value('title')))
                    celly.add_attr('nowrap','nowrap')
                    celly.add_style('cursor: pointer;')
                    celly.add_style('font-size: 80%s;' % '%')
                    celly.add_behavior(obs.get_launch_wo_deliv_behavior(my.work_order_code,my.work_order_sk,deliv_code))
                    if count % source_limit == 0:
                        deliv_table.add_row()
                    inner_cell = deliv_table.add_cell(inner_table)
                    inner_cell.add_attr('valign','top')
                    spacer = deliv_table.add_cell(' &nbsp;&nbsp; ')
                    count = count + 1
                else:
                    with open('/var/www/html/Lost_Sources','a') as lostsources:
                        lostsources.write('%s:%s SOURCE: %s\n' % (my.order_sk, my.work_order_code, deliv_code))
                        lostsources.close()

        if len(wodelivs) < 1:
            inter_table.add_style('border-bottom-right-radius', '10px')
            inter_table.add_style('border-top-right-radius', '10px')
        if len(wodelivs) < 1 and len(wointers) < 1:
            inter_pass_table.add_style('border-bottom-right-radius', '10px')
            inter_pass_table.add_style('border-top-right-radius', '10px')
        if len(inter_passins) < 1 and len(wointers) < 1 and len(wodelivs) < 1:
            table.add_style('border-bottom-right-radius', '10px')
            table.add_style('border-top-right-radius', '10px')

        table2 = Table()
        table2.add_row()
        barcode_text_wdg = TextWdg('wo_barcode_insert')
        barcode_text_wdg.add_behavior(obs.get_wo_barcode_insert_behavior(my.work_order_code, my.work_order_sk))
        bct = table2.add_cell(barcode_text_wdg)
        bct.add_attr('align','right')
        bct.add_attr('width','100%s' % '%')

        two_gether = Table()
        two_gether.add_row()
        if len(sources) > 0:
            srcs = two_gether.add_cell(table)
            srcs.add_attr('width','100%s' % '%')
            srcs.add_attr('valign','top')
        if len(inter_passins) > 0:
            ips = two_gether.add_cell(inter_pass_table)
            ips.add_attr('width','100%s' % '%')
            ips.add_attr('valign','top')
        if len(wointers) > 0:
            intr = two_gether.add_cell(inter_table)
            intr.add_attr('width','100%s' % '%')
            intr.add_attr('valign','top')
        if len(wodelivs) > 0:
            delvs = two_gether.add_cell(deliv_table)
            delvs.add_attr('width','100%s' % '%')
            delvs.add_attr('valign','top')
        long = two_gether.add_cell(' ')
        long.add_style('width: 100%s' % '%')
        bcentry = two_gether.add_cell(table2)
        bcentry.add_attr('valign','top')
        bcentry.add_attr('align','right')

        for source in sources:
            if source.get_value('children') in [None,'']:
                update_str = ''
                for wod in wodelivs:
                    if update_str == '':
                        update_str = wod.get_value('deliverable_source_code')
                    else:
                        update_str = '%s,%s' % (update_str, wod.get_value('deliverable_source_code'))
                    d_search = Search("twog/source")
                    d_search.add_filter('code',wod.get_value('deliverable_source_code'))
                    d_src = d_search.get_sobject()
                    ancestors = d_src.get_value('ancestors')
                    if ancestors.find(source.get_value('code')) == -1:
                        if ancestors in [None,'']:
                            ancestors = source.get_value('code')
                        else:
                            ancestors = '%s,%s' % (ancestors, source.get_value('code'))
                        my.server.update(d_src.get_search_key(), {'ancestors': ancestors})
                if len(wodelivs) > 0:
                    my.server.update(source.get_search_key(), {'children': update_str})

#        print "WO SOURCES TIME = %s" % (time.time() - wo_sources_time)
        return two_gether


class EquipmentUsedRow(BaseRefreshWdg):

    def init(my):
        my.search_type = 'twog/equipment_used'
        my.title = 'Equipment Used'
        my.sk = ''
        my.code = ''
        my.user = ''
        my.parent_sk = ''
        my.parent_sid = ''
        my.order_sid = ''
        my.order_sk = ''
        my.x_butt = "<img src='/context/icons/common/BtnKill.gif' title='Delete' name='Delete'/>"
        my.disp_mode = 'Small'
        my.small = False
        my.groups_str = ''
        my.is_master = False
        my.is_master_str = 'false'
        my.on_color = '#ff0000'
        my.off_color = '#c6aeae'

    def get_display(my):
#        eq_used_row_time = time.time()
        my.sk = str(my.kwargs.get('sk'))
        my.code = my.sk.split('code=')[1]
        my.parent_sk = str(my.kwargs.get('parent_sk'))
        my.parent_sid = str(my.kwargs.get('parent_sid'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        order_code = my.order_sk.split('code=')[1]
        if 'user' in my.kwargs.keys():
            my.user = my.kwargs.get('user')
        else:
            my.user = Environment.get_user_name()
        if 'groups_str' in my.kwargs.keys():
            my.groups_str = my.kwargs.get('groups_str')
        if my.groups_str in [None,'']:
            group_search = Search("sthpw/login_in_group")
            group_search.add_filter('login',my.user)
            my_groups = group_search.get_sobjects()
            for mg in my_groups:
                if my.groups_str == '':
                    my.groups_str = mg.get_value('login_group')
                else:
                    my.groups_str = '%s,%s' % (my.groups_str, mg.get_value('login_group'))

        user_is_scheduler = False
        if 'scheduling' in my.groups_str:
            user_is_scheduler = True

        if 'display_mode' in my.kwargs.keys():
            my.disp_mode = str(my.kwargs.get('display_mode'))
        if my.disp_mode == 'Small':
            my.small = True
        if 'is_master' in my.kwargs.keys():
            my.is_master_str = my.kwargs.get('is_master')
            if my.is_master_str == 'true':
                my.is_master = True
        else:
            order_search = Search("twog/order")
            order_search.add_filter('code',order_code)
            order = order_search.get_sobject()
            order_classification = order.get_value('classification')
            if order_classification in ['master','Master']:
                my.is_master = True
                my.is_master_str = 'true'
        obs = OBScripts(order_sk=my.order_sk, user=my.user, groups_str=my.groups_str, display_mode=my.disp_mode, is_master=my.is_master_str)
        if 'main_obj' in my.kwargs.keys():
            main_obj = my.kwargs.get('main_obj')
        else:
            main_search = Search("twog/equipment_used")
            main_search.add_filter('code',my.code)
            main_obj = main_search.get_sobject()
        eq_length = main_obj.get_value('length')
        table = Table()
        table.add_attr('cellpadding','0')
        table.add_attr('cellspacing','0')
        table.add_attr('class','EquipmentUsedRow_%s' % my.code)
        table.add_style('background-color: %s;' % my.off_color)
        table.add_style('border-collapse', 'separate')
        table.add_style('border-spacing', '25px 3px')
        table.add_style('width: 100%s;' % '%')
        table.add_style('border-bottom-right-radius', '10px')
        table.add_style('border-bottom-left-radius', '10px')
        table.add_style('border-top-right-radius', '10px')
        table.add_style('border-top-left-radius', '10px')
        row1 = table.add_row()
        row1.add_attr('width','100%s' % '%')
        name_to_use = main_obj.get_value('name')
        if eq_length not in [None,'']:
            name_to_use = '%s: %s' % (name_to_use, eq_length)
        eu_cell = table.add_cell('<b><u>%s</u></b>' % name_to_use)
        eu_cell.add_attr('nowrap','nowrap')
        eu_cell.add_style('cursor: pointer;')
        eu_cell.add_behavior(obs.get_panel_change_behavior(my.search_type, my.code, my.sk, my.order_sk, my.title, '', 'builder/refresh_from_save','',my.parent_sk,main_obj.get_value('name'), user_is_scheduler))
        top_buttons = Table()
        top_buttons.add_row()
        if my.is_master and not my.small:
            which_icon = IconWdg.TEMPLATE
            which_title = 'Template This Equipment'
            if main_obj.get_value('equipment_used_templ_code') not in ['', None]:
                which_icon = IconWdg.CHECK
                which_title = 'Un-Template This Equipment'
            button = ButtonSmallNewWdg(title=which_title, icon=which_icon)
            eq_templ_code = main_obj.get_value('equipment_used_templ_code')
            if not eq_templ_code:
                eq_templ_code = ''
            button.add_behavior(obs.get_template_single_eu_behavior(my.sk,eq_templ_code))
            top_buttons.add_cell(button)
        if my.small:
            #select_check = CheckboxWdg('select_%s' % (my.code))
            select_check = CustomCheckboxWdg(name='select_%s' % my.code,value_field=my.code,checked='false',dom_class='ob_selector',parent_table="EquipmentUsedRow_%s" % my.code,normal_color=my.off_color,selected_color=my.on_color,code=my.code,ntype='equipment_used',search_key=my.sk,additional_js=obs.get_selected_color_behavior(my.code, 'EquipmentUsedRow', my.on_color, my.off_color))
            #select_check.set_persistence()
            #select_check.set_value(False)
            #select_check.add_attr('code',my.code)
            #select_check.add_attr('ntype','equipment_used')
           # select_check.add_attr('parent_table','EquipmentUsedRow_%s' % my.code)
           # select_check.add_attr('normal_color',my.off_color)
           # select_check.add_attr('selected_color',my.on_color)
           # select_check.add_attr('search_key',my.sk)
           # select_check.add_behavior(obs.get_selected_color_behavior(my.code, 'EquipmentUsedRow', my.on_color, my.off_color))
            cb = top_buttons.add_cell(select_check)
        elif user_is_scheduler:
            xb = top_buttons.add_cell(my.x_butt)
            xb.add_attr('align','right')
            xb.add_style('cursor: pointer;')
            xb.add_behavior(obs.get_killer_behavior(my.sk, my.parent_sk, 'WorkOrderRow', main_obj.get_value('name')))
        unit_cell = table.add_cell('UNITS: %s' % main_obj.get_value('units'))
        unit_cell.add_attr('nowrap','nowrap')
        unit_cell.add_style('font-size: 10px;')
        second_cell = None
        if eq_length in [None,'']:
            if main_obj.get_value('units') in ['gb','tb']:
                second_cell = table.add_cell('EST SIZE: %s' % main_obj.get_value('expected_duration'))
            else:
                second_cell = table.add_cell('EST DUR: %s' % main_obj.get_value('expected_duration'))
        else:
            second_cell = table.add_cell('LEN: %s' % eq_length)
        second_cell.add_style('font-size: 10px;')
        second_cell.add_attr('nowrap','nowrap')
        if main_obj.get_value('units') not in ['gb','tb']:
            third_cell = table.add_cell('QUANT: %s' % main_obj.get_value('expected_quantity'))
            third_cell.add_style('font-size: 10px;')
            third_cell.add_attr('nowrap','nowrap')
            if my.small:
                third_cell.add_style('font-size: 8px;')
            else:
                third_cell.add_style('font-size: 10px;')
        long_cell1 = table.add_cell(top_buttons)
        long_cell1.add_attr('colspan','4')
        long_cell1.add_attr('align','right')
        long_cell1.add_style('width: 100%s' % '%')
        if my.small:
            eu_cell.add_style('font-size: 8px;')
            unit_cell.add_style('font-size: 8px;')
            second_cell.add_style('font-size: 8px;')
            long_cell1.add_style('font-size: 8px;')
        else:
            eu_cell.add_style('font-size: 10px;')
            unit_cell.add_style('font-size: 10px;')
            second_cell.add_style('font-size: 10px;')
            long_cell1.add_style('font-size: 10px;')
        tab2ret = Table()
        tab2ret.add_attr('width','100%s' % '%')
        top_row = tab2ret.add_row()
        top_row.add_attr('class','top_%s' % my.sk)
        tab2ret.add_cell(table)
#        print "EQ USED ROW TIME = %s" % (time.time() - eq_used_row_time)
        return table

