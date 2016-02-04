from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget.button_new_wdg import ButtonSmallNewWdg

from pyasm.common import Environment
from pyasm.web import Table
from pyasm.widget import IconWdg

from order_builder_utils import OBScripts
from order_checker import OrderCheckerLauncherWdg


class BuilderTools(BaseRefreshWdg):
    #This is the bunch of tools (buttons) that appear on the order builder's top row.
    def init(my):
        my.order_sk = ''
        my.user = ''
        my.groups_str = ''
        my.disp_mode = ''
        my.is_master = False
        my.is_master_str = 'false'
        my.small = False

    def get_display(my):
        from scraper import *
        my.order_sk = my.kwargs.get('order_sk')
        order_code = my.order_sk.split('code=')[1]
        my.groups_str = my.kwargs.get('groups_str')
        main_obj = None
        if 'display_mode' in my.kwargs.keys():
            my.disp_mode = my.kwargs.get('display_mode')
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
        if 'is_master' in my.kwargs.keys():
            my.is_master_str = my.kwargs.get('is_master')
            if my.is_master_str == 'true':
                my.is_master = True
        else:
            from client.tactic_client_lib import TacticServerStub
            server = TacticServerStub.get()
            main_obj = server.eval("@SOBJECT(twog/order['code','%s'])" % order_code)[0]
            if main_obj.get('classification') in ['master','Master']:
                my.is_master = True
                my.is_master_str = 'true'
        user_is_scheduler = False
        if 'scheduling' in my.groups_str:
            user_is_scheduler = True
        if main_obj in [None,'']:
            from client.tactic_client_lib import TacticServerStub
            server = TacticServerStub.get()
            main_obj = server.eval("@SOBJECT(twog/order['code','%s'])" % order_code)[0]
        obs = OBScripts(order_sk=my.order_sk,user=my.user,groups_str=my.groups_str,display_mode=my.disp_mode)
        table = Table()
        table.add_attr('cellspacing','3')
        table.add_attr('cellpadding','3')
        table.add_attr('height','100%s' % '%')
        table.add_attr('bgcolor','#e4e6f0')
        table.add_style('border-bottom-right-radius', '10px')
        table.add_style('border-bottom-left-radius', '10px')
        table.add_style('border-top-right-radius', '10px')
        table.add_style('border-top-left-radius', '10px')

        #NEW START
        table.add_row()
        title = table.add_cell(' &nbsp;&nbsp;&nbsp;<i><b>2G Order Builder</b></i> ')
        title.add_attr('nowrap','nowrap')
        title.add_style('font-size: 120%s;' % '%')
        selected_obj = table.add_cell('')
        selected_obj.add_attr('class','selected_sobject')
        selected_obj.add_attr('width','100%s' % '%')

        associator_launcher = OrderAssociatorLauncherWdg(code=order_code,search_on_load='false')
        associator = table.add_cell(associator_launcher)
        associator.add_attr('align','right')

        lnk = None
        if main_obj.get('imdb_url') not in [None,'','none']:
            lnk = table.add_cell('<a href="%s" target="_blank">Link</a>' % main_obj.get('imdb_url'))
        else:
            lnk = table.add_cell("No Link")
            #Then there is no link
        lnk.add_attr('align','left')
        lnk.add_attr('nowrap','nowrap')
        table.add_cell('&nbsp;&nbsp;&nbsp;&nbsp;')

        refresher = ButtonSmallNewWdg(title="Refresh", icon=IconWdg.REFRESH)
        refresher.add_behavior(obs.get_refresh_behavior(my.user))
        refr = table.add_cell(refresher)
        refr.add_attr('align','right')

        checker_launcher = OrderCheckerLauncherWdg(order_code=order_code)
        checker = table.add_cell(checker_launcher)
        checker.add_attr('align','right')

        if user_is_scheduler:
            global_replacer = ButtonSmallNewWdg(title="Global Replacer", icon=IconWdg.DEPENDENCY)
            global_replacer.add_behavior(obs.get_global_replacer_wdg(my.user))
            globalr = table.add_cell(global_replacer)
            globalr.add_attr('align','right')

            if my.small:
                normal_edit = ButtonSmallNewWdg(title="Normal Edit", icon=IconWdg.NORMAL_EDIT)
                normal_edit.add_behavior(obs.get_quick_edit_behavior(my.user))
                normr = table.add_cell(normal_edit)
                normr.add_attr('align','right')
            else:
                quick_edit = ButtonSmallNewWdg(title="Quick Edit", icon=IconWdg.QUICK_EDIT)
                quick_edit.add_behavior(obs.get_quick_edit_behavior(my.user))
                quickr = table.add_cell(quick_edit)
                quickr.add_attr('align','right')


            clear_cache = ButtonSmallNewWdg(title="Clear Cache", icon=IconWdg.TRASH)
            clear_cache.add_behavior(obs.get_clear_cache_behavior(my.user))
            clearc = table.add_cell(clear_cache)
            clearc.add_attr('align','right')

            source_adder = ButtonSmallNewWdg(title="Create New Source", icon=IconWdg.SOURCE_ADD_TAPE)
            source_adder.add_behavior(obs.get_create_source_behavior())
            sexa = table.add_cell(source_adder)
            sexa.add_attr('align','right')

        eq_exp = ButtonSmallNewWdg(title="Show Equipment", icon=IconWdg.ARROW_OUT_EQUIPMENT)
        eq_exp.add_behavior(obs.get_equipment_expander_behavior())
        eqb = table.add_cell(eq_exp)
        eqb.add_attr('align','right')

        eq_coll = ButtonSmallNewWdg(title="Hide Equipment", icon=IconWdg.ARROW_UP_EQUIPMENT)
        eq_coll.add_behavior(obs.get_equipment_collapser_behavior())
        eqlb = table.add_cell(eq_coll)
        eqlb.add_attr('align','right')

        source_exp = ButtonSmallNewWdg(title="Show Sources", icon=IconWdg.ARROW_OUT_SOURCE)
        source_exp.add_behavior(obs.get_source_expander_behavior())
        sexb = table.add_cell(source_exp)
        sexb.add_attr('align','right')

        source_coll = ButtonSmallNewWdg(title="Hide Sources", icon=IconWdg.ARROW_UP_SOURCE)
        source_coll.add_behavior(obs.get_source_collapser_behavior())
        sclb = table.add_cell(source_coll)
        sclb.add_attr('align','right')

        expander_button = ButtonSmallNewWdg(title="Expand All", icon=IconWdg.ARROW_OUT)
        expander_button.add_behavior(obs.get_expander_behavior())
        exb = table.add_cell(expander_button)
        exb.add_attr('align','right')

        collapser_button = ButtonSmallNewWdg(title="Collapse All", icon=IconWdg.ARROW_UP_GREEN)
        collapser_button.add_behavior(obs.get_collapser_behavior())
        clb = table.add_cell(collapser_button)
        clb.add_attr('align','right')

        space = table.add_cell(' ')
        space.add_attr('width','100%s' % '%')

        return table
