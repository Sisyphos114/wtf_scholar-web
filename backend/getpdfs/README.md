This directory contains scripts for downloading PDF files for bibliography entries in biblio.txt

More precisely, the Python scripts are for generating and maintaining lists of URLs to download.

The generated lists and the scripts for downloading are in the directory download/

==> biblio.txt <==
The literature which we want to download (with duplicates)

==> biblio.uniq.txt <==
The literature which we want to download (without slightly fewer duplicates)

==> geturls.py <==
Find the URL for each literature entry in biblio.txt, save URLs to odois.txt, otitle.txt, etc

==> find_missing.py <==
Find the files that has not been successfully processed

==> processed, missing <==
Auxiliary output files 
