from client.tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget.button_new_wdg import ButtonSmallNewWdg

from pyasm.common import Environment
from pyasm.search import Search
from pyasm.web import Table
from pyasm.widget import IconWdg

from alternative_elements.customcheckbox import CustomCheckboxWdg
from common_tools.common_functions import fix_date
from order_builder_utils import OBScripts, get_selected_color_behavior, get_upload_behavior

from equipment_used_row import EquipmentUsedRow
from nighttime_hotlist.nighttime_hotlist import BigBoardSingleWOSelectWdg, IndieBigBoardSelectWdg
from work_order_printer import WorkOrderPrintLauncherWdg
from work_order_sources_row import WorkOrderSourcesRow
from prereq_count_wdg import PreReqCountWdg


class WorkOrderRow(BaseRefreshWdg):

    def init(my):
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
        row1.add_attr('width', '100%')
        row1.add_style('width: 100%;')
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
            select_check = CustomCheckboxWdg(name='select_%s' % my.code, value_field=my.code, checked='false', dom_class='ob_selector', parent_table="WorkOrderRow_%s" % my.code, process=main_obj.get_value('process'), work_group=main_obj.get_value('work_group'), proj_code=main_obj.get_value('proj_code'), title_code=main_obj.get_value('title_code'), order_code=order_code, task_code=main_obj.get_value('task_code'), normal_color=my.off_color, selected_color=my.on_color, code=my.code, ntype='work_order', search_key=my.sk, task_sk=task_sk, additional_js=get_selected_color_behavior(my.code, 'WorkOrderRow', my.on_color, my.off_color))
            cb = top_buttons.add_cell(select_check)
        elif user_is_scheduler:
            xb = top_buttons.add_cell(my.x_butt)
            xb.add_attr('align', 'right')
            xb.add_style('cursor: pointer;')
            xb.add_behavior(obs.get_killer_behavior(my.sk, my.parent_sk, 'ProjRow', main_obj.get_value('process')))
        long_cell1 = table.add_cell(top_buttons)
        long_cell1.add_attr('align', 'right')
        long_cell1.add_attr('colspan', '1')
        long_cell1.add_style('width: 100%')
        table.add_row()
        ccel = table.add_cell('Code: %s' % my.code)
        ccel.add_attr('nowrap','nowrap')
        start_cell = table.add_cell('Start: %s' % fix_date(start_date))
        start_cell.add_attr('nowrap','nowrap')
        end_cell = table.add_cell('End: %s' % fix_date(end_date))
        end_cell.add_attr('nowrap', 'nowrap')
        active_cell = table.add_cell(active_status)
        active_cell.add_attr('align', 'right')
        active_cell.add_attr('colspan', '3')
        active_cell.add_style("width: 100%;")
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
                er.add_attr('align', 'right')
                er.add_attr('valign', 'bottom')
                er.add_attr('colspan', '3')
                er.add_attr('width', '100%')

            bbr.add_row()

            if not my.is_master and user_is_scheduler and task_exists:
                indie_button = IndieBigBoardSelectWdg(search_key=task.get_search_key(),indie_bigboard=task.get_value('indie_bigboard'),title_code=parent_obj.get_value('title_code'),lookup_code=my.code)
                indie = bbr.add_cell(indie_button)
                indie.add_attr('align','right')
                indie.add_attr('valign','bottom')

                big_button = BigBoardSingleWOSelectWdg(search_key=task.get_search_key(),bigboard=task.get_value('bigboard'),title_code=parent_obj.get_value('title_code'),lookup_code=my.code)
                bbw = bbr.add_cell(big_button)
                bbw.add_attr('align','right')
                bbw.add_attr('valign','bottom')

            print_button = WorkOrderPrintLauncherWdg(work_order_code=my.code)
            prnt = bbr.add_cell(print_button)
            prnt.add_attr('align','right')
            prnt.add_attr('valign','bottom')

            upload = ButtonSmallNewWdg(title="Upload", icon=IconWdg.PUBLISH)
            upload.add_behavior(get_upload_behavior(my.sk))
            up = bbr.add_cell(upload)
            up.add_attr('align','right')
            up.add_attr('valign','bottom')

            note_adder = ButtonSmallNewWdg(title="Add Note", icon=IconWdg.NOTE_ADD)
            note_adder.add_behavior(obs.get_launch_note_behavior(my.parent_sk, parent_obj.get_value('process')))
            nadd = bbr.add_cell(note_adder)
            nadd.add_attr('align', 'right')
            nadd.add_attr('valign', 'bottom')
            nadd.add_style('cursor: pointer;')

            if user_is_scheduler:
                add_eq_used_butt = ButtonSmallNewWdg(title="Add Equipment", icon=IconWdg.EQUIPMENT_ADD)
                add_eq_used_butt.add_behavior(obs.get_eu_add_behavior(main_obj.get_value('process'),main_obj.get_search_key(), main_obj.get_value('code')))
                eu_adder = bbr.add_cell(add_eq_used_butt)
                eu_adder.add_attr('width','100%')
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
                templ_butt.add_attr('class', 'templ_butt_%s' % my.sk)
                templ_butt.add_attr('width', '100%')
                templ_butt.add_attr('align', 'right')
                templ_butt.add_attr('valign', 'bottom')
            bl = bottom_buttons.add_cell(bbl)
            bl.add_attr('valign', 'bottom')
            bl.add_attr('align', 'left')
            bl.add_attr('width', '100%')
            br = bottom_buttons.add_cell(bbr)
            br.add_attr('valign', 'bottom')

            bbs = table.add_cell(bottom_buttons)
            bbs.add_attr('width', '100%')
            bbs.add_attr('align', 'left')
            bbs.add_attr('valign', 'bottom')

            if user_is_scheduler:
                src_row = table.add_row()
                src_row.add_attr('class', 'wo_sources_row')
                wos = WorkOrderSourcesRow(work_order_code=my.code, work_order_sk=my.sk, order_sk=my.order_sk)
                wos_cell = table.add_cell(wos)
                wos_cell.add_attr('colspan', '4')
                wos_cell.add_attr('class', 'wo_sources_%s' % my.sk)

        bottom = Table()
        bottom.add_attr('width', '100%')
        bottom.add_attr('cellpadding', '0')
        bottom.add_attr('cellspacing', '0')
        for eu in eus:
            eu_sk = eu.get_search_key()
            if eu.get_value('client_code') in [None,'']:
                my.server.update(eu_sk, {'client_code': main_obj.get_value('client_code')}, triggers=False)
            eu_row = bottom.add_row()
            eu_row.add_attr('class', 'EquipmentUsedRowRow row_%s' % eu_sk)
            eu_obj = EquipmentUsedRow(sk=eu_sk, parent_sk=my.sk, order_sk=my.order_sk, parent_sid=my.search_id, groups_str=my.groups_str, user=my.user, display_mode=my.disp_mode, is_master=my.is_master_str,main_obj=eu)
            eu_cell = bottom.add_cell(eu_obj)
            eu_cell.add_attr('width', '100%')
            eu_cell.add_attr('sk', eu_sk)
            eu_cell.add_attr('order_sk', my.order_sk)
            eu_cell.add_attr('parent_sk', my.sk )
            eu_cell.add_attr('parent_sid', my.search_id )
            eu_cell.add_attr('call_me', eu.get_value('name'))
            eu_cell.add_attr('wot_code', main_obj.get_value('work_order_templ_code'))
            eu_cell.add_attr('my_class', 'EquipmentUsedRow')
            eu_cell.add_attr('class', 'cell_%s' % eu_sk)
        tab2ret = Table()
        tab2ret.add_attr('width', '100%')
        top_row = tab2ret.add_row()
        top_row.add_attr('class', 'top_%s' % my.sk)
        tab2ret.add_cell(table)
        bot_row = tab2ret.add_row()
        if not open_bottom:
            bot_row.add_style('display: none;')
        else:
            bot_row.add_style('display: table-row;')
        bot_row.add_attr('class', 'bot_%s' % my.sk)
        bot = tab2ret.add_cell(bottom)
        bot.add_style('padding-left: 40px;')

        return tab2ret
