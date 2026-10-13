import os
from flask import request

@app.route("/download")
def download():
    filename = request.args.get("file")
    path = os.path.join("/var/data", filename)
    with open(path) as f:      # 🚩
        return f.read()

#from pathlib import Path
#base = Path("/var/data").resolve()
#target = (base / filename).resolve()
#if not str(target).startswith(str(base) + os.sep):
#    abort(403)
