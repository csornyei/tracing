from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

from src.config import config
from src.database import Base, engine
from src.routes.user import router as user_router
from src.routes.todo import router as todo_router
from src.tracing import setup_tracing

setup_tracing(service_name="todo-app", otlp_endpoint=config.OTLP_ENDPOINT)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_router)
app.include_router(todo_router)

FastAPIInstrumentor.instrument_app(app)
SQLAlchemyInstrumentor().instrument(engine=engine)
