from flask import Flask
from flask import request
from multiprocessing import Process

import util
from conf import config
from main import notify_rt_oneshot


app = Flask(__name__)
logger = util.setup_logger()



@app.route("/")
def hello():
    logger.debug('123')
    return "Hello World!"


@app.route("/bus_watcher", methods=['POST'])
def bus_watcher():
    data = request.json
    route = data['route']
    dep_station = data['dep_station']
    at = data['at']

    t = Process(target=notify_rt_oneshot, args=(route, dep_station, at))
    t.deamon = True
    t.start()

    return "Enabled notify for bus %s from %s when it's at %s" % (route,
                                                                  dep_station,
                                                                  at)


app.run(host="0.0.0.0", port=config.port, debug=config.debug)
