"""
A collection of functions that are used in the hot list classes, but don't need to be part of the classes themselves.

Note that for the time being, I'm just copying the functions from their classes and removing the 'self' argument.
These functions could use some serious rewriting. I hope to get to that soon.

Author: Tyler Standridge
"""

import datetime
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


def get_dates_and_colors(date, date_str, due_date):
    date_time = date.split(' ')
    sdate = date_time[0]
    stime = ''

    if len(date_time) > 2:
        stime = date_time[2]
        if stime in [None, '', '00:00:00', '00:00']:
            stime = ''
    elif len(date_time) > 1:
        stime = date_time[1]
        if stime in [None, '', '00:00:00', '00:00']:
            stime = ''

    stime_s = stime.split(':')

    if len(stime_s) > 2:
        stime = '%s:%s' % (stime_s[0], stime_s[1])

    better_lookin_date = date_str
    color = '#FFFFFF'

    if sdate not in [None, '']:
        this_date = datetime.datetime.strptime(sdate, '%Y-%m-%d')

        if this_date == due_date:
            # Due today, yellow
            color = "#E0B600"
        elif this_date < due_date:
            # Past due, red
            color = "#FF0000"
        else:
            # Due in the future
            color = "#66CD00"

        tdds = sdate.split('-')
        tyear = ''
        tmonth = ''
        tday = ''

        if len(tdds) == 3:
            tyear = tdds[0]
            tmonth = tdds[1]
            tday = tdds[2]
        better_lookin_date = '%s/%s/%s' % (tmonth, tday, tyear)

        if better_lookin_date == '//':
            better_lookin_date = date_str

    if stime not in [None, '']:
        stime_s = stime.split(':')
        hour = stime_s[0]
        am_pm = 'AM'
        hour_str = hour

        if hour == '00':
            hour_str = '12'
        elif int(hour) < 12:
            am_pm = 'AM'
        else:
            hour_str = str(int(hour) - 12)
            am_pm = 'PM'

        stime = '%s:%s %s' % (hour_str, stime_s[1], am_pm)
        better_lookin_date = '%s &nbsp;&nbsp;&nbsp;%s' % (better_lookin_date, stime)

    return (better_lookin_date, color)
