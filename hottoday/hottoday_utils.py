"""
A collection of functions that are used in the hot list classes, but don't need to be part of the classes themselves.

Note that for the time being, I'm just copying the functions from their classes and removing the 'self' argument.
These functions could use some serious rewriting. I hope to get to that soon.

Author: Tyler Standridge
"""

import datetime
from tactic_client_lib import TacticServerStub
from pyasm.search import Search


def get_platform_img(platform):
    img_path = ''
    platform_search = Search("twog/platform")
    platform_search.add_filter('name', platform)
    platform_search_object = platform_search.get_sobject()

    if platform_search_object:
        platform_id = platform_search_object.get_id()

        snaps_s = Search("sthpw/snapshot")
        snaps_s.add_filter('search_id', platform_id)
        snaps_s.add_filter('search_type', 'twog/platform?project=twog')
        snaps_s.add_filter('is_current', '1')
        snaps_s.add_filter('version', '0', op='>')
        snaps_s.add_where("\"context\" in ('publish','icon','MISC')")
        snaps_s.add_order_by('timestamp desc')
        snaps = snaps_s.get_sobjects()

        if len(snaps) > 0:
            server = TacticServerStub.get()
            snap = snaps[0]
            img_path = server.get_path_from_snapshot(snap.get_code(), mode="web")

            if img_path:
                img_path = 'http://' + server.get_server_name() + img_path
        return img_path
    else:
        return None


def get_client_img(client_code):
    img_path = ''
    client_search = Search("twog/client")
    client_search.add_filter('code', client_code)
    client_search_object = client_search.get_sobject()

    if client_search_object:
        client_id = client_search_object.get_id()

        snaps_s = Search("sthpw/snapshot")
        snaps_s.add_filter('search_id', client_id)
        snaps_s.add_filter('search_type', 'twog/client?project=twog')
        snaps_s.add_filter('is_current', '1')
        snaps_s.add_filter('version', '0', op='>')
        snaps_s.add_where("\"context\" in ('publish','icon','MISC')")
        snaps_s.add_order_by('timestamp desc')
        snaps = snaps_s.get_sobjects()

        if len(snaps) > 0:
            server = TacticServerStub.get()
            snap = snaps[0]
            img_path = server.get_path_from_snapshot(snap.get_code(), mode="web")

            if img_path:
                img_path = 'http://' + server.get_server_name() + img_path
        return img_path
    else:
        return None


def get_date_status(delivery_datetime):
    """
    Checks the status of a delivery date against today's date.

    If the delivery date is after today's date, return the string 'on_time'
    If the delivery date is today, return the string 'due_today'
    Otherwise, return 'late'

    :param delivery_datetime: A datetime.datetime object
    :return: String ('on_time', 'due_today', 'late')
    """
    todays_date = datetime.date.today()
    delivery_date = delivery_datetime.date()

    if todays_date < delivery_date:
        return 'on_time'
    elif todays_date == delivery_date:
        return 'due_today'
    else:
        return 'late'


# The following functions are Javascript behaviors that the hot list uses

def get_launch_note_behavior(sk, name):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      var sk = '%s';
                      var name = '%s';
                      kwargs =  {'search_key': sk, 'append_process': 'Client Services,Redelivery/Rejection Request,Redelivery/Rejection Completed', 'chronological': true};
                      spt.panel.load_popup('Notes for ' + name, 'tactic.ui.widget.DiscussionWdg', kwargs);
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (sk, name)}
    return behavior


def get_onload():
    return r'''
        mytimer = function(timelen){
            setTimeout('refresh_bigboard()', timelen); // uncomment me
        }
        refresh_bigboard = function(){
            board_els = document.getElementsByClassName('bigboard');
            auto_el = document.getElementById('auto_refresh');
            auto = auto_el.getAttribute('auto');
            scroll_el = document.getElementById('scroll_el');
            scroll = scroll_el.getAttribute('scroll');
            if(auto == 'yes'){
                for(var r = 0; r < 1; r++){
                    spt.app_busy.show("Refreshing...");
                    //alert('reloading scroll = ' + scroll);
                    spt.api.load_panel(board_els[r], 'nighttime_hotlist.BigBoardWdg2',
                        {'auto_refresh': auto, 'scroll': scroll});
                    spt.app_busy.hide();
                }
            }
            //mytimer(120000);
        }
        mytimer(120000);
    '''


