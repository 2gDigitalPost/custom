from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Environment
from pyasm.search import Search
from pyasm.web import Table

from common_tools.full_instructions import FullInstructionsLauncherWdg
from common_tools.common_functions import fix_date
from widget.new_icon_wdg import CustomIconWdg
from widget.button_small_new_wdg import ButtonSmallNewWdg

from title_row import TitleRow
from order_builder_utils import OBScripts, get_upload_behavior

class OrderTable(BaseRefreshWdg):
    ''' This is the top level view of the dynamic order builder part '''

    def init(my):
        my.search_type = 'twog/order'
        my.title = "Order"
        my.sk = ''
        my.sid = ''
        my.code = ''
        my.allowed_titles_str = ''
        my.allowed_titles = []
        my.user = ''
        my.width = '1000px'
        my.height = '300px'
        my.disp_mode = 'Normal'
        my.small = False
        my.groups_str = ''
        my.is_master = False
        my.is_master_str = 'false'

    def get_display(my):
        import common_tools.utils as ctu
        from common_tools.copy_url_button import CopyUrlButton

        my.sk = str(my.kwargs.get('sk'))
        my.sid = str(my.kwargs.get('search_id'))
        allowed_search_titles = ''
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
            my.disp_mode = my.kwargs.get('display_mode')
        if my.disp_mode == 'Small':
            my.small = True
        my.code = my.sk.split('code=')[1]
        if 'allowed_titles' in my.kwargs.keys():
            my.allowed_titles_str = str(my.kwargs.get('allowed_titles'))
            split_allow = my.allowed_titles_str.split('|')
            for sa in split_allow:
                if allowed_search_titles == '':
                    allowed_search_titles = "('%s'" % sa
                else:
                    allowed_search_titles = "%s,'%s'" % (allowed_search_titles, sa)
            if allowed_search_titles != '':
                allowed_search_titles = '%s)' % allowed_search_titles
        if my.allowed_titles_str == '':
            my.allowed_titles_str = 'NOTHING|NOTHING'
        main_search = Search("twog/order")
        main_search.add_filter('code', my.code)
        main_obj = main_search.get_sobject()
        if 'is_master' in my.kwargs.keys():
            my.is_master_str = my.kwargs.get('is_master')
            if my.is_master_str == 'true':
                my.is_master = True
        else:
            if main_obj.get_value('classification') in ['master', 'Master']:
                my.is_master = True
                my.is_master_str = 'true'
        sched_full_name = ''
        if main_obj.get_value('login') not in [None,'']:
            sched_s = Search('sthpw/login')
            sched_s.add_filter('location', 'internal')
            sched_s.add_filter('login', main_obj.get_value('login'))
            sched = sched_s.get_sobject()
            if sched:
                sched_full_name = '%s %s' % (sched.get_value('first_name'), sched.get_value('last_name'))

        sales_full_name = ''
        if main_obj.get_value('sales_rep') not in [None,'']:
            sales_s = Search('sthpw/login')
            sales_s.add_filter('location', 'internal')
            sales_s.add_filter('login', main_obj.get_value('sales_rep'))
            sales = sales_s.get_sobject()
            if sales:
                sales_full_name = '%s %s' % (sales.get_value('first_name'), sales.get_value('last_name'))

        obs = OBScripts(order_sk=my.sk, user=my.user, groups_str=my.groups_str, display_mode=my.disp_mode,
                        is_master=my.is_master_str)
        title_search = Search("twog/title")
        title_search.add_filter('order_code', main_obj.get_value('code'))
        if allowed_search_titles != '':
            title_search.add_where("\"code\" in %s" % allowed_search_titles)
        titles = title_search.get_sobjects()
        table = Table()
        table.add_attr('I_AM', 'ORDER TABLE')
        if user_is_scheduler:
            table.add_attr('SOY', 'ORDER-O TABLE-O')

        table.add_attr('cellpadding', '0')
        table.add_attr('cellspacing', '0')
        table.add_style('border-collapse', 'separate')
        table.add_style('border-spacing', '25px 0px')
        table.add_style('color: #00033a;')
        table.add_style('background-color: #d9edf7;')
        table.add_style('width: 100%;')
        table.add_style('border-bottom-right-radius', '10px')
        table.add_style('border-bottom-left-radius', '10px')
        table.add_style('border-top-right-radius', '10px')
        table.add_style('border-top-left-radius', '10px')
        order_name_row = table.add_row()
        full_o_name = main_obj.get('name')
        if main_obj.get('details') not in [None,'']:
            full_o_name = '%s - %s' % (full_o_name, main_obj.get('details'))
        order_name_cell = table.add_cell('<b><u>Order: %s</u><b>' % full_o_name)
        order_name_cell.add_attr('nowrap','nowrap')
        order_name_cell.add_style('cursor: pointer;')
        order_name_cell.add_behavior(obs.get_panel_change_behavior(my.search_type, my.code, my.sk, my.sk, my.title, '',
                                                                   'builder/refresh_from_save', '', my.sk,
                                                                   main_obj.get_value('name'), user_is_scheduler))
        order_due_cell = table.add_cell("Due: %s" % fix_date(main_obj.get_value('due_date')).split(' ')[0])
        order_due_cell.add_attr('nowrap', 'nowrap')
        long_cell1 = table.add_cell('Scheduler: %s' % sched_full_name)
        long_cell1.add_style('width: 100%')
        order_sales_row = table.add_row()
        order_po_cell = table.add_cell("Code: %s &nbsp; &nbsp; PO Number: %s" % (my.code,
                                                                                 main_obj.get_value('po_number')))
        order_po_cell.add_attr('nowrap', 'nowrap')
        order_sales_cell = table.add_cell('Sales Rep: %s' % sales_full_name)
        order_sales_cell.add_attr('nowrap', 'nowrap')
        bottom_buttons = Table()
        bottom_buttons.add_row()

        order_builder_url = ctu.get_order_builder_url(my.code)
        copy_url_button = CopyUrlButton(title='Copy URL to Clipboard', url=order_builder_url)
        copy_url_cell = bottom_buttons.add_cell(copy_url_button)
        copy_url_cell.add_attr('align', 'right')

        instructions_button = FullInstructionsLauncherWdg(title='View Instructions', search_key=my.sk)
        instructions_cell = bottom_buttons.add_cell(instructions_button)
        instructions_cell.add_attr('align', 'right')

        if user_is_scheduler:
            tcloner = ButtonSmallNewWdg(title="Title Cloner", icon=CustomIconWdg.icons.get('STAR'))
            tcloner.add_behavior(get_launch_title_cloner_behavior(my.sk, main_obj.get_value('name'), my.user))
            dcl = bottom_buttons.add_cell(tcloner)
            dcl.add_attr('align', 'right')

            tchanger = ButtonSmallNewWdg(title="Title Changer", icon=CustomIconWdg.icons.get('CALENDAR'))
            tchanger.add_behavior(get_launch_title_changer_behavior(my.sk, main_obj.get_value('name'), my.user))
            dcal = bottom_buttons.add_cell(tchanger)
            dcal.add_attr('align', 'right')

            tdeletor = ButtonSmallNewWdg(title="Title Deletor", icon=CustomIconWdg.icons.get('TABLE_ROW_DELETE'))
            tdeletor.add_behavior(get_launch_title_deletor_behavior(my.sk, main_obj.get_value('name'), my.user))
            dfilt = bottom_buttons.add_cell(tdeletor)
            dfilt.add_attr('align', 'right')

        tfilter = ButtonSmallNewWdg(title="Filter Titles", icon=CustomIconWdg.icons.get('CONTENTS'))
        tfilter.add_behavior(get_launch_title_filter_behavior(my.sk, main_obj.get_value('name'), my.user))
        filt = bottom_buttons.add_cell(tfilter)
        filt.add_attr('align', 'right')

        upload = ButtonSmallNewWdg(title="Upload", icon=CustomIconWdg.icons.get('PUBLISH'))
        upload.add_behavior(get_upload_behavior(my.sk))
        up = bottom_buttons.add_cell(upload)
        up.add_attr('align', 'right')

        note_adder = ButtonSmallNewWdg(title="Add Note", icon=CustomIconWdg.icons.get('NOTE_ADD'))
        note_adder.add_behavior(obs.get_launch_note_behavior(my.sk, main_obj.get_value('name')))
        nadd = bottom_buttons.add_cell(note_adder)
        nadd.add_attr('align', 'right')
        nadd.add_style('cursor: pointer;')

        if user_is_scheduler:
            title_adder = ButtonSmallNewWdg(title="Add Titles", icon=CustomIconWdg.icons.get('INSERT_MULTI'))
            title_adder.add_behavior(get_title_add_behavior(my.sk, my.sid, main_obj.get_value('client_code'),
                                                            main_obj.get_value('name')))
            tadd = bottom_buttons.add_cell(title_adder)
            tadd.add_attr('align', 'right')
            tadd.add_style('cursor: pointer;')

        long_cell2 = table.add_cell(bottom_buttons)
        long_cell2.add_attr('align', 'right')
        long_cell2.add_attr('valign', 'bottom')
        long_cell2.add_style('width: 100%')
        bottom = Table()
        bottom.add_attr('width', '100%')
        bottom.add_attr('cellpadding', '0')
        bottom.add_attr('cellspacing', '0')
        for title in titles:
            title_sk = title.get_search_key()
            title_row = bottom.add_row()
            title_row.add_attr('width', '100%')
            title_row.add_attr('class', 'row_%s' % title_sk)
            title_obj = TitleRow(sk=title_sk, parent_sk=my.sk, parent_sid=my.sid, groups_str=my.groups_str,
                                 user=my.user, display_mode=my.disp_mode, is_master=my.is_master_str, main_obj=title)
            content_cell = bottom.add_cell(title_obj)
            content_cell.add_attr('width', '100%')
            content_cell.add_attr('sk', title_sk)
            content_cell.add_attr('order_sk', my.sk)
            content_cell.add_attr('parent_sk', my.sk)
            content_cell.add_attr('parent_sid', my.sid)
            content_cell.add_attr('call_me', title.get_value('title'))
            content_cell.add_attr('episode', title.get_value('episode'))
            content_cell.add_attr('my_class', 'TitleRow')
            content_cell.add_attr('client_code', title.get_value('client_code'))
            content_cell.add_attr('class', 'cell_%s' % title_sk)
        tab2ret = Table()
        tab2ret.add_attr('width', '100%')
        tab2ret.add_row()
        tab2ret.add_cell(table)
        tab2ret.add_row()
        bot = tab2ret.add_cell(bottom)
        bot.add_style('padding-left: 40px;')

        return tab2ret


