"""Root router to import all other routers."""

import logging
from typing import Callable

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRoute

#from app.config import config_app
#from app.converters import api_converters
#from app.edna import api_edna
#from app.external_doi import api_external_doi

from config import config_app
#from converters import api_converters
#from edna import api_edna
#from external_doi import api_external_doi

#from doi_agency import datacite


# Setup logging
log = logging.getLogger(__name__)


class RouteErrorHandler(APIRoute):
    """Custom APIRoute that handles application errors and exceptions."""

    def get_route_handler(self) -> Callable:
        """Original route handler for extension."""
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """Route handler with improved logging."""
            try:
                return await original_route_handler(request)
            except Exception as e:
                if isinstance(e, HTTPException):
                    raise Exception from e
                log.exception(f"Uncaught error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")

        return custom_route_handler


# Create APIRouter() instance
api_router = APIRouter()

# Add routers to api_router
#api_router.include_router(api_converters.router)
#api_router.include_router(api_external_doi.router)
#api_router.include_router(api_edna.router)

# Setup error router
error_router = APIRouter(route_class=RouteErrorHandler)


@api_router.get("/", include_in_schema=False)
async def home():
    """Redirect home to docs."""
    return RedirectResponse(f"{config_app.ROOT_PATH}/docs")
