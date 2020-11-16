#!/bin/bash
rm dist/rozhlasdl-0.9.??-py3-none-any.whl
python setup.py sdist bdist_wheel
pip install -I dist/rozhlasdl-0.9.??-py3-none-any.whl
