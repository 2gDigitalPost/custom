from tactic.ui.common import BaseRefreshWdg
from tactic.ui.input import TextInputWdg, TextAreaInputWdg

from pyasm.web import DivWdg
from pyasm.search import Search
from pyasm.widget import MultiSelectWdg, SelectWdg, TextAreaWdg, SubmitWdg

from order_builder_utils import get_label_widget, get_select_widget_from_search_type


class TitleEntryWdg(BaseRefreshWdg):
    def get_display(self):
        outer_div = DivWdg()
        outer_div.add_class('new-title-entry-form')

        title_name_input = TextInputWdg()
        title_name_input.set_name('name')

        outer_div.add(get_label_widget('Name'))
        outer_div.add(title_name_input)

        episode_input = TextInputWdg()
        episode_input.set_name('episode')

        outer_div.add(get_label_widget('Episode'))
        outer_div.add(episode_input)

        description_input = TextAreaInputWdg()
        description_input.set_name('description')

        outer_div.add(get_label_widget('Description'))
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
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}'''
        }

        return behavior
