#!/bin/bash
rm -rf build dist
python setup.py py2app
zip versions/charactrv0.2.zip dist/charactr.app 
