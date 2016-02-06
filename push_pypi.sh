#!/bin/bash

# clean pyc, the MANIFEEST ignore does not seem to work..
find .|grep ".pyc$" | xargs rm

python setup.py register -r pypi

python setup.py sdist upload -r pypi