def get_scroll_by_row():
    behavior = {'type': 'load', 'cbjs_action': '''
        try{
            hctime = 500;
            timer2 = function(timelen, next_count, up_or_down, element, origtime){
                send_str = 'do_scroll(' + next_count + ', ' + up_or_down + ', ' + timelen + ', ' + origtime + ')';
                if(element != ''){
                    //element.scrollIntoView();
                    if(element.getAttribute('viz') == 'true'){
                        element.setAttribute('viz','false');
                        element.style.display = 'none';
                    }else{
                        element.setAttribute('viz','true');
                        element.style.display = 'table-row';
                    }
                }
                setTimeout(send_str, timelen);
            }
            do_scroll = function(next_count, up_or_down, timelen, origtime){
                buttons = document.getElementsByClassName('auto_buttons')[0];
                scroll_el = buttons.getElementById('scroll_el');
                scroll = scroll_el.getAttribute('scroll');
                if(scroll == 'yes'){
                    element = '';
                    trs = document.getElementsByClassName('trow');
                    trslen = trs.length;
                    preup = up_or_down;
                    if((trslen - 9 < next_count && up_or_down == 1) || (next_count == 1 && up_or_down == -1)){
                        up_or_down = up_or_down * -1;
                    }
                    if(preup == up_or_down){
                        next_count = next_count + up_or_down;
                    }
                    for(var r = 0; r < trslen - 1; r++){
                        if(trs[r].getAttribute('num') == next_count){
                            element = trs[r];
                        }
                    }
                    nexttime = 0;
                    if(next_count == 1 || next_count == trslen - 8){
                        nexttime = origtime * 8;
                    }else{
                        nexttime = origtime;
                    }
                    timer2(nexttime, next_count, up_or_down, element, origtime);
                }
            }
            timer2(hctime, 0, 1, '', hctime);
        }catch(err){
                  spt.app_busy.hide();
                  spt.alert(spt.exception.handler(err));
        }
     '''}
    return behavior


