PYTHON ?= python

.PHONY: install test run webhook deploy rollback status

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest -q

run:
	$(PYTHON) -m warden.cli run

webhook:
	$(PYTHON) -m warden.cli webhook 5000

deploy:
	$(PYTHON) -m warden.cli deploy latest

rollback:
	$(PYTHON) -m warden.cli rollback

status:
	$(PYTHON) -m warden.cli status
