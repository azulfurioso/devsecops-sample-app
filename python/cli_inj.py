import os
from flask import request

@app.route("/ping")
def ping():
    host = request.args.get("host")
    return os.popen(f"ping -c 1 {host}").read()  # 🚩
    # fix
    # import subprocess
    # subprocess.run(["ping", "-c", "1", host], shell=False, check=True)
