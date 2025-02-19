import argparse
import pathlib
import json
import base64
import logging
import sys
import tempfile
import os
import math
#from packaging.version import Version
import re

from lxml import etree as ET
import requests

#import pytest

import python_on_whales
from python_on_whales import docker
from python_on_whales import exceptions as d_exceptions

LOGGER = logging.getLogger(__name__)
root_logger = logging.getLogger()

#https://support.datacite.org/docs/api-get-doi

USER_AGENT = "https://github.com/eawag-rdm/datacite-export"
USER_EMAIL = "noreply@example.com"
DEFAULT_HEADER = {
    "User-Agent": USER_AGENT,
    "From": USER_EMAIL
    }
PAGE_URL_TEMPLATE = "https://api.datacite.org/dois?prefix=%s&page[size]=%i&page[number]=%i"
PAGE1_URL_TEMPLATE = "https://api.datacite.org/dois?prefix=%s&page[size]=1&page[number]=1"
CURSOR_URL_TEMPLATE = "https://api.datacite.org/dois?prefix=%s&page[cursor]=1&page[size]=%i"
#CURSOR_URL_TEMPLATE2 = "https://api.datacite.org/dois?provider-id=%s&page[cursor]=1&page[size]=%i"
DOI_URL_TEMPLATE = "https://api.datacite.org/dois/%s"
TIMEOUT=None

def doi_to_file(doi):
    pass

def get_doi_list_fastapi(doi_prefix, cache):
    """DO NOT USE: Template for binding for FastAPI call to DataCite API cursor call
    to list DOIs by prefix

    Attributes:
        doi_prefix (str): DOI prefix for provider
        cache (str): session specific folder path

    Todo:
        * Add in call to XML scraping
        * Design FastAPI asynchronous return for results
    """
    if (sys.version_info.major >= 3) and (sys.version_info.major >= 12):
        temp_dir = tempfile.TemporaryDirectory(dir=cache,delete=False)
    else:
        #This probably won't work
        temp_dir = tempfile.TemporaryDirectory(dir=cache)

    fid = pathlib.Path(temp_dir.name).name
    doi_file = pathlib.Path(temp_dir.name) / "doi.txt"

    #this is blocking and should be modified with a fork or spawn
    result = get_doi_list_cursor(doi_prefix=doi_prefix,
                                 filename=doi_file,
                                 header_line = True)

##    return {
##        "status_code": 200,
##        "result": json.dumps(result)
##        }

##    return {
##        "status_code": 200,
##        "result": dict(zip(range(1,len(result)+1),result))
##        }

    return {
        "status_code": 200,
        "message": f"Request {fid} started.",
        "status_url": f"/request?fid={fid}"
        }

def get_doi_list(doi_prefix="10.14454",
                 headers=DEFAULT_HEADER,
                 filename=None):

    """Calls the record count appropriate page or cursor based DOI list function

    Note: This call is done on a basis of a single DOI prefix for a provider.
    Providers can have multiple prefixes (I think).

    Attributes:
        doi_prefix (str): DOI prefix for provider
        headers (dict): request header to inform DataCite about API call
        filename (str): file path where to write the DOI list

    Todo:
        * Consider supporting a provider id instead/in addition to a DOI prefixe

    """
    #logic to determine page or cursor approach

    #check record count with pagination
    url_template = PAGE1_URL_TEMPLATE
    url = url_template % (doi_prefix)
    data = None
    LOGGER.debug("DataCite DOI query: %s", url)
    json_response = json.loads(requests.get(url, headers=headers, data=data, timeout=TIMEOUT).text)
    if json_response["meta"]["total"] > 10000:
        LOGGER.info("Gathering records with cursor API call(s)")
        fun = get_doi_list_cursor
        #return get_doi_list_cursor(doi_prefix, headers=headers, filename=filename)
    else:
        LOGGER.info("Gathering records with pagnation API call(s)")
        fun = get_doi_list_page
        #return get_doi_list_page(doi_prefix, headers=headers, filename=filename)

    return fun(doi_prefix, headers=headers, filename=filename)

