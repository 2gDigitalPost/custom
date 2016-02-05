from tactic.ui.common import BaseRefreshWdg

from pyasm.search import Search
from pyasm.web import Table


class PreReqCountWdg(BaseRefreshWdg):

    def init(my):
        my.sob_sk = ''
        my.sob_code = ''
        my.sob_st = ''
        my.sob_name = ''
        my.prereq_st = ''
        my.pipeline = ''
        my.order_sk = ''

    def get_display(my):
        my.sob_code = str(my.kwargs.get('sob_code'))
        my.sob_sk = str(my.kwargs.get('sob_sk'))
        my.sob_st = str(my.kwargs.get('sob_st'))
        my.prereq_st = str(my.kwargs.get('prereq_st'))
        my.sob_name = str(my.kwargs.get('sob_name'))
        my.pipeline = str(my.kwargs.get('pipeline'))
        my.order_sk = str(my.kwargs.get('order_sk'))
        code_type = 'title_code'
        if my.sob_st == 'twog/work_order':
            code_type = 'work_order_code'
        all_search = Search(my.prereq_st)
        all_search.add_filter(code_type, my.sob_code)
        all_pres = all_search.get_sobjects()

        satisfied = 0
        unsatisfied = 0
        for ap in all_pres:
            if ap.get_value('satisfied') == True:
                satisfied += 1
            else:
                unsatisfied += 1

        table = Table()
        table.add_row()
        fcolor = '#FF0000'
        if satisfied + unsatisfied > 0:
            if (satisfied/(satisfied + unsatisfied)) == 1:
                fcolor = '#458b00'
        prereq_launcher = table.add_cell('<font color="%s"><u>Checklist: (%s/%s)</u></font>' % (fcolor, satisfied, satisfied + unsatisfied))
        prereq_launcher.add_attr('nowrap', 'nowrap')
        prereq_launcher.add_attr('valign', 'bottom')
        prereq_launcher.add_style('font-size: 80%;')
        prereq_launcher.add_style('font-color: #2e2e2e;')
        prereq_launcher.add_style('cursor: pointer;')
        prereq_launcher.add_behavior(get_launch_prereq_behavior(my.sob_code, my.sob_st, my.sob_sk, my.sob_name,
                                                                my.pipeline, my.order_sk))

        return table


def get_launch_prereq_behavior(sob_code, sob_st, sob_sk, sob_name, pipeline, order_sk):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
                    try{
                      //alert('m21');
                      var server = TacticServerStub.get();
                      sob_code = '%s';
                      sob_st = '%s';
                      sob_sk = '%s';
                      sob_name = '%s';
                      pipeline = '%s';
                      order_sk = '%s';
                      spt.panel.load_popup('Checklist for ' + sob_name, 'order_builder.PreReqWdg', {sob_code: sob_code, sob_sk: sob_sk, sob_st: sob_st, sob_name: sob_name, pipeline: pipeline, order_sk: order_sk});
            }
            catch(err){
                      spt.app_busy.hide();
                      spt.alert(spt.exception.handler(err));
                      //alert(err);
            }
     ''' % (sob_code, sob_st, sob_sk, sob_name, pipeline, order_sk)}
    return behavior