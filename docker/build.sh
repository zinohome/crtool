#!/bin/bash
IMGNAME=tls/crtool
IMGVERSION=v0.1.3s
docker build --no-cache -t $IMGNAME:$IMGVERSION .