from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, SelectField, SubmitField, TextAreaField
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

class FilterHistoryForm(Form):
    item_name = StringField(u'Item', 
                         validators=[
                             Regexp(r'^[A-Za-z0-9-%]*$',
                                    message='Not a valid SQL "like" expression'
                                    )
                             ]
                         )
    action = SelectField(u'Action')
    item_type = SelectField(u'Type')
    userid = SelectField(u'User', coerce=int)
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
    comment = TextAreaField('Comment', validators=[Length(max=512)])

class RoleForm(Form):
    name = StringField(u'Role name', validators=[DataRequired(), 
                                                   Regexp(r'^[A-Za-z0-9-]+$',
                                                          message='Invalid characters'),
                                                    Length(max=30)
                                                   ])
    comment = TextAreaField('Comment', validators=[Length(max=512)])
    submit = SubmitField(u'Add Role')
class StageForm(Form):
    name = StringField(u'Stage name', validators=[DataRequired(), 
                                                   Regexp(r'^[A-Za-z0-9-]+$',
                                                          message='Invalid characters')
                                                   ])
    comment = TextAreaField('Comment', validators=[Length(max=512)])
    submit = SubmitField(u'Add Stage')

class DomainForm(Form):
    name = StringField(u'Domain name', validators=[DataRequired(), 
                                                   Regexp(r'^[A-Za-z0-9-.]+\.[a-z]{2,6}$',
                                                          message='Not a domain name')
                                                   ])
    comment = TextAreaField('Comment', validators=[Length(max=512)])
    submit = SubmitField(u'Add Domain')

