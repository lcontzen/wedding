import os
from flask import Flask, request, session, g, redirect, url_for, \
                  render_template
from flask_bootstrap import Bootstrap


app = Flask(__name__)  # create the application instance :)
Bootstrap(app)
app.config.from_object(__name__)  # load config from this file , wedding.py
app.config.from_envvar('WEDDING_SETTINGS', silent=True)


@app.route('/')
def show_index():
    return render_template('index.html')
