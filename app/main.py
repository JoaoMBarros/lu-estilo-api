from fastapi import FastAPI
from app.user.routes import user_router
from app.client.routes import client_router
from app.category.routes import category_router
from app.product.routes import product_router
from app.order.routes import order_router
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import sentry_sdk

sentry_sdk.init(
    dsn="https://96c64d76ebac02afd75dcf96b674760b@o4507465106587648.ingest.us.sentry.io/4507465108160512",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

app = FastAPI()

app.include_router(user_router)
app.include_router(client_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(order_router)

# Overriding the default exception handler to return a more user-friendly error message
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({"field": error["loc"][1], "detail": error["msg"]})
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": errors})

@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0