"""Constants used in doi_agency module"""

from enum import Enum
from typing import Any

from typing_extensions import TypedDict


class ConvertSuccess(TypedDict):
    """External platform conversion success class."""

    status_code: int
    result: dict


class ConvertError(TypedDict):
    """External platform conversion error class."""

    status_code: int
    message: str
    error: Any


class DOIAgency(str, Enum):
    """DOI agency class."""

    DATACITE = "datacite"


DOI_AGENCY_NAMES = {
    "datacite": DOIAgency.DATACITE
}

#EXTERNAL_PLATFORM_PREFIXES = {"10.5281": ExternalPlatform.ZENODO}
