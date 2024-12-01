import uvicorn
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from main import app

api = FastAPI()
api.mount("/", WSGIMiddleware(app.server))

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8050)
