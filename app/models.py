from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for
from . import db, login_manager
from pytz import timezone

class History(db.Model):
    __tablename__ = 'history'
    id            = db.Column(db.Integer, primary_key=True)
    date          = db.Column(db.DateTime)
    userid        = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    item_id       = db.Column(db.Integer)
    item_name     = db.Column(db.String(64))
    item_type     = db.Column(db.String(64))
    action        = db.Column(db.String(24))
    comment       = db.Column(db.Text)

    def __init__(self, action, item, user):
        self.action = action
        if type(item) == Host:
            self.item_name = item.hostname
        else:
            self.item_name = item.name

        self.item_id = item.id
        self.item_type = type(item).__name__
        self.comment = item.comment
        self.userid = user
        if current_app.config['TIMEZONE'] == 'NAIVE':
            tz=None
        else:
            tz = timezone(current_app.config['TIMEZONE'])
        self.date = datetime.now(tz).replace(microsecond=0)

    def __repr__(self):
        return '<History %r %r %r>' % (self.action, self.item_type, self.item_name)

    def __unicode__(self):
        return '%r_%r_%r' % (self.action, self.item_type, self.item_name)

class Host(db.Model):
    __tablename__ = "host"
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(64), index=True, unique=True)
    domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    stage_id = db.Column(db.Integer, db.ForeignKey('stage.id'))
    last_modified = db.Column(db.DateTime)
    modified_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    comment = db.Column(db.Text)

    def __init__(self, hostname, stage, domain, role, user, comment):
        self.hostname = hostname
        self.domain_id = domain
        self.stage_id = stage
        self.role_id = role
        self.modified_by = user
        self.comment = comment
        if current_app.config['TIMEZONE'] == 'NAIVE':
            tz=None
        else:
            tz = timezone(current_app.config['TIMEZONE'])
        self.last_modified = datetime.now(tz)

    def __repr__(self):
        return '<Host %r>' % (self.hostname)

    def __unicode__(self):
        return self.hostname

class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    comment = db.Column(db.Text)
    hosts = db.relationship('Host', backref='domain', lazy='dynamic')

    def __repr__(self):
        return '<Domain %r>' % (self.name)

    def __unicode__(self):
        return self.name

class Stage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    comment = db.Column(db.Text)
    hosts = db.relationship('Host', backref='stage', lazy='dynamic')

    def __repr__(self):
        return '<Stage %r>' % (self.name)

    def __unicode__(self):
        return self.name

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    comment = db.Column(db.Text)
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
    confirmed = db.Column(db.Boolean, default=False)
    activated = db.Column(db.Boolean, default=False)
    #hosts = db.relationship('Host', backref='creator', lazy='dynamic')
    #domains = db.relationship('Domain', backref='creator', lazy='dynamic')
    #stages = db.relationship('Stage', backref='creator', lazy='dynamic')
    #roles = db.relationship('Role', backref='creator', lazy='dynamic')
    events = db.relationship('History', backref='creator', lazy='dynamic')

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

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def generate_activation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'activate': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    @staticmethod
    def activate(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        user = User.query.get(data['activate'])
        if user.activated is False:
            user.activated = True
            db.session.add(user)
        return user

    def __repr__(self):
        return '<User %r>' % (self.username)


@login_manager.user_loader
def load_user(id):
        return User.query.get(int(id))

