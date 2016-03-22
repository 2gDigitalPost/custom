from tactic.ui.common import BaseTableElementWdg

from pyasm.search import Search
from pyasm.web import Table, DivWdg
from pyasm.widget import SelectWdg

from alternative_elements.customcheckbox import CustomCheckboxWdg


class TitleCloneSelectorWdg(BaseTableElementWdg):
    # This allows the uset to select titles to clone and attach to new orders or existing orders
    # Will copy everything (minus unique stuff) from one title and create another exactly like it
    def init(my):
        nothing = 'true'

    def get_clone_here(my, order_code):
        # This just makes it so that the titles can easily be cloned to the same order the user is in currently
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                            order_code = '%s';
                            var top_el = spt.api.get_parent(bvr.src_el, '.clone_titles_selector');
                            order_el = top_el.getElementById('clone_order_name');
                            order_el.value = order_code;
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                          //alert(err);
                }
        ''' % order_code}
        return behavior

    def get_display(my):
        user_name = my.kwargs.get('user')
        code = my.kwargs.get('code')
        sk = my.kwargs.get('sk')

        t_search = Search("twog/title")
        t_search.add_filter('order_code',code)
        titles = t_search.get_sobjects()
        widget = DivWdg()
        table = Table()
        table.add_attr('class','clone_titles_selector')
        # Select all or none
        toggle_behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                        try{
                            var checked_img = '<img src="/context/icons/custom/custom_checked.png"/>'
                            var not_checked_img = '<img src="/context/icons/custom/custom_unchecked.png"/>'
                            var top_el = spt.api.get_parent(bvr.src_el, '.clone_titles_selector');
                            inputs = top_el.getElementsByClassName('title_selector');
                            var curr_val = bvr.src_el.getAttribute('checked');
                            image = '';
                            if(curr_val == 'false'){
                                curr_val = false;
                                image = not_checked_img;
                            }else if(curr_val == 'true'){
                                curr_val = true;
                                image = checked_img;
                            }
                            for(var r = 0; r < inputs.length; r++){
                                inputs[r].setAttribute('checked',curr_val);
                                inputs[r].innerHTML = image;
                            }
                }
                catch(err){
                          spt.app_busy.hide();
                          spt.alert(spt.exception.handler(err));
                }
        '''}
        # Here need textbox for either an order code to clone to, or if the order code is invalid then create a new order with what is in the textbox as its name
        table2 = Table()
        table2.add_row()
        uto = table2.add_cell('<input type="button" value="Clone to Same Order"/>')
        uto.add_behavior(my.get_clone_here(code))
        table2.add_row()
        # User can enter a new name, which will create a new order with that name and place the clones inside
        # Or user can provide an exiting order code, so the cloned titles will go into that one
        t22 = table2.add_cell('Order Code or New Name:')
        t22.add_attr('nowrap','nowrap')
        namer = table2.add_cell('<input type="text" id="clone_order_name"/>')
        charge_sel = SelectWdg("charge_sel")
        charge_sel.add_style('width: 120px;')
        charge_sel.add_attr('id','charge_sel')
        charges = ['New','Redo','Redo - No Charge']
        # Allow the user to tell us whether this is a normal order, a redo, or a redo with no charge
        for ch in charges:
            charge_sel.append_option(ch,ch)
        table2.add_cell(' Type: ')
        table2.add_cell(charge_sel)
        table2.add_cell('Count: ')
        table2.add_cell('<input type="text" value="1" id="clone_order_count"/>')
        yn = SelectWdg('duplicate_order_vals')
        yn.add_style('width: 100px;')
        yn.append_option('No','No')
        yn.append_option('Yes','Yes')
        tac = table2.add_cell('Duplicate Order Values? ')
        tac.add_attr('nowrap','nowrap')
        table2.add_cell(yn)
        table.add_row()
        ncell = table.add_cell(table2)
        t2b = Table()
        t2b.add_attr('id','t2b')
        # Put the toggler in if there are more than 1 titles
        if len(titles) > 1:
            t2b.add_row()
            toggler = CustomCheckboxWdg(name='chk_clone_toggler',additional_js=toggle_behavior,value_field='toggler',id='selection_toggler',checked='false')

            t2b.add_row()
            t2b.add_cell(toggler)
            t2b.add_cell('<b><- Select/Deselect ALL</b>')
        table.add_row()
        table.add_cell(t2b)
        t3b = Table()
        t3b.add_attr('id','t3b')
        # Display list of titles to choose from
        for title in titles:
            t3b.add_row()
            t3b.add_row()

            tname = title.get_value('title')
            if title.get_value('episode') not in [None,'']:
                tname = '%s: %s' % (tname, title.get_value('episode'))
            checkbox = CustomCheckboxWdg(name='clone_title_%s' % title.get_code(),value_field=title.get_code(),checked='false',text=tname,text_spot='right',text_align='left',nowrap='nowrap',dom_class='title_selector')

            ck = t3b.add_cell(checkbox)

            cter = t3b.add_cell(' --- Count: ')
            # This is how many clones you want to add of each title
            inser = t3b.add_cell('<input type="text" value="1" id="clone_count_%s" style="width: 40px;"/>' % title.get_code())
        table.add_row()
        table.add_cell(t3b)

        if len(titles) < 1:
            table.add_row()
            table.add_cell('There are no titles in this Order')

        table.add_row()
        go_butt = ''
        if len(titles) > 0:
            go_butt = table.add_cell('<input type="button" class="clone_titles" value="Clone"/>')
            go_butt.add_attr('sk',sk)
            go_butt.add_attr('search_type','twog/order')
            go_butt.add_attr('user',user_name)
            behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
        try{
          var my_sk = '%s';
          var my_user = '%s';
          var my_code = my_sk.split('code=')[1];
          if(confirm("Do You Really Want To Clone These Titles?")){
              var server = TacticServerStub.get();
              current_order = server.eval("@SOBJECT(twog/order['code','" + my_code + "'])")[0];
              var top_el = spt.api.get_parent(bvr.src_el, '.clone_titles_selector');
              oname_input = top_el.getElementById('clone_order_name');
              oname = oname_input.value;
              charge_type_el = top_el.getElementById('charge_sel');
              charge_type = charge_type_el.value;
              redo = false;
              no_charge = false;
              if(charge_type.indexOf('Redo') != -1){
                  redo = true;
                  if(charge_type.indexOf('No Charge') != -1){
                      no_charge = true;
                  }
              }
              clone_order_count = top_el.getElementById('clone_order_count').value;
              if(isNaN(clone_order_count)){
                  alert("'" + clone_order_count + "' is not a number. Proceeding as if you entered '1' for the number of orders to create.");
                  clone_order_count = 1;
              }else{
                  clone_order_count = Number(clone_order_count);
              }
              proceed = true;
              clone_type = '';
              that_order = null;
              new_order = false;
              new_order_codes = '';
              duplicate = false;
              if(oname == '' || oname == null){
                  //Just an alert to remind them they have to tell us where the title clones should go
                  alert("You must enter an existing order code or a new order name to put the cloned titles in");
                  proceed = false;
              //}else if(oname.indexOf('ORDER') != -1){
              }else if(/^ORDER([0-9]{5,})$/.test(oname)){
                  //If "ORDER" is in the name, assume that it is actually an order code
                  if(clone_order_count != 1){
                      alert("You have indicated that you want these clones to go into " + clone_order_count + " new orders. However, we can't do that if you are specifying an order as well (" + oname + "). Please fix this and then try again.");
                      proceed = false;
                  }
                  that_order = server.eval("@SOBJECT(twog/order['code','" + oname + "'])");
                  if(that_order.length == 1 && proceed){
                      that_order = that_order[0];
                      new_order_codes = that_order.code;
                      proceed = true;
                      clone_type = that_order.name + ' (' + that_order.code + ')';
                      alert("Cloning the selected titles to " + that_order.name + "(" + that_order.code + ")");
                  }else{
                      //Only proceed if we could find the order they wanted to attach the title clones to
                      proceed = false;
                      alert("Could not find the Order with code '" + oname + "'");
                  }
              }else if(proceed){
                  yes_no_els = top_el.getElementsByTagName('select');
                  for(var xp = 0; xp < yes_no_els.length; xp++){
                      if(yes_no_els[xp].getAttribute('name') == 'duplicate_order_vals'){
                          if(yes_no_els[xp].value == 'Yes'){
                              duplicate = true;
                          }
                      }
                  }
                  packet = {'client_code': current_order.client_code, 'client_name': current_order.client_name, 'classification': 'Bid', 'no_charge': no_charge, 'redo': redo, 'login': my_user};
                  if(duplicate){
                      packet['sap_po'] = current_order.sap_po;
                      packet['sales_rep'] = current_order.sales_rep;
                      packet['platform'] = current_order.platform;
                      packet['client_rep'] = current_order.client_rep;
                      packet['sales_rep'] = current_order.sales_rep;
                      packet['start_date'] = current_order.start_date;
                      packet['due_date'] = current_order.due_date;
                      packet['expected_delivery_date'] = current_order.expected_delivery_date;
                      packet['expected_price'] = current_order.expected_price;
                  }
                  for(var dr = 1; dr < clone_order_count + 1; dr++){
                      new_name = oname + ' ' + dr;
                      clone_type = 'New Order: ' + oname;
                      if(clone_order_count == 1){
                          new_name = oname;
                          clone_type = 'New Orders (' + clone_order_count + '): ' + oname;
                      }
                      packet['name'] = new_name;
                      that_order = server.insert('twog/order', packet);
                      proceed = true;
                      new_order = true;
                      if(new_order_codes == ''){
                          new_order_codes = that_order.code;
                      }else{
                          new_order_codes = new_order_codes + ',' + that_order.code;
                      }
                  }
              }
              if(proceed){
                  //Good to go...
                  clone_titles = [];
                  checks = top_el.getElementsByClassName('title_selector');
                  for(var r = 0; r < checks.length; r++){
                      //see which titles will be cloned, and which ones will not
                      title_code = checks[r].getAttribute('value_field');
                      if(checks[r].getAttribute('checked') == 'true'){
                          clone_titles.push(title_code)
                      }
                  }
                  //Get number of times per selected title that we want to clone each title
                  counters = {};
                  for(var r = 0; r < clone_titles.length; r++){
                      this_count_el = top_el.getElementById('clone_count_' + clone_titles[r]);
                      ccount = this_count_el.value;

                      if(!isNaN(ccount)){
                          //If it is a number, give it that number
                          counters[clone_titles[r]] = this_count_el.value;
                      }else{
                          //If it isn't a number, just assume the user wants to clone it once
                          counters[clone_titles[r]] = '1';
                          alert(clone_titles[r] + "'s " + ccount + " is not a number. Will clone only once.");
                      }

                  }

                  if(confirm("Are You Sure You Want To Clone These " + clone_titles.length + " Titles to " + clone_type + "?")){
                      title_str = '';
                      //Create string like "TITLE12345[10],TITLE23456[2]" to pass to the TitleClonerCmd
                      //Bracketed items are the number of times to clone the title
                      for(var r = 0; r < clone_titles.length; r++){
                          title_code = clone_titles[r];
                          if(title_str == ''){
                              title_str = title_code + '[' + counters[title_code] + ']';
                          }else{
                              title_str = title_str  + ',' + title_code + '[' + counters[title_code] + ']';
                          }
                      }
                      spt.app_busy.show("Creating Clones...");

                      //Here send the order and title info to the cloner wdg
                      copy_attributes = 'false'
                      if(duplicate){
                          copy_attributes = 'true';
                      }
                      kwargs = {'order_code': new_order_codes, 'titles': title_str, 'user_name': my_user, 'no_charge': no_charge, 'redo': redo, 'copy_attributes': copy_attributes};
                      //now send to the cloning process
                      thing = server.execute_cmd('manual_updaters.TitleClonerCmd', kwargs);
                      if(clone_order_count == 1){
                          //Here load a new tab with the order getting the clones
                          var class_name = 'order_builder.order_builder.OrderBuilder';
                          kwargs = {
                                   'sk': that_order.__search_key__,
                                   'user': my_user
                          };
                          spt.tab.add_new('order_builder_' + that_order.code, 'Order Builder For ' + that_order.name, class_name, kwargs);
                      }else{
                          alert("Please reload your list of orders in the order view. You will see your " + clone_order_count + " new cloned orders there.");
                      }
                      spt.popup.close(spt.popup.get_popup(bvr.src_el));
                      spt.app_busy.hide();
                  }else{
                      if(new_order && clone_order_count == 1){
                          server.retire_sobject(that_order.__search_key__);
                      }else if(clone_order_count > 1){
                          code_split = new_order_codes.split(',');
                          for(var ww = 0; ww < code_split.length; ww++){
                             server.retire_sobject(server.build_search_key('twog/order', code_split[ww]));
                          }
                      }
                  }

              }
          }
}
catch(err){
          spt.app_busy.hide();
          spt.alert(spt.exception.handler(err));
          //alert(err);
}
             ''' % (sk, user_name)}
            #Add the clone behavior
            go_butt.add_behavior(behavior)
        widget.add(table)

        return widget
