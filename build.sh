#!/bin/bash
rm -rf build.sh
python setup.py py2app
zip -r ../charactr.zip dist/charactr.app
