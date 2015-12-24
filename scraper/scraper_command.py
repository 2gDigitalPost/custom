__all__ = ["IMDBImageAssociatorCmd"]

from pyasm.command import Command
from client.tactic_client_lib import TacticServerStub
from pyasm.checkin import FileCheckin
from pyasm.search import Search
import urllib


class IMDBImageAssociatorCmd(Command):
    """
    This appears to be the class that is called when you click "Associate All Selected" on the IMDb Order Associator
    tab. I say 'appears' because I really don't know yet; I didn't write this and it's not documented at all.
    """
    # TODO: Figure out what this really does and update the docstring

    def __init__(self, **kwargs):
        super(IMDBImageAssociatorCmd, self).__init__(**kwargs)
        self.orders = str(kwargs.get('orders_to_associate')).split(',')
        self.server = TacticServerStub.get()

    def check(self):
        return True
    
    def execute(self):
        pic_dict = {}
        pics = []
        order_dict = {}
        for ocode in self.orders:
            ord_s = Search('twog/order')
            ord_s.add_filter('code', ocode)
            order = ord_s.get_sobject()
            if order:
                order_dict[ocode] = order
                poster = order.get_value('imdb_poster_url')
                if poster not in pics:
                    pics.append(poster)
                    pic_dict[poster] = [ocode]
                else:
                    pic_dict[poster].append(ocode)
        pic_places = {}
        number = 0
        for pic in pics:
            extension_s = pic.split('.')
            extension = extension_s[len(extension_s) - 1]
            place = '/var/www/html/imdb_images/associator%s.%s' % (number, extension) 
            f = open(place, 'wb')
            f.write(urllib.urlopen(pic).read())
            f.close()
            pic_places[pic] = place
            number += 1

        for pic in pics:
            server_path = pic_places[pic]
            linked_orders = pic_dict[pic]
            for ocode in linked_orders: 
                sobject = order_dict[ocode]
                if sobject:
                    file_types = ['main']
                    context = "icon"
                    checkin = FileCheckin(
                        sobject,
                        file_paths=server_path,
                        file_types=file_types,
                        context=context,
                        mode="copy"
                    )
                    checkin.execute()

        return ''

    def check_security(self):
        """give the command a callback that allows it to check security"""
        return True

    def get_title(self):
        return "Make Note"
