all: test lint

test:
	python -m unittest tests/test_*

lint:
	-pylint snptk/*
	-pyflakes snptk/*

