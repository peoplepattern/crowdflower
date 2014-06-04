from setuptools import setup, find_packages

setup(
    name='crowdflower',
    version='0.0.2',
    author='Christopher Brown',
    author_email='io@henrian.com',
    url='https://github.com/chbrown/crowdflower',
    keywords='',
    description='',
    long_description=open('README.md').read(),
    license=open('LICENSE').read(),
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        # https://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 1 - Alpha',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=[
        'requests>=2.0.0',
        'grequests',
    ],
    entry_points={
        'console_scripts': [
        ],
    },
)
