#!/usr/bin/env python3
import capnp

from cereal import messaging
from openpilot.common.realtime import set_core_affinity
from openpilot.common.swaglog import cloudlog
from flask import Flask, jsonify


def capnp_to_dict(capnp_obj):
    # Convert capnp._DynamicStructReader to a dictionary recursively
    result = {}
    for field in capnp_obj.schema.fields:
        value = getattr(capnp_obj, field)
        if isinstance(value, capnp._DynamicStructReader):
            result[field] = capnp_to_dict(value)
        else:
            result[field] = value
    return result


app = Flask(__name__)

@app.errorhandler(500)
def internal_error(error):
  return jsonify({"error": error})

@app.route('/data/<service>', methods=['GET'])
def data(service):
  sm = messaging.SubMaster([service])
  sm.update()

  return jsonify(capnp_to_dict(sm[service]))


def main():
  try:
    set_core_affinity([0, 1, 2, 3])
  except Exception:
    cloudlog.exception("laica: failed to set core affinity")

  app.run(host="0.0.0.0", port=1414)


if __name__ == '__main__':
  main()
