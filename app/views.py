from flask import render_template, flash
from app import app
from app.models import Host, Role, Stage, Domain
from app.tables import HostTable
from app.forms import FilterHostForm

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
def index():
    form = FilterHostForm()
    form.role.choices = [(h.id, h.name) for h in Role.query.all()]
    form.stage.choices = [(s.id, s.name) for s in Stage.query.all()]
    form.domain.choices = [(d.id, d.name) for d in Domain.query.all()]

    if form.validate_on_submit():
      role = form.role.data
      domain = form.domain.data
      stage = form.stage.data
      items = Host.query.filter(Host.domain_id==domain,
                                Host.role_id==role,
                                Host.stage_id==stage).all()
    else:
      flash('Not filtered data.')
      items = Host.query.all()
    table = HostTable(items)
    return render_template("index.html",
                           form = form,
                           table = table,
                           title='Home')
