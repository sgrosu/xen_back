#!/bin/bash

find /run/sr-mount/c0749ff3-6f96-ebd7-9610-0ece005b7b9f/vm/ -type f -mtime +2 -exec rm {} \;
