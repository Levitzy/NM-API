from flask import Flask, Request
from app import app as flask_app

# Handle Vercel serverless function request
def handler(request: Request):
    with flask_app.request_context(request.environ):
        return flask_app.full_dispatch_request()
