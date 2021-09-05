tests: unittest

.PHONY: venv
venv:
	if [ ! -d "venv" ]; then python3 -m venv venv; fi
	venv/bin/pip3 install -r requirements.txt

unittest:
	venv/bin/python3 -m unittest

.PHONY: integrationtests
integrationtests:
	venv/bin/python3 -m unittest integrationtest/test_*.py
