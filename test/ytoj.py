import yaml
import json

patch_map = {}
patches = []

with open("./test/patch.yaml") as infile:
  patch_map = yaml.load(infile, Loader=yaml.FullLoader)
  print(patch_map)
  for key in patch_map.keys():
    print(key)
    op = {"op": "add"}
    if key == "tolerations":
      op["path"] =  "/spec/tolerations"
      op["value"] = patch_map[key]
    elif key == "nodeSelectorTerms":
      op["path"] = "/spec/affinity"
      op["value"] = {"nodeAffinity": {"requiredDuringSchedulingIgnoredDuringExecution": {"nodeSelectorTerms": patch_map[key]}}}
    else:
      continue

    patches.append(op)

print(json.dumps(patches))

conf = {}
with open("./test/conf.yaml") as infile:
  conf = yaml.load(infile, Loader=yaml.FullLoader)
  print(conf)

  for key in conf.keys():
    print(key)
    