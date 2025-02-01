from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from app.main import app

api = FastAPI()
api.mount("/", WSGIMiddleware(app.server))
