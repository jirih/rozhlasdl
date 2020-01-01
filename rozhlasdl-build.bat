@echo off
rmdir /s /q build dist rozhlasdl.egg-info
python setup.py sdist bdist_wheel