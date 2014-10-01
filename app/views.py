from flask import render_template, flash, redirect, url_for
from app import app, db
from .models import Host, Role, Stage, Domain
from .tables import HostTable
from .forms import FilterHostForm, NewHostForm

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
      flash('Filtered data.')
    else:
      items = Host.query.all()
    table = HostTable(items, classes=['table', 'table-striped'])
    return render_template("index.html",
                           form = form,
                           table = table,
                           title='Home')

@app.route('/host/new', methods = ['GET', 'POST'])
def new_host():
    form = NewHostForm()
    form.role.choices = [(h.id, h.name) for h in Role.query.all()]
    form.stage.choices = [(s.id, s.name) for s in Stage.query.all()]
    form.domain.choices = [(d.id, d.name) for d in Domain.query.all()]

    if form.validate_on_submit():
        hostname = form.hostname.data
        if Host.query.filter(Host.hostname == hostname).first():
            flash('Hostname must be unique')
        else:
            role = form.role.data
            domain = form.domain.data
            stage = form.stage.data
            h = Host(hostname=hostname, role_id=role, domain_id=domain,
                     stage_id=stage)
            db.session.add(h)
            db.session.commit()
            flash('Added new host: %s' % hostname)
            return redirect(url_for('index'))

    return render_template("host.html",
                       form = form,
                       title='Add Host')

@app.route('/host/edit/<host_id>', methods = ['GET', 'POST'])
def edit_host(host_id):
    host = Host.query.get(host_id)
    if not host:
        flash('Host does not exist')
        return redirect( url_for('index'))

    form = NewHostForm()
    form.role.choices = [(h.id, h.name) for h in Role.query.all()]
    form.stage.choices = [(s.id, s.name) for s in Stage.query.all()]
    form.domain.choices = [(d.id, d.name) for d in Domain.query.all()]

    if form.validate_on_submit():
        host.hostname = form.hostname.data
        host.role_id = form.role.data
        host.domain_id = form.domain.data
        host.stage_id = form.stage.data
        db.session.add(host)
        db.session.commit()
        flash('Changed host: %s' % host.hostname)
        return redirect(url_for('index'))
    else:
        form.hostname.data = host.hostname
        form.role.data = host.role_id
        form.stage.data = host.stage_id
        form.domain.data = host.domain_id

        return render_template("host.html",
                       form = form,
                       title='Change Host')

@app.route('/host/del/<host_id>', methods = ['GET', 'POST'])
def delete_host(host_id):
    h = Host.query.get(host_id)
    if h:
        db.session.delete(h)
        db.session.commit()
        flash('Removed host: %s' % h.hostname)
    else:
        flash('Host does not exist')
    return redirect(url_for('index'))

