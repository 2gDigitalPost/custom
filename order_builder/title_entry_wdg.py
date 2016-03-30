from tactic.ui.common import BaseRefreshWdg
from tactic.ui.input import TextInputWdg
from tactic.ui.widget import CalendarWdg

from pyasm.web import DivWdg
from pyasm.search import Search
from pyasm.widget import MultiSelectWdg, SelectWdg

from order_builder_utils import get_label_widget, get_select_widget_from_search_type


class TitleEntryWdg(BaseRefreshWdg):
    def get_display(self):
        outer_div = DivWdg()

        order_name_input = TextInputWdg()

        outer_div.add(get_label_widget('Name'))
        outer_div.add(order_name_input)

        return outer_div
