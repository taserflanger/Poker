import json

d = {"an": 12, "a": "andres", "c": [1, 2, 3], "d": {"a": 2}}
d = json.dumps(d)
a = d.encode("utf-8")
c = {"b": [{"andres": None} for i in range(3)]}
c = json.dumps(c)
a = c.encode("utf-8")
c = {"a": [{"andres": None} for i in range(3)], "flag": 1000}
c = json.dumps(c)
a = c.encode("utf-8")
