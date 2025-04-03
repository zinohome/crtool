#!/bin/bash
FIND_FILE="/opt/crtool/config/gunicorn.py"
FIND_STR="workers"
if [ `grep -c "$FIND_STR" $FIND_FILE` -ne '0' ];then
    echo "gunicorn config exist"
else
    cp /opt/crtool/config/gunicorn_default.py /opt/crtool/config/gunicorn.py
fi
cd /opt/crtool && \
nohup /opt/crtool/venv/bin/gunicorn -c /opt/crtool/config/gunicorn.py main:app >> /tmp/crtool.log 2>&1 &