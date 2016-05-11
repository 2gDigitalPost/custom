from tactic.ui.common import BaseRefreshWdg
from tactic.ui.input import TextInputWdg

from pyasm.web import DivWdg
from pyasm.widget import SubmitWdg

from order_builder_utils import get_label_widget, get_select_widget_from_search_type


class OrderEntryWdg(BaseRefreshWdg):
    def get_display(self):
        outer_div = DivWdg()
        outer_div.add_class('new-order-entry-form')

        order_name_input = TextInputWdg()
        order_name_input.set_name('name')

        outer_div.add(get_label_widget('Name'))
        outer_div.add(order_name_input)

        po_number_input = TextInputWdg()
        po_number_input.set_name('po_number')

        outer_div.add(get_label_widget('PO Number'))
        outer_div.add(po_number_input)

        client_select_wdg = get_select_widget_from_search_type('twog/client', 'client', 'name', 'code')

        outer_div.add(get_label_widget('Client'))
        outer_div.add(client_select_wdg)

        sales_rep_select_wdg = get_select_widget_from_search_type('sthpw/login_in_group', 'Client', 'login_full_name',
                                                                  'code', [('login_group', 'sales')])

        outer_div.add(get_label_widget('Sales Rep'))
        outer_div.add(sales_rep_select_wdg)

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
    function submit_form() {
        spt.api.app_busy_show('Saving...');

        var client_code = values.client;

        // Set up the object for the new title. Note that 'master_title' is always set to true.
        var new_order = {
            'name': values.name,
            'po_number': values.po_number,
            'client_code': client_code
        }

        var server = TacticServerStub.get();

        // Have to set 'triggers' to false to avoid all the other stupid custom crap. Will remove once this method
        // of inserting becomes the norm.
        server.insert('twog/order', new_order, {'triggers': false});

        spt.api.app_busy_hide();
    }

    // Get the form values
    var outer_div = spt.api.get_parent(bvr.src_el, '.new-order-entry-form');
    var values = spt.api.get_input_values(outer_div);

    if (!values.client || values.client == '') {
        spt.api.app_busy_hide();
        spt.alert("Please select a client.");
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
