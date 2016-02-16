from client.tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget.button_new_wdg import ButtonSmallNewWdg

from pyasm.common import Environment
from pyasm.web import Table
from widget.new_icon_wdg import CustomIconWdg

from order_checker import OrderCheckerLauncherWdg


class BuilderTools(BaseRefreshWdg):
    # This is the bunch of tools (buttons) that appear on the order builder's top row.
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
            server = TacticServerStub.get()
            main_obj = server.eval("@SOBJECT(twog/order['code','%s'])" % order_code)[0]
            if main_obj.get('classification') in ['master', 'Master']:
                my.is_master = True
                my.is_master_str = 'true'
        user_is_scheduler = False
        if 'scheduling' in my.groups_str:
            user_is_scheduler = True
        if main_obj in [None, '']:
            server = TacticServerStub.get()
            main_obj = server.eval("@SOBJECT(twog/order['code','%s'])" % order_code)[0]
        table = Table()
        table.add_attr('cellspacing', '3')
        table.add_attr('cellpadding', '3')
        table.add_attr('height', '100%')
        table.add_attr('bgcolor', '#e4e6f0')
        table.add_style('border-bottom-right-radius', '10px')
        table.add_style('border-bottom-left-radius', '10px')
        table.add_style('border-top-right-radius', '10px')
        table.add_style('border-top-left-radius', '10px')

        # NEW START
        table.add_row()
        title = table.add_cell(' &nbsp;&nbsp;&nbsp;<i><b>2G Order Builder</b></i> ')
        title.add_attr('nowrap', 'nowrap')
        title.add_style('font-size: 120%;')
        selected_obj = table.add_cell('')
        selected_obj.add_attr('class', 'selected_sobject')
        selected_obj.add_attr('width', '100%')

        associator_launcher = OrderAssociatorLauncherWdg(code=order_code, search_on_load='false')
        associator = table.add_cell(associator_launcher)
        associator.add_attr('align', 'right')

        if main_obj.get('imdb_url') not in [None, '', 'none']:
            lnk = table.add_cell('<a href="%s" target="_blank">Link</a>' % main_obj.get('imdb_url'))
        else:
            lnk = table.add_cell("No Link")
        lnk.add_attr('align', 'left')
        lnk.add_attr('nowrap', 'nowrap')
        table.add_cell('&nbsp;&nbsp;&nbsp;&nbsp;')

        refresher = ButtonSmallNewWdg(title="Refresh", icon=CustomIconWdg.icons.get('REFRESH'))
        refresher.add_behavior(get_refresh_behavior(my.order_sk, my.user))
        refr = table.add_cell(refresher)
        refr.add_attr('align', 'right')

        checker_launcher = OrderCheckerLauncherWdg(order_code=order_code)
        checker = table.add_cell(checker_launcher)
        checker.add_attr('align', 'right')

        if user_is_scheduler:
            global_replacer = ButtonSmallNewWdg(title="Global Replacer", icon=CustomIconWdg.icons.get('DEPENDENCY'))
            global_replacer.add_behavior(get_global_replacer_wdg(my.order_sk, my.user))
            globalr = table.add_cell(global_replacer)
            globalr.add_attr('align', 'right')

            if my.small:
                normal_edit = ButtonSmallNewWdg(title="Normal Edit", icon=CustomIconWdg.icons.get('NORMAL_EDIT'))
                normal_edit.add_behavior(get_quick_edit_behavior(my.order_sk, my.user))
                normr = table.add_cell(normal_edit)
                normr.add_attr('align', 'right')
            else:
                quick_edit = ButtonSmallNewWdg(title="Quick Edit", icon=CustomIconWdg.icons.get('QUICK_EDIT'))
                quick_edit.add_behavior(get_quick_edit_behavior(my.order_sk, my.user))
                quickr = table.add_cell(quick_edit)
                quickr.add_attr('align', 'right')

            clear_cache = ButtonSmallNewWdg(title="Clear Cache", icon=CustomIconWdg.icons.get('TRASH'))
            clear_cache.add_behavior(get_clear_cache_behavior(my.order_sk, my.user))
            clearc = table.add_cell(clear_cache)
            clearc.add_attr('align', 'right')

            source_adder = ButtonSmallNewWdg(title="Create New Source", icon=CustomIconWdg.icons.get('SOURCE_ADD_TAPE'))
            source_adder.add_behavior(get_create_source_behavior(my.order_sk))
            sexa = table.add_cell(source_adder)
            sexa.add_attr('align', 'right')

        eq_exp = ButtonSmallNewWdg(title="Show Equipment", icon=CustomIconWdg.icons.get('ARROW_OUT_EQUIPMENT'))
        eq_exp.add_behavior(get_equipment_expander_behavior(my.order_sk))
        eqb = table.add_cell(eq_exp)
        eqb.add_attr('align', 'right')

        eq_coll = ButtonSmallNewWdg(title="Hide Equipment", icon=CustomIconWdg.icons.get('ARROW_UP_EQUIPMENT'))
        eq_coll.add_behavior(get_equipment_collapser_behavior(my.order_sk))
        eqlb = table.add_cell(eq_coll)
        eqlb.add_attr('align', 'right')

        source_exp = ButtonSmallNewWdg(title="Show Sources", icon=CustomIconWdg.icons.get('ARROW_OUT_SOURCE'))
        source_exp.add_behavior(get_source_expander_behavior(my.order_sk))
        sexb = table.add_cell(source_exp)
        sexb.add_attr('align', 'right')

        source_coll = ButtonSmallNewWdg(title="Hide Sources", icon=CustomIconWdg.icons.get('ARROW_UP_SOURCE'))
        source_coll.add_behavior(get_source_collapser_behavior(my.order_sk))
        sclb = table.add_cell(source_coll)
        sclb.add_attr('align', 'right')

        expander_button = ButtonSmallNewWdg(title="Expand All", icon=CustomIconWdg.icons.get('ARROW_OUT'))
        expander_button.add_behavior(get_expander_behavior(my.order_sk))
        exb = table.add_cell(expander_button)
        exb.add_attr('align', 'right')

        collapser_button = ButtonSmallNewWdg(title="Collapse All", icon=CustomIconWdg.icons.get('ARROW_UP_GREEN'))
        collapser_button.add_behavior(get_collapser_behavior(my.order_sk))
        clb = table.add_cell(collapser_button)
        clb.add_attr('align', 'right')

        space = table.add_cell(' ')
        space.add_attr('width', '100%')

        return table


