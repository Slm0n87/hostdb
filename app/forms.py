from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, SelectField, SubmitField
#from wtforms.validators import DataRequired

class FilterHostForm(Form):
    role = SelectField(u'Role', coerce=int)
    stage = SelectField(u'Stage', coerce=int)
    domain = SelectField(u'Domain', coerce=int)
    submit = SubmitField(u'Filter')
