from tactic.ui.common import BaseRefreshWdg
from tactic.ui.input import TextInputWdg, TextAreaInputWdg
from tactic.ui.widget import CalendarInputWdg

from pyasm.web import DivWdg
from pyasm.widget import SubmitWdg

from order_builder.order_builder_utils import get_label_widget, get_select_widget_from_search_type


class NewOnboardingTask(BaseRefreshWdg):
    def get_display(self):
        outer_div = DivWdg()
        outer_div.add_class('new-onboarding-task-entry-form')

        page_label = "New Onboarding Task"
        outer_div.add(page_label)

        self.get_process_widget(outer_div)
        self.get_description_widget(outer_div)
        self.get_priority_widget(outer_div)
        self.get_assigned_to_select_widget(outer_div)
        self.get_due_date_widget(outer_div)
        self.get_submit_widget(outer_div)

        return outer_div

    @staticmethod
    def get_process_widget(outer_div):
        process_input = TextInputWdg()
        process_input.set_name('process')

        outer_div.add(get_label_widget('Process'))
        outer_div.add(process_input)

    @staticmethod
    def get_assigned_to_select_widget(outer_div):
        user_search_filters = [('login_group', 'onboarding')]
        assigned_to_select_widget = get_select_widget_from_search_type('sthpw/login_in_group', 'login', 'login', 'code',
                                                                       user_search_filters)
        assigned_to_select_widget.set_name('assigned')

        outer_div.add(get_label_widget('Assigned To'))
        outer_div.add(assigned_to_select_widget)

    @staticmethod
    def get_description_widget(outer_div):
        description_input = TextAreaInputWdg(name='description')
        description_input.add_class('description')

        outer_div.add(get_label_widget('Description'))
        outer_div.add(description_input)

    @staticmethod
    def get_priority_widget(outer_div):
        priority_input = TextInputWdg()
        priority_input.set_name('priority')

        outer_div.add(get_label_widget('Priority'))
        outer_div.add(priority_input)

    @staticmethod
    def get_due_date_widget(outer_div):
        due_date_wdg = CalendarInputWdg('Due Date')
        due_date_wdg.add_class('due_date')
        due_date_wdg.set_name('due_date')

        outer_div.add(get_label_widget('Due Date'))
        outer_div.add(due_date_wdg)

    def get_submit_widget(self, outer_div):
        submit_button = SubmitWdg('Submit')
        submit_button.add_behavior(self.submit_button_behavior())

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
        var new_onboarding_task = {
            'process': process,
            'description': description,
            'status': 'Pending',
            'priority': priority,
            'assigned': assigned,
            'assigned_login_group': 'onboarding',
            'bid_end_date': due_date,
            'login': login
        }

        var server = TacticServerStub.get();

        // Have to set 'triggers' to false to avoid all the other stupid custom crap. Will remove once this method
        // of inserting becomes the norm.
        server.insert('sthpw/task', new_onboarding_task, {'triggers': false});

        spt.api.app_busy_hide();

        // Get the board table by its ID
        var entry_form = document.getElementsByClassName('new-onboarding-task-entry-form')[0];

        // Refresh the view
        spt.api.app_busy_show("Refreshing...");
        spt.api.load_panel(entry_form, 'tasks.NewOnboardingTask');
        spt.api.app_busy_hide();
    }

    // Get the form values
    var outer_div = spt.api.get_parent(bvr.src_el, '.new-onboarding-task-entry-form');
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
