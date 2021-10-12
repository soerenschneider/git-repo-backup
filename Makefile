tests: unittest

.PHONY: venv
venv:
	if [ ! -d "venv" ]; then python3 -m venv venv; fi
	venv/bin/pip3 install -r requirements.txt

pylint:
	if [ ! -d "venv" ]; then python3 -m venv venv; fi
	venv/bin/pip3 install pylint
	PYTHONPATH=git_repo_backup venv/bin/pylint git_repo_backup/*.py

unittest: venv
	venv/bin/python3 -m unittest

.PHONY: integrationtests
integrationtests:
	venv/bin/python3 -m unittest integrationtest/test_*.py

smoketest: venv
	PYTHONPATH=git_repo_backup venv/bin/python3 git_repo_backup -c contrib/example-smoketest.json -d /tmp
