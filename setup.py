from setuptools import setup, find_packages

setup(
    name='crowdflower',
    version='0.0.7',
    author='Christopher Brown',
    author_email='io@henrian.com',
    url='https://github.com/chbrown/crowdflower',
    keywords='crowdflower crowdsourcing api client',
    description='Crowdflower API - Python Client',
    long_description=open('README.rst').read(),
    license=open('LICENSE').read(),
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        # https://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=[
        'requests>=2.0.0',
    ],
    entry_points={
        'console_scripts': [
        ],
    },
)
