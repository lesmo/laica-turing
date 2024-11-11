#!/usr/bin/env python3
from typing import Dict
from cereal import messaging
from openpilot.common.params import Params
from openpilot.common.realtime import set_core_affinity
from openpilot.common.swaglog import cloudlog
from flask import Flask, jsonify, make_response

from openpilot.selfdrive.laica.util import capnp_to_json


app = Flask(__name__)
sm_map: Dict[str, messaging.SubMaster] = {}

params_reader = Params()
params_memory = Params("/dev/shm/params")


@app.errorhandler(500)
def internal_error(error):
  return jsonify({"error": error})

@app.route('/data/<service>', methods=['GET'])
def data(service):
  sm = sm_map.get(service, None)

  if sm is None:
    sm = messaging.SubMaster([service])
    sm_map[service] = sm
  
  sm.update()

  json = capnp_to_json(sm[service])
  res = make_response(json)
  res.headers['Content-Type'] = 'application/json'

  return res

@app.route('/params/<key>', methods=['GET'])
def params(key):
  data = params_memory.get(key)
  res = make_response(data or '{}')
  res.headers['Content-Type'] = 'application/json'

  return res

@app.route('/params_memory/<key>', methods=['GET'])
def params_memory(key):
  data = params_memory.get(key)
  res = make_response(data or '{}')
  res.headers['Content-Type'] = 'application/json'

  return res

def main():
  try:
    set_core_affinity([0, 1, 2, 3])
  except Exception:
    cloudlog.exception("laica: failed to set core affinity")

  app.run(host="0.0.0.0", port=1414)


if __name__ == '__main__':
  main()
