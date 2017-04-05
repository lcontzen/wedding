import os
import sqlite3
from flask import Flask, request, abort, session, g, redirect, url_for, \
                  render_template, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
Bootstrap(app)
app.config.from_object(__name__)
app.config.update(dict(
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.root_path, 'wedding.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY='devkeyfixme',
    USERNAME='admin',
    PASSWORD='devpasswdfixme',
    FIRSTNAME='laurent',
    NAME='contzen',
    ))
app.config.from_envvar('WEDDING_SETTINGS', silent=True)
db = SQLAlchemy(app)


class Invited(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50))
    name = db.Column(db.String(50))
    party_size = db.Column(db.Integer)
    commune = db.Column(db.Boolean)
    ceremony = db.Column(db.Boolean)
    cocktail = db.Column(db.Boolean)
    dinner = db.Column(db.Boolean)
    party = db.Column(db.Boolean)
    babies = db.Column(db.Boolean)

    def __init__(self, firstname, name, party_size, commune, ceremony,
                 cocktail, dinner, party, babies):
        self.firstname = firstname
        self.name = name
        self.party_size = party_size
        self.commune = commune
        self.ceremony = ceremony
        self.cocktail = cocktail
        self.dinner = dinner
        self.party = party
        self.babies = babies

    def __repr__(self):
        return '<Invited %s %s>' % (self.firstname, self.name)


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    db.drop_all()
    db.create_all()
    db.session.add(Invited('laurent', 'contzen', 2, True, True, True, True,
                           True, True))
    db.session.add(Invited('a', 'b', 3, False, True, True, False, True, False))
    db.session.commit()


@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database.')


@app.route('/')
def show_index():
    session.clear()
    return render_template('index.html')


@app.route('/infos')
def show_infos():
    session.clear()
    return render_template('infos.html')


@app.route('/rsvp', methods=['GET', 'POST'])
def show_rsvp():
    error = None
    if not session.get('logged_in'):  # Login part of page
        if request.method == 'POST':
            db = get_db()
            q = """ select *
            from invited
            where firstname = '%s' and name = '%s';"""\
            % (request.form['firstname'].lower(), request.form['name'].lower())
            r = db.execute(q).fetchone()
            if r:
                session['firstname'] = request.form['firstname'].capitalize()
                session['name'] = request.form['name'].capitalize()
                for k in r.keys():
                    session[k] = r[k]
                session['logged_in'] = True
                return redirect(url_for('show_rsvp'))
            else:
                error = "Nom ou prénom erroné. Veuillez réessayer."
        return render_template('rsvp.html', error=error)
    elif request.method == 'POST':  # Thanks par of page
        session['submitted'] = True
        for i in range(session['party_size']):
            replies = request.form
            if replies['firstname_' + str(i)] != '' or \
               replies['name_' + str(i)] != '':
                r = {}
                r['firstname'] = replies['firstname_' + str(i)]
                r['name'] = replies['name_' + str(i)] if\
                    replies['name_' + str(i)] != '' else replies['name_0']
                for k in ['commune', 'ceremony', 'cocktail',
                          'dinner', 'party', 'babies']:
                    r[k] = 1 if k+'_'+str(i) in replies.keys() else 0
                r['comments'] = replies['comments_' + str(i)]
                q = """insert into replies(firstname, name, commune, ceremony,
cocktail, dinner, party, babies, comments, filled_in_by) values('%s', '%s',
%i, %i, %i, %i, %i, %i, '%s', '%s');""" % (r['firstname'].capitalize(),
                                           r['name'].capitalize(),
                                           r['commune'], r['ceremony'],
                                           r['cocktail'], r['dinner'],
                                           r['party'], r['babies'],
                                           r['comments'],
                                           session['firstname'] +
                                           ' ' + session['name'])
                c = get_db()
                c.execute(q)
                c.commit()
        return render_template('rsvp.html')
    else:  # Form
        return render_template('rsvp.html')


@app.route('/liste')
def show_list():
    session.clear()
    return render_template('liste.html')
