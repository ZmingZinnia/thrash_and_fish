#!/bin/sh
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
if [ -z `echo $PYTHONPATH | grep -q $SCRIPTPATH` ]; then
    export PYTHONPATH=$PYTHONPATH:$SCRIPTPATH
fi

req=`cat requirements.txt`
installed_req=`pip freeze`
if [ "$req" != "$installed_req" ];  then
    echo "Inconsistent dependent environment"
    echo "Please use the new environment and install all dependencies using pip install"
else
    python3 $SCRIPTPATH/adnmb/run.py
fi

