#!/bin/bash
IMGNAME=tls/crtool
IMGVERSION=v0.1.2s
docker build --no-cache -t $IMGNAME:$IMGVERSION .