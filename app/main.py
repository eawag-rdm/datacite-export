"""Main init file for FastAPI project datacite-export"""

import os
print(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#from app.config import config_app, log_level
#from app.router import api_router, error_router

from app.config import config_app, log_level
from app.router import api_router, error_router

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


# Setup logging
logging.basicConfig(
    level=log_level,
    format=(
        "%(asctime)s.%(msecs)03d [%(levelname)s] "
        "%(name)s | %(funcName)s:%(lineno)d | %(message)s"
    ),
    datefmt="%y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


def get_application() -> FastAPI:
    """Create app instance using config_app."""
    _app = FastAPI(
        title="datacite-export",
        description="DOI prefix record extraction from DataCite with option DCAT-AP CH trigger",
        version=config_app.APP_VERSION,
        license_info={
            "name": "Not specified"
        },
        debug=config_app.DEBUG,
        root_path=config_app.ROOT_PATH,
    )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(config_app.CORS_ORIGIN)],
        allow_headers=["*"],
    )

    return _app


# Create app instance
app = get_application()

# Add routers
app.include_router(api_router)
app.include_router(error_router)
