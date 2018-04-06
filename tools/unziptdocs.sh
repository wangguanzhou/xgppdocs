#!/bin/bash

# for zipfile in *.zip; do
#    unzip $zipfile -d ./
# done

for file in S2*.{doc, DOC, docx, DOCX, pdf, PDF}; do
    filename="$file"
    tdocnum=${filename:0:9}
    ext=${filename##.*}
    newfile="$tdocnum"."$ext"
    mv "$file" "$newfile"
    echo $file moved to $newfile
done