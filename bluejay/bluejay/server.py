from flask import Flask, render_template, request, send_from_directory
import subprocess
from subprocess import Popen, PIPE, STDOUT
import pexpect
import time
import json 
from collections import defaultdict, OrderedDict

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
 
process = None
import sys
CODE = sys.argv[1] if len(sys.argv) > 2 else "test"
 
#results = subprocess.run(f"export PYTHONPATH=$(pwd) && source env.list && python3 agents/bluejay_agent.py -c {code}", shell=True, cwd="../..")
def reload_chirpy(code): 
	print("Reloading chirpy")
	global process
	process = Popen(
		f"export PYTHONPATH=$(pwd) && source env.list && python3 agents/bluejay_agent.py -c {CODE} 2>&1",
		stdout=PIPE,
		stdin=PIPE,
		stderr=PIPE,
		shell=True,
		cwd="../..",
		text=True,
	)
	
	process.stdout.readline()
	#process.stdout.readline()

	# process = pexpect.spawnu(f'python3 agents/bluejay_agent.py -c {code}', cwd='../..')
	# print('sending line')
	# process.sendline('\n')
	# time.sleep(5)
	# process.expect('')
	# print(process.before)
	# print(process.after)
	
def execute_chirpy(input_line, reset=False):
	code = "cat"
	if process is None or str(reset).lower() == 'true':
		print("Detected chirpy died, restarting...")
		reload_chirpy(code)
	else:
		input = (input_line)
		process.stdin.write(input_line + '\n')
		process.stdin.flush()
	output = process.stdout.readline()
	# open the logs
	with open(f'/tmp/logs/output_{CODE}.log', 'r') as f:
		data = f.read()
		logs = data.split('<<<END TURN>>>')[-2]
	
	full_logs = logs.split('\n\n')
	logs = [log for log in full_logs if 'BLUEJAY' in log[:20]]		
	logs = ['\n'.join(log.split('\n')[1:]) for log in logs]
	log_outputs = {}
	for line in logs:
		if ':' not in line:
			continue
		tag, value = line.split(':', maxsplit=1)
		tag = tag.strip()
		value = value.strip()
		log_outputs[tag] = value
	
	return output, log_outputs, full_logs
	#return line
	
def augment_result(result):
	logs = result['logs']
	for key in ['rg_state']:
		if key in logs:
			result['rg_state'] = json.loads(logs['rg_state'])
	supernodes = defaultdict(lambda: {"entry_conditions": [], "available": False, "chosen": False, "score": 0})
	subnodes = defaultdict(lambda: {"entry_conditions": [], "available": False, "chosen": False})
	prompts = defaultdict(lambda: {"entry_conditions": [], "available": False, "chosen": False})

	for key, value in logs.items():
		if 'predicate_supernode_entry_conditions' in key:
			_, supernode_name, variable_name = key.split('//')
			supernodes[supernode_name]['entry_conditions'].append(json.loads(value))
		if 'predicate_subnode_entry_conditions' in key:
			_, subnode_name, variable_name = key.split('//')
			subnodes[subnode_name]['entry_conditions'].append(json.loads(value))
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
				
	if 'supernode_chosen' in logs:
		supernodes[logs['supernode_chosen']]['chosen'] = True
		
	supernodes = OrderedDict(sorted(supernodes.items(), key=lambda kv: kv[1]['score'] + kv[1]['available'], reverse=True))
	
	result['supernodes'] = supernodes
	
	
	if 'subnodes_chosen' in logs:
		subnodes[logs['subnodes_chosen']]['chosen'] = True
	result['subnodes'] = OrderedDict(sorted(subnodes.items(), key=lambda kv: kv[1]['available'] + kv[1]['chosen'], reverse=True))
		
	if 'prompts_chosen' in logs:
		prompts[logs['prompts_chosen']]['chosen'] = True
	result['prompts'] = OrderedDict(sorted(prompts.items(), key=lambda kv: kv[1]['available'] + kv[1]['chosen'], reverse=True))
		
		
	if 'rg_state' in logs:
		result['rg_state'] = json.loads(logs['rg_state'])	
	
	
@app.route("/api/ping")
def main():
	input_line = request.args.get('input', 'hi')
	reset = request.args.get('reset', False)
	output, logs, full_logs = execute_chirpy(input_line, reset=reset)
	result = {
		"text": output,
		"logs": logs,
		"full_logs": full_logs,
	}
	augment_result(result)
		
	return result

@app.route("/api/reset")
def reset():
	reload_chirpy(code='cat')
	return "Reset."


@app.route("/")
def frontpage():
	return send_from_directory('static', 'index.html')


if __name__ == '__main__':
	if len(sys.argv) > 2:
		while True:
			input_line = input('> ')
			output, logs, full_logs = execute_chirpy(input_line)
			result = {
				"text": output,
				"logs": logs,
				#"full_logs": full_logs,
			}
			augment_result(result)
			print('output::', output)
			print('logs::', json.dumps(logs, indent=2))
			print('result::', json.dumps(result, indent=2))
	else:
		app.run(host='0.0.0.0', port=8765, debug=True)