#!/bin/bash
rm -rf build dist
python setup.py py2app
zip chv0.X.zip dist/charactr.app 
cp chv0.X.zip ../Dropbox/versions
