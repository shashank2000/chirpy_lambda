#!/bin/bash
# Startup script. Usage: `bash chirp.sh ENV_NAME`

eval "$(conda shell.bash hook)"
conda activate $1

if [[ $(lsof -i:4080) ]]
then
  echo "Already attached to port 4080."
else
  echo "Not yet attached to port 4080. Running portforward.sh..."
  bash portforward.sh &
fi
source env.list
export PYTHONPATH=$(pwd)
python3 agents/remote_non_persistent.py