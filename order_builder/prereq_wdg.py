from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Environment
from pyasm.search import Search
from pyasm.web import Table
from pyasm.widget import TextWdg

from alternative_elements.customcheckbox import CustomCheckboxWdg
from widget.new_icon_wdg import CustomIconWdg
from widget.button_small_new_wdg import ButtonSmallNewWdg


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
            kill_title_pqs_btn.add_behavior(get_kill_wos_title_prereqs_behavior(my.sob_sk, my.order_sk, my.sob_name,
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
                killer.add_behavior(get_prereq_killer_behavior(p.get_value('code'), my.prereq_st, my.sob_code,
                                                               my.sob_sk, my.sob_st, my.sob_name, my.pipeline,
                                                               my.order_sk))
            prereq_text = 'PreReq: '
            if my.sob_st == 'twog/work_order':
                if p.get_value('from_title') == True:
                    prereq_text = 'Title PreReq: '
            alabel = table.add_cell(prereq_text)
            alabel.add_attr('align', 'center')
            table.add_cell('<input type="text" class="prereq_%s" value="%s" style="width: 500px;"/>' % (p.get_value('code'), p.get_value('prereq')))
            save_butt = table.add_cell('<input type="button" class="save_%s" value="Save"/>' % (p.get_value('code')))
            save_butt.add_behavior(get_save_prereq_behavior(p.get_value('code'), my.prereq_st, my.sob_code,
                                                            my.pipeline))

            if p.get_value('satisfied') == True:
                check_val = 'true'
            else:
                check_val = 'false'
            checkbox = CustomCheckboxWdg(name='satisfied_%s' % p.get_value('code'), value_field=p.get_value('code'),
                                         checked=check_val, dom_class='prereq_selector', code=p.get_value('code'),
                                         additional_js=get_change_satisfied_behavior(p.get_value('code'),
                                                                                     my.prereq_st, my.sob_code,
                                                                                     p.get_value('satisfied'),
                                                                                     my.sob_sk, my.sob_st,
                                                                                     my.sob_name, my.pipeline,
                                                                                     my.order_sk))

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
                            template_button.add_behavior(get_template_prereq_behavior(my.sob_code, my.pipeline,
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
                            template_button.add_behavior(get_template_wo_prereq_behavior(my.sob_code, my.prereq_st,
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
            prereq_text_wdg.add_behavior(get_create_prereq_change_behavior(my.sob_code, my.prereq_st, my.sob_sk,
                                                                           my.sob_st, my.sob_name, my.pipeline,
                                                                           my.order_sk))
            table.add_cell(prereq_text_wdg)
            create_butt = table.add_cell('<input type="button" class="create_prereq" value="Create"/>')
            create_butt.add_behavior(get_create_prereq_behavior(my.sob_code, my.prereq_st, my.sob_sk, my.sob_st,
                                                                my.sob_name, my.pipeline, my.order_sk))
        overhead.add_row()
        oh_cell = overhead.add_cell(table)
        oh_cell.add_attr('class', 'prereq_adder_cell')

        return overhead


def get_kill_wos_title_prereqs_behavior(sob_sk, order_sk, sob_name, pipeline):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      var sob_sk = "%s";
                      var order_sk = "%s";
                      var sob_name = "%s";
                      var pipeline = "%s";
                      var wo_code = sob_sk.split('code=')[1];
                      if(confirm("Are you sure you want to delete all PreReq items inherited from the Title?")){
                          var server = TacticServerStub.get();
                          var work_order_prereqs = server.eval("@SOBJECT(twog/work_order_prereq['work_order_code','" + wo_code + "']['from_title','in','True'])");
                          for(var r = 0; r < work_order_prereqs.length; r++){
                              server.delete_sobject(work_order_prereqs[r].__search_key__);
                          }
                          var overhead_el = spt.api.get_parent(bvr.src_el, '.overhead_' + wo_code);
                          var oh_cell = overhead_el.getElementsByClassName('prereq_adder_cell')[0];
                          spt.api.load_panel(oh_cell, 'order_builder.PreReqWdg', {'sob_code': wo_code, 'sob_sk': sob_sk, 'sob_st': 'twog/work_order', 'sob_name': sob_name, 'pipeline': pipeline, 'order_sk': order_sk});
                      }
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (sob_sk, order_sk, sob_name, pipeline)}

    return behavior


def get_prereq_killer_behavior(prereq_code, prereq_st, sob_code, sob_sk, sob_st, sob_name, pipeline, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      //alert('m15');
                      var server = TacticServerStub.get();
                      prereq_code = '%s';
                      prereq_st = '%s';
                      sob_code = '%s';
                      sob_sk = '%s';
                      sob_st = '%s';
                      sob_name = '%s';
                      pipeline = '%s';
                      order_sk = '%s';
                      //need to finish
                      var overhead_el = spt.api.get_parent(bvr.src_el, '.overhead_' + sob_code);
                      var oh_cell = overhead_el.getElementsByClassName('prereq_adder_cell')[0];
                      pre_sk = server.build_search_key(prereq_st, prereq_code);
                      server.retire_sobject(pre_sk);
                      spt.api.load_panel(oh_cell, 'order_builder.PreReqWdg', {sob_code: sob_code, sob_sk: sob_sk, sob_st: sob_st, sob_name: sob_name, pipeline: pipeline, order_sk: order_sk});
                      top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                      var count_cell = top_el.getElementsByClassName('prereq_count_' + sob_code)[0];
                      spt.api.load_panel(count_cell, 'order_builder.PreReqCountWdg', {sob_code: sob_code, sob_sk: sob_sk, sob_st: sob_st, sob_name: sob_name, prereq_st: prereq_st, pipeline: pipeline, order_sk: order_sk});
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (prereq_code, prereq_st, sob_code, sob_sk, sob_st, sob_name, pipeline, order_sk)}
    return behavior


def get_save_prereq_behavior(prereq_code, prereq_st, sob_code, pipeline):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      //alert('m31');
                      var server = TacticServerStub.get();
                      prereq_code = '%s';
                      prereq_st = '%s';
                      sob_code = '%s';
                      pipeline = '%s';
                      var top_el = spt.api.get_parent(bvr.src_el, '.prereq_adder_' + sob_code);
                      cell = top_el.getElementsByClassName('prereq_' + prereq_code)[0];
                      server.update(server.build_search_key(prereq_st, prereq_code), {'prereq': cell.value});
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (prereq_code, prereq_st, sob_code, pipeline)}
    return behavior


def get_change_satisfied_behavior(prereq_code, prereq_st, sob_code, current_state, sob_sk, sob_st, sob_name, pipeline,
                                  order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      var server = TacticServerStub.get();
                      prereq_code = '%s';
                      prereq_st = '%s';
                      sob_code = '%s';
                      state = '%s';
                      sob_sk = '%s';
                      sob_st = '%s';
                      sob_name = '%s';
                      pipeline = '%s';
                      order_sk = '%s';
                      new_val = '';
                      if(state == 'False'){
                          new_val = 'True';
                      }else{
                          new_val = 'False';
                      }
                      server.update(server.build_search_key(prereq_st, prereq_code), {'satisfied': new_val});
                      var overhead_el = spt.api.get_parent(bvr.src_el, '.overhead_' + sob_code);
                      var oh_cell = overhead_el.getElementsByClassName('prereq_adder_cell')[0];
                      spt.api.load_panel(oh_cell, 'order_builder.PreReqWdg', {sob_code: sob_code, sob_sk: sob_sk, sob_st: sob_st, sob_name: sob_name, pipeline: pipeline, order_sk: order_sk});
                      top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                      var count_cell = top_el.getElementsByClassName('prereq_count_' + sob_code)[0];
                      spt.api.load_panel(count_cell, 'order_builder.PreReqCountWdg', {sob_code: sob_code, sob_sk: sob_sk, sob_st: sob_st, sob_name: sob_name, prereq_st: prereq_st, pipeline: pipeline, order_sk: order_sk});
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
            }
     ''' % (prereq_code, prereq_st, sob_code, current_state, sob_sk, sob_st, sob_name, pipeline, order_sk)}

    return behavior


def get_template_prereq_behavior(sob_code, pipeline, prereq_st, prereq_code):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      //alert('m27');
                      var server = TacticServerStub.get();
                      sob_code = '%s';
                      pipeline = '%s';
                      prereq_st = '%s';
                      prereq_code = '%s';
                      prereq_expr = "@GET(" + prereq_st + "['code','" + prereq_code + "'].prereq)";
                      prereq = server.eval(prereq_expr)[0];
                      server.insert('twog/pipeline_prereq', {'pipeline_code': pipeline, 'prereq': prereq});
                      var top_el = spt.api.get_parent(bvr.src_el, '.prereq_adder_' + sob_code);
                      var cell = top_el.getElementsByClassName('prereq_templ_' + prereq_code)[0];
                      cell.innerHTML = '<img border="0" style="vertical-align: middle" title="Templated" name="Templated" src="/context/icons/silk/tick.png">';
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (sob_code, pipeline, prereq_st, prereq_code)}
    return behavior


def get_template_wo_prereq_behavior(sob_code, prereq_st, prereq_code, work_order_templ_code):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      //alert('m26');
                      var server = TacticServerStub.get();
                      sob_code = '%s';
                      prereq_st = '%s';
                      prereq_code = '%s';
                      work_order_templ_code = '%s';
                      prereq_expr = "@GET(" + prereq_st + "['code','" + prereq_code + "'].prereq)";
                      prereq = server.eval(prereq_expr)[0];
                      server.insert('twog/work_order_prereq_templ', {'work_order_templ_code': work_order_templ_code, 'prereq': prereq});
                      var top_el = spt.api.get_parent(bvr.src_el, '.prereq_adder_' + sob_code);
                      var cell = top_el.getElementsByClassName('prereq_templ_' + prereq_code)[0];
                      cell.innerHTML = '<img border="0" style="vertical-align: middle" title="Templated" name="Templated" src="/context/icons/silk/tick.png">';
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
    ''' % (sob_code, prereq_st, prereq_code, work_order_templ_code)}

    return behavior


def get_create_prereq_change_behavior(sob_code, prereq_st, sob_sk, sob_st, sob_name, pipeline, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'change', 'cbjs_action': '''
                    try{
                      var server = TacticServerStub.get();
                      sob_code = '%s';
                      prereq_st = '%s';
                      sob_sk = '%s';
                      sob_st = '%s';
                      sob_name = '%s';
                      pipeline = '%s';
                      order_sk = '%s';
                      which_code = 'title_code';
                      if(sob_st == 'twog/work_order'){
                          which_code = 'work_order_code';
                      }
                      var overhead_el = spt.api.get_parent(bvr.src_el, '.overhead_' + sob_code);
                      var oh_cell = overhead_el.getElementsByClassName('prereq_adder_cell')[0];
                      var top_el = spt.api.get_parent(bvr.src_el, '.prereq_adder_' + sob_code);
                      var new_prereq_inp = '';//top_el.getElementsByClassName('new_prereq')[0];
                      inps = top_el.getElementsByTagName('input');
                      for(var r = 0; r < inps.length; r++){
                          if(inps[r].name == 'new_prereq'){
                              new_prereq_inp = inps[r];
                          }
                      }
                      var prereq = new_prereq_inp.value;
                      left_count = prereq.split('(').length;
                      right_count = prereq.split(')').length;
                      if(left_count > right_count){
                          for(var x = 0; x < (left_count - right_count); x++){
                              prereq = prereq + ')';
                          }
                      }else if(right_count > left_count){
                          for(var x = 0; x < (right_count - left_count); x++){
                              prereq = '(' + prereq;
                          }
                      }
                      data = {'prereq': prereq, 'satisfied': false}
                      data[which_code] = sob_code;
                      server.insert(prereq_st, data);
                      spt.api.load_panel(oh_cell, 'order_builder.PreReqWdg', {sob_code: sob_code, sob_sk: sob_sk, sob_st: sob_st, sob_name: sob_name, pipeline: pipeline, order_sk: order_sk});
                      top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                      var count_cell = top_el.getElementsByClassName('prereq_count_' + sob_code)[0];
                      spt.api.load_panel(count_cell, 'order_builder.PreReqCountWdg', {sob_code: sob_code, sob_sk: sob_sk, sob_st: sob_st, sob_name: sob_name, prereq_st: prereq_st, pipeline: pipeline, order_sk: order_sk});
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (sob_code, prereq_st, sob_sk, sob_st, sob_name, pipeline, order_sk)}
    return behavior


def get_create_prereq_behavior(sob_code, prereq_st, sob_sk, sob_st, sob_name, pipeline, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      var server = TacticServerStub.get();
                      sob_code = '%s';
                      prereq_st = '%s';
                      sob_sk = '%s';
                      sob_st = '%s';
                      sob_name = '%s';
                      pipeline = '%s';
                      order_sk = '%s';
                      which_code = 'title_code';
                      if(sob_st == 'twog/work_order'){
                          which_code = 'work_order_code';
                      }
                      var overhead_el = spt.api.get_parent(bvr.src_el, '.overhead_' + sob_code);
                      var oh_cell = overhead_el.getElementsByClassName('prereq_adder_cell')[0];
                      var top_el = spt.api.get_parent(bvr.src_el, '.prereq_adder_' + sob_code);
                      var new_prereq_inp = '';//top_el.getElementsByClassName('new_prereq')[0];
                      inps = top_el.getElementsByTagName('input');
                      for(var r = 0; r < inps.length; r++){
                          if(inps[r].name == 'new_prereq'){
                              new_prereq_inp = inps[r];
                          }
                      }
                      var prereq = new_prereq_inp.value;
                      left_count = prereq.split('(').length;
                      right_count = prereq.split(')').length;
                      if(left_count > right_count){
                          for(var x = 0; x < (left_count - right_count); x++){
                              prereq = prereq + ')';
                          }
                      }else if(right_count > left_count){
                          for(var x = 0; x < (right_count - left_count); x++){
                              prereq = '(' + prereq;
                          }
                      }
                      data = {'prereq': prereq, 'satisfied': false}
                      data[which_code] = sob_code;
                      server.insert(prereq_st, data);
                      spt.api.load_panel(oh_cell, 'order_builder.PreReqWdg', {sob_code: sob_code, sob_sk: sob_sk, sob_st: sob_st, sob_name: sob_name, pipeline: pipeline, order_sk: order_sk});
                      top_el = document.getElementsByClassName('twog_order_builder_' + order_sk)[0];
                      var count_cell = top_el.getElementsByClassName('prereq_count_' + sob_code)[0];
                      spt.api.load_panel(count_cell, 'order_builder.PreReqCountWdg', {sob_code: sob_code, sob_sk: sob_sk, sob_st: sob_st, sob_name: sob_name, prereq_st: prereq_st, pipeline: pipeline, order_sk: order_sk});
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (sob_code, prereq_st, sob_sk, sob_st, sob_name, pipeline, order_sk)}
    return behavior
