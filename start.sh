# script for running in development environement

export FLASK_APP=main.py
export FLASK_DEBUG=1
export FLASK_ENV=development


script_name=$0
script_full_path=$(dirname "$0")
register_findb_script="$script_full_path/register_findb.py"

python $register_findb_script && echo $register_findb_script succeeded || echo $register_findb_script failed


flask run
