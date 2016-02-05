from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget.button_new_wdg import ButtonSmallNewWdg

from pyasm.common import Environment
from pyasm.search import Search
from pyasm.web import Table
from pyasm.widget import IconWdg

from alternative_elements.customcheckbox import CustomCheckboxWdg

from order_builder_utils import OBScripts, get_selected_color_behavior


class EquipmentUsedRow(BaseRefreshWdg):

    def init(my):
        my.search_type = 'twog/equipment_used'
        my.title = 'Equipment Used'
        my.sk = ''
        my.code = ''
        my.user = ''
        my.parent_sk = ''
        my.parent_sid = ''
        my.order_sid = ''
        my.order_sk = ''
        my.x_butt = "<img src='/context/icons/common/BtnKill.gif' title='Delete' name='Delete'/>"
        my.disp_mode = 'Small'
        my.small = False
        my.groups_str = ''
        my.is_master = False
        my.is_master_str = 'false'
        my.on_color = '#ff0000'
        my.off_color = '#c6aeae'

    def get_display(my):
        my.sk = str(my.kwargs.get('sk'))
        my.code = my.sk.split('code=')[1]
        my.parent_sk = str(my.kwargs.get('parent_sk'))
        my.parent_sid = str(my.kwargs.get('parent_sid'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        order_code = my.order_sk.split('code=')[1]
        if 'user' in my.kwargs.keys():
            my.user = my.kwargs.get('user')
        else:
            my.user = Environment.get_user_name()
        if 'groups_str' in my.kwargs.keys():
            my.groups_str = my.kwargs.get('groups_str')
        if my.groups_str in [None,'']:
            group_search = Search("sthpw/login_in_group")
            group_search.add_filter('login',my.user)
            my_groups = group_search.get_sobjects()
            for mg in my_groups:
                if my.groups_str == '':
                    my.groups_str = mg.get_value('login_group')
                else:
                    my.groups_str = '%s,%s' % (my.groups_str, mg.get_value('login_group'))

        user_is_scheduler = False
        if 'scheduling' in my.groups_str:
            user_is_scheduler = True

        if 'display_mode' in my.kwargs.keys():
            my.disp_mode = str(my.kwargs.get('display_mode'))
        if my.disp_mode == 'Small':
            my.small = True
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
        obs = OBScripts(order_sk=my.order_sk, user=my.user, groups_str=my.groups_str, display_mode=my.disp_mode, is_master=my.is_master_str)
        if 'main_obj' in my.kwargs.keys():
            main_obj = my.kwargs.get('main_obj')
        else:
            main_search = Search("twog/equipment_used")
            main_search.add_filter('code',my.code)
            main_obj = main_search.get_sobject()
        eq_length = main_obj.get_value('length')
        table = Table()
        table.add_attr('cellpadding','0')
        table.add_attr('cellspacing','0')
        table.add_attr('class','EquipmentUsedRow_%s' % my.code)
        table.add_style('background-color: %s;' % my.off_color)
        table.add_style('border-collapse', 'separate')
        table.add_style('border-spacing', '25px 3px')
        table.add_style('width: 100%s;' % '%')
        table.add_style('border-bottom-right-radius', '10px')
        table.add_style('border-bottom-left-radius', '10px')
        table.add_style('border-top-right-radius', '10px')
        table.add_style('border-top-left-radius', '10px')
        row1 = table.add_row()
        row1.add_attr('width','100%s' % '%')
        name_to_use = main_obj.get_value('name')
        if eq_length not in [None,'']:
            name_to_use = '%s: %s' % (name_to_use, eq_length)
        eu_cell = table.add_cell('<b><u>%s</u></b>' % name_to_use)
        eu_cell.add_attr('nowrap','nowrap')
        eu_cell.add_style('cursor: pointer;')
        eu_cell.add_behavior(obs.get_panel_change_behavior(my.search_type, my.code, my.sk, my.order_sk, my.title, '', 'builder/refresh_from_save','',my.parent_sk,main_obj.get_value('name'), user_is_scheduler))
        top_buttons = Table()
        top_buttons.add_row()
        if my.is_master and not my.small:
            which_icon = IconWdg.TEMPLATE
            which_title = 'Template This Equipment'
            if main_obj.get_value('equipment_used_templ_code') not in ['', None]:
                which_icon = IconWdg.CHECK
                which_title = 'Un-Template This Equipment'
            button = ButtonSmallNewWdg(title=which_title, icon=which_icon)
            eq_templ_code = main_obj.get_value('equipment_used_templ_code')
            if not eq_templ_code:
                eq_templ_code = ''
            button.add_behavior(get_template_single_eu_behavior(my.order_sk, my.is_master_str, my.sk, eq_templ_code))
            top_buttons.add_cell(button)
        if my.small:
            select_check = CustomCheckboxWdg(name='select_%s' % my.code, value_field=my.code, checked='false', dom_class='ob_selector', parent_table="EquipmentUsedRow_%s" % my.code, normal_color=my.off_color, selected_color=my.on_color, code=my.code, ntype='equipment_used', search_key=my.sk, additional_js=get_selected_color_behavior(my.code, 'EquipmentUsedRow', my.on_color, my.off_color))
            cb = top_buttons.add_cell(select_check)
        elif user_is_scheduler:
            xb = top_buttons.add_cell(my.x_butt)
            xb.add_attr('align','right')
            xb.add_style('cursor: pointer;')
            xb.add_behavior(obs.get_killer_behavior(my.sk, my.parent_sk, 'WorkOrderRow', main_obj.get_value('name')))
        unit_cell = table.add_cell('UNITS: %s' % main_obj.get_value('units'))
        unit_cell.add_attr('nowrap','nowrap')
        unit_cell.add_style('font-size: 10px;')

        if eq_length in [None,'']:
            if main_obj.get_value('units') in ['gb','tb']:
                second_cell = table.add_cell('EST SIZE: %s' % main_obj.get_value('expected_duration'))
            else:
                second_cell = table.add_cell('EST DUR: %s' % main_obj.get_value('expected_duration'))
        else:
            second_cell = table.add_cell('LEN: %s' % eq_length)
        second_cell.add_style('font-size: 10px;')
        second_cell.add_attr('nowrap','nowrap')
        if main_obj.get_value('units') not in ['gb','tb']:
            third_cell = table.add_cell('QUANT: %s' % main_obj.get_value('expected_quantity'))
            third_cell.add_style('font-size: 10px;')
            third_cell.add_attr('nowrap','nowrap')
            if my.small:
                third_cell.add_style('font-size: 8px;')
            else:
                third_cell.add_style('font-size: 10px;')
        long_cell1 = table.add_cell(top_buttons)
        long_cell1.add_attr('colspan', '4')
        long_cell1.add_attr('align', 'right')
        long_cell1.add_style('width: 100%')
        if my.small:
            eu_cell.add_style('font-size: 8px;')
            unit_cell.add_style('font-size: 8px;')
            second_cell.add_style('font-size: 8px;')
            long_cell1.add_style('font-size: 8px;')
        else:
            eu_cell.add_style('font-size: 10px;')
            unit_cell.add_style('font-size: 10px;')
            second_cell.add_style('font-size: 10px;')
            long_cell1.add_style('font-size: 10px;')
        tab2ret = Table()
        tab2ret.add_attr('width', '100%')
        top_row = tab2ret.add_row()
        top_row.add_attr('class', 'top_%s' % my.sk)
        tab2ret.add_cell(table)

        return table


def get_template_single_eu_behavior(order_sk, is_master_str, eq_sk, eq_templ_code):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    function oc(a){
                        var o = {};
                        for(var i=0;i<a.length;i++){
                            o[a[i]]='';
                        }
                        return o;
                    }
                    try{
                      //alert('m68');
                      var server = TacticServerStub.get();
                      var eq_sk = '%s'; //this is the equipment code
                      var eq_templ_code = '%s';
                      var order_sk = '%s';
                      var is_master_str = '%s';
                      var eq_code = eq_sk.split('code=')[1];
                      //var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder_' + order_sk);
                      var top_el = spt.api.get_parent(bvr.src_el, '.twog_order_builder');
                      display_mode = top_el.getAttribute('display_mode');
                      groups_str = top_el.getAttribute('groups_str');
                      user = top_el.getAttribute('user');
                      var client_code = top_el.get('client');
                      my_cell = top_el.getElementsByClassName('cell_' + eq_sk)[0];
                      sk = eq_sk;
                      parent_sk = my_cell.getAttribute('parent_sk')
                      wo_code = parent_sk.split('code=')[1];
                      wot_code = my_cell.getAttribute('wot_code');
                      parent_sid = my_cell.getAttribute('parent_sid')
                      order_sk = my_cell.getAttribute('order_sk')
                      if(eq_templ_code != ''){
                          eqt_sk = server.build_search_key('twog/equipment_used_templ', eq_templ_code);
                          server.retire_sobject(eqt_sk);
                          server.update(eq_sk, {'equipment_used_templ_code': ''})
                      }else{
                          me_expr = "@SOBJECT(twog/equipment_used['code','" + eq_code + "'])";
                          eq = server.eval(me_expr)[0];
                          templ = server.insert('twog/equipment_used_templ',{'work_order_templ_code': wot_code, 'name': eq.name, 'description': eq.description, 'client_code': client_code, 'equipment_code': eq.equipment_code, 'expected_cost': eq.expected_cost, 'expected_duration': eq.expected_duration, 'expected_quantity': eq.expected_quantity, 'units': eq.units})
                          server.update(eq_sk, {'equipment_used_templ_code': templ.code})
                      }

                      spt.api.load_panel(my_cell, 'order_builder.EquipmentUsedRow', {'sk': sk, 'parent_sk': parent_sk, 'parent_sid': parent_sid, 'order_sk': order_sk, 'display_mode': display_mode, 'user': user, 'groups_str': groups_str, is_master: is_master_str});


            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (eq_sk, eq_templ_code, order_sk, is_master_str)}
    return behavior
