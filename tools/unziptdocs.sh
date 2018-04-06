#!/bin/bash

for zipfile in *.zip; do
    unzip $zipfile -d ./
done 