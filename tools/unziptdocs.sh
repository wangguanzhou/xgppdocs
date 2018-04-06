#!/bin/bash

# for zipfile in *.zip; do
#    unzip $zipfile -d ./
# done

for file in S2*.{doc, DOC, docx, DOCX, pdf, PDF}; do
    echo $file
done