all: test bdd

test:
	python -m unittest tests/test_*

bdd:
	aloe --stop --detailed-errors --verbose tests/features/*.feature

lint:
	-pylint snptk/*
	-pyflakes snptk/*

