from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Union
import logging

logger = logging.getLogger(__name__)

class APIError(Exception):
    def __init__(self, status_code: int, message: str, details: Union[str, dict] = None):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(message)

async def error_handler_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except APIError as e:
        logger.error(f"API Error: {e.message}", exc_info=True)
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": e.message,
                "details": e.details,
                "path": request.url.path
            }
        )
    except ValueError as e:
        logger.error(f"Validation Error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Validation Error",
                "message": str(e),
                "path": request.url.path
            }
        )
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "path": request.url.path
            }
        )
