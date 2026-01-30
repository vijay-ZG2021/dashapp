from flask import Flask, render_template
from dashapp import init_dash

def create_app():
    flask_app = Flask(__name__)
    init_dash(flask_app)
    return flask_app

server = create_app()   # 🔥 THIS IS WHAT AZURE NEEDS

