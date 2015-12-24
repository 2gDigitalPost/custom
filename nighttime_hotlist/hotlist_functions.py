"""
A collection of functions that are used in the hot list classes, but don't need to be part of the classes themselves.

Note that for the time being, I'm just copying the functions from their classes and removing the 'self' argument.
These functions could use some serious rewriting. I hope to get to that soon.

Author: Tyler Standridge
"""

from tactic_client_lib import TacticServerStub
from pyasm.search import Search


def get_platform_img(platform):
    # TODO: Looks nearly identical to get_client_img, possibly merge the two into one function
    img_path = ''
    platform_search = Search("twog/platform")
    platform_search.add_filter('name', platform)
    platform = platform_search.get_sobject()
    platform_id = platform.get_id()
    snaps_s = Search("sthpw/snapshot")
    snaps_s.add_filter('search_id', platform_id)
    snaps_s.add_filter('search_type', 'twog/platform?project=twog')
    snaps_s.add_filter('is_current', '1')
    snaps_s.add_filter('version', '0', op='>')
    snaps_s.add_where("\"context\" in ('publish','icon','MISC')")
    snaps_s.add_order_by('timestamp desc')
    snaps = snaps_s.get_sobjects()
    if len(snaps) > 0:
        server = TacticServerStub.get()
        snap = snaps[0]
        img_path = server.get_path_from_snapshot(snap.get_code(), mode="web")
        if img_path not in [None, '']:
            img_path = 'http://' + server.get_server_name() + img_path
    return img_path


def get_client_img(client_code):
    # TODO: Looks nearly identical to get_platform_img, possibly merge the two into one function
    img_path = ''
    client_search = Search("twog/client")
    client_search.add_filter('code', client_code)
    client = client_search.get_sobject()
    client_id = client.get_id()
    snaps_s = Search("sthpw/snapshot")
    snaps_s.add_filter('search_id', client_id)
    snaps_s.add_filter('search_type', 'twog/client?project=twog')
    snaps_s.add_filter('is_current', '1')
    snaps_s.add_filter('version', '0', op='>')
    snaps_s.add_where("\"context\" in ('publish','icon','MISC')")
    snaps_s.add_order_by('timestamp desc')
    snaps = snaps_s.get_sobjects()
    if len(snaps) > 0:
        server = TacticServerStub.get()
        snap = snaps[0]
        img_path = server.get_path_from_snapshot(snap.get_code(), mode="web")
        if img_path not in [None, '']:
            img_path = 'http://' + server.get_server_name() + img_path
    return img_path
