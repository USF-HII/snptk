all: test lint

test:
	python -m unittest tests/test_*

bdd:
	aloe -vd tests/features/*.feature

lint:
	-pylint snptk/*
	-pyflakes snptk/*

