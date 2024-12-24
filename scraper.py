import argparse
import pathlib

import requests
import json
import base64
from lxml import etree as ET

import logging
import sys

import os

import math

import pytest

import python_on_whales
from python_on_whales import docker
from python_on_whales import exceptions as d_exceptions

LOGGER = logging.getLogger(__name__)
root_logger = logging.getLogger()

#https://support.datacite.org/docs/api-get-doi

def get_doi_list(doi_prefix="10.14454",
                 headers={"User-Agent": "https://github.com/eawag-rdm/datacite-export", "From": "noreply@example.com"},
                 filename=None):
    
    #logic to determine page or cursor approach

    #check record count with pagination
    url_template = "https://api.datacite.org/dois?prefix=%s&page[size]=1&page[number]=1"
    url = url_template % (doi_prefix)
    data = None
    LOGGER.debug("DataCite DOI query: %s" % url)
    json_response = json.loads(requests.get(url, headers=headers, data=data).text)    
    if json_response["meta"]["total"] > 10000:
        LOGGER.info("Gathering records with cursor API call(s)")
        return get_doi_list_cursor(doi_prefix, headers=headers, filename=filename)
    else:
        LOGGER.info("Gathering records with pagnation API call(s)")
        return get_doi_list_page(doi_prefix, headers=headers, filename=filename)

def get_doi_list_page(doi_prefix="10.14454",
                 url_template = "https://api.datacite.org/dois?prefix=%s&page[size]=%i&page[number]=%i",
                 page_size = 100,
                 start_page = 1,
                 stop_offset = 0,
                 headers={"User-Agent": "https://github.com/eawag-rdm/datacite-export", "From": "noreply@example.com"},
                 filename=None):
    doi_list = []

    url = url_template % (doi_prefix, page_size, start_page)
    data = None
    LOGGER.info("DataCite DOI query")
    LOGGER.debug("DataCite DOI query: %s" % url)
    json_response = json.loads(requests.get(url, headers=headers, data=data).text)

    page_count = json_response["meta"]["totalPages"]
    result_count = json_response["meta"]["total"]

    LOGGER.info("Processing page(s)")
    LOGGER.debug("Processing page 1 of %i" % page_count)
    doi_list.extend(datacite_doi_json_to_list(json_response))
    
    
    for i in range(start_page + 1, start_page + page_count - stop_offset):
        LOGGER.debug("Processing page %i of %i" % (i, page_count))
        
        url = url_template % (doi_prefix, page_size, i)
        data = None
        json_response = json.loads(requests.get(url, headers=headers, data=data).text)

        doi_list.extend(datacite_doi_json_to_list(json_response))

    LOGGER.info("Processing complete")
    if filename is not None:
        with open(filename,"w") as f:
            for d in doi_list:
                f.write("%s\n" % d)
        
    try:
        assert len(doi_list) == result_count
    except AssertionError:
        LOGGER.warn("Result count %i but actual DOI count %i" % (result_count, len(doi_list)))

    return doi_list

def get_doi_list_cursor(doi_prefix="10.14454",
#                        url_template = "https://api.datacite.org/dois?provider-id=%s&page[cursor]=1&page[size]=%i",
                        url_template = "https://api.datacite.org/dois?prefix=%s&page[cursor]=1&page[size]=%i",
                        page_size=1000,
                        headers={"User-Agent": "https://github.com/eawag-rdm/datacite-export", "From": "noreply@example.com"},
                        filename=None):
    doi_list = []

#    url = url_template % (provider, page_size)
    url = url_template % (doi_prefix, page_size)
    data = None

    LOGGER.info("Processing page(s)")
    LOGGER.debug("Getting page 1")
    json_response = json.loads(requests.get(url, headers=headers, data=data).text)

    result_count = json_response["meta"]["total"]
    doi_list.extend(datacite_doi_json_to_list(json_response))

    if result_count > page_size:
        next_url = json_response["links"]["next"]

        page_count = math.ceil(result_count/float(page_size))
        for i in range(2,page_count+1):
            LOGGER.debug("Getting page %i" % i)
            LOGGER.debug("Next url: %s" % next_url)
            json_response = json.loads(requests.get(url, headers=headers, data=data).text)

            doi_list.extend(datacite_doi_json_to_list(json_response))

            next_url = json_response["links"]["next"]

    LOGGER.info("Processing complete")
    if filename is not None:
        with open(filename,"w") as f:
            for d in doi_list:
                f.write("%s\n" % d)

    return doi_list

