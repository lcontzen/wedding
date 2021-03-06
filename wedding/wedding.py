import os
import datetime
import unicodedata
import logging
from flask import Flask, request, abort, session, g, redirect, url_for, \
                  render_template, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
Bootstrap(app)
app.config.from_object(__name__)
app.config.update(dict(
    SQLALCHEMY_DATABASE_URI='sqlite:///' +
                            os.path.join(app.root_path, 'wedding.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY='devkeyfixme',
    ))
app.config.from_envvar('WEDDING_SETTINGS', silent=True)
db = SQLAlchemy(app)
logging.basicConfig(filename='wedding/wedding.log',
                    level=logging.INFO,
                    format='%(asctime)s|%(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logging.warning("App started")


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

    def __init__(self, firstname, name, party_size, commune, ceremony,
                 cocktail, dinner, party):
        self.firstname = firstname
        self.name = name
        self.party_size = party_size
        self.commune = commune
        self.ceremony = ceremony
        self.cocktail = cocktail
        self.dinner = dinner
        self.party = party

    def __repr__(self):
        return '<Invited %s %s>' % (self.firstname, self.name)


class Replies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50))
    name = db.Column(db.String(50))
    commune = db.Column(db.Boolean)
    ceremony = db.Column(db.Boolean)
    cocktail = db.Column(db.Boolean)
    dinner = db.Column(db.Boolean)
    party = db.Column(db.Boolean)
    comments = db.Column(db.Text)
    filled_in_by = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    unavailable = db.Column(db.Boolean)

    def __init__(self, firstname, name, commune, ceremony, cocktail, dinner,
                 party, comments, filled_in_by, unavailable):
        self.firstname = firstname
        self.name = name
        self.commune = commune
        self.ceremony = ceremony
        self.cocktail = cocktail
        self.dinner = dinner
        self.party = party
        self.comments = comments
        self.filled_in_by = filled_in_by
        self.unavailable = unavailable

    def __repr__(self):
        return '<Reply %s %s %s>' % (self.firstname, self.name, self.timestamp)


def cleanup_name(name):
    name = ''.join(c for c in unicodedata.normalize('NFD', name)
                   if unicodedata.category(c) != 'Mn')
    name = name.replace('-', '').replace(' ', '')
    return name.lower()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


def init_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    logging.critical("flask initdb has been run.")


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
            r_fn = cleanup_name(request.form['firstname'])
            r_n = cleanup_name(request.form['name'])
            user = Invited.query.filter_by(firstname=r_fn, name=r_n).first()
            if user:
                logging.warning('%s %s successfully logged in.' % (r_fn, r_n))
                session['firstname'] = r_fn.capitalize()
                session['name'] = r_n.capitalize()
                session['party_size'] = user.party_size
                session['commune'] = user.commune
                session['ceremony'] = user.ceremony
                session['cocktail'] = user.cocktail
                session['dinner'] = user.dinner
                session['party'] = user.party
                session['logged_in'] = True
                return redirect(url_for('show_rsvp'))
            else:
                error = "Nom ou prénom erroné. Veuillez réessayer."
                logging.error('%s %s failed to log in.' % (r_fn, r_n))
        return render_template('rsvp.html', error=error)
    elif request.method == 'POST':  # Thanks part of page
        session['submitted'] = True
        session['added'] = 0
        for i in range(session['party_size']):
            replies = request.form
            if replies['firstname_' + str(i)] != '' or \
               replies['name_' + str(i)] != '':
                r = {}
                r['firstname'] = replies['firstname_' + str(i)] if\
                    replies['firstname_' + str(i)] != '' else\
                    replies['firstname_0']
                r['name'] = replies['name_' + str(i)] if\
                    replies['name_' + str(i)] != '' else replies['name_0']
                for k in ['commune', 'ceremony', 'cocktail',
                          'dinner', 'party', 'unavailable']:
                    r[k] = True if k+'_'+str(i) in replies.keys() else False
                r['comments'] = replies['comments_' + str(i)]

                db.session.add(Replies(r['firstname'].capitalize(),
                                       r['name'].capitalize(),
                                       r['commune'], r['ceremony'],
                                       r['cocktail'], r['dinner'],
                                       r['party'], r['comments'],
                                       session['firstname'] +
                                       ' ' + session['name'],
                                       r['unavailable']))
                db.session.commit()
                session['added'] += 1
        logging.warning('%s %s successfully replied for %s persons' %
                        (replies['firstname_0'],
                         replies['name_0'],
                         session['added']))
        return render_template('rsvp.html')
    else:  # Form
        return render_template('rsvp.html')


@app.route('/liste')
def show_list():
    session.clear()
    return render_template('liste.html')


if __name__ == "__main__":
    app.run(threaded=True)
