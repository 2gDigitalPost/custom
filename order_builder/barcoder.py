from tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseRefreshWdg

from pyasm.search import Search


class Barcoder(BaseRefreshWdg):
    def init(my):
        my.server = TacticServerStub.get()
        my.order_sk = ''
        if 'order_sk' in my.kwargs.keys():
            my.order_sk = str(my.kwargs.get('order_sk'))

    def get_new_barcode(my, deliverable):
        new_bc = 'XsXsXsXsX'
        repeat = True
        while repeat:
            last_search = Search("twog/barcode")
            last_search.add_filter('name','The only entry')
            last_bc = last_search.get_sobject()
            last_num = int(last_bc.get_value('number'))
            new_num = last_num + 1
            my.server.update(last_bc.get_search_key(), {'number': new_num})
            new_bc = "2GV%s" % new_num
            if deliverable == 'true':
                new_bc = "2GV%s" % new_num
            bc_search = Search("twog/source")
            bc_search.add_filter('barcode',new_bc)
            bc_sources = bc_search.get_sobjects()
            if len(bc_sources) < 2:
               repeat = False

        return new_bc
