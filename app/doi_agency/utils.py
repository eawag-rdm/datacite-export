"""Utils for doi_agency module."""

import csv
from logging import getLogger

#import xlsxwriter

from app.doi_agency.constants import (
    DOI_AGENCY_NAMES,
#    EXTERNAL_PLATFORM_PREFIXES,
    ConvertError,
    ConvertSuccess,
    DOIAgency,
)
from app.doi_agency.datacite import get_doi_list_cursor
#from app.external_doi.dryad import convert_dryad_doi
#from app.external_doi.zenodo import convert_zenodo_doi

log = getLogger(__name__)


def get_doi_agency(doi_agency_name: str) -> DOIAgency | None:
    """Return DOIAgency that corresponds to input DOI agency.

    If agency is not found then returns None.

    Args:
        doi (str): Input DOI agency

    Returns:
        ExternalPlatform | None
    """
    # Search by names for doi that corresponds to supported external platform
    for key, value in DOI_AGENCY_NAMES.items():
        if key is doi_agency_name:
            return value
        
    return None
