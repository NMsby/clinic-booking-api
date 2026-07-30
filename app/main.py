from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.services.exceptions import BusinessRuleViolation, ConflictError, NotFoundError

app = FastAPI(title="Clinic Booking API")


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(BusinessRuleViolation)
async def business_rule_violation_handler(request: Request, exc: BusinessRuleViolation) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})
