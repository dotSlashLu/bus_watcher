# encoding=utf8
import re
import json
import time
import logging
import requests

from conf import config


logger = logging.getLogger()
UA = ('mozilla/5.0 (linux; u; android 4.1.2; zh-cn; mi-one plus build/jzo54k)'
      ' applewebkit/534.30 (khtml, like gecko) version/4.0 mobile safari/534.'
      '30 micromessenger/5.0.1.352')
ROUTE_UUID = {
    'Z75': '770e7b3f-bd59-4d2b-b5c5-fad3abbadd80'
}
EVENT = 'bus_near'
ERR_EVENT = 'bus_near_err'


def get_stations(route):
    URL = 'http://test.zhbuswx.com/StationList/GetStationList'
    uuid = ROUTE_UUID.get(route)
    if not uuid:
        raise Exception('route uuid not found')
    params = {
        'id': uuid,
        '_': int(time.time() * 1000)
    }
    return requests.get(URL, params=params, headers={'user-agent': UA})


def get_rt(route, dep_station):
    """get bus real-time position
        remote API return example:
        ```
            {
                flag: 1002,
                data: [{
                    BusNumber: "粤C20705",
                    CurrentStation: "唐家",
                    LastPosition: "8"
                },
                {
                    BusNumber: "粤C20709",
                    CurrentStation: "后环",
                    LastPosition: "5"
                }]
            }
        ```
    """
    URL = 'http://test.zhbuswx.com/RealTime/GetRealTime'
    params = {
        'id': route,
        'fromStation': dep_station,
        '_': int(time.time() * 1000)
    }
    return requests.get(URL, params=params, headers={'user-agent': UA})


def notify(event, values=None):
    URL = ('https://maker.ifttt.com/trigger/{event}/with/key/{key}'
            .format(event=event, key=config.ifttt_key))
    if values:
        data = {}
        for i, v in enumerate(values):
            data['value' + str(i + 1)] = v
        requests.post(URL, data=json.dumps(data),
                      headers={'content-type': 'application/json'})
    else:
        requests.post(URL)


def notify_rt(route, dep_station, at):
    req = get_rt(route, dep_station)
    logger.debug('Got result: %s' % req.text)
    res = json.loads(req.text)['data']
    matched = [b for b in res if re.match(at, b['CurrentStation'])]
    if matched:
        notify(EVENT, [matched[0]['CurrentStation']])
        return True
    return False


def notify_err(e):
    notify(ERR_EVENT, [e])


def notify_rt_oneshot(route, dep_station, at, interval=10):
    try:
        route = route.upper()
        while not notify_rt(route, dep_station, at):
            time.sleep(interval)
        return
    except Exception as e:
        notify_err(str(e))


if __name__ == '__main__':
    notify_rt_oneshot('Z75', u'后环', u'公交招呼站2')
