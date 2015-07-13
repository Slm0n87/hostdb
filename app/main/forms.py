from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Regexp, Length

class FilterHostForm(Form):
    namelike = StringField(u'Hostname', 
                         validators=[
                             Regexp(r'^[A-Za-z0-9-%]*$',
                                    message='Not a hostname "like" expression'
                                    )
                             ]
                         )
    role = SelectField(u'Role', coerce=int)
    stage = SelectField(u'Stage', coerce=int)
    domain = SelectField(u'Domain', coerce=int)
    submit = SubmitField(u'Filter')
    allhosts = SubmitField(u'Reset')

class NewHostForm(Form):
    hostname = StringField(u'Hostname', validators=[DataRequired(), 
                                                   Regexp(r'^[A-Za-z0-9-]+$',
                                                          message='Invalid characters')
                                                   ])
    domain = SelectField(u'Domain', coerce=int)
    role = SelectField(u'Role', coerce=int)
    stage = SelectField(u'Stage', coerce=int)
    geohost = BooleanField(u'georedundant?')

class RoleForm(Form):
    name = StringField(u'Role name', validators=[DataRequired(), 
                                                   Regexp(r'^[A-Za-z0-9-]+$',
                                                          message='Invalid characters'),
                                                    Length(max=30)
                                                   ])
    submit = SubmitField(u'Add Role')
class StageForm(Form):
    name = StringField(u'Stage name', validators=[DataRequired(), 
                                                   Regexp(r'^[A-Za-z0-9-]+$',
                                                          message='Invalid characters')
                                                   ])
    submit = SubmitField(u'Add Stage')

class DomainForm(Form):
    name = StringField(u'Domain name', validators=[DataRequired(), 
                                                   Regexp(r'^[A-Za-z0-9-.]+\.[a-z]{2,6}$',
                                                          message='Not a domain name')
                                                   ])
    submit = SubmitField(u'Add Domain')