# JavaScript behavior functions

def get_refresh_behavior(order_sk, login):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try{
    order_sk = '%s';
    user_name = '%s';
    var top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
    groups_str = top_el.getAttribute('groups_str');
    display_mode = top_el.getAttribute('display_mode');
    is_master_str = top_el.getAttribute('is_master_str');
    allowed_titles = top_el.getAttribute('allowed_titles');
    kwargs = {'order_sk': order_sk, 'sk': order_sk, 'groups_str': groups_str, 'user': user_name, 'display_mode': display_mode, 'is_master': is_master_str, 'allowed_titles': allowed_titles}
    class_name = 'order_builder.order_builder.OrderBuilder';
    cover = document.getElementsByClassName('twog_order_builder_cover_' + order_sk)[0];
    cover_cell = cover.getElementsByClassName('cover_cell')[0];
    spt.api.load_panel(cover_cell, class_name, kwargs);
}
catch(err){
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (order_sk, login)}
    return behavior

def get_global_replacer_wdg(order_sk, login):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try{
    order_sk = '%s';
    user_name = '%s';
    var top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
    allowed_titles_str = top_el.getAttribute('allowed_titles');
    kwargs = {'order_sk': order_sk, 'user_name': user_name, 'allowed_titles_str': allowed_titles_str}
    spt.panel.load_popup('Global Replacer', 'order_builder.GlobalReplacerWdg', kwargs);
}
catch(err){
          spt.app_busy.hide();
          spt.alert(spt.exception.handler(err));
          //alert(err);
}
     ''' % (order_sk, login)}
    return behavior


def get_quick_edit_behavior(order_sk, login):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try{
    order_sk = '%s';
    user_name = '%s';
    var top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
    groups_str = top_el.getAttribute('groups_str');
    display_mode = top_el.getAttribute('display_mode');
    is_master_str = top_el.getAttribute('is_master_str');
    allowed_titles = top_el.getAttribute('allowed_titles');
    new_display_mode = '';
    if(display_mode == 'Small'){
        new_display_mode = 'Normal';
    }else{
        new_display_mode = 'Small';
    }
    //alert("DISP MODE = " + display_mode + " NEW = " + new_display_mode);
    kwargs = {'order_sk': order_sk, 'sk': order_sk, 'groups_str': groups_str, 'user': user_name, 'display_mode': new_display_mode, 'is_master': is_master_str, 'allowed_titles': allowed_titles}
    class_name = 'order_builder.order_builder.OrderBuilder';
    cover = document.getElementsByClassName('twog_order_builder_cover_' + order_sk)[0];
    cover_cell = cover.getElementsByClassName('cover_cell')[0];
    spt.api.load_panel(cover_cell, class_name, kwargs);
    //spt.panel.load_popup('Global Replacer', 'order_builder.BuildTools', kwargs);
}
catch(err){
          spt.app_busy.hide();
          spt.alert(spt.exception.handler(err));
          //alert(err);
}
     ''' % (order_sk, login)}
    return behavior


