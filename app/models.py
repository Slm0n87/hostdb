from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(64), index=True, unique=True)
    domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    stage_id = db.Column(db.Integer, db.ForeignKey('stage.id'))

    def __repr__(self):
        return '<Host %r>' % (self.hostname)

    def __unicode__(self):
        return self.hostname

class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    hosts = db.relationship('Host', backref='domain', lazy='dynamic')

    def __repr__(self):
        return '<Domain %r>' % (self.name)

    def __unicode__(self):
        return self.name

class Stage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    hosts = db.relationship('Host', backref='stage', lazy='dynamic')

    def __repr__(self):
        return '<Stage %r>' % (self.name)

    def __unicode__(self):
        return self.name

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    hosts = db.relationship('Host', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % (self.name)

    def __unicode__(self):
        return self.name

class User(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id',db.Integer , primary_key=True)
    username = db.Column('username', db.String(20), unique=True , index=True)
    password = db.Column('password' , db.String(128))
    email = db.Column('email',db.String(50),unique=True , index=True)
    registered_on = db.Column('registered_on' , db.DateTime)
 
    def __init__(self, username, password, email):
        self.username = username
        self.set_password(password)
        self.email = email
        self.registered_on = datetime.utcnow()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return unicode(self.id)
 
    def __repr__(self):
        return '<User %r>' % (self.username)
