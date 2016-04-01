from tactic.ui.common import BaseRefreshWdg
from tactic.ui.input import TextInputWdg
from tactic.ui.widget import CalendarWdg

from pyasm.web import DivWdg
from pyasm.search import Search
from pyasm.widget import SelectWdg, MultiSelectWdg, SubmitWdg

from order_builder_utils import get_label_widget, get_select_widget_from_search_type


class OrderTitleEntryWdg(BaseRefreshWdg):
    def get_display(self):
        outer_div = DivWdg()

        order_search_filters = [('classification', 'Master', '!='),
                                ('classification', 'Completed', '!='),
                                ('classification', 'Test', '!=')]

        order_select_wdg = get_select_widget_from_search_type('twog/order', 'Order', 'name', 'code',
                                                              order_search_filters)

        outer_div.add(get_label_widget('Order Code'))
        outer_div.add(order_select_wdg)

        platform_select_wdg = get_select_widget_from_search_type('twog/platform', 'Platform', 'name', 'code')

        outer_div.add(get_label_widget('Platform'))
        outer_div.add(platform_select_wdg)

        title_select_wdg = get_select_widget_from_search_type('twog/title', 'Title', 'title', 'code',
                                                              [('master_title', True)])

        outer_div.add(get_label_widget('Title'))
        outer_div.add(title_select_wdg)

        due_date_wdg = CalendarWdg()

        outer_div.add(get_label_widget('Due Date'))
        outer_div.add(due_date_wdg)

        language_wdg = self.get_languages_widget()

        outer_div.add(get_label_widget('Language'))
        outer_div.add(language_wdg)

        territory_wdg = get_select_widget_from_search_type('twog/territory', 'Territory', 'name', 'code')

        outer_div.add(get_label_widget('Territory'))
        outer_div.add(territory_wdg)

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

    var server = TacticServerStub.get();

    server.

    // Get the form values
    var outer_div = spt.api.get_parent(bvr.src_el, '.new-order-entry-form');
    var values = spt.api.get_input_values(outer_div);

    // Set up the object for the new title. Note that 'master_title' is always set to true.
    var new_order = {
        'name': values.name,
        'po_number': values.po_number,
        'client_code': values.client_code
    }


    // Have to set 'triggers' to false to avoid all the other stupid custom crap. Will remove once this method
    // of inserting becomes the norm.
    server.insert('twog/order', new_order, {'triggers': false});

    spt.api.app_busy_hide();
}
catch(err) {
    spt.app_busy.hide();
    spt.alert(spt.exception.handler(err));
}'''
        }

        return behavior

    @staticmethod
    def get_languages_widget():
        languages_search = Search('twog/language')

        languages_wdg = MultiSelectWdg('Languages')
        languages_wdg.add_empty_option('----')
        languages_wdg.set_search_for_options(languages_search, label_column='name', value_column='code')

        return languages_wdg
