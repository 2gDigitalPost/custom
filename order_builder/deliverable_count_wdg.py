from tactic.ui.common import BaseRefreshWdg

from pyasm.search import Search
from pyasm.web import Table


class DeliverableCountWdg(BaseRefreshWdg):

    def init(self):
        self.title_code = ''
        self.order_sk = ''

    def get_display(self):
        self.order_sk = str(self.kwargs.get('order_sk'))
        self.title_code = str(self.kwargs.get('title_code'))
        full_title = str(self.kwargs.get('full_title'))
        delivs_search = Search("twog/work_order_deliverables")
        delivs_search.add_filter('title_code', self.title_code)
        delivs = delivs_search.get_sobjects()
        linked = []
        for d in delivs:
            linked.append(d.get_value('satisfied'))
        satisfied = 0
        unsatisfied = 0
        for link in linked:
            if link == True:
                satisfied += 1
            else:
                unsatisfied += 1

        table = Table()
        table.add_row()
        deliverable_launcher = table.add_cell('<u>Delivs: (%s/%s)</u>' % (satisfied, satisfied + unsatisfied))
        deliverable_launcher.add_attr('nowrap', 'nowrap')
        deliverable_launcher.add_attr('valign', 'bottom')
        deliverable_launcher.add_style('font-size: 80%;')
        deliverable_launcher.add_style('font-color: #2e2e2e;')
        deliverable_launcher.add_style('cursor: pointer;')
        deliverable_launcher.add_behavior(get_launch_deliverables_behavior(self.order_sk, self.title_code, full_title))

        return table


def get_launch_deliverables_behavior(order_sk, title_code, title_name):
    behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    var server = TacticServerStub.get();
    title_code = '%s';
    title_name = '%s';
    order_sk = '%s';
    spt.panel.load_popup('Permanents for ' + title_name, 'order_builder.DeliverableWdg', {title_code: title_code , order_sk: order_sk});
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
     ''' % (title_code, title_name, order_sk)}
    return behavior
