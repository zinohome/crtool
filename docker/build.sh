#!/bin/bash
IMGNAME=tls/crtool
IMGVERSION=v0.1.1
docker build --no-cache -t $IMGNAME:$IMGVERSION .