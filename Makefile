test:
	pytest --tb=short --verbosity=2

watch-tests:
	ls *.py | entr pytest --tb=short --verbosity=2

black:
	black -l 86 $$(find * -name '*.py')
