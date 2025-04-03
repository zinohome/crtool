#!/bin/bash
FIND_FILE="/opt/crtool/backend/appconfig/hypercorn.py"
FIND_STR="workers"
if [ `grep -c "$FIND_STR" $FIND_FILE` -ne '0' ];then
    echo "hypercorn config exist"
else
    cp /opt/crtool/backend/appconfig/hypercorn_default.py /opt/crtool/backend/appconfig/hypercorn.py
fi

FIND_DB_FILE="/opt/crtool/backend/appconfig/hypercorn.py"
if [ ! -f "$FIND_DB_FILE" ]; then
    echo "sample database exist"
else
    cp /opt/crtool/backend/crud/sample.db /opt/crtool/backend/data/
fi
cd /opt/crtool/backend && \
nohup /opt/crtool/backend/venv/bin/hypercorn -c /opt/crtool/backend/appconfig/hypercorn.py main:app >> /tmp/crtool.log 2>&1 &