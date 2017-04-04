import os
from flask import Flask, request, session, g, redirect, url_for, \
                  render_template
from flask_bootstrap import Bootstrap


app = Flask(__name__)
Bootstrap(app)
app.config.from_object(__name__)
app.config.from_envvar('WEDDING_SETTINGS', silent=True)


@app.route('/')
def show_index():
    return render_template('index.html')


@app.route('/infos')
def show_infos():
    return render_template('infos.html')


@app.route('/rsvp')
def show_rsvp():
    return render_template('rsvp.html')


@app.route('/liste')
def show_list():
    return render_template('liste.html')
