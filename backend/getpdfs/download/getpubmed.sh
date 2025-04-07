# Download from URLs in opmid.txt
#!/usr/bin/env bash

Link="http://www.ncbi.nlm.nih.gov/pubmed/"

for f in `cat opmid.txt |cut -d\  -f 2`;
do
   wget  --user-agent="Mozilla/5.0 (Windows NT 5.2; rv:2.0.1) Gecko/20100101 Firefox/4.0.1" \
         -l1 --no-parent -A.pdf ${Link}${f}/pdf/ -O ${f}.pdf
done