def save_priorities():
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
        function do_proj_prios(title_code, new_priority) {
            //This is for assigning the projects the same priority
            var server = TacticServerStub.get();
            projects = server.eval("@SOBJECT(twog/proj['title_code','" + title_code + "'])");
            for (var w = 0; w < projects.length; w++) {
                wts_expr = "@SOBJECT(twog/work_order['proj_code','" + projects[w].code + "'].WT:sthpw/task['bigboard','True']['status','!=','Completed'])"
                wts = server.eval(wts_expr);
                if (wts.length > 0) {
                    server.update(projects[w].__search_key__, {'priority': new_priority});
                }
            }
        }
        try {
            var server = TacticServerStub.get();
            var buttons_el = spt.api.get_parent(bvr.src_el, '.auto_buttons');
            auto_el = buttons_el.getElementById('auto_refresh');
            auto = auto_el.getAttribute('auto');
            scroll_el = buttons_el.getElementById('scroll_el');
            scroll = scroll_el.getAttribute('scroll');

            var priority_inputs = document.getElementsByClassName('count_order');
            all_dict = {};

            for (var r = 0; r < priority_inputs.length; r++) {
                var val = priority_inputs[r].value;
                var old_val = priority_inputs[r].getAttribute('current_count');
                current_priority = priority_inputs[r].getAttribute('current_priority');
                t_sk = '';
                t_code = '';
                indie_search_key = '';
                row_type = priority_inputs[r].getAttribute('row_type');
                if (row_type == 'title') {
                    t_sk = priority_inputs[r].getAttribute('title_sk');
                    t_code = t_sk.split('code=')[1];
                    ami_ext = priority_inputs[r].getAttribute('external_rejection')
                    if (ami_ext == 'true') {
                        t_sk = priority_inputs[r].getAttribute('ext_sk');
                    }
                } else {
                    t_sk = priority_inputs[r].getAttribute('task_sk');
                    t_code = t_sk.split('code=')[1];
                    indie_search_key = '';
                    indie = server.eval("@SOBJECT(twog/indie_priority['task_code','" + t_code + "']['@ORDER_BY','timestamp desc'])");
                    if (indie.length > 0) {
                        indie_search_key = indie[0].__search_key__;
                    }
                }

                var changed = false;
                if (old_val != val) {
                   changed = true;
                }

                all_dict[old_val] = {
                    'current_count': old_val,
                    'current_priority': current_priority,
                    'sk': t_sk,
                    'row_type': row_type,
                    'changed': changed,
                    'new_count': val,
                    'indie_search_key': indie_search_key,
                    'code': t_code
                };

            }
            for (var r = 1; r < priority_inputs.length + 1; r++) {
                if (all_dict[r]['changed']) {
                    new_count = Number(all_dict[r]['new_count']);
                    row_type = all_dict[r]['row_type'];
                    pre_prio = 0;
                    post_prio = 500;
                    if (new_count != 1) {
                        pre_prio = Number(all_dict[new_count - 1]['current_priority']);
                    }
                    if (new_count != priority_inputs.length + 1) {
                        post_prio = Number(all_dict[new_count + 1]['current_priority']);
                    }
                    new_priority = (pre_prio + post_prio) / 2;
                    if (row_type == 'title') {
                        server.update(all_dict[r]['sk'], {'priority': new_priority});
                    } else {
                        server.update(all_dict[r]['sk'], {'indie_priority': new_priority});
                        server.update(all_dict[r]['indie_search_key'], {'indie_priority': new_priority});
                    }
                }
            }

            // Get the board table by its ID
            var board_table = document.getElementById('bigboard');

            // Refresh the view
            spt.app_busy.show("Refreshing...");
            spt.api.load_panel(board_table, 'hottoday.HotTodayWdg', {'auto_refresh': auto, 'auto_scroll': scroll, 'groups': 'ALL'});
            spt.app_busy.hide();
        }
        catch(err) {
                  spt.app_busy.hide();
                  spt.alert(spt.exception.handler(err));
        }
     '''}
    return behavior


def show_change(ider):
    behavior = {'css_class': 'clickme', 'type': 'change', 'cbjs_action': '''
            try{
                var ider = '%s';
                moi = document.getElementById(ider);
                moi.style.backgroundColor = "#FF0000";
                if(moi.value != moi.getAttribute('current_count')){
                    if(isNaN(moi.value)){
                        moi.value = moi.getAttribute('current_count');
                        moi.style.backgroundColor = "#ffffff";
                    }
                }
        }
        catch(err){
                  spt.app_busy.hide();
                  spt.alert(spt.exception.handler(err));
        }
     ''' % ider}
    return behavior


def set_scroll():
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
        try{
            var buttons_el = spt.api.get_parent(bvr.src_el, '.auto_buttons');
            auto_el = buttons_el.getElementById('auto_refresh');
            auto = auto_el.getAttribute('auto');
            scroll_el = buttons_el.getElementById('scroll_el');
            scroll = scroll_el.getAttribute('scroll');
            //group_el = buttons_el.getElementById('group_select');
            //group = group_el.value;
            if(scroll == 'no'){
                bvr.src_el.innerHTML = '<input type="button" value="Unset Auto-Scroll"/>';
                bvr.src_el.setAttribute('scroll','yes');
                scroll = 'yes';
            }else{
                bvr.src_el.innerHTML = '<input type="button" value="Set Auto-Scroll"/>';
                bvr.src_el.setAttribute('scroll','no');
                scroll = 'no';
            }
            board_els = document.getElementsByClassName('bigboard');
            for(var r = 0; r < 1; r++){
                spt.app_busy.show("Refreshing...");
                //spt.api.load_panel(board_els[r], 'nighttime_hotlist.BigBoardWdg2', {'auto_refresh': auto, 'auto_scroll': scroll, 'groups': group});
                spt.api.load_panel(board_els[r], 'nighttime_hotlist.BigBoardWdg2', {'auto_refresh': auto, 'auto_scroll': scroll, 'groups': 'ALL'});
                spt.app_busy.hide();
            }
        }
        catch(err){
                  spt.app_busy.hide();
                  spt.alert(spt.exception.handler(err));
        }
     '''}
    return behavior


