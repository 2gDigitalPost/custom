from client.tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Environment
from pyasm.search import Search
from pyasm.web import Table
from pyasm.widget import TextWdg
from widget.new_icon_wdg import CustomIconWdg

from alternative_elements.customcheckbox import CustomCheckboxWdg
from common_tools.common_functions import fix_date
from order_builder_utils import OBScripts, get_selected_color_behavior, get_upload_behavior
from widget.button_small_new_wdg import ButtonSmallNewWdg

from work_order_row import WorkOrderRow


class ProjRow(BaseRefreshWdg):

    def init(my):
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
        table.add_attr('cellpadding', '0')
        table.add_attr('cellspacing', '0')
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
            select_check = CustomCheckboxWdg(name='select_%s' % my.code, value_field=my.code, checked='false', dom_class='ob_selector', parent_table="ProjRow_%s" % my.code, normal_color=my.off_color, selected_color=my.on_color, code=my.code, ntype='proj', search_key=my.sk, task_sk=task_sk, additional_js=get_selected_color_behavior(my.code, 'ProjRow', my.on_color, my.off_color))
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
                    hack_edit = ButtonSmallNewWdg(title="Edit Connections", icon=CustomIconWdg.icons.get('HACKUP'))
                    hack_edit.add_behavior(obs.get_edit_hackup_connections(my.code, main_obj.get_value('process')))
                    he = bottom_buttons.add_cell(hack_edit)
                    he.add_attr('align','right')
                    he.add_attr('valign','bottom')
                if user_is_scheduler:
                    adder = ButtonSmallNewWdg(title="Add A Work Order", icon=CustomIconWdg.icons.get('ADD'))
                    adder.add_behavior(obs.get_multi_add_wos_behavior(my.sk))
                    add = bottom_buttons.add_cell(adder)
                    add.add_attr('align','right')
                    priority = ButtonSmallNewWdg(title="Change Priority", icon=CustomIconWdg.icons.get('PRIORITY'))
                    priority.add_behavior(obs.get_change_priority_behavior(main_obj.get_value('code'), main_obj.get_value('process')))
                    prio = bottom_buttons.add_cell(priority)
                    prio.add_attr('align','right')
                    duedate = ButtonSmallNewWdg(title="Change Due Date", icon=CustomIconWdg.icons.get('CALENDAR'))
                    duedate.add_behavior(obs.get_change_due_date_behavior(main_obj.get_value('code'), main_obj.get_value('process')))
                    due = bottom_buttons.add_cell(duedate)
                    due.add_attr('align','right')

            upload = ButtonSmallNewWdg(title="Upload", icon=CustomIconWdg.icons.get('PUBLISH'))
            upload.add_behavior(get_upload_behavior(my.sk))
            up = bottom_buttons.add_cell(upload)
            up.add_attr('align','right')

            note_adder = ButtonSmallNewWdg(title="Add Note", icon=CustomIconWdg.icons.get('NOTE_ADD'))
            note_adder.add_behavior(obs.get_launch_note_behavior(my.sk, main_obj.get_value('process')))
            nadd = bottom_buttons.add_cell(note_adder)
            nadd.add_attr('align','right')
            nadd.add_style('cursor: pointer;')

            if user_is_scheduler:
                pipe_button = ButtonSmallNewWdg(title="Assign Pipeline", icon=CustomIconWdg.icons.get('PIPELINE'))
                pipe_button.add_behavior(obs.get_scratch_pipe_behavior('twog/proj',my.search_id,my.parent_sid,my.width,my.height, main_obj.get_value('pipeline_code'),main_obj.get_search_key(),'ProjRow',main_obj.get_value('process')))
                scratch = bottom_buttons.add_cell(pipe_button)

            templ_icon = None
            templ_title = ''
            if my.is_master:
                if main_obj.get_value('templ_me') == True:
                    templ_icon = CustomIconWdg.icons.get('CHECK')
                    templ_title = "This is the Templating Project"
                else:
                   templ_icon = CustomIconWdg.icons.get('TEMPLATE')
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