def get_launch_title_cloner_behavior(sk, name, user_name):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    var sk = '%s';
    var name = '%s';
    var user = '%s';

    kwargs = {
        'sk': sk,
        'code': sk.split('code=')[1],
        'user': user
    };

    spt.panel.load_popup('Clone Selected Titles to New Order...', 'order_builder.TitleCloneSelectorWdg', kwargs);
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (sk, name, user_name)}
    return behavior


def get_launch_title_changer_behavior(sk, name, user_name):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    var sk = '%s';
    var name = '%s';
    var user = '%s';

    kwargs = {
        'sk': sk,
        'code': sk.split('code=')[1],
        'user': user
    };

    spt.panel.load_popup('Change Values on Titles...', 'order_builder.TitleDuePrioBBWdg', kwargs);
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (sk, name, user_name)}
    return behavior


def get_launch_title_deletor_behavior(sk, name, user_name):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    var sk = '%s';
    var name = '%s';
    var user = '%s';

    var top_el = document.getElementsByClassName('twog_order_builder_' + sk)[0];
    allowed_titles = top_el.getAttribute('allowed_titles');

    kwargs = {
        'sk': sk,
        'code': sk.split('code=')[1],
        'allowed_titles_str': allowed_titles,
        'user': user
    };

    spt.panel.load_popup('Delete Titles in ' + name, 'order_builder.TitleDeletorWdg', kwargs);
}
catch(err){
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (sk, name, user_name)}
    return behavior


def get_launch_title_filter_behavior(sk, name, user_name):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    var sk = '%s';
    var name = '%s';
    var user = '%s';

    kwargs = {
        'sk': sk,
        'code': sk.split('code=')[1],
        'user': user
    };

    spt.panel.load_popup('Select Titles for ' + name, 'order_builder.TitleSelectorWdg', kwargs);
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (sk, name, user_name)}
    return behavior


def get_title_add_behavior(order_sk, order_sid, client_code, work_order_name): # SIDDED
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    var order_sk = '%s';
    var order_sid = '%s';
    var client_code = '%s';
    var work_order_name = '%s';
    spt.panel.load_popup('Add Titles to ' + work_order_name, 'order_builder.TitleAdderWdg', {'order_sk': order_sk, 'client_code': client_code, 'order_sid': order_sid, 'order_sk': order_sk});
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (order_sk, order_sid, client_code, work_order_name)}
    return behavior
