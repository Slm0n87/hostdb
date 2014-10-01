from app import db

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
