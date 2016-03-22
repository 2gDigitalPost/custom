"""
A collection of functions that are used in the hot list classes, but don't need to be part of the classes themselves.

Note that for the time being, I'm just copying the functions from their classes and removing the 'self' argument.
These functions could use some serious rewriting. I hope to get to that soon.

Author: Tyler Standridge
"""

import datetime
from tactic_client_lib import TacticServerStub
from pyasm.prod.biz import ProdSetting
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


def show_platform_connection():
    """
    A short convenience function to check Tactic's Project Settings for a value called
    show_platform_connection_on_hot_today, which tells the hot list whether or not to display Client-Platform
    connections as part of Edel's tasks.

    show_platform_connection_on_hot_today should be a string value set to either 'True' or 'False' (sadly Tactic
    does not support Boolean values for ProdSettings)

    :return: Boolean
    """

    # Cast the value to str, just in case it returns None
    show_platform_connection_string = str(ProdSetting.get_value_by_key('show_platform_connection_on_hot_today'))

    if show_platform_connection_string.lower() == 'true':
        return True
    else:
        return False


# The following functions are Javascript behaviors that the hot list uses

def get_launch_note_behavior_for_hotlist(sk, name):
    """
    Get the note widget for the specific title. Function is similar to get_launch_note_behavior in order_builder module,
    but there are some slight differences (hence the name change).

    :param sk: The title's search key
    :param name: The title's name
    :return: Javascript behavior
    """
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
        }
     ''' % (sk, name)}
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

            var priority_inputs = document.getElementsByClassName('count_order');
            var all_dict = {};

            for (var r = 0; r < priority_inputs.length; r++) {
                var val = priority_inputs[r].value;
                var old_val = priority_inputs[r].getAttribute('current_count');
                var current_priority = priority_inputs[r].getAttribute('current_priority');
                var title_search_key = '';
                var title_code = '';
                var indie_search_key = '';
                var row_type = priority_inputs[r].getAttribute('row_type');
                if (row_type == 'title') {
                    title_search_key = priority_inputs[r].getAttribute('title_sk');
                    title_code = title_search_key.split('code=')[1];

                    var ami_ext = priority_inputs[r].getAttribute('external_rejection')
                    if (ami_ext == 'true') {
                        title_search_key = priority_inputs[r].getAttribute('ext_sk');
                    }
                } else {
                    title_search_key = priority_inputs[r].getAttribute('task_sk');
                    title_code = title_search_key.split('code=')[1];

                    var indie = server.eval("@SOBJECT(twog/indie_priority['task_code','" + title_code + "']['@ORDER_BY','timestamp desc'])");
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
                    'search_key': title_search_key,
                    'row_type': row_type,
                    'changed': changed,
                    'new_count': val,
                    'indie_search_key': indie_search_key,
                    'code': title_code
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
                        server.update(all_dict[r]['search_key'], {'priority': new_priority});
                    } else {
                        server.update(all_dict[r]['search_key'], {'indie_priority': new_priority});
                        server.update(all_dict[r]['indie_search_key'], {'indie_priority': new_priority});
                    }
                }
            }

            // Get the board table by its ID
            var board_table = document.getElementById('hotlist_div');

            // Refresh the view
            spt.app_busy.show("Refreshing...");
            spt.api.load_panel(board_table, 'hottoday.HotTodayWdg');
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
        try {
            var ider = '%s';
            moi = document.getElementById(ider);
            moi.style.backgroundColor = "#FF0000";
            if (moi.value != moi.getAttribute('current_count')) {
                if (isNaN(moi.value)) {
                    moi.value = moi.getAttribute('current_count');
                    moi.style.backgroundColor = "#ffffff";
                }
            }
        }
        catch(err) {
            spt.app_busy.hide();
            spt.alert(spt.exception.handler(err));
        }
     ''' % ider}
    return behavior


def bring_to_top():
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
        try {
            body = document.getElementById('hotlist-body');
            body.scrollTop = 0;
        }
        catch(err) {
            spt.app_busy.hide();
            spt.alert(spt.exception.handler(err));
        }
            '''
                }
    return behavior


def get_scrollbar_width():
    return {'type': 'load', 'cbjs_action':
            '''
function getScrollbarWidth() {
    var outer = document.createElement("div");
    outer.style.visibility = "hidden";
    outer.style.width = "100px";
    document.body.appendChild(outer);

    var widthNoScroll = outer.offsetWidth;
    // force scrollbars
    outer.style.overflow = "scroll";

    // add innerdiv
    var inner = document.createElement("div");
    inner.style.width = "100%";
    outer.appendChild(inner);

    var widthWithScroll = inner.offsetWidth;

    // remove divs
    outer.parentNode.removeChild(outer);

    return widthNoScroll - widthWithScroll;
}

var thead = document.getElementById('thead-section');
thead.style.padding = "0px " + getScrollbarWidth() + "px 0px 0px";
            '''
            }


def open_client_platform_connection_tab():
    """
    Open the Client Platform Connection tab

    :return: Javascript behavior
    """
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try{
    var class_name = 'tactic.ui.panel.ViewPanelWdg';
    var kwargs = {
        search_type: 'twog/client_platform',
        view: 'client_platform_hl',
    }

    spt.tab.add_new('client_platform', 'Client Platform Connections', class_name, kwargs);
}
catch(err){
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
    '''
                }
    return behavior