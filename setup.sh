#!/usr/bin/env bash
# This copy is PRE-SETUP: the database already has the press, all 9 journals,
# sample issues/articles and your superuser account built in.
# This script only needs to install Python packages into a virtual environment.
# Run it once:  bash setup.sh
set -e
cd "$(dirname "$0")"
PY=${PYTHON_BIN:-}
if [ -z "$PY" ]; then for c in python3.12 python3.11 python3.10 python3; do command -v $c >/dev/null 2>&1 && PY=$c && break; done; fi
echo "Using $PY"
[ -d .venv ] || $PY -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo
echo "=========================================================="
echo " DONE.  Start the website with:  bash run.sh"
echo " Then open http://localhost:8000/"
echo " Log in with the email kunalrajpurohit@glcmumbai.example"
echo " and the password you were given separately."
echo " (Janeway logs in by email, not by a plain username.)"
echo " Change the password the first time you log in."
echo "=========================================================="
