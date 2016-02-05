from tactic.ui.common import BaseRefreshWdg

from pyasm.search import Search
from pyasm.web import Table

from order_builder_utils import OBScripts


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

        obs = OBScripts(order_sk=my.order_sk)
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
        prereq_launcher.add_behavior(obs.get_launch_prereq_behavior(my.sob_code, my.sob_st, my.sob_sk, my.sob_name, my.pipeline))

        return table
