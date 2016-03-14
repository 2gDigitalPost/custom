from tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import CalendarInputWdg

from pyasm.common import Environment

from pyasm.search import Search
from pyasm.web import Table, DivWdg
from pyasm.widget import SelectWdg

from alternative_elements.customcheckbox import *


class ProjectAdderWdg(BaseRefreshWdg):
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
                            try{
                                   var server = TacticServerStub.get();
                                   order_sk = '%s';
                                   order_code = order_sk.split('code=')[1];
                                   top_el = document.getElementById('manual_proj_adder_top_' + order_sk);
                                   title_code = top_el.getAttribute('title_code');
                                   parent_sk = top_el.getAttribute('parent_sk');
                                   user_name = top_el.getAttribute('user_name');
                                   make_em = [];
                                   comma_names = top_el.getElementById('comma_names').value;
                                   if(comma_names != '' && comma_names != ' ' && comma_names != null){
                                       make_em = comma_names.split(',');
                                   }else{
                                       primary_name = top_el.getElementById('primary_name').value;
                                       from_number = top_el.getElementById('from_number').value;
                                       to_number = top_el.getElementById('to_number').value;
                                       if(isNaN(from_number)){
                                           from_number = -1;
                                       }else{
                                           from_number = Number(from_number);
                                           if(isNaN(to_number)){
                                               to_number = -1;
                                           }else{
                                               to_number = Number(to_number);
                                           }
                                       }
                                       if(from_number == -1){
                                           make_em.push(primary_name);
                                       }else{
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
                                   for(var r = 0; r < dates.length; r++){
                                       dname = dates[r].getAttribute('name');
                                       val = dates[r].value;
                                       if(dname == 'start_date'){
                                           start_date = val;
                                       }else if(dname = 'due_date'){
                                           due_date = val;
                                       }
                                   }
                                   priority = top_el.getElementById('priority').value;
                                   platform = top_el.getElementById('platform').value;
                                   //
                                   title = server.eval("@SOBJECT(twog/title['code','" + title_code + "'])")[0];
                                   order = server.eval("@SOBJECT(twog/order['code','" + order_code + "'])")[0];
                                   client_code = title.client_code
                                   client = server.eval("@SOBJECT(twog/client['code','" + client_code + "'])");
                                   client_name = '';
                                   if(client.length > 0){
                                       client = client[0];
                                       client_name = client.name
                                   }
                                   codes_inorder = [title_code];
                                   //HERE INSERT TASKS AND PROJS
                                   spt.app_busy.show('CREATING PROJECTS');

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
                                       new_proj = server.insert('twog/proj', {'process': make_em[r].trim(), 'title_code': title_code, 'parent_pipe': 'Manually Inserted into ' + title.pipeline_code, 'login': user_name, 'creation_type': 'hackup', 'status': 'Pending', 'order_code': order_code, 'client_code': client_code, 'priority': priority, 'platform': platform, 'client_name': client_name, 'title': title.title, 'episode': title.episode, 'territory': title.territory, 'po_number': order.po_number, 'order_name': order.name, 'start_date': start_date, 'due_date': due_date, 'comes_from': filler, 'goes_to': 'NEEDS_TO_BE_FILLED'})
                                       codes_inorder.push(new_proj.code);
                                       spt.app_busy.show('CREATING ' + new_proj.process);
                                       new_task_data = {'process': new_proj.process, 'context': new_proj.process, 'active': false, 'client_name': client_name, 'title': title.title, 'episode': title.episode, 'territory': title.territory, 'creator_login': user_name, 'lookup_code': new_proj.code, 'search_type': 'twog/title?project=twog', 'search_id': title.id, 'pipeline_code': 'Manually Inserted into ' + title.pipeline_code, 'po_number': order.po_number, 'status': 'Pending', 'title_code': title_code, 'order_code': order_code, 'order_name': order.name, 'client_code': client_code, 'platform': new_proj.platform, 'priority': priority, 'territory': title.territory, 'project_code': 'twog', 'bid_end_date': due_date, 'bid_start_date': start_date};
                                       if(order.classification == 'in_production' || order.classification == 'In Production'){
                                           new_task_data['active'] = true;
                                       }
                                       new_task = server.insert('sthpw/task',new_task_data);
                                       server.update(new_proj.__search_key__, {'task_code': new_task.code});
                                   }
                                   spt.app_busy.show('CREATING CONNECTIONS');
                                   //CONNECT EACH TO THE NEXT AS A HACKUP
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
                              //alert(err);
                    }
        ''' % (my.order_sk)}

        return behavior

    def get_display(my):
        table = Table()

        tbl_id = 'manual_proj_adder_top_%s' % my.order_sk

        table.add_attr("id", tbl_id)
        table.add_attr('search_type', 'twog/proj')
        table.add_attr('order_sk', my.order_sk)
        table.add_attr('parent_sk', my.parent_sk)
        table.add_attr('title_code', my.title_code)
        table.add_attr('user_name', Environment.get_user_name())

        ctbl = Table()
        ctbl.add_row()
        c1 = ctbl.add_cell('Project Names (Comma Delimited)')
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

        platform_search = Search("twog/platform")
        platform_search.add_order_by('name desc')
        platforms = platform_search.get_sobjects()
        plat_sel = SelectWdg("platform")
        plat_sel.add_attr('id', 'platform')
        plat_sel.append_option('--Select--', '')
        for p in platforms:
            plat_sel.append_option(p.get_value('name'), p.get_value('name'))
        ptbl.add_row()
        ptbl.add_cell("Priority: ")
        ptbl.add_cell('<input type="text" id="priority" style="width: 50px;"/>')
        ptbl.add_row()
        ptbl.add_cell('Platform: ')
        ptbl.add_cell(plat_sel)
        proj_search = Search("twog/proj")
        proj_search.add_filter('title_code', my.parent_code)
        proj_search.add_order_by('order_in_pipe')
        projs = proj_search.get_sobjects()
        btbl.add_row()
        p1 = btbl.add_cell('<u>First Proj Comes After</u>')
        p1.add_attr('nowrap', 'nowrap')
        p2 = btbl.add_cell('<u>Last Proj Leads To</u>')
        p2.add_attr('nowrap', 'nowrap')
        fromtbl = Table()
        for p in projs:
            fromtbl.add_row()

            checker = CustomCheckboxWdg(name='from_check', value_field=p.get_value('code'), id=p.get_value('code'),
                                        checked='false', dom_class='from_check', code=p.get_value('code'))

            fromtbl.add_cell(checker)
            fromtbl.add_cell("%s (%s)" % (p.get_value('process'), p.get_value('code')))
        totbl = Table()
        for p in projs:
            totbl.add_row()

            checker = CustomCheckboxWdg(name='to_check', value_field=p.get_value('code'), checked='false',
                                        id=p.get_value('code'), dom_class='to_check', code=p.get_value('code'))

            totbl.add_cell(checker)
            totbl.add_cell("%s (%s)" % (p.get_value('process'), p.get_value('code')))
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
        saction = stbl.add_cell('<input type="button" value="Create Projects"/>')
        saction.add_behavior(my.get_save())
        s2 = stbl.add_cell('&nbsp;')
        s2.add_attr('width', '40%')

        ss = table.add_cell(stbl)
        ss.add_attr('colspan', '2')
        ss.add_attr('align', 'center')

        widget = DivWdg()
        widget.add(table)
        return widget
