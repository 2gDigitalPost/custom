from tactic.ui.common import BaseRefreshWdg
from tactic.ui.input import TextInputWdg, TextAreaInputWdg
from tactic.ui.widget import CalendarInputWdg

from pyasm.web import DivWdg
from pyasm.search import Search
from pyasm.widget import CheckboxWdg, MultiSelectWdg, SubmitWdg

from order_builder_utils import get_label_widget, get_select_widget_from_search_type


class OrderTitleEntryWdg(BaseRefreshWdg):
    def get_display(self):
        outer_div = DivWdg()
        outer_div.add_class('new-order-title-entry-form')

        order_title_name_input = TextInputWdg()
        order_title_name_input.set_name('name')

        outer_div.add(get_label_widget('Name'))
        outer_div.add(order_title_name_input)

        order_search_filters = [('classification', 'Master', '!='),
                                ('classification', 'Completed', '!='),
                                ('classification', 'Test', '!=')]

        order_select_wdg = get_select_widget_from_search_type('twog/order', 'order_code', 'name', 'code',
                                                              order_search_filters)

        outer_div.add(get_label_widget('Order Code'))
        outer_div.add(order_select_wdg)

        platform_select_wdg = get_select_widget_from_search_type('twog/platform', 'platform_code', 'name', 'code')

        outer_div.add(get_label_widget('Platform'))
        outer_div.add(platform_select_wdg)

        title_select_wdg = get_select_widget_from_search_type('twog/title', 'title_code', 'title', 'code',
                                                              [('master_title', True)])

        outer_div.add(get_label_widget('Title'))
        outer_div.add(title_select_wdg)

        due_date_wdg = CalendarInputWdg('Due Date')
        due_date_wdg.add_class('due_date')

        outer_div.add(get_label_widget('Due Date'))
        outer_div.add(due_date_wdg)

        language_wdg = self.get_languages_widget()

        outer_div.add(get_label_widget('Language'))
        outer_div.add(language_wdg)

        territory_wdg = get_select_widget_from_search_type('twog/territory', 'territory', 'name', 'code')

        outer_div.add(get_label_widget('Territory'))
        outer_div.add(territory_wdg)

        description_input = TextAreaInputWdg()
        description_input.set_name('description')
        description_input.add_class('description')

        outer_div.add(get_label_widget('Description'))
        outer_div.add(description_input)

        self.get_total_program_runtime_wdg(outer_div)

        checkboxes_div = DivWdg()

        no_charge_wdg = CheckboxWdg('no_charge', 'No Charge')
        redo_wdg = CheckboxWdg('redo', 'Redo')

        checkboxes_div.add(no_charge_wdg)
        checkboxes_div.add(redo_wdg)

        outer_div.add(checkboxes_div)

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

    // Get the form values
    var outer_div = spt.api.get_parent(bvr.src_el, '.new-order-title-entry-form');
    var values = spt.api.get_input_values(outer_div);

    var total_program_runtime = String(values.total_program_runtime);
    console.log(total_program_runtime);
    if (total_program_runtime) {
        var runtime_re = /^[\d]+:[\d]+$/;
        var match = total_program_runtime.match(runtime_re);

        if (match < 1) {
            throw("Total program runtime must be in the format MM:SS (it can also be left blank).")
        }
    }

    // Set up the object for the new title_order entry.
    var new_title_order = {
        'name': values.name,
        'order_code': values.order_code,
        'title_code': values.title_code,
        'platform': values.platform_code,
        'due_date': values.due_date,
        'languages': values.languages,
        'territory': values.territory,
        'description': values.description,
        'total_program_runtime': values.total_program_runtime,
        'no_charge': values.no_charge,
        'redo': values.redo
    }

    // Have to set 'triggers' to false to avoid all the other stupid custom crap. Will remove once this method
    // of inserting becomes the norm.
    server.insert('twog/title_order', new_title_order, {'triggers': false});

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

    @staticmethod
    def get_total_program_runtime_wdg(outer_div):
        total_program_runtime_input = TextInputWdg()
        total_program_runtime_input.set_name('total_program_runtime')

        outer_div.add(get_label_widget('Total Program Runtime'))
        outer_div.add(total_program_runtime_input)
