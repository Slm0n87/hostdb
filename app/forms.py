from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Regexp

class FilterHostForm(Form):
    role = SelectField(u'Role', coerce=int)
    stage = SelectField(u'Stage', coerce=int)
    domain = SelectField(u'Domain', coerce=int)
    submit = SubmitField(u'Filter')

class NewHostForm(Form):
    hostname = StringField(u'Hostname', validators=[DataRequired(), 
                                                   Regexp(r'^[A-Za-z0-9-]+$',
                                                          message='Invalid characters')
                                                   ])
    role = SelectField(u'Role', coerce=int)
    stage = SelectField(u'Stage', coerce=int)
    domain = SelectField(u'Domain', coerce=int)
