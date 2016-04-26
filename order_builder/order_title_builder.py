from tactic.ui.common import BaseRefreshWdg
from tactic.ui.input import TextInputWdg, TextAreaInputWdg
from tactic.ui.widget import CalendarInputWdg

from pyasm.web import DivWdg
from pyasm.search import Search
from pyasm.widget import CheckboxWdg, MultiSelectWdg, SubmitWdg, ButtonWdg

from order_builder_utils import get_label_widget, get_select_widget_from_search_type


class OrderTitleEntryWdg(BaseRefreshWdg):
    def get_display(self):
        outer_div = DivWdg()
        outer_div.add_class('new-order-title-entry-form')

        self.get_order_code_select_widget(outer_div)
        self.get_order_entry_widget(outer_div)
        self.get_title_select_widget(outer_div)
        self.get_title_entry_wdg(outer_div)
        self.get_platform_select_widget(outer_div)

        self.get_languages_widget(outer_div)
        self.get_territory_widget(outer_div)
        self.get_description_input_widget(outer_div)
        self.get_total_program_runtime_widget(outer_div)
        self.get_checkboxes_section(outer_div)

        submit_button = SubmitWdg('Submit')
        submit_button.add_behavior(self.submit_button_behavior())

        popup_button = ButtonWdg('Popup')
        popup_button.add_behavior({'css_class': 'popup_click', 'type': 'click_up', 'cbjs_action': 'spt.panel.load_popup("Test", "order_builder.OrderTitleEntryWdg", {});'})
        outer_div.add(popup_button)

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

    if (total_program_runtime) {
        var runtime_re = /^[\d]+:[\d]+$/;
        var match = total_program_runtime.match(runtime_re);

        if (match < 1) {
            throw("Total program runtime must be in the format MM:SS (it can also be left blank).")
        }
    }

    var bigboard;
    var no_charge;
    var redo;
    var repurpose;

    if (values.bigboard == 'on') {
        bigboard = true;
    }
    else {
        bigboard = false;
    }

    if (values.no_charge == 'on') {
        no_charge = true;
    }
    else {
        no_charge = false;
    }

    if (values.redo == 'on') {
        redo = true;
    }
    else {
        redo = false;
    }

    // Set up the object for the new title_order entry.
    var new_title_order = {
        'name': String(values.title_code + " in " + values.order_code),
        'order_code': values.order_code,
        'title_code': values.title_code,
        'platform': values.platform_code,
        'due_date': values.due_date,
        'languages': values.languages,
        'territory': values.territory,
        'description': values.description,
        'total_program_runtime': total_program_runtime,
        'bigboard': bigboard,
        'no_charge': no_charge,
        'redo': redo,
        'repurpose': repurpose
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
    def get_order_code_select_widget(outer_div):
        order_search_filters = [('classification', 'Master', '!='),
                                ('classification', 'Completed', '!='),
                                ('classification', 'Test', '!=')]

        order_select_wdg = get_select_widget_from_search_type('twog/order', 'order_code', 'name', 'code',
                                                              order_search_filters)

        outer_div.add(get_label_widget('Order'))
        outer_div.add(order_select_wdg)

    @staticmethod
    def get_order_entry_widget(outer_div):
        add_order_button = ButtonWdg('New Order')
        add_order_button.set_behavior({'css_class': 'popup_click', 'type': 'click_up', 'cbjs_action': 'spt.panel.load_popup("New Order", "order_builder.OrderEntryWdg", {});'})

        outer_div.add(add_order_button)

    @staticmethod
    def get_title_select_widget(outer_div):
        title_select_wdg = get_select_widget_from_search_type('twog/title', 'title_code', 'title', 'code',
                                                              [('master_title', True)], ['title'])

        outer_div.add(get_label_widget('Title'))
        outer_div.add(title_select_wdg)

    @staticmethod
    def get_title_entry_wdg(outer_div):
        add_order_button = ButtonWdg('New Title')
        add_order_button.set_behavior({'css_class': 'popup_click', 'type': 'click_up', 'cbjs_action': 'spt.panel.load_popup("New Title", "order_builder.TitleEntryPopupWdg", {});'})

        outer_div.add(add_order_button)

    @staticmethod
    def get_platform_select_widget(outer_div):
        platform_select_wdg = get_select_widget_from_search_type('twog/platform', 'platform_code', 'name', 'code')

        outer_div.add(get_label_widget('Platform'))
        outer_div.add(platform_select_wdg)

    @staticmethod
    def get_due_date_widget(outer_div):
        due_date_wdg = CalendarInputWdg('Due Date')
        due_date_wdg.add_class('due_date')

        outer_div.add(get_label_widget('Due Date'))
        outer_div.add(due_date_wdg)

    @staticmethod
    def get_languages_widget(outer_div):
        languages_search = Search('twog/language')

        languages_wdg = MultiSelectWdg('Languages')
        languages_wdg.add_empty_option('----')
        languages_wdg.set_search_for_options(languages_search, label_column='name', value_column='code')

        outer_div.add(get_label_widget('Language'))
        outer_div.add(languages_wdg)

    @staticmethod
    def get_territory_widget(outer_div):
        territory_wdg = get_select_widget_from_search_type('twog/territory', 'territory', 'name', 'code')

        outer_div.add(get_label_widget('Territory'))
        outer_div.add(territory_wdg)

    @staticmethod
    def get_description_input_widget(outer_div):
        description_input = TextAreaInputWdg()
        description_input.set_name('description')
        description_input.add_class('description')

        outer_div.add(get_label_widget('Description'))
        outer_div.add(description_input)

    @staticmethod
    def get_total_program_runtime_widget(outer_div):
        total_program_runtime_input = TextInputWdg()
        total_program_runtime_input.set_name('total_program_runtime')

        outer_div.add(get_label_widget('Total Program Runtime'))
        outer_div.add(total_program_runtime_input)

    @staticmethod
    def get_checkboxes_section(outer_div):
        checkboxes_div = DivWdg()

        bigboard_wdg = CheckboxWdg('bigboard', 'Hot Title?')
        no_charge_wdg = CheckboxWdg('no_charge', 'No Charge')
        redo_wdg = CheckboxWdg('redo', 'Redo')
        repurpose_wdg = CheckboxWdg('repurpose', 'Repurpose')

        bigboard_wdg.get_value()

        checkboxes_div.add(bigboard_wdg)
        checkboxes_div.add(no_charge_wdg)
        checkboxes_div.add(redo_wdg)
        checkboxes_div.add(repurpose_wdg)

        outer_div.add(checkboxes_div)
