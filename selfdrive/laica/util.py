import json
import capnp

class CapnpEncoder(json.JSONEncoder):
  """CapnpEncoder is a JSONEncoder that can encode capnp messages.

  See: https://github.com/capnproto/pycapnp/issues/28
  """

  DYNAMIC_ENUM_MARKER = "_de_"

  def default(self, obj):
    if isinstance(obj, capnp.lib.capnp._DynamicStructBuilder) or isinstance(obj, capnp.lib.capnp._DynamicStructReader):
      return obj.to_dict()
    return json.JSONEncoder.default(self, obj)
  

def capnp_to_json(message):
  return json.dumps(message, cls=CapnpEncoder)


def json_to_capnp(capnp_message_type, json_string):
    loaded_dict = json.loads(json_string)
    return capnp_message_type.new_message(**loaded_dict)
