from tactic.ui.common import BaseRefreshWdg
from pyasm.web import DivWdg
from pyasm.widget import SubmitWdg

import task_utils


class NewPipelineRequest(BaseRefreshWdg):
    def init(self):
        self.title_sobject = self.get_sobject_from_kwargs()

    def get_display(self):
        outer_div = DivWdg()
        outer_div.add_class('new-pipeline-request-entry-form')

        page_label = "<div>Fill out the following form to request a pipeline for {0}. The request will be " \
                     "added to the Onboarding department's list, and will be addressed as soon as possible. You will " \
                     "receive a notification when the request is complete.</div><br/>".format(
            self.title_sobject.get('code')
        )
        outer_div.add(page_label)

        task_utils.get_description_widget(outer_div)
        task_utils.get_priority_widget(outer_div)
        task_utils.get_due_date_widget(outer_div)
        self.get_submit_widget(outer_div)

        return outer_div

    def get_submit_widget(self, outer_div):
        submit_button = SubmitWdg('Submit')
        submit_button.add_behavior(self.submit_button_behavior(self.title_sobject.get('code')))

        outer_div.add(submit_button)

    @staticmethod
    def submit_button_behavior(title_code):
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
        var process = "Make a Workflow for %s";
        var description = values.description;
        var priority = values.priority;
        var due_date = values.due_date;

        // Set up the object for the new task.
        var new_pipeline_request = {
            'process': process,
            'description': description,
            'status': 'Ready',
            'priority': priority,
            'assigned_login_group': 'onboarding',
            'bid_end_date': due_date,
            'login': login,
            'pipeline_code': 'twog_pipeline_request'
        }

        var server = TacticServerStub.get();

        // Have to set 'triggers' to false to avoid all the other stupid custom crap. Will remove once this method
        // of inserting becomes the norm.
        server.insert('sthpw/task', new_pipeline_request, {'triggers': false});

        spt.api.app_busy_hide();
        // Get the board table by its ID
        var entry_form = document.getElementsByClassName('new-pipeline-request-entry-form')[0];

        // Refresh the view
        spt.popup.close('Request a new pipeline');

        spt.info("Your request for a new pipeline has been submitted. You will be notified when it is complete.");
    }

    // Get the form values
    var outer_div = spt.api.get_parent(bvr.src_el, '.new-pipeline-request-entry-form');
    var values = spt.api.get_input_values(outer_div);

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
}''' % title_code
        }

        return behavior
