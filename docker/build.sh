#!/bin/bash
IMGNAME=tls/crtool
IMGVERSION=v0.1.3
docker build --no-cache -t $IMGNAME:$IMGVERSION .