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
        self.title_order_sobject = self.get_sobject_from_kwargs()

    def get_display(self):
        outer_div = DivWdg()
        outer_div.add_class('new-title-order-task-entry-form')

        page_label = "New Task"
        outer_div.add(page_label)

        task_utils.get_process_widget(outer_div)
        task_utils.get_description_widget(outer_div)
        task_utils.get_priority_widget(outer_div)
        task_utils.get_due_date_widget(outer_div)
        self.get_submit_widget(outer_div)

        return outer_div

    def get_submit_widget(self, outer_div):
        submit_button = SubmitWdg('Submit')
        # submit_button.add_behavior(self.submit_button_behavior())

        outer_div.add(submit_button)

    @staticmethod
    def submit_button_behavior():
        behavior = {
            'css_class': 'clickme',
            'type': 'click_up',
            'cbjs_action': '''
try {
    var submit_form = function(values) {
        spt.api.app_busy_show('Saving...');

        var env = spt.Environment.get();
        var login = env.user;

        // Get the values needed to submit the form
        var process = values.process;
        var description = values.description;
        var priority = values.priority;
        var assigned = values.assigned;
        var due_date = values.due_date;

        // Set up the object for the new task.
        var new_title_order_task = {
            'process': process,
            'description': description,
            'status': 'Pending',
            'priority': priority,
            'bid_end_date': due_date,
            'login': login
        }

        var server = TacticServerStub.get();

        // Have to set 'triggers' to false to avoid all the other stupid custom crap. Will remove once this method
        // of inserting becomes the norm.
        server.insert('sthpw/task', new_title_order_task, {'triggers': false});

        spt.api.app_busy_hide();

        // Get the board table by its ID
        var entry_form = document.getElementsByClassName('new-title-order-task-entry-form')[0];

        // Refresh the view
        spt.api.app_busy_show("Refreshing...");
        spt.api.load_panel(entry_form, 'tasks.NewTitleOrderTask');
        spt.api.app_busy_hide();
    }

    // Get the form values
    var outer_div = spt.api.get_parent(bvr.src_el, '.new-title-order-task-entry-form');
    var values = spt.api.get_input_values(outer_div);

    // Process is required, so if it is blank, alert the user
    if (!values.process || values.process == '') {
        spt.api.app_busy_hide();
        spt.alert("Process field is required.");
        return;
    }

    // Due date is not required, but it is recommended, so alert the user if it's blank
    /*
    if (!values.due_date || values.due_date == '') {
        spt.api.app_busy_hide();
        spt.confirm("You did not enter a due date. You don't have to, but it's highly recommended. Do you want to add one?",
        submit_form(values), null, {
		    okText: 'Continue without Due Date',
		    cancelText: 'Cancel',
		    focus: true,
		    textPClass: 'MooDialogConfirm',
            type: 'html'
	    });
    }
    else {
        submit_form(values);
    }
    */

    if (!values.due_date || values.due_date == '') {
        spt.api.app_busy_hide();
        spt.alert("Due Date field is required.");
        return;
    }

    submit_form(values);
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}'''
        }

        return behavior
