from tactic.ui.common import BaseRefreshWdg

from pyasm.web import DivWdg
from pyasm.widget import SubmitWdg

import task_utils


class NewDownloadTask(BaseRefreshWdg):
    def get_display(self):
        outer_div = DivWdg()
        outer_div.add_class('new-download-task-entry-form')

        page_label = "New Download Request"
        outer_div.add(page_label)

        task_utils.get_process_widget(outer_div)
        task_utils.get_description_widget(outer_div)
        task_utils.get_priority_widget(outer_div)
        task_utils.get_due_date_widget(outer_div)
        self.get_submit_widget(outer_div)

        return outer_div

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
        var new_download_task = {
            'process': 'Download: ' + process,
            'description': description,
            'status': 'Pending',
            'priority': priority,
            'assigned_login_group': 'vault',
            'bid_end_date': due_date,
            'login': login
        }

        var server = TacticServerStub.get();

        // Have to set 'triggers' to false to avoid all the other stupid custom crap. Will remove once this method
        // of inserting becomes the norm.
        server.insert('sthpw/task', new_download_task, {'triggers': false});

        spt.api.app_busy_hide();

        // Get the board table by its ID
        var entry_form = document.getElementsByClassName('new-download-task-entry-form')[0];

        // Refresh the view
        spt.api.app_busy_show("Refreshing...");
        spt.api.load_panel(entry_form, 'tasks.NewDownloadTask');
        spt.api.app_busy_hide();
    }

    // Get the form values
    var outer_div = spt.api.get_parent(bvr.src_el, '.new-download-task-entry-form');
    var values = spt.api.get_input_values(outer_div);

    // Process is required, so if it is blank, alert the user
    if (!values.process || values.process == '') {
        spt.api.app_busy_hide();
        spt.alert("Process field is required.");
        return;
    }

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
