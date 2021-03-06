from tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import CalendarInputWdg

from pyasm.common import Environment

from pyasm.search import Search
from pyasm.web import Table, DivWdg
from pyasm.widget import SelectWdg

from alternative_elements.customcheckbox import *


class WorkOrderAdderWdg(BaseRefreshWdg):
    def init(my):
        my.server = TacticServerStub.get()
        my.order_sk = str(my.kwargs.get('order_sk'))
        my.parent_sk = my.kwargs.get('parent_sk')
        my.parent_code = my.parent_sk.split('code=')[1]

        if 'TITLE' in my.parent_code:
            my.title_code = my.parent_code
        else:
            my.title_code = my.server.eval("@GET(twog/proj['code','%s'].title_code)" % my.parent_code)[0]

    def get_save(my):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
function encode_utf8( s )
{
    return unescape( encodeURIComponent( s ) );
}

try{
    var server = TacticServerStub.get();
    order_sk = '%s';
    order_code = order_sk.split('code=')[1];
    top_el = document.getElementById('manual_wo_adder_top_' + order_sk);
    title_code = top_el.getAttribute('title_code');
    parent_sk = top_el.getAttribute('parent_sk');
    proj_code = parent_sk.split('code=')[1];
    user_name = top_el.getAttribute('user_name');
    make_em = [];
    comma_names = top_el.getElementById('comma_names').value;
    if(comma_names != '' && comma_names != ' ' && comma_names != null) {
        make_em = comma_names.split(',');
    } else {
        primary_name = top_el.getElementById('primary_name').value;
        from_number = top_el.getElementById('from_number').value;
        to_number = top_el.getElementById('to_number').value;
        if(isNaN(from_number)){
            from_number = -1;
        } else {
            from_number = Number(from_number);
            if(isNaN(to_number)){
                to_number = -1;
            } else {
                to_number = Number(to_number);
            }
        }
        if(from_number == -1){
            make_em.push(primary_name);
        } else {
            if(to_number == -1){
                make_em.push(primary_name + ' ' + from_number);
            }else{
                for(var r = from_number; r < to_number + 1; r++){
                    make_em.push(primary_name + ' ' + r);
                }
            }
        }
    }
    dates = top_el.getElementsByClassName('spt_calendar_input');
    start_date = ''
    due_date = '';
    for(var r = 0; r < dates.length; r++) {
        dname = dates[r].getAttribute('name');
        val = dates[r].value;
        if(dname == 'start_date'){
        start_date = val;
        } else if(dname = 'due_date') {
            due_date = val;
        }
    }

    instructions = top_el.getElementById('instructions').value;
    instructions = encode_utf8(instructions);
    assigned_login_group = top_el.getElementById('assigned_login_group').value;
    assigned = top_el.getElementById('assigned').value;
    title_id_num = top_el.getElementById('title_id_num').value;
    estimated_work_hours = top_el.getElementById('estimated_work_hours').value;
    proj = server.eval("@SOBJECT(twog/proj['code','" + proj_code + "'])")[0];
    title = server.eval("@SOBJECT(twog/title['code','" + title_code + "'])")[0];
    order = server.eval("@SOBJECT(twog/order['code','" + order_code + "'])")[0];
    client_code = title.client_code
    client = server.eval("@SOBJECT(twog/client['code','" + client_code + "'])");
    client_name = '';
    client_hold = 'no problems';
    if(client.length > 0){
       client = client[0];
       client_name = client.name
       client_billing_status = client.billing_status;
       if(client_billing_status.indexOf('Do Not Book') != -1){
           client_hold = 'nobook';
       }else if(client_billing_status.indexOf('Do Not Ship') != -1){
           client_hold = 'noship';
       }
    }
    codes_inorder = [proj_code];

    spt.app_busy.show('CREATING WORK ORDERS');
    nada_before = true;
    from_els = top_el.getElementsByClassName('from_check');
    for(var r = 0; r < from_els.length; r++){
       if(from_els[r].getAttribute('checked') == 'true'){
           nada_before = false;
       }
    }
    for(var r = 0; r < make_em.length; r++){
       filler = 'NEEDS_TO_BE_FILLED'
       if(r == 0 && nada_before){
           filler = ''
       }
       new_wo = server.insert('twog/work_order', {'process': make_em[r].trim(), 'work_group': assigned_login_group, 'instructions': instructions, 'estimated_work_hours': estimated_work_hours, 'proj_code': proj_code, 'parent_pipe': 'Manually Inserted into ' + proj.pipeline_code, 'login': user_name, 'creation_type': 'hackup', 'title_code': title.code, 'order_code': order_code, 'client_code': client_code, 'client_name': client_name, 'assigned': assigned, 'platform': proj.platform, 'title_id_number': title_id_num, 'territory': title.territory, 'priority': proj.priority, 'title': title.title, 'episode': title.episode, 'due_date': due_date, 'po_number': order.po_number, 'order_name': order.name, 'comes_from': filler, 'goes_to': 'NEEDS_TO_BE_FILLED'});
       spt.app_busy.show('CREATING ' + new_wo.process);
       codes_inorder.push(new_wo.code);
       new_task_data = {'process': new_wo.process, 'context': new_wo.process, 'assigned_login_group': assigned_login_group, 'assigned': assigned, 'active': false, 'client_name': client_name, 'title': title.title, 'episode': title.episode, 'territory': title.territory, 'creator_login': user_name, 'lookup_code': new_wo.code, 'search_type': 'twog/proj?project=twog', 'search_id': proj.id, 'pipeline_code': 'Manually Inserted into ' + proj.pipeline_code, 'po_number': order.po_number, 'status': 'Pending', 'title_code': title.code, 'order_code': order_code, 'order_name': order.name, 'client_code': client_code, 'client_hold': client_hold, 'platform': proj.platform, 'priority': proj.priority, 'project_code': 'twog', 'bid_end_date': due_date, 'bid_start_date': start_date};
       if(order.classification == 'in_production' || order.classification == 'In Production'){
           new_task_data['active'] = true;
       }
       new_task = server.insert('sthpw/task',new_task_data);
       server.update(new_wo.__search_key__, {'task_code': new_task.code});
    }
    //CONNECT EACH TO THE NEXT AS A HACKUP
    spt.app_busy.show('CREATING CONNECTIONS');
    for(var r = 0; r < codes_inorder.length - 1; r++){
       server.insert('twog/hackpipe_out', {'lookup_code': codes_inorder[r], 'out_to': codes_inorder[r + 1]})
    }
    //DO FINAL HACKUP CONNECTIONS HERE WITH THE FIRST PROJ INSERTED CONNECTING TO FROMS, LAST PROJ CONNECTING TO TOS
    from_els = top_el.getElementsByClassName('from_check');
    for(var r = 0; r < from_els.length; r++){
       if(from_els[r].getAttribute('checked') == 'true'){
           server.insert('twog/hackpipe_out', {'lookup_code': from_els[r].getAttribute('id'), 'out_to': codes_inorder[1]})
       }
    }
    to_els = top_el.getElementsByClassName('to_check');
    for(var r = 0; r < to_els.length; r++){
       if(to_els[r].getAttribute('checked') == 'true'){
           server.insert('twog/hackpipe_out', {'out_to': to_els[r].getAttribute('id'), 'lookup_code': codes_inorder[codes_inorder.length - 1]})
       }
    }
    last_inserted = codes_inorder[codes_inorder.length - 1];
    if(last_inserted.indexOf('PROJ') != -1){
       server.insert('twog/simplify_pipe', {'proj_code': last_inserted});
    }else{
       server.insert('twog/simplify_pipe', {'work_order_code': last_inserted});
    }

    //AT THE END HERE, WE WANT TO ADD EQUIPMENT TO ALL INSERTED WOS

    var big_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
    display_mode = big_el.getAttribute('display_mode');
    user = big_el.getAttribute('user');
    groups_str = big_el.get('groups_str');
    allowed_titles = big_el.getAttribute('allowed_titles');
    parent_el = big_el.getElementsByClassName('cell_' + parent_sk)[0];
    found_parent_sk = parent_el.get('parent_sk');
    found_parent_sid = parent_el.get('parent_sid');
    send_data = {sk: parent_sk, parent_sid: found_parent_sid, parent_sk: found_parent_sk, order_sk: order_sk, user: user, groups_str: groups_str, allowed_titles: allowed_titles, display_mode: display_mode};
    parent_pyclass = '';
    if(parent_sk.indexOf('twog/proj') != -1){
       parent_pyclass = 'ProjRow'
    }else if(parent_sk.indexOf('twog/title') != -1){
       parent_pyclass = 'TitleRow'
    }
    spt.api.load_panel(parent_el, 'order_builder.' + parent_pyclass, send_data);
    spt.popup.close(spt.popup.get_popup(bvr.src_el));
    spt.app_busy.hide();
}
catch(err){
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
         ''' % my.order_sk}

        return behavior

    def get_display(my):
        table = Table()
        tbl_id = 'manual_wo_adder_top_%s' % my.order_sk

        table.add_attr("id", tbl_id)
        table.add_attr('search_type', 'twog/work_order')
        table.add_attr('order_sk', my.order_sk)
        table.add_attr('parent_sk', my.parent_sk)
        table.add_attr('title_code', my.title_code)
        table.add_attr('user_name', Environment.get_user_name())

        ctbl = Table()
        ctbl.add_row()
        c1 = ctbl.add_cell('Work Order Names (Comma Delimited)')
        c1.add_attr('nowrap', 'nowrap')
        ctbl.add_row()
        ctbl.add_cell('<textarea cols="100" rows="5" id="comma_names" order_sk="%s"></textarea>' % my.order_sk)

        table.add_row()
        table.add_cell(ctbl)
        table.add_row()
        mid = table.add_cell('-- OR --')
        mid.add_attr('align', 'center')

        ntbl = Table()
        ntbl.add_row()
        ntbl.add_cell('Name: ')
        ntbl.add_cell('<input type="text" id="primary_name" style="width: 200px;"/>')
        n1 = ntbl.add_cell(' &nbsp;From Number: ')
        n1.add_attr('nowrap', 'nowrap')
        ntbl.add_cell('<input type="text" id="from_number" style="width: 50px;"/>')
        n2 = ntbl.add_cell(' &nbsp;To Number: ')
        n2.add_attr('nowrap', 'nowrap')
        ntbl.add_cell('<input type="text" id="to_number" style="width: 50px;"/>')

        table.add_row()
        table.add_cell(ntbl)

        ptbl = Table()

        start_date = CalendarInputWdg('start_date')
        start_date.set_option('show_time', 'true')
        start_date.set_option('show_activator', 'true')
        start_date.set_option('display_format', 'MM/DD/YYYY HH:MM')
        start_date.set_option('time_input_default', '5:00 PM')
        ptbl.add_row()
        ptbl.add_cell("Start Date: ")
        ptbl.add_cell(start_date)

        due_date = CalendarInputWdg('due_date')
        due_date.set_option('show_time', 'true')
        due_date.set_option('show_activator', 'true')
        due_date.set_option('display_format', 'MM/DD/YYYY HH:MM')
        due_date.set_option('time_input_default', '5:00 PM')
        ptbl.add_row()
        ptbl.add_cell("Due Date: ")
        ptbl.add_cell(due_date)

        btbl = Table()
        etbl = Table()

        g_search = Search("sthpw/login_group")
        g_search.add_where("\"login_group\" not in ('user','client')")
        g_search.add_order_by('login_group')
        groups = g_search.get_sobjects()
        group_sel = SelectWdg('assigned_login_group')
        group_sel.add_attr('id', 'assigned_login_group')
        group_sel.append_option('--Select--', '')
        for group in groups:
            group_sel.append_option(group.get_value('login_group'), group.get_value('login_group'))
        user_search = Search("sthpw/login")
        user_search.add_filter('location', 'internal')
        user_search.add_filter('license_type', 'user')
        user_search.add_order_by('login')
        users = user_search.get_sobjects()
        user_sel = SelectWdg("assigned")
        user_sel.add_attr('id', 'assigned')
        user_sel.append_option('--Select--', '')
        for u in users:
            user_sel.append_option(u.get_value('login'), u.get_value('login'))
        ptbl.add_row()
        p1 = ptbl.add_cell('Work Group: ')
        p1.add_attr('nowrap', 'nowrap')
        ptbl.add_cell(group_sel)
        ptbl.add_row()
        ptbl.add_cell('Assigned: ')
        ptbl.add_cell(user_sel)
        ptbl.add_row()
        p2 = ptbl.add_cell('Title Id Number: ')
        p2.add_attr('nowrap', 'nowrap')
        ptbl.add_cell('<input type="text" id="title_id_num" style="width: 200px;"/>')
        ptbl.add_row()
        p3 = ptbl.add_cell('Estimated Work Hours: ')
        p3.add_attr('nowrap', 'nowrap')
        ptbl.add_cell('<input type="text" id="estimated_work_hours" style="width: 50px;"/>')
        ptbl.add_row()
        p4 = ptbl.add_cell('Instructions: ')
        p4.add_attr('valign', 'top')
        ptbl.add_cell('<textarea cols="100" rows="20" id="instructions"></textarea>')
        wo_search = Search("twog/work_order")
        wo_search.add_filter('proj_code', my.parent_code)
        wo_search.add_order_by('order_in_pipe')
        wos = wo_search.get_sobjects()

        btbl.add_row()
        p5 = btbl.add_cell('<u>First WO Comes After</u>')
        p5.add_attr('nowrap', 'nowrap')
        p6 = btbl.add_cell('<u>Last WO Leads To</u>')
        p6.add_attr('nowrap', 'nowrap')
        fromtbl = Table()
        for p in wos:
            fromtbl.add_row()

            checker = CustomCheckboxWdg(name='from_check', value_field=p.get_value('code'), id=p.get_value('code'),
                                        checked='false', dom_class='from_check', code=p.get_value('code'))

            fromtbl.add_cell(checker)
            f1 = fromtbl.add_cell("%s (%s)" % (p.get_value('process'), p.get_value('code')))
            f1.add_attr('nowrap', 'nowrap')
        totbl = Table()
        for p in wos:
            totbl.add_row()

            checker = CustomCheckboxWdg(name='to_check', value_field=p.get_value('code'), checked='false',
                                        id=p.get_value('code'), dom_class='to_check', code=p.get_value('code'))

            totbl.add_cell(checker)
            t1 = totbl.add_cell("%s (%s)" % (p.get_value('process'), p.get_value('code')))
            t1.add_attr('nowrap', 'nowrap')
        btbl.add_row()
        btbl.add_cell(fromtbl)
        btbl.add_cell(totbl)

        table.add_row()
        table.add_cell(ptbl)
        table.add_row()
        table.add_cell(btbl)
        table.add_row()
        table.add_cell(etbl)
        table.add_row()

        stbl = Table()
        stbl.add_row()
        s1 = stbl.add_cell('&nbsp;')
        s1.add_attr('width', '40%')
        saction = stbl.add_cell('<input type="button" value="Create Work Orders"/>')
        saction.add_behavior(my.get_save())
        s2 = stbl.add_cell('&nbsp;')
        s2.add_attr('width', '40%')

        ss = table.add_cell(stbl)
        ss.add_attr('colspan', '2')
        ss.add_attr('align', 'center')

        widget = DivWdg()
        widget.add(table)
        return widget

