from tactic.ui.input import TextInputWdg, TextAreaInputWdg
from tactic.ui.widget import CalendarInputWdg

from order_builder.order_builder_utils import get_label_widget, get_select_widget_from_search_type


def get_process_widget(outer_div):
    process_input = TextInputWdg()
    process_input.set_name('process')

    outer_div.add(get_label_widget('Process'))
    outer_div.add(process_input)


def get_assigned_to_select_widget(outer_div):
    user_search_filters = [('login_group', 'onboarding')]
    assigned_to_select_widget = get_select_widget_from_search_type('sthpw/login_in_group', 'login', 'login', 'code',
                                                                   user_search_filters)
    assigned_to_select_widget.set_name('assigned')

    outer_div.add(get_label_widget('Assigned To'))
    outer_div.add(assigned_to_select_widget)


def get_description_widget(outer_div):
    description_input = TextAreaInputWdg(name='description')
    description_input.add_class('description')

    outer_div.add(get_label_widget('Description'))
    outer_div.add(description_input)


def get_priority_widget(outer_div):
    priority_input = TextInputWdg()
    priority_input.set_name('priority')

    outer_div.add(get_label_widget('Priority'))
    outer_div.add(priority_input)


def get_due_date_widget(outer_div):
    due_date_wdg = CalendarInputWdg('Due Date')
    due_date_wdg.add_class('due_date')
    due_date_wdg.set_name('due_date')

    outer_div.add(get_label_widget('Due Date'))
    outer_div.add(due_date_wdg)
