#!/bin/bash

source env/bin/activate
echo ""
echo "checking for linting errors"
flake8 --select E,W --max-line-length=140 --ignore E722,W503,W504,E128 ausis/ installer
echo "lint errors checked"
echo ""
(
cd ausis || exit
echo "checking for unit test"
python3 -m unittest discover
echo "unit tests checked"
echo ""
)