def datacite_doi_json_to_list(dc_j):
    doi_list = []

    for d in dc_j["data"]:
        doi_list.append(d["attributes"]["doi"])

    return doi_list

def get_xml_list():
    pass

def get_xml_list_datacite(doi_list=["10.14454/FXWS-0523"],
                          url_template = "https://api.datacite.org/dois/%s",
                          headers={"User-Agent": "https://github.com/eawag-rdm/datacite-export", "From": "noreply@example.com"},
                          folder=None):

    xml_list = []

    LOGGER.info("Getting DOI record XML")
    for i,d in enumerate(doi_list, start=1):
        LOGGER.debug("Getting record %i: %s" % (i, d))
        url = url_template % (d)
        data = None
        response = requests.get(url, headers=headers, data=data)
        dc_xml_et = ET.fromstring(
            base64.b64decode(
                json.loads(response.text)["data"]["attributes"]["xml"]))

        if folder:
            LOGGER.debug("Saving record to disk")
            ET.ElementTree(dc_xml_et).write(os.path.join(folder, "%i.xml" %i), pretty_print=True)
            
        xml_list.append(dc_xml_et)

    return xml_list

def get_xml_list_bolognese(doi_url="https://doi.org/10.7554/elife.01567",
                           docker_image="bolognese-cli"):
    try:
        docker.run(docker_image,
                  [doi_url],
                  remove=True)
    except python_on_whales.ClientNotFoundError as e:
        LOGGER.error("Docker not found")
    except d_exceptions.NoSuchImage as e:
        LOGGER.error("Docker image not found")

if __name__ == "__test__":
    #example pagination
    doi_prefix_eawag = "10.25678"
    folder_eawag = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                "cache",
                                "eawag")  
    doi_list_eawag = get_doi_list_page(doi_prefix_eawag, folder=folder_eawag)
    xml_list_eawag = get_xml_list(doi_list_eawag, folder=folder_eawag)

    #example cursor
    doi_prefix_wsl = "10.16904"
    folder_wsl = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              "cache",
                              "wsl")
    doi_list_wsl = get_doi_list_cursor(doi_prefix_wsl, folder=folder_wsl)
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
    headers={"User-Agent": "https://github.com/eawag-rdm/datacite-export",
             "From": args.mailto}  

    #DOIs to be written to the specified file
    #consquently logging to sys.stdout enabled
    if args.doi is not None:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(datefmt='%Y.%m.%d %H:%M:%S ')
        handler.setFormatter(formatter)
        logging.basicConfig(level=logging.DEBUG, handlers=[handler])
        LOGGER.info("Logging to sys.stdout enabled")
        LOGGER.info("Results will be written to \"%s\"" % args.doi.name)

    #logging to the specified file
    if args.log is not None:
        fh = logging.FileHandler(args.log.name, "w")
        fh.setLevel(logging.INFO)
        LOGGER.addHandler(fh)

        LOGGER.info("Log will be written to \"%s\"" % args.log.name)

    #set logging level
    log_level = None
    if args.info or (args.verbosity == 1) or ((args.v is not None) and (args.v == 1)):
        #to logging.INFO
        log_level = "INFO"
        
        for handler in LOGGER.handlers:
            if isinstance(handler, type(logging.StreamHandler())):
                handler.setLevel(logging.INFO)

        LOGGER.info('Logging level INFO')
                
    elif args.debug or (args.verbosity == 2) or ((args.v is not None) and (args.v > 1)):
        #to logging.DEBUG
        log_level = "DEBUG"
        
        for handler in LOGGER.handlers:
            if isinstance(handler, type(logging.StreamHandler())):
                handler.setLevel(logging.DEBUG)

            LOGGER.debug('Logging level DEBUG')
            
    LOGGER.info("Begining scrape of DOI prefix \"%s\" with User-Agent \"%s\" and logging level %s"
              % (args.doi_prefix, args.mailto, log_level))

    if args.doi is None:
        print(get_doi_list(args.doi_prefix, headers=headers))
    else:
        get_doi_list(args.doi_prefix,headers=headers, filename=args.doi.name)

    get_xml_list_bolognese()

    

    
