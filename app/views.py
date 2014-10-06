from flask import render_template, flash, redirect, url_for, session, g, request
from app import app, db
from .models import Host, Role, Stage, Domain
from .tables import HostTable
from .forms import FilterHostForm, NewHostForm, RoleForm
from .forms import DomainForm, StageForm
import re

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
def index():
    form = FilterHostForm()
    form.role.choices = [(h.id, h.name) for h in Role.query.all()]
    form.role.choices.insert(0, (0, 'all'))
    form.stage.choices = [(s.id, s.name) for s in Stage.query.all()]
    form.stage.choices.insert(0, (0, 'all'))
    form.domain.choices = [(d.id, d.name) for d in Domain.query.all()]
    form.domain.choices.insert(0, (0, 'all'))

    stage = session.get('stage', None)
    role = session.get('role', None)
    domain = session.get('domain', None)

    # Form was submitted ...
    if form.validate_on_submit():
        # 'Filter' clicked
        if request.form['submit'] == 'Filter':
            role = form.role.data
            domain = form.domain.data
            stage = form.stage.data
        # 'All' clicked - reset all fields everywhere
        else:
            role = None
            session['role'] = None
            domain = None
            session['domain'] = None
            stage = None
            session['stage'] = None
            form.role.data = None
            form.stage.data = None
            form.domain.data = None
    # set filter dropdowns to the values of the session
    else:
        form.role.data = session['role']
        form.stage.data = session['stage']
        form.domain.data = session['domain']


    items = Host.query
    if role:
        items = items.filter(Host.role_id==role)
        session['role'] = role
    if stage:
        items = items.filter(Host.stage_id==stage)
        session['stage'] = stage
    if domain:
        items = items.filter(Host.domain_id==domain)
        session['domain'] = domain
    items = items.order_by('hostname asc').all()
    if session['role'] or session['stage'] or session['domain']:
        flash('Filtered data.', 'info')
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
        hostnames = [form.hostname.data]
        if form.geohost.data:
            hostnames.append(re.sub(r'a([^a]?)$', r'b\1', form.hostname.data))

        for hostname in hostnames:
            if Host.query.filter(Host.hostname == hostname).first():
                flash('Host %s exists already!' % hostname, 'warning')
            else:
                role = form.role.data
                domain = form.domain.data
                stage = form.stage.data
                h = Host(hostname=hostname, role_id=role, domain_id=domain,
                         stage_id=stage)
                db.session.add(h)
                db.session.commit()
                flash('Added new host: %s' % hostname, 'success')
        return redirect(url_for('index'))

    return render_template("host.html",
                       form = form,
                       title='Add Host')

@app.route('/host/edit/<host_id>', methods = ['GET', 'POST'])
def edit_host(host_id):
    host = Host.query.get(host_id)
    if not host:
        flash('Host does not exist', 'warning')
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
        flash('Changed host: %s' % host.hostname, 'success')
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
        flash('Removed host: %s' % h.hostname, 'success')
    else:
        flash('Host does not exist', 'warning')
    return redirect(url_for('index'))

@app.route('/add/role', methods = ['GET', 'POST'])
def add_role():
    form = RoleForm()

    if form.validate_on_submit():
        if Role.query.filter(Role.name == form.name.data).first():
            flash('Role %s exists already!' % form.name.data, 'warning')
            return redirect(url_for('add_role'))
        else:
            r = Role(name=form.name.data)
            db.session.add(r)
            db.session.commit()
            flash('Added new role: %s' % form.name.data, 'success')
        return redirect(url_for('index'))

    return render_template("admin.html",
                       form = form,
                       title='Add role')

@app.route('/add/stage', methods = ['GET', 'POST'])
def add_stage():
    form= StageForm()

    if form.validate_on_submit():
        if Stage.query.filter(Stage.name == form.name.data).first():
            flash('Stage %s exists already!' % form.name.data, 'warning')
            return redirect(url_for('add_stage'))
        else:
            r = Stage(name=form.name.data)
            db.session.add(r)
            db.session.commit()
            flash('Added new stage: %s' % form.name.data, 'success')
        return redirect(url_for('index'))

    return render_template("admin.html",
                       form = form,
                       title='Add stage')

@app.route('/add/domain', methods = ['GET', 'POST'])
def add_domain():
    form = DomainForm()

    if form.validate_on_submit():
        if Domain.query.filter(Domain.name == form.name.data).first():
            flash('Domain %s exists already!' % form.name.data, 'warning')
            return redirect(url_for('add_domain'))
        else:
            r = Domain(name=form.name.data)
            db.session.add(r)
            db.session.commit()
            flash('Added new domain: %s' % form.name.data, 'success')
        return redirect(url_for('index'))

    return render_template("admin.html",
                       form = form,
                       title='Add domain')

