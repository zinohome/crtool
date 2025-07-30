#!/bin/bash
IMGNAME=tls/crtool
IMGVERSION=v0.1.6
docker build --no-cache -t $IMGNAME:$IMGVERSION .