def get_doi_list_page(doi_prefix="10.14454",
                 url_template = PAGE_URL_TEMPLATE,
                 page_size = 100,
                 start_page = 1,
                 stop_offset = 0,
                 headers=DEFAULT_HEADER,
                 filename=None):

    """Explictly page based API call to list full DOIs

    Note: This call is done on a basis of a single DOI prefix for a provider.
    Providers can have multiple prefixes (I think).

    Attributes:
        doi_prefix (str): DOI prefix for provider
        url_template (str): URL template for API call
        page_size (int): max number of items per page
        start_page (int): page to start on begining with 1 meaning no exclusion
        stop_offset (int): page to stop at ending with 0 meaning no exclusion
        headers (dict): request header to inform DataCite about API call
        filename (str): file path where to write the DOI list

    Todo:
        * Consider supporting a provider id instead/in addition to a DOI prefixe

    """
    doi_list = []

    url = url_template % (doi_prefix, page_size, start_page)
    data = None
    LOGGER.info("DataCite DOI query")
    LOGGER.debug("DataCite DOI query: %s", url)
    json_response = json.loads(requests.get(url, headers=headers, data=data, timeout=TIMEOUT).text)

    page_count = json_response["meta"]["totalPages"]
    result_count = json_response["meta"]["total"]

    LOGGER.info("Processing page(s)")
    LOGGER.debug("Processing page 1 of %i", page_count)
    doi_list.extend(datacite_doi_json_to_list(json_response))


    for i in range(start_page + 1, start_page + page_count - stop_offset):
        LOGGER.debug("Processing page %i of %i", i, page_count)

        url = url_template % (doi_prefix, page_size, i)
        data = None
        json_response = json.loads(requests.get(url, headers=headers, data=data, timeout=TIMEOUT).text)

        doi_list.extend(datacite_doi_json_to_list(json_response))

    LOGGER.info("Processing complete")
    if filename is not None:
        with open(filename,"w") as f:
            for d in doi_list:
                f.write(f"{d}\n")

    try:
        assert len(doi_list) == result_count
    except AssertionError:
        LOGGER.warn("Result count %i but actual DOI count %i", result_count, len(doi_list))

    return doi_list

def get_doi_list_cursor(doi_prefix="10.14454",
                        url_template = CURSOR_URL_TEMPLATE,
                        page_size=1000,
                        headers=DEFAULT_HEADER,
                        filename=None,
                        header_line=False):

    """Explictly cursor based API call to list full DOIs

    Note: This call is done on a basis of a single DOI prefix for a provider.
    Providers can have multiple prefixes (I think).

    Attributes:
        doi_prefix (str): DOI prefix for provider
        url_template (str): URL template for API call
        page_size (int): max number of items per page
        headers (dict): request header to inform DataCite about API call
        filename (str): file path where to write the DOI list

    Todo:
        * Consider supporting a provider id instead/in addition to a DOI prefixe

    """

    doi_list = []

#    url = url_template % (provider, page_size)
    url = url_template % (doi_prefix, page_size)
    data = None


    LOGGER.info("Processing cursor(s)")
    LOGGER.debug("Getting cursor 1")
    json_response = json.loads(requests.get(url, headers=headers, data=data, timeout=TIMEOUT).text)

    result_count = json_response["meta"]["total"]
    doi_list.extend(datacite_doi_json_to_list(json_response))

    if result_count > page_size:
        next_url = json_response["links"]["next"]

        page_count = math.ceil(result_count/float(page_size))
        for i in range(2,page_count+1):
            LOGGER.debug("Getting cursor %i", i)
            LOGGER.debug("Next url: %s", next_url)
            json_response = json.loads(requests.get(url, headers=headers, data=data, timeout=TIMEOUT).text)

            doi_list.extend(datacite_doi_json_to_list(json_response))

            next_url = json_response["links"]["next"]

    LOGGER.info("Processing complete")
    if filename is not None:
        with open(filename,"w") as f:
            if header_line:
                f.write(f"{len(doi_list)}\n")
            for d in doi_list:
                f.write("{d}\n")

    return doi_list

def datacite_doi_json_to_list(dc_j):
    """Extracts DOI values from a list of DataCite JSON objects

    Attributes:
        dc_j (list): list of DataCite JSON objects

    Todo:
        * Integrate this into the scrape to reduce memory footprint
    """
    doi_list = []

    for d in dc_j["data"]:
        doi_list.append(d["attributes"]["doi"])

    return doi_list

def get_xml_list():
    """Calls the resource appropriate function to obtain DOI XML records

    Note: This should default to using Bolognese via python_on_wheels

    Todo:
        * Everything
    """

def get_xml_list_datacite(doi_list=["10.14454/FXWS-0523"],
                          url_template = DOI_URL_TEMPLATE,
                          headers=DEFAULT_HEADER,
                          folder=None):
    """Explictly API based call to get DOI XML record

    Attributes:
        doi_list (list): list of full DOI strings
        url_template (str): url template for API call
        headers (dict): request header to inform DataCite about API call
        folder (str): path string for where to save XML files

    Todo:
        * Rate limiting needed
    """
    if folder:
        if not pathlib.Path(folder).is_dir():
            pathlib.Path(folder).mkdir(parents=True)
            
    xml_list = []
    LOGGER.info("Getting DOI record XML")
    for i,d in enumerate(doi_list, start=1):
        LOGGER.debug("Getting record %i: %s", i, d)
        url = url_template % (d)
        data = None
        response = requests.get(url, headers=headers, data=data, timeout=TIMEOUT)
        dc_xml_et = ET.fromstring(
            base64.b64decode(
                json.loads(response.text)["data"]["attributes"]["xml"]))

        if folder:
            LOGGER.debug("Saving record to disk")
            ET.ElementTree(dc_xml_et).write(os.path.join(folder, f"{i}.xml"), pretty_print=True)

        xml_list.append(dc_xml_et)

    return xml_list

