VARIABLE_SECRETS_DIR ?= '~/mocha/secrets'


test:
	./epvenv39/Scripts/python -m pytest tests

test_only:
	./epvenv39/Scripts/python -m pytest tests/$(case).py -k $(k)