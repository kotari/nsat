from flask import Flask, request, jsonify
import logging
import base64
import yaml
import json

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

conf = {}
with open("./rules.yaml") as infile:
  conf = yaml.load(infile, Loader=yaml.FullLoader)

@app.route('/')
def hello_world():
  return "Hello self signed certificate is working"

@app.route('/nsathook', methods=['POST'])
def namespace_toleration_webhook():
  request_info = request.get_json()
  app.logger.info(request_info)
  if (request_info["apiVersion"] != "admission.k8s.io/v1" or request_info["kind"] != "AdmissionReview"):
    return jsonify(message="Wrong apiVersion or kind: " + request_info["apiVersion"] + " - " + request_info["kind"]), 400

  req = request_info["request"]
  uid = req.get("uid")
  resp = {}
  resp["apiVersion"] = request_info["apiVersion"]
  resp["kind"] = request_info["kind"]
  resp["response"] = {}
  resp["response"]["uid"] = uid
  resp["response"]["allowed"] = True

  # patch the pod
  if (req["kind"]["group"] == "" and req["kind"]["version"] == "v1" and req["kind"]["kind"] == "Pod" and req["operation"] == "CREATE") :
    patches = []
    if conf.get(req["namespace"]) is not None:
      # do something
      patches.append({"op": "add", "path": "/metadata/labels/nsatRuleFound", "value": "True"})
      rules = conf.get(req["namespace"])
      for key in rules.keys():
        op = {"op": "add"}
        if key == "tolerations":
          op["path"] =  "/spec/tolerations"
          op["value"] = rules[key]
        elif key == "nodeSelectorTerms":
          op["path"] = "/spec/affinity"
          op["value"] = {"nodeAffinity": {"requiredDuringSchedulingIgnoredDuringExecution": {"nodeSelectorTerms": rules[key]}}}
        else:
          continue
        patches.append(op)
    else:
      patches.append({"op": "add", "path": "/metadata/labels/nsatRuleFound", "value": "False"})

    resp["response"]["patchType"] = "JSONPatch"
    resp["response"]["patch"] = base64.standard_b64encode(json.dumps(patches).encode("ascii")).decode("utf-8")
  app.logger.info(resp)
  return jsonify(resp)

if __name__ == '__main__':
  app.run(ssl_context=('certs/servercrt.pem', 'certs/serverkey.pem'),debug=True)
  # app.run(debug=True)
