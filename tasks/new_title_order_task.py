from tactic.ui.common import BaseRefreshWdg, BaseTableElementWdg
from pyasm.web import DivWdg, Table
from pyasm.widget import SubmitWdg

import task_utils


class NewTaskButton(BaseTableElementWdg):
    def init(self):
        # self.title_order_code = self.get_current_sobject().get_code()
        pass

    @staticmethod
    def get_launch_behavior(search_key):
        behavior = {'css_class': 'clickme', 'type': 'click_up', 'cbjs_action': '''
try {
    var class_name = 'tasks.NewTitleOrderTask';

    kwargs = {
        'parent_key': '%s'
    }

    spt.panel.load_popup('New Task', class_name, kwargs);
}
catch(err){
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}
         ''' % search_key}
        return behavior

    def get_display(self):
        if 'code' in self.kwargs.keys():
            code = self.kwargs.get('code')
        else:
            sobject = self.get_current_sobject()
            code = sobject.get_code()
        title_code = ''
        if 'title_code' in self.kwargs.keys():
            title_code = self.kwargs.get('title_code')

        widget = DivWdg()
        table = Table()
        table.add_attr('width', '50px')
        table.add_row()
        cell1 = table.add_cell('<img border="0" style="vertical-align: middle" title="" src="/context/icons/custom/work.png">')
        cell1.add_attr('code', code)
        cell1.add_attr('title_code', title_code)
        launch_behavior = self.get_launch_behavior(self.get_current_sobject().get_search_key())
        cell1.add_style('cursor: pointer;')
        cell1.add_behavior(launch_behavior)
        widget.add(table)

        return widget


class NewTitleOrderTask(BaseRefreshWdg):
    def init(self):
        self.something = self.get_sobject_from_kwargs()

    def get_display(self):
        outer_div = DivWdg()
        outer_div.add_class('new-onboarding-task-entry-form')

        page_label = "New Task for Title"
        outer_div.add(page_label)

        task_utils.get_process_widget(outer_div)
        task_utils.get_description_widget(outer_div)
        task_utils.get_priority_widget(outer_div)
        task_utils.get_assigned_to_select_widget(outer_div)
        task_utils.get_due_date_widget(outer_div)
        self.get_submit_widget(outer_div)

        return outer_div

    def get_submit_widget(self, outer_div):
        submit_button = SubmitWdg('Submit')
        # submit_button.add_behavior(self.submit_button_behavior())

        outer_div.add(submit_button)
