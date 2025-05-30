#!/bin/bash
IMGNAME=tls/crtool
IMGVERSION=v0.1.4
docker build --no-cache -t $IMGNAME:$IMGVERSION .