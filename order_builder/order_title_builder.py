from tactic.ui.common import BaseRefreshWdg
from tactic.ui.input import TextInputWdg
from tactic.ui.widget import CalendarWdg

from pyasm.web import DivWdg
from pyasm.search import Search
from pyasm.widget import MultiSelectWdg, SelectWdg

from order_builder_utils import get_label_widget, get_select_widget_from_search_type


class OrderTitleEntryWdg(BaseRefreshWdg):
    def get_display(self):
        outer_div = DivWdg()

        order_name_input = TextInputWdg()

        outer_div.add(get_label_widget('Order Name'))
        outer_div.add(order_name_input)

        client_select_wdg = get_select_widget_from_search_type('twog/client', 'Client', 'name', 'code')

        outer_div.add(get_label_widget('Client'))
        outer_div.add(client_select_wdg)

        platform_select_wdg = get_select_widget_from_search_type('twog/platform', 'Platform', 'name', 'code')

        outer_div.add(get_label_widget('Platform'))
        outer_div.add(platform_select_wdg)

        title_select_wdg = get_select_widget_from_search_type('twog/title', 'Title', 'title', 'code',
                                                              {'master_title': True})

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

        return outer_div

    @staticmethod
    def get_languages_widget():
        languages_search = Search('twog/language')

        languages_wdg = MultiSelectWdg('Languages')
        languages_wdg.add_empty_option('----')
        languages_wdg.set_search_for_options(languages_search, label_column='name', value_column='code')

        return languages_wdg