def get_clear_cache_behavior(order_sk, login):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try{
    if(confirm('Do you really want to clear your cache? Data stored about the last deleted and removed projects and work orders will be discarded.')){
        var server = TacticServerStub.get();
        login = '%s';
        order_sk = '%s';
        order_code = order_sk.split('code=')[1];
        proj_transfers = server.eval("@SOBJECT(twog/proj_transfer['login','" + login + "'])");
        for(var r = 0; r < proj_transfers.length; r++){
            server.delete_sobject(proj_transfers[r].__search_key__);
        }
        work_order_transfers = server.eval("@SOBJECT(twog/work_order_transfer['login','" + login + "'])");
        for(var r = 0; r < work_order_transfers.length; r++){
            server.delete_sobject(work_order_transfers[r].__search_key__);
        }
        clone_actions = server.eval("@SOBJECT(twog/action_tracker['login','" + login + "']['action','cloning'])");
        for(var r = 0; r < clone_actions.length; r++){
            server.delete_sobject(clone_actions[r].__search_key__);
        }
        ptasks = server.eval("@SOBJECT(twog/order['code','" + order_code + "'].twog/title.twog/proj.PT:sthpw/task)");
        for(var r = 0; r < ptasks.length; r++){
            server.update(ptasks[r].__search_key__, {'transfer_wo': ''});
        }
        wtasks = server.eval("@SOBJECT(twog/order['code','" + order_code + "'].twog/title.twog/proj.twog/work_order.WT:sthpw/task)");
        for(var r = 0; r < wtasks.length; r++){
            server.update(wtasks[r].__search_key__, {'transfer_wo': ''});
        }
        alert('Cache Cleared');
    }
}
catch(err){
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (login, order_sk)}

    return behavior


def get_create_source_behavior(order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
        try {
            var order_sk = '%s';
            spt.tab.add_new('create_new_source_ob', 'Create New Source', 'order_builder.NewSourceWdg', kwargs);
        }
        catch(err) {
            spt.app_busy.hide();
            spt.alert(spt.exception.handler(err));
        }
     ''' % order_sk}

    return behavior


def get_equipment_expander_behavior(order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    var order_sk = '%s';
    var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
    rows = top_el.getElementsByClassName('EquipmentUsedRowRow');
    for(var r =0; r < rows.length; r++) {
        rows[r].style.display = 'table-row';
    }
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % order_sk}
    return behavior


def get_equipment_collapser_behavior(order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    var order_sk = '%s';
    var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
    rows = top_el.getElementsByClassName('EquipmentUsedRowRow');
    for(var r =0; r < rows.length; r++) {
        rows[r].style.display = 'none';
    }
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % order_sk}

    return behavior


def get_source_expander_behavior(order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    var order_sk = '%s';
    var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
    rows = top_el.getElementsByClassName('sources_row');
    for(var r =0; r < rows.length; r++){
        rows[r].style.display = 'table-row';
    }
    rows = top_el.getElementsByClassName('wo_sources_row');
    for(var r =0; r < rows.length; r++){
        rows[r].style.display = 'table-row';
    }
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % order_sk}

    return behavior


def get_source_collapser_behavior(order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try{
    var order_sk = '%s';
    var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
    rows = top_el.getElementsByClassName('sources_row');
    for(var r =0; r < rows.length; r++){
        rows[r].style.display = 'none';
    }
    rows = top_el.getElementsByClassName('wo_sources_row');
    for(var r =0; r < rows.length; r++){
        rows[r].style.display = 'none';
    }
}
catch(err){
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % order_sk}

    return behavior


def get_expander_behavior(order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try{
    var order_sk = '%s';
    var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
    var trs = top_el.getElementsByTagName('tr');
    for(var r = 0; r < trs.length; r++){
        if(trs[r].style.display == 'none' && trs[r].get('class') != 'closer_row' &&  trs[r].get('class') != 'pipe_row' && (trs[r].get('class') != 'qe_errors_row_' + order_sk)){
            trs[r].style.display = 'table-row';
        }
    }
}
catch(err){
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % order_sk}

    return behavior


def get_collapser_behavior(order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try{
    var order_sk = '%s';
    var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
    var trs = top_el.getElementsByTagName('tr');
    for(var r = 0; r < trs.length; r++){
        if(trs[r].style.display == 'table-row' && trs[r].get('class') != 'closer_row' &&  trs[r].get('class') != 'pipe_row' && (trs[r].get('class') != 'qe_errors_row_' + order_sk)){
            trs[r].style.display = 'none';
        }
    }
}
catch(err){
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % order_sk}

    return behavior
