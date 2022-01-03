import os.path as osp
from pathlib import Path
import webbrowser
import json
import requests
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.config["DEBUG"] = True
chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s' # default Chrome path for Windows

def create_missing_directories(output_path):
    dirs = osp.split(output_path)[0]
    if not osp.exists(dirs):
        Path(dirs).mkdir(parents=True, exist_ok=True)

@app.route("/")
def index():
    return redirect(url_for('inputs'))

@app.route("/inputs", methods=['GET', 'POST'])
def inputs():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        mode = 'i' #request.form['mode']
        arg = None
        if mode == 'i':
            arg = request.form['ip']
        else:
            arg = request.form['file']
        payload = {'mode':mode,
                'log': '*', #request.form['log'],
                'host':'AGENT_HOST', # specify IP of agent host
                'arg':arg,
                'time':request.form['time'],
                'out':request.form['out']}
        r = requests.get('http://CONTROLLER_HOST_ADDRESS:PORT/run', params=payload) # specify IP and port of controller host
        # Note: there is a port mapping from bmj-cluster port 13680 to node-ovs port 8000
        import time; time.sleep(2)
        json_str = json.dumps(r.json(), indent = 4)
        out_path = osp.join("json", request.form['out'])
        create_missing_directories(out_path)
        with open(out_path, "w") as output:
            output.write(json_str)
        parent_dir = Path(__file__).parent.resolve()
        webbrowser.get(chrome_path).open("file://"+ osp.realpath(osp.join(parent_dir, "index.html")), new=2)
        return render_template('index.html', completed="Sniffing completed.")