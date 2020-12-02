# book2pdf
Suck down the pages of an Islandora book and merge them into
as single PDF. Saves output PDF to current directory. Connects to Solr; you must
be on the VPN for this to work.

When --collection is used, automagically retrieves PDFs for all books in a given
collection. Automatically ignores those books that already have PDF datastreams.
If --force is used then build PDFs even if they already have PDF datastreams.

Example:
$ python3 book2pdf.py smith:1322496
or
$ python3 book2pdf.py --collection smith:mrbc--teatro

To ingest the generated PDFs back into the respective objects in Compass use [Islandora datastream crud utility](https://github.com/SFULibrary/islandora_datastream_crud).

Technical notes:
- Uses JPGs from the LARGE_JPG datastream of book pages.
- Uses img2pdf to merge jpgs into PDF.
- Respects page sequence numbers found in RELS-EXT.
- Requires Python3.