def get_xml_list_bolognese(doi_url="https://doi.org/10.7554/elife.01567",
                           docker_image="bolognese-cli"):
    """Explictly Bolognese Docker call to get DOI XML record

    Attributes:
        doi_url (str): full DOI URL

    Todo:
        * Rate limiting needed
        * Bolognese should support request headers
        * Bolognese should support DOI batch requests
        * Batch requests would need a path string for where to save XML files        
    """
    try:
        xml = docker.run(docker_image,
                         [doi_url, "-t", "datacite"],
                         remove=True)
        print(xml)
    except python_on_whales.ClientNotFoundError as e:
        LOGGER.error("Docker not found")
    except d_exceptions.NoSuchImage as e:
        LOGGER.error("Docker image not found")

if __name__ == "__test__":
    #example pagination
    DOI_PREFIX_EAWAG = "10.25678"
    folder_eawag = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                "cache",
                                "eawag")  
    doi_list_eawag = get_doi_list_page(DOI_PREFIX_EAWAG, folder=folder_eawag)
    xml_list_eawag = get_xml_list(doi_list_eawag, folder=folder_eawag)

    #example cursor
    DOI_PREFIX_WSL = "10.16904"
    folder_wsl = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              "cache",
                              "wsl")
    doi_list_wsl = get_doi_list_cursor(DOI_PREFIX_WSL, folder=folder_wsl)
    xml_list_wsl = get_xml_list(doi_list_wsl, folder=folder_wsl)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("doi_prefix",
                        help="DOI prefix used to get suffixes")
    parser.add_argument("mailto",
                        help="contanct email address for the User-Agent header")
    parser.add_argument("-d", "--doi", type=argparse.FileType('w', encoding='UTF-8'),
                        help="JSON output file for DOI")
    parser.add_argument("-c", "--cache", type=pathlib.Path,
                        help="Output folder to cache results")
    parser.add_argument("-l", "--log", type=argparse.FileType('w', encoding='UTF-8'),
                        help="Output file for log")
    parser.add_argument("-v", action="count", default=0,
                        help="increase output verbosity")
    parser.add_argument("--info",
                        help="set output verbosity to 1 (INFO)",
                        action="store_true")
    parser.add_argument("--debug",
                        help="set output verbosity to 2 (DEBUG)",
                        action="store_true")
    parser.add_argument("--verbosity", type=int, choices=[0, 1, 2],
                        help="set output verbosity")

    args = parser.parse_args()

    ##consider adding an ERROR level logging

    #set User-Agent for requests
    headers={"User-Agent": USER_AGENT,
             "From": args.mailto}  

    #DOIs to be written to the specified file
    #consquently logging to sys.stdout enabled
    if args.doi is not None:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(datefmt='%Y.%m.%d %H:%M:%S ')
        handler.setFormatter(formatter)
        logging.basicConfig(level=logging.DEBUG, handlers=[handler])
        root_logger.addHandler(handler)
        LOGGER.info("Logging to sys.stdout enabled")
        LOGGER.info("Results will be written to \"%s\"", args.doi.name)

    #logging to the specified file
    if args.log is not None:
        fh = logging.FileHandler(args.log.name, "w")
        fh.setLevel(logging.INFO)
        LOGGER.addHandler(fh)

        LOGGER.info("Log will be written to \"%s\"", args.log.name)

    #set logging level
    LOG_LEVEL = None
    if args.info or (args.verbosity == 1) or ((args.v is not None) and (args.v == 1)):
        #to logging.INFO
        LOG_LEVEL = "INFO"
        print(f"Logging level set to {LOG_LEVEL}")

        for handler in LOGGER.handlers:
            if isinstance(handler, type(logging.StreamHandler())):
                handler.setLevel(logging.INFO)

        LOGGER.info('Logging level INFO')

    elif args.debug or (args.verbosity == 2) or ((args.v is not None) and (args.v > 1)):
        #to logging.DEBUG
        LOG_LEVEL = "DEBUG"
        print(f"Logging level set to {LOG_LEVEL}")

        for handler in LOGGER.handlers:
            if isinstance(handler, type(logging.StreamHandler())):
                handler.setLevel(logging.DEBUG)

            LOGGER.debug('Logging level DEBUG')

    LOGGER.info("Begining scrape of DOI prefix \"%s\" with User-Agent \"%s\" and logging level %s",
                args.doi_prefix,
                args.mailto,
                LOG_LEVEL)

    if args.doi is None:
        doi_list = get_doi_list_cursor(args.doi_prefix, headers=headers)
        print(doi_list)
    else:
        doi_list = get_doi_list_cursor(args.doi_prefix,headers=headers, filename=args.doi.name)

    LOGGER.info("Begin scrape of DOI records.")

    if args.cache is None:
        print(get_xml_list_datacite(doi_list, headers=headers))
    else:
        get_xml_list_datacite(doi_list, headers=headers, folder=args.cache)
