all: install

install:
	python setup.py install

develop:
	python setup.py develop

publish:
	pandoc README.md -o README.rst
	python setup.py register sdist upload
