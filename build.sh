#!/bin/bash
set -ef -o pipefail

SERVER_NAME=http://bbpgb027.epfl.ch:5000/docs/hmd

echo "***************************"
echo "Install Python Dependencies"
echo "***************************"

virtualenv venv
source venv/bin/activate
pip install pip==1.4.1 --upgrade
pip install argparse==1.2.1
pip install -r requirements.txt -i http://bbpgb019.epfl.ch:9090/simple

echo "*******************"
echo "Build Documentation"
echo "*******************"

make html

echo "*********************"
echo "Create and Upload zip"
echo "*********************"
pushd build/html
zip -r ../../index.zip .
popd

export PYTHONPATH=source
VERSION=`python -c 'import conf; print conf.version'`
NAME=`python -c 'import conf; print conf.project'`
echo "Project: $NAME, version: $VERSION"

[[ -z "$JENKINS_HOME" ]] && echo "Not running in jenkins: not uploading" && exit

curl -X POST                              \
   -F filedata=@index.zip                 \
   -F name="$NAME"                        \
   -F version="$VERSION"                  \
   $SERVER_NAME
