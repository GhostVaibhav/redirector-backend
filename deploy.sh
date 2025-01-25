#!/bin/bash

python ./package.py
pulumi up
rm -f store.py.zip
