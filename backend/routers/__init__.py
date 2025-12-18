"""
Routers package for Contract Drift Detector API.
"""

from .contracts import router as contracts_router
from .versions import router as versions_router
from .changes import router as changes_router
from .alerts import router as alerts_router

__all__ = [
    "contracts_router",
    "versions_router", 
    "changes_router",
    "alerts_router",
]
