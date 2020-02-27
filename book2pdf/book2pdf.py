description = """Suck down the pages of an Islandora book and merge them into
as single PDF. Saves output PDF to current directory. Connects to Solr; you must
be on the VPN for this to work.

When --collection is used, automagically retrieves PDFs for all books in a given
collection. Automatically ignores those books that already have PDF datastreams.

Example:
$ python3 book2pdf.py smith:1322496
or
$ python3 book2pdf.py --collection smith:mrbc--teatro

Technical notes:
- Uses JPGs from the LARGE_JPG datastream of book pages.
- Uses img2pdf to merge jpgs into PDF.
- Respects page sequence numbers found in RELS-EXT.
- Requires Python3.

"""
import requests
import sys
import tempfile
import subprocess
import logging
import re
import argparse
from argparse import RawTextHelpFormatter


SOLR_LOCATION = "http://compass-fedora-stage.fivecolleges.edu:8080/solr/collection1"
ISLANDORA_OBJECTS_LOCATION = "https://compass-stage.fivecolleges.edu/islandora/object"

def get_page_sequence_number(pid):
    """Get the RELS-EXT of a book page and extract the sequence number.
    Returns a string in order to preserve existing zero padding.
    Returns an empty string if fails.
    """

    try:
        RELS_EXT_request = requests.get(f"{ISLANDORA_OBJECTS_LOCATION}/{page_pid}/datastream/RELS-EXT/view")
        # Use regular expression instead of lxml or beautiful soup for fewer
        # dependencies, and greater resilience to variations in xml namespace/schema versions etc.
        matches = re.search('<islandora:isSequenceNumber>[0-9]+</islandora:isSequenceNumber>', RELS_EXT_request.text)
        sequence_tag = matches.group(0)
        # Strip off the xml tags to get just the value
        sequence_tag_value = sequence_tag.replace('<islandora:isSequenceNumber>', '').replace('</islandora:isSequenceNumber>', '')
        sequence_number_string = sequence_tag_value
    except Exception as e:
        logging.warning(f"Failed to get sequence number for page {pid}")
        logging.debug(e)
        return ''
    
    return sequence_number_string

def build_pdf_from_pid(book_pid):
    logging.info("Building PDF for %s" % book_pid)
    try:
        solr_request = requests.get(f"{SOLR_LOCATION}/select?q=RELS_EXT_isPageOf_uri_s%3A%22info%3Afedora%2F{book_pid}%22&fl=PID&wt=json&indent=true&rows=1000000")
    except:
        logging.error("Failed to connect to Solr. Are you on the VPN?")
    page_pids = solr_request.json()['response']['docs']
    jpg_filenames = []
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        for page_pid in page_pids:
            page_pid = page_pid['PID']
            sequence_number_string = get_page_sequence_number(page_pid)
            jpg_filename = f"{tmp_dir_name}/{sequence_number_string}-{page_pid}.jpg"
            subprocess.call(f"curl -s {ISLANDORA_OBJECTS_LOCATION}/{page_pid}/datastream/LARGE_JPG/view > {jpg_filename}", shell=True)
            jpg_filenames.append(jpg_filename)
        jpg_filenames.sort()
        jpg_filenames_line = ' '.join(jpg_filenames)
        pdf_filename = "%s_PDF.pdf" % book_pid.replace(":", "_")
        img2pdf_command = f"img2pdf {jpg_filenames_line} > {pdf_filename}"
        img2pdf_return = subprocess.call(img2pdf_command, shell=True)
        if img2pdf_return != 0:
            logging.error(f"Failed to build PDF for {book_pid}")

def process_whole_collection(collection_pid):
    logging.info("Building PDFs from %s" % collection_pid)
    try:
        solr_request = requests.get(f"{SOLR_LOCATION}/select?q=RELS_EXT_isMemberOfCollection_uri_s%3A+%22info%3Afedora%2F{collection_pid}%22+AND+RELS_EXT_hasModel_uri_s%3A+%22info%3Afedora%2Fislandora%3AbookCModel%22&rows=10000&fl=PID,fedora_datastreams_ms,fedora_datastream_latest_PDF_SIZE_ms&wt=json&indent=true")
    except:
        logging.error("Failed to connect to Solr. Are you on the VPN?")
    books_list = solr_request.json()['response']['docs']
    for book_info in books_list:
        if 'PDF' not in book_info['fedora_datastreams_ms']:
            logging.debug("No PDF datastream, building book pdf for %s" % book_info['PID'])
            build_pdf_from_pid(book_info['PID'])
        else:
            existing_pdf_size = int(book_info['fedora_datastream_latest_PDF_SIZE_ms'][0])
            if existing_pdf_size < 1:
                logging.warning("PDF datastream exists but size less than 1, building book PDF for %s" % book_info['PID'])
                build_pdf_from_pid(book_info['PID'])

if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description=description, formatter_class=RawTextHelpFormatter)
    argparser.add_argument('PID', help="PID of the book or collection of books you want to make into PDF(s). E.g. smith:1322496")
    argparser.add_argument("--collection", help="Process a whole collection", action="store_true")
    cliargs = argparser.parse_args()
    pid = cliargs.PID
    if cliargs.collection is True:
        process_whole_collection(pid)
    else:
        build_pdf_from_pid(pid)
