#!/bin/bash
rm -rf build dist
python setup.py py2app --matplotlib-backends -
