from flask import Flask, render_template, request, send_from_directory
import subprocess
from subprocess import Popen, PIPE, STDOUT
import pexpect
import time
import json
import os
from collections import defaultdict, OrderedDict
from flask_cors import CORS

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
CORS(app, origins=[r'https://chirpycardinal-22-23-\w*-stanfordnlp.vercel.app', 'https://bluejay.vercel.app'])

process = None
import sys

CODE = sys.argv[1] if len(sys.argv) > 2 else "test"

# results = subprocess.run(f"export PYTHONPATH=$(pwd) && source env.list && python3 agents/bluejay_agent.py -c {code}", shell=True, cwd="../..")
def reload_chirpy(code):
    print("Reloading chirpy")
    global process
    process = Popen(
        f"export PYTHONPATH=$(pwd) && python3 agents/bluejay_agent.py -c {CODE} 2>&1",
        stdout=PIPE,
        stdin=PIPE,
        stderr=PIPE,
        shell=True,
        cwd="../..",
        text=True,
    )

    process.stdout.readline()


def execute_chirpy(input_line, reset=False, **kwargs):
    if len(kwargs):
        input_line += "///" + json.dumps(kwargs)
    if process is None or str(reset).lower() == "true":
        print("Detected chirpy died, restarting...")
        reload_chirpy(CODE)
    else:
        process.stdin.write(input_line + "\n")
        process.stdin.flush()
    output = process.stdout.readline()
    # open the logs

    with open(f"/tmp/logs/output_{CODE}.log", "r") as f:
        data = f.read()
        if "<<<END TURN>>>" in data:
            logs = data.split("<<<END TURN>>>")[-2]
        else:
            logs = "[BLUEJAY]\nerror: Error: Unable to parse logs."

    full_logs = logs.split("\n\n")
    logs = [log for log in full_logs if "BLUEJAY" in log[:20]]
    logs = ["\n".join(log.strip().split("\n")[1:]) for log in logs]
    logs = [x for x in logs if len(x)]
    log_outputs = {}
    for line in logs:
        if ":" not in line:
            continue
        tag, value = line.split(":", maxsplit=1)
        tag = tag.strip()
        value = value.strip()
        log_outputs[tag] = value

    if "error" in log_outputs:
        output = "Error"
        error = log_outputs["error"]
    else:
        error = ""

    return output, log_outputs, full_logs, error
    # return line


FALSY = ["False", "0", "None"]


def augment_result(result):
    logs = result["logs"]
    for key in ["rg_state"]:
        if key in logs:
            result["rg_state"] = json.loads(logs["rg_state"])
    supernodes = defaultdict(
        lambda: {
            "entry_conditions": [],
            "available": False,
            "chosen": False,
            "score": 0,
        }
    )
    subnodes = defaultdict(lambda: {"entry_conditions": [], "available": False, "chosen": False})
    prompts = defaultdict(lambda: {"entry_conditions": [], "available": False, "chosen": False})

    for key, value in logs.items():
        if "predicate_supernode_entry_conditions" in key:
            _, supernode_name, variable_name = key.split("//")
            supernodes[supernode_name]["entry_conditions"].append(json.loads(value))
        if "predicate_subnode_entry_conditions" in key:
            _, subnode_name, variable_name = key.split("//")
            subnodes[subnode_name]["entry_conditions"].append(json.loads(value))
        if key == "supernodes":
            for (name, data) in json.loads(value).items():
                supernodes[name]["score"] = data["score"]
                supernodes[name]["available"] = True
        if key == "subnodes":
            for (name, data) in json.loads(value).items():
                subnodes[name]["available"] = True
        if key == "prompts":
            for (name, data) in json.loads(value).items():
                prompts[name]["available"] = True

    if "supernode_chosen" in logs:
        supernodes[logs["supernode_chosen"]]["chosen"] = True

    supernodes = OrderedDict(
        sorted(
            supernodes.items(),
            key=lambda kv: kv[1]["score"] + kv[1]["available"],
            reverse=True,
        )
    )

    result["supernodes"] = supernodes

    if "subnodes_chosen" in logs:
        subnodes[logs["subnodes_chosen"]]["chosen"] = True
    result["subnodes"] = OrderedDict(
        sorted(
            subnodes.items(),
            key=lambda kv: kv[1]["available"] + kv[1]["chosen"],
            reverse=True,
        )
    )

    if "prompts_chosen" in logs:
        prompts[logs["prompts_chosen"]]["chosen"] = True
    result["prompts"] = OrderedDict(
        sorted(
            prompts.items(),
            key=lambda kv: kv[1]["available"] + kv[1]["chosen"],
            reverse=True,
        )
    )

    if "rg_state" in logs:
        rg_state = json.loads(logs["rg_state"])
        rg_state = {k: {"value": v, "falsy": v in FALSY} for k, v in rg_state.items()}
        print(rg_state)
        result["rg_state"] = OrderedDict(sorted(rg_state.items(), key=lambda kv: kv[1]["falsy"]))

    result["stop"] = "stop" in logs


@app.route("/api/ping")
def main():
    input_line = request.args.get("input", "hi")
    reset = request.args.get("reset", False)
    kwargs = json.loads(request.args.get("kwargs", "{}"))
    if kwargs:
        input_line += "////" + json.dumps(kwargs)
    output, logs, full_logs, error = execute_chirpy(input_line, reset=reset)
    result = {
        "text": output,
        "logs": logs,
        "full_logs": full_logs,
        "error": error,
    }
    augment_result(result)

    return result


@app.route("/api/reset")
def reset():
    reload_chirpy(code="cat")
    return "Reset."


@app.route("/api/supernodes")
def get_supernodes():
    BASE_PATH = os.path.dirname(os.path.realpath(__file__))
    active_supernodes_path = os.path.join(BASE_PATH, "..", "..", "chirpy", "symbolic_rgs", "active_supernodes.list")
    with open(active_supernodes_path, "r") as f:
        out = [x.strip() for x in f]
    out = [x for x in out if not x.startswith("#")]
    out = [x for x in out if x]
    return {"supernodes": out}


@app.route("/")
def frontpage():
    return send_from_directory("static", "index.html")


if __name__ == "__main__":
    if len(sys.argv) > 2:
        while True:
            input_line = input("> ")
            output, logs, full_logs, error = execute_chirpy(input_line)
            result = {
                "text": output,
                "logs": logs,
                # "full_logs": full_logs,
            }
            augment_result(result)
            print("output::", output)
            print("logs::", json.dumps(logs, indent=2))
            print("result::", json.dumps(result, indent=2))
            print("error::", error)
    else:
        app.run(host="0.0.0.0", port=8765, debug=True)
