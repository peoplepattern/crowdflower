from setuptools import setup, find_packages

setup(
    name='crowdflower',
    version='0.1.2',
    author='Christopher Brown',
    author_email='io@henrian.com',
    url='https://github.com/peoplepattern/crowdflower',
    keywords='crowdflower crowdsourcing api client',
    description='CrowdFlower API - Python client',
    long_description=open('README.rst').read(),
    license=open('LICENSE').read(),
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        # https://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
    ],
    install_requires=[
        'requests>=2.0.0',
    ],
)
