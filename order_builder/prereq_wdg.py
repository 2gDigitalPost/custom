from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Environment
from pyasm.search import Search
from pyasm.web import Table
from pyasm.widget import TextWdg

from alternative_elements.customcheckbox import CustomCheckboxWdg
from widget.new_icon_wdg import CustomIconWdg
from widget.button_small_new_wdg import ButtonSmallNewWdg

from order_builder_utils import OBScripts


class PreReqWdg(BaseRefreshWdg):

    def init(my):
        my.sob_sk = ''
        my.sob_code = ''
        my.sob_name = ''
        my.sob_st = ''
        my.prereq_st = ''
        my.prereq_field = ''
        my.pipeline = ''
        my.order_sk = ''
        my.x_butt = "<img src='/context/icons/common/BtnKill_Black.gif' title='Delete' name='Delete'/>"
        my.is_master = False

    def get_display(my):
        my.sob_code = str(my.kwargs.get('sob_code'))
        my.sob_sk = str(my.kwargs.get('sob_sk'))
        my.sob_st = str(my.kwargs.get('sob_st'))
        my.sob_name = str(my.kwargs.get('sob_name'))
        my.pipeline = str(my.kwargs.get('pipeline'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        order_code = my.order_sk.split('code=')[1]
        if 'is_master' in my.kwargs.keys():
            my.is_master = my.kwargs.get('is_master')
        else:
            order_search = Search("twog/order")
            order_search.add_filter('code', order_code)
            order = order_search.get_sobject()
            order_classification = order.get_value('classification')
            if order_classification in ['master', 'Master']:
                my.is_master = True
        obs = OBScripts(order_sk=my.order_sk)
        if my.sob_st == 'twog/title':
            my.prereq_st = 'twog/title_prereq'
            my.prereq_field = 'title_code'
        elif my.sob_st == 'twog/work_order':
            my.prereq_st = 'twog/work_order_prereq'
            my.prereq_field = 'work_order_code'

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

        prereq_search = Search(my.prereq_st)
        prereq_search.add_filter(my.prereq_field,my.sob_code)
        prereqs = prereq_search.get_sobjects()
        overhead = Table()
        overhead.add_attr('class', 'overhead_%s' % my.sob_code)
        table = Table()
        table.add_attr('class', 'prereq_adder_%s' % my.sob_code)
        table.add_row()
        if my.sob_st == 'twog/work_order' and user_is_scheduler:
            kill_title_pqs_btn = table.add_cell('<input type="button" value="Remove\nTitle PreReqs"/>')
            kill_title_pqs_btn.add_attr('colspan','2')
            kill_title_pqs_btn.add_behavior(obs.get_kill_wos_title_prereqs_behavior(my.sob_sk, my.order_sk, my.sob_name,
                                                                                    my.pipeline))
        else:
            table.add_cell(' ')
            table.add_cell(' ')
        table.add_cell(' ')
        table.add_cell(' ')
        sat = table.add_cell('Satisfied?')
        sat.add_attr('align', 'center')
        table.add_cell(' ')
        for p in prereqs:
            table.add_row()
            if user_is_scheduler:
                killer = table.add_cell(my.x_butt)
                killer.add_style('cursor: pointer;')
                killer.add_behavior(obs.get_prereq_killer_behavior(p.get_value('code'), my.prereq_st, my.sob_code,
                                                                   my.sob_sk, my.sob_st, my.sob_name, my.pipeline))
            prereq_text = 'PreReq: '
            if my.sob_st == 'twog/work_order':
                if p.get_value('from_title') == True:
                    prereq_text = 'Title PreReq: '
            alabel = table.add_cell(prereq_text)
            alabel.add_attr('align', 'center')
            table.add_cell('<input type="text" class="prereq_%s" value="%s" style="width: 500px;"/>' % (p.get_value('code'), p.get_value('prereq')))
            save_butt = table.add_cell('<input type="button" class="save_%s" value="Save"/>' % (p.get_value('code')))
            save_butt.add_behavior(obs.get_save_prereq_behavior(p.get_value('code'), my.prereq_st, my.sob_code,
                                                                my.pipeline))

            if p.get_value('satisfied') == True:
                check_val = 'true'
            else:
                check_val = 'false'
            checkbox = CustomCheckboxWdg(name='satisfied_%s' % p.get_value('code'), value_field=p.get_value('code'),
                                         checked=check_val, dom_class='prereq_selector', code=p.get_value('code'),
                                         additional_js=obs.get_change_satisfied_behavior(p.get_value('code'),
                                                                                         my.prereq_st, my.sob_code,
                                                                                         p.get_value('satisfied'),
                                                                                         my.sob_sk, my.sob_st,
                                                                                         my.sob_name, my.pipeline))

            ck = table.add_cell(checkbox)
            ck.add_attr('align','center')
            if my.is_master:
                if my.sob_st == 'twog/title':
                    table.add_cell(' &nbsp; ')
                    templ_search = Search("twog/pipeline_prereq")
                    templ_search.add_filter('pipeline_code', my.pipeline)
                    templ_search.add_filter('prereq', p.get_value('prereq'))
                    templ_rez = templ_search.get_sobjects()
                    templ_count = len(templ_rez)
                    if templ_count == 0:
                        template_button = ButtonSmallNewWdg(title="Template This PreReq",
                                                            icon=CustomIconWdg.icons.get('TEMPLATE'))
                        if my.is_master and user_is_scheduler:
                            template_button.add_behavior(obs.get_template_prereq_behavior(my.sob_code, my.pipeline,
                                                                                          my.prereq_st,
                                                                                          p.get_value('code')))
                    else:
                        template_button = '<img border="0" style="vertical-align: middle" title="Templated" name="Templated" src="/context/icons/silk/tick.png">'
                    tb = table.add_cell(template_button)
                    tb.add_class('prereq_templ_%s' % p.get_value('code'))
                elif my.sob_st == 'twog/work_order':
                    table.add_cell(' &nbsp; ')
                    wot_search = Search("twog/work_order")
                    wot_search.add_filter('code', my.sob_code)
                    wot = wot_search.get_sobject()
                    work_order_templ_code = wot.get_value('work_order_templ_code')
                    templ_search = Search("twog/work_order_prereq_templ")
                    templ_search.add_filter('work_order_templ_code', work_order_templ_code)
                    templ_search.add_filter('prereq', p.get_value('prereq'))
                    templ_rez = templ_search.get_sobjects()
                    templ_count = len(templ_rez)
                    if templ_count == 0:
                        template_button = ButtonSmallNewWdg(title="Template This PreReq", icon=CustomIconWdg.icons.get('TEMPLATE'))
                        if my.is_master:
                            template_button.add_behavior(obs.get_template_wo_prereq_behavior(my.sob_code, my.prereq_st,
                                                                                             p.get_value('code'),
                                                                                             work_order_templ_code))
                    else:
                        template_button = '<img border="0" style="vertical-align: middle" title="Templated" name="Templated" src="/context/icons/silk/tick.png">'
                    tb = table.add_cell(template_button)
                    tb.add_class('prereq_templ_%s' % p.get_value('code'))
        table.add_row()
        table.add_cell('<hr/>')
        table.add_row()
        table.add_cell(' &nbsp; ')
        if user_is_scheduler:
            label = table.add_cell('New PreReq: ')
            label.add_attr('nowrap', 'nowrap')
            prereq_text_wdg = TextWdg('new_prereq')
            prereq_text_wdg.add_behavior(obs.get_create_prereq_change_behavior(my.sob_code, my.prereq_st, my.sob_sk,
                                                                               my.sob_st, my.sob_name, my.pipeline))
            table.add_cell(prereq_text_wdg)
            create_butt = table.add_cell('<input type="button" class="create_prereq" value="Create"/>')
            create_butt.add_behavior(obs.get_create_prereq_behavior(my.sob_code, my.prereq_st, my.sob_sk, my.sob_st,
                                                                    my.sob_name, my.pipeline))
        overhead.add_row()
        oh_cell = overhead.add_cell(table)
        oh_cell.add_attr('class', 'prereq_adder_cell')

        return overhead
