#!/usr/bin/env python3
from cereal import messaging
from openpilot.common.realtime import set_core_affinity
from openpilot.common.swaglog import cloudlog
from flask import Flask, jsonify, make_response

from .util import capnp_to_json


app = Flask(__name__)

@app.errorhandler(500)
def internal_error(error):
  return jsonify({"error": error})

@app.route('/data/<service>', methods=['GET'])
def data(service):
  sm = messaging.SubMaster([service])
  sm.update()

  json = capnp_to_json(sm[service])
  res = make_response(json)
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
