from flask import Flask, render_template, request
import subprocess
from subprocess import Popen, PIPE, STDOUT
import pexpect
import time

app = Flask(__name__)
 
process = None
import sys
CODE = sys.argv[1]
 
#results = subprocess.run(f"export PYTHONPATH=$(pwd) && source env.list && python3 agents/bluejay_agent.py -c {code}", shell=True, cwd="../..")
def reload_chirpy(code): 
	print("Reloading chirpy")
	global process
	process = Popen(
		f"export PYTHONPATH=$(pwd) && source env.list && python3 agents/bluejay_agent.py -c abcde",
		stdout=PIPE,
		stdin=PIPE,
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
	
def execute_chirpy(input_line):
	code = "cat"
	if process is None:
		print("Detected chirpy died, restarting...")
		reload_chirpy(code)
	else:
		input = (input_line)
		process.stdin.write(input_line + '\n')
		process.stdin.flush()
	return process.stdout.readline()
	#return line

@app.route("/api/ping")
def main():
	input_line = request.args.get('input', 'hi')
	output = execute_chirpy(input_line)
	return {
		"text": output,
		"rg_state": {
			"Food__UserFavoriteFood": "mashed potatoes",
			"Global__UserName": "Em",
		},
		"subnodes": {
			"Global__Thingy": {
				"available": True,
				"chosen": True,
			},
			"Global__Thingy23": {
				"available": True,
				"chosen": False,
			}
		},
		"supernodes": {
			"Global__Thingy": {
				"available": True,
				"chosen": True,
			},
			"Global__Thingy23": {
				"available": True,
				"chosen": False,
			}
		}
	}

@app.route("/api/reset")
def reset():
	reload_chirpy(code='cat')
	return "Reset."


if __name__ == '__main__':
	if len(sys.argv) > 2:
	
		while True:
			input_line = input('> ')
			output = execute_chirpy(input_line)
			print('output::', output)
	else:
		app.run(host='0.0.0.0', port=8765, debug=True)