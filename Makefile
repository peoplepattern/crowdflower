all: develop README.rst

develop:
	python setup.py develop

install:
	python setup.py install

README.rst: README.md
	pandoc README.md -o $@

publish: README.rst
	python setup.py register sdist upload
