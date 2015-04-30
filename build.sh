#!/bin/bash
rm -rf build.sh
python setup.py py2app
zip -r dist/charactr.zip dist/charactr.app
