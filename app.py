from flask import Flask, render_template
from dashapp import init_dash

app = Flask(__name__)

# Initialize Dash
dash_app = init_dash(app)

@app.route('/')
def index():
    return '<a href="/dash">Go to Dash</a>' 

if __name__ == '__main__':
    app.run(debug=True)
