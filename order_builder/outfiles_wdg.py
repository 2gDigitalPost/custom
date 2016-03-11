from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Environment
from pyasm.search import Search
from pyasm.web import Table

from alternative_elements.customcheckbox import *
from widget.new_icon_wdg import CustomIconWdg
from widget.button_small_new_wdg import ButtonSmallNewWdg

from order_builder_utils import OBScripts, get_open_intermediate_behavior


class OutFilesWdg(BaseRefreshWdg):

    def init(my):
        my.work_order_sk = ''
        my.work_order_code = ''
        my.client_code = ''
        my.order_sk = ''
        my.x_butt = "<img src='/context/icons/common/BtnKill_Black.gif' title='Delete' name='Delete'/>"
        my.is_master = False
        my.is_master_str = 'false'

    def get_display(my):
        my.work_order_sk = str(my.kwargs.get('work_order_sk'))
        my.work_order_code = str(my.kwargs.get('work_order_code'))
        my.client_code = str(my.kwargs.get('client_code'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        order_code = my.order_sk.split('code=')[1]
        overhead = Table()
        overhead.add_attr('class','out_overhead_%s' % my.work_order_code)
        overhead.add_attr('client_code',my.client_code)
        obs = OBScripts(order_sk=my.order_sk)
        wo_search = Search("twog/work_order")
        wo_search.add_filter('code',my.work_order_code)
        work_order = wo_search.get_sobject()
        delivs_search = Search("twog/work_order_deliverables")
        delivs_search.add_filter('work_order_code',my.work_order_code)
        delivs = delivs_search.get_sobjects()
        inter_search = Search("twog/work_order_intermediate")
        inter_search.add_filter('work_order_code',my.work_order_code)
        inters = inter_search.get_sobjects()

        user_group_names = Environment.get_group_names()
        groups_str = ''
        for mg in user_group_names:
            if groups_str == '':
                groups_str = mg
            else:
                groups_str = '%s,%s' % (groups_str, mg)
        user_is_scheduler = False
        if 'scheduling' in groups_str:
            user_is_scheduler = True

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
        table = Table()
        table.add_row()
        table.add_cell('<font size="4"><b><u>Intermediates</u></b></font>')
        add_inter = table.add_cell('<input type="button" value="Add Intermediate File"/>')
        add_inter.add_attr('nowrap','nowrap')
        add_inter.add_style('cursor: pointer;')
        add_inter.add_behavior(obs.get_add_inter_behavior(my.work_order_code, my.client_code, my.is_master_str))
        inters_tbl = Table()
        for inter1 in inters:
            i_search = Search("twog/intermediate_file")
            i_search.add_filter('code',inter1.get_value('intermediate_file_code'))
            inter = i_search.get_sobject()
            inters_tbl.add_row()
            if user_is_scheduler:
                killer = inters_tbl.add_cell(my.x_butt)
                killer.add_style('cursor: pointer;')
                killer.add_behavior(obs.get_intermediate_killer_behavior(inter1.get_value('code'), inter.get_value('title'), my.work_order_code, my.is_master_str))
            alabel = inters_tbl.add_cell('Intermediate: ')
            alabel.add_attr('align','center')
            popper = inters_tbl.add_cell('<u>%s</u>' % inter.get_value('title'))
            popper.add_attr('nowrap','nowrap')
            popper.add_style('cursor: pointer;')
            popper.add_behavior(get_open_intermediate_behavior(inter.get_value('code'), my.work_order_code,
                                                               my.client_code, my.order_sk))

            if str(inter1.get_value('satisfied')) == 'True':
                check_val = 'true'
            else:
                check_val = 'false'
            checkbox = CustomCheckboxWdg(name='satisfied_%s' % inter.get_value('code'),value_field=inter.get_value('code'),checked=check_val,dom_class='inter_selector',code=inter.get_value('code'),additional_js=obs.get_change_inter_satisfied_behavior(inter1.get_value('code'), my.work_order_code, my.client_code, str(inter1.get_value('satisfied'))))

            ck = inters_tbl.add_cell(checkbox)
            ck.add_attr('align','center')
            inters_tbl.add_cell(' &nbsp; ')
            if my.is_master:
                if inter.get_value('intermediate_file_templ_code') in [None,'']:
                    template_button = ButtonSmallNewWdg(title="Template This Intermediate File", icon=CustomIconWdg.icons.get('TEMPLATE'))
                    template_button.add_behavior(obs.get_template_intermediate_behavior(inter.get_value('code'), my.work_order_code))
                else:
                    template_button = '<img border="0" style="vertical-align: middle" title="Templated" name="Templated" src="/context/icons/silk/tick.png">'
                tb = inters_tbl.add_cell(template_button)
                tb.add_class('inter_templ_%s' % inter.get_value('code'))
        table.add_row()
        intr = table.add_cell(inters_tbl)
        intr.add_attr('colspan','2')
        table.add_row()
        table.add_cell('<hr/>')
        table.add_row()
        table.add_cell('<font size="4"><b><u>Permanents</u></b></font>')
        add_delv = table.add_cell('<input type="button" value="Add Permanent Element"/>')
        add_delv.add_style('cursor: pointer;')
        add_delv.add_behavior(obs.get_add_deliverable_behavior(my.work_order_code, my.client_code))
        delv_tbl = Table()
        client_search = Search("twog/client")
        client_search.add_order_by('name desc')
        clients = client_search.get_sobjects()
        client_sel = '<select class="deliver_to_DELIV_CODE"><option value="">--Select--</option>'
        for client in clients:
            client_sel = '%s<option value="%s">%s</option>' % (client_sel, client.get_value('name'), client.get_value('name'))
        client_sel = '%s</select>' % client_sel
        for deliv1 in delivs:
            d_search = Search("twog/source")
            d_search.add_filter('code',deliv1.get_value('deliverable_source_code'))
            deliv = d_search.get_sobject()
            deliv_name = '%s, Episode: %s, Type: %s' % (deliv.get_value('title'),deliv.get_value('episode'), deliv.get_value('source_type'))
            delv_tbl.add_row()
            if user_is_scheduler:
                killer = delv_tbl.add_cell(my.x_butt)
                killer.add_style('cursor: pointer;')
                killer.add_behavior(obs.get_deliverable_killer_behavior(deliv1.get_value('code'), my.work_order_code, deliv1.get_value('title_code'), deliv.get_value('code'), '%s (%s: %s)' % (deliv1.get_value('name'), deliv.get_value('title'), deliv.get_value('episode')), my.is_master_str))
            alabel = delv_tbl.add_cell('Permanent: ')
            alabel.add_attr('align','center')
            popper = delv_tbl.add_cell('<u>%s</u>' % deliv.get_value('title'))
            popper.add_attr('nowrap','nowrap')
            popper.add_style('cursor: pointer;')
            popper.add_behavior(obs.get_open_deliverable_behavior(deliv.get_value('code'), my.work_order_code, deliv1.get_value('title_code'), my.client_code))

            if str(deliv1.get_value('satisfied')) == 'True':
                check_val = 'true'
            else:
                check_val = 'false'
            checkbox = CustomCheckboxWdg(name='satisfied_%s' % deliv.get_value('code'),value_field=deliv.get_value('code'),checked=check_val,dom_class='deliv_selector',code=deliv.get_value('code'),additional_js=obs.get_change_deliverable_satisfied_behavior(deliv1.get_value('code'), my.work_order_code, deliv1.get_value('title_code'), str(deliv1.get_value('satisfied')), my.client_code))

            ck = delv_tbl.add_cell(checkbox)
            ck.add_attr('align','center')
            delv_tbl.add_cell(' &nbsp; ')
            if my.is_master:
                if deliv.get_value('templ_code') in [None,'']:
                    template_button = ButtonSmallNewWdg(title="Template This Intermediate File", icon=CustomIconWdg.icons.get('TEMPLATE'))
                    template_button.add_behavior(obs.get_template_deliverable_behavior(deliv1.get_value('code'), work_order.get_value('work_order_templ_code'), deliv1.get_value('deliverable_source_code'), my.work_order_code))
                else:
                    template_button = '<img border="0" style="vertical-align: middle" title="Templated" name="Templated" src="/context/icons/silk/tick.png">'
                tb = delv_tbl.add_cell(template_button)
                tb.add_class('deliverable_templ_%s' % deliv1.get_value('code'))
            bot_delv = Table()
            bot_delv.add_row()
            bot_delv.add_cell('Name: ')
            bot_delv.add_cell('<input type="text" class="deliv_name_%s" value="%s"/>' % (deliv1.get_value('code'), deliv1.get_value('name')))
            bot_delv.add_row()
            nw = bot_delv.add_cell('Deliver To: ')
            nw.add_attr('nowrap','nowrap')
            this_client_sel = client_sel.replace('DELIV_CODE',deliv1.get_value('code'))
            this_client_sel = this_client_sel.replace('value="%s"' % deliv1.get_value('deliver_to'), 'value="%s" selected="selected"' % deliv1.get_value('deliver_to'))
            bot_delv.add_cell(this_client_sel)
            bot_delv.add_row()
            bot_delv.add_cell('Attn: ')
            bot_delv.add_cell('<input type="text" class="deliv_attn_%s" value="%s"/>' % (deliv1.get_value('code'), deliv1.get_value('attn')))
            bot_delv.add_row()
            save_cell = bot_delv.add_cell('<input type="button" value="Save Permanent Element Info"/>')
            save_cell.add_behavior(obs.get_save_deliv_info_behavior(deliv1.get_value('code'), my.work_order_code, deliv1.get_value('title_code'), my.client_code, my.is_master_str))

            delv_tbl.add_row()
            bot = delv_tbl.add_cell(bot_delv)
            bot.add_attr('colspan','4')
        table.add_row()
        delv = table.add_cell(delv_tbl)
        delv.add_attr('colspan', '2')
        overhead.add_row()
        oh_cell = overhead.add_cell(table)
        oh_cell.add_attr('class','out_list_cell')
        return overhead
