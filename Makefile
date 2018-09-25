all:
	pylint snptk/*
	pyflakes snptk/*
	python -m unittest tests/test_*
