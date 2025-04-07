
This directory contains scripts to create a vectorstore from text documents in the directory md/

The text documentns are assumed to be converted from PDFs (see getpdfs/)

==> find_dup_mds.py <==
Find papers in md/ of the same content (check using first 1000 letters)

==> paper2emb.py <==
Embed text documents in md/ into vectorstore

==> generate_rag.py <==
Main vectorstore test script: generates simple article using vectorstore. also supports interactive use

==> generate_toolrag.py <==
Same as generate_rag.py but with tool. Doesn't work since PPLX doesn't support tool yet

==> fix_article.py <==
Align the output of generate_rag.py to a given outline. Made obsolete by secondstorm.