def get_reload():
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
        try{
            var buttons_el = spt.api.get_parent(bvr.src_el, '.auto_buttons');
            auto = bvr.src_el.get('auto');
            scroll_el = buttons_el.getElementById('scroll_el');
            scroll = scroll_el.getAttribute('scroll');
            //group_el = buttons_el.getElementById('group_select');
            //group = group_el.value;
            if(auto == 'no'){
                bvr.src_el.innerHTML = '<input type="button" value="Unset Auto-Refresh"/>';
                bvr.src_el.setAttribute('auto','yes');
                auto = 'yes';
            }else{
                bvr.src_el.innerHTML = '<input type="button" value="Set Auto-Refresh"/>';
                bvr.src_el.setAttribute('auto','no');
                auto = 'no';
            }
            board_els = document.getElementsByClassName('bigboard');
            for(var r = 0; r < 1; r++){
                spt.app_busy.show("Refreshing...");
                //spt.api.load_panel(board_els[r], 'nighttime_hotlist.BigBoardWdg2', {'auto_refresh': auto, 'auto_scroll': scroll, 'groups': group});
                spt.api.load_panel(board_els[r], 'nighttime_hotlist.BigBoardWdg2', {'auto_refresh': auto, 'auto_scroll': scroll, 'groups': 'ALL'});
                spt.app_busy.hide();
            }
        }
        catch(err){
                  spt.app_busy.hide();
                  spt.alert(spt.exception.handler(err));
        }
     '''}
    return behavior


def change_group():
    behavior = {'css_class': 'clickme', 'type': 'change', 'cbjs_action': '''
            try{
            var buttons_el = spt.api.get_parent(bvr.src_el, '.auto_buttons');
            auto = bvr.src_el.get('auto');
            scroll_el = buttons_el.getElementById('scroll_el');
            scroll = scroll_el.getAttribute('scroll');
            //group_el = buttons_el.getElementById('group_select');
            //group = group_el.value;
            group = 'ALL';
            board_els = document.getElementsByClassName('bigboard');
            for(var r = 0; r < 1; r++){
                spt.app_busy.show("Refreshing...");
                spt.api.load_panel(board_els[r], 'nighttime_hotlist.BigBoardWdg2', {'auto_refresh': auto, 'auto_scroll': scroll, 'groups': group});
                spt.app_busy.hide();
            }
        }
        catch(err){
                  spt.app_busy.hide();
                  spt.alert(spt.exception.handler(err));
        }
     '''}
    return behavior


def bring_to_top():
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    body = document.getElementById('hotlist_div');
    body.scrollTop = 0;
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
    '''}
    return behavior


def toggle_groupings():
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
        try {
            prio = bvr.src_el.getAttribute('current_priority');
            state = bvr.src_el.getAttribute('state');
            if(state == 'opened') {
                bvr.src_el.setAttribute('state','closed');
                state = 'closed';
            } else {
                bvr.src_el.setAttribute('state','opened');
                state = 'opened';
            }

            top_el = document.getElementById('title_body');
            rows = top_el.getElementsByClassName('trow');
            for(var r = 0; r < rows.length; r++) {
                if(rows[r].getAttribute('current_priority') == prio) {
                    if(state == 'closed') {
                        //rows[r].setAttribute('viz','false');
                        rows[r].style.display = 'none';
                    } else {
                        //rows[r].setAttribute('viz','true');
                        rows[r].style.display = 'table-row';
                    }
                }
            }


        }
        catch(err){
            spt.app_busy.hide();
            spt.alert(spt.exception.handler(err));
        }
    '''}
    return behavior
