from tactic.ui.common import BaseRefreshWdg
from tactic.ui.input import TextInputWdg, TextAreaInputWdg

from pyasm.web import DivWdg
from pyasm.widget import SubmitWdg

from order_builder.order_builder_utils import get_label_widget


class WorkOrderEntryWdg(BaseRefreshWdg):
    def init(self):
        # self.title_order_code = self.kwargs('title_order_code')
        self.title_order = self.get_sobject_from_kwargs()

    def get_display(self):
        outer_div = DivWdg()
        outer_div.add_class('new-work-order-entry-form')

        page_label = "Work Order for {0}".format(self.title_order)
        outer_div.add(page_label)

        process_input = TextInputWdg()
        process_input.set_name('process')

        outer_div.add(get_label_widget('Process'))
        outer_div.add(process_input)

        instructions_input = TextAreaInputWdg()
        instructions_input.set_name('instructions')

        outer_div.add(get_label_widget('Instructions'))
        outer_div.add(instructions_input)

        description_input = TextAreaInputWdg()
        description_input.set_name('description')

        outer_div.add(get_label_widget('Description (Optional)'))
        outer_div.add(description_input)

        submit_button = SubmitWdg('Submit')
        submit_button.add_behavior(self.submit_button_behavior())

        outer_div.add(submit_button)

        return outer_div

    @staticmethod
    def submit_button_behavior():
        behavior = {
            'css_class': 'clickme',
            'type': 'click_up',
            'cbjs_action': '''
try {
    spt.api.app_busy_show('Saving...');

    // Get the form values
    var outer_div = spt.api.get_parent(bvr.src_el, '.new-title-entry-form');
    var values = spt.api.get_input_values(outer_div);

    // Set up the object for the new title. Note that 'master_title' is always set to true.
    var new_title = {
        'title': values.name,
        'episode': values.episode,
        'description': values.description,
        'master_title': true
    }

    var server = TacticServerStub.get();

    // Have to set 'triggers' to false to avoid all the other stupid custom crap. Will remove once this method
    // of inserting becomes the norm.
    server.insert('twog/title', new_title, {'triggers': false});

    spt.api.app_busy_hide();

    // Get the board table by its ID
    var entry_form = document.getElementsByClassName('new-title-entry-form')[0];

    // Refresh the view
    spt.api.app_busy_show("Refreshing...");
    spt.api.load_panel(entry_form, 'order_builder.TitleEntryWdg');
    spt.api.app_busy_hide();

}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}'''
        }

        return behavior
