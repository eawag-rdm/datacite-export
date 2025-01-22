"""Router used to gather DOI records from a DOI agency given a DOI prefix.
"""
import logging
from typing import Annotated, List, Any, Dict
from pydantic import TypeAdapter, ValidationError

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.doi_agency.constants import ConvertSuccess, ConvertError, DOIAgency
#from app.external_doi.dryad import convert_dryad_doi
#from app.external_doi.utils import get_doi_external_platform, convert_doi
#from app.external_doi.zenodo import convert_zenodo_doi

from app.doi_agency.utils import get_doi_agency
from app.doi_agency.datacite import get_doi_list_fastapi

log = logging.getLogger(__name__)

# Setup doi_agency router
router = APIRouter(prefix="/doi_agency", tags=["doi_agency"])


@router.get(
    "/list",
    name="doi_list",
    status_code=200,
    responses={
        200: {
            "model": Dict[str, Any],
            "description": "DOI list successfully returned",
        },
        400: {"model": ConvertError},
        404: {"model": ConvertError},
        500: {"model": ConvertError},
    },
)
async def convert_external_doi(
    doi_agency_name: Annotated[
        str,
        Query(
            description="DOI agency",
            openapi_examples={
                "datacite": {
                    "summary": "DataCite agency",
                    "value": "datacite",
                },
            },
        ),
    ],    
    doi_prefix: Annotated[
        str,
        Query(
            description="DOI prefix",
            openapi_examples={
                "datacite": {
                    "summary": "DataCite DOI prefix",
                    "value": "10.25678",
                },
            },
        ),
    ],
    user_agent: Annotated[
        str,
        Query(
            description="email address to send to DOI agency for API call",
            openapi_examples={
                "normal": {
                    "summary": "Example user_agent value",
                    "value": "user@example.com",
                }
            },
        ),
    ],
    dcat_trigger: Annotated[
        bool,
        Query(
            alias="DCAT-AP CH convert",
            description="If true conversion to the DCAT-AP CH format is triggered.",
        ),
    ] = False,
):
    """Retrieve a DOI list given the DOI prefix

    Currently supports DOIs issued by DataCite.
    """

    try:
#        doi_agency = get_doi_agency(doi_agency_name)
#        match doi_agency:
#            case DOIAgency.DATACITE:
#                log.info("Here")
#                result = get_doi_list_cursor(doi_prefix=doi_prefix)

        result = get_doi_list_fastapi(doi_prefix=doi_prefix, cache=os.getenv("CACHE"))

        #cont = result.get("result", {})
        #sc = result.get("status_code", 500)
        return JSONResponse(result)

    except:
        pass
        
##        # Extract status code from conversion result
##        sc = result.get("status_code", 500)
##
##        # Return result if conversion successful
##        if is_type_valid(result, ConvertSuccess):
##            cont = result.get("result", {})
##            return JSONResponse(content=cont, status_code=sc)
##
##        # Return error if conversion failed
##        elif is_type_valid(result, ConvertError):
##            return JSONResponse(content=result, status_code=sc)
##
##        # Else raise exception if result cannot be validated as success or error
##        else:
##            raise Exception("Failed to validate result of conversion")
##
##    except Exception as e:
##        log.error(e)
##        return JSONResponse(
##            {
##                "status_code": 500,
##                "message": "Failed to bind to DOI agency '%s'" % doi_agency_name,
##                "error": "Check logs for error",
##            }
##        )


def is_type_valid(obj: Any, typ: Any) -> bool:
    """Return True if object is validated as type. Else return False.

    :param obj: Object to validate
    :param typ: Type used to validate object
    :return: boolean
    """
    try:
        validator = TypeAdapter(typ)
        validator.validate_python(obj)
        return True
    except ValidationError:
        return False
