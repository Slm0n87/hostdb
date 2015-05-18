from flask import render_template, flash, redirect, url_for, session, g, request, current_app
from flask.ext.login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from .. import db
from ..email import send_email
from . import main
from ..models import Host, Role, Stage, Domain, User
from .tables import HostTable
from .forms import FilterHostForm, NewHostForm, RoleForm
from .forms import DomainForm, StageForm
import re
from datetime import datetime, tzinfo
import pytz

@main.route('/', methods = ['GET', 'POST'])
@main.route('/index', methods = ['GET', 'POST'])
@main.route('/index/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    form = FilterHostForm()
    form.role.choices = [(h.id, h.name) for h in Role.query.all()]
    form.role.choices.insert(0, (0, 'all'))
    form.stage.choices = [(s.id, s.name) for s in Stage.query.all()]
    form.stage.choices.insert(0, (0, 'all'))
    form.domain.choices = [(d.id, d.name) for d in Domain.query.all()]
    form.domain.choices.insert(0, (0, 'all'))

    for key in ['role', 'stage', 'domain']:
        if not session.has_key(key):
            session[key] = None

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
        form.role.data = session.get('role', None)
        form.stage.data = session.get('stage', None)
        form.domain.data = session.get('domain', None)


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
    items = items.order_by('hostname asc').paginate(page,
                                                    current_app.config['HOSTS_PER_PAGE'], False)
    if session['role'] or session['stage'] or session['domain']:
        flash('Filtered data.', 'info')
    table = HostTable(items.items, classes=['table', 'table-striped'])
    return render_template("index.html",
                           form = form,
                           table = table,
                           items=items,
                           title='Home')

@main.route('/host/new', methods = ['GET', 'POST'])
@login_required
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
                h = Host(hostname=hostname,
                         role=role,
                         domain=domain,
                         stage=stage,
                         user = g.user.id)
                db.session.add(h)
                db.session.commit()
                flash('Added new host: %s' % hostname, 'success')
        return redirect(url_for('.index'))

    return render_template("host.html",
                       form = form,
                       title='Add Host')

@main.route('/host/edit/<host_id>', methods = ['GET', 'POST'])
@login_required
def edit_host(host_id):
    host = Host.query.get(host_id)
    if not host:
        flash('Host does not exist', 'warning')
        return redirect( url_for('.index'))

    form = NewHostForm()
    form.role.choices = [(h.id, h.name) for h in Role.query.all()]
    form.stage.choices = [(s.id, s.name) for s in Stage.query.all()]
    form.domain.choices = [(d.id, d.name) for d in Domain.query.all()]

    if form.validate_on_submit():
        host.hostname = form.hostname.data
        host.role_id = form.role.data
        host.domain_id = form.domain.data
        host.stage_id = form.stage.data
        host.modified_by = g.user.id
        host.last_modified = datetime.now(tz=pytz.utc)
        db.session.add(host)
        db.session.commit()
        flash('Changed host: %s' % host.hostname, 'success')
        return redirect(url_for('.index'))
    else:
        form.hostname.data = host.hostname
        form.role.data = host.role_id
        form.stage.data = host.stage_id
        form.domain.data = host.domain_id

        return render_template("host.html",
                       form = form,
                       title='Change Host')

@main.route('/host/del/<host_id>', methods = ['GET', 'POST'])
@login_required
def delete_host(host_id):
    h = Host.query.get(host_id)
    if h:
        db.session.delete(h)
        db.session.commit()
        flash('Removed host: %s' % h.hostname, 'success')
    else:
        flash('Host does not exist', 'warning')
    return redirect(url_for('.index'))

@main.route('/add/role', methods = ['GET', 'POST'])
@login_required
def add_role():
    form = RoleForm()

    if form.validate_on_submit():
        if Role.query.filter(Role.name == form.name.data).first():
            flash('Role %s exists already!' % form.name.data, 'warning')
            return redirect(url_for('.add_role'))
        else:
            r = Role(name=form.name.data)
            db.session.add(r)
            db.session.commit()
            flash('Added new role: %s' % form.name.data, 'success')
        return redirect(url_for('.index'))

    return render_template("admin.html",
                       form = form,
                       title='Add role')

@main.route('/add/stage', methods = ['GET', 'POST'])
@login_required
def add_stage():
    form= StageForm()

    if form.validate_on_submit():
        if Stage.query.filter(Stage.name == form.name.data).first():
            flash('Stage %s exists already!' % form.name.data, 'warning')
            return redirect(url_for('.add_stage'))
        else:
            r = Stage(name=form.name.data)
            db.session.add(r)
            db.session.commit()
            flash('Added new stage: %s' % form.name.data, 'success')
        return redirect(url_for('.index'))

    return render_template("admin.html",
                       form = form,
                       title='Add stage')

@main.route('/add/domain', methods = ['GET', 'POST'])
@login_required
def add_domain():
    form = DomainForm()

    if form.validate_on_submit():
        if Domain.query.filter(Domain.name == form.name.data).first():
            flash('Domain %s exists already!' % form.name.data, 'warning')
            return redirect(url_for('.add_domain'))
        else:
            r = Domain(name=form.name.data)
            db.session.add(r)
            db.session.commit()
            flash('Added new domain: %s' % form.name.data, 'success')
        return redirect(url_for('.index'))

    return render_template("admin.html",
                       form = form,
                       title='Add domain')

@main.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', title='Register')
    user = User(request.form['username'] , request.form['password'],request.form['email'])
    db.session.add(user)
    db.session.commit()
    token = user.generate_confirmation_token()
    send_email(user.email, 'Confirm Your Account',
               'email/confirm', user=user, token=token)
    flash('A confirmation email has been sent to you by email.', 'info')
    return redirect(url_for('.login'))

@main.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!', 'info')
        token2 = current_user.generate_activation_token()
        send_email(current_app.config['MAIL_ADMIN'], 'Activate account for %s' % current_user.email,
                   'email/activate', user=current_user, token=token2)
        flash('An admin has been notified to activate the account before you can login.', 'info')
    else:
        flash('The confirmation link is invalid or has expired.', 'warning')
    logout_user()
    return redirect(url_for('.index'))

@main.route('/activate/<token>')
@login_required
def activate(token):
    user = current_user.activate(token)
    if user:
        send_email(user.email, 'Your account has been activated',
                   'email/activated', user=user)
        flash('You have activated the account for user %s.' % user.username, 'info')
    else:
        flash('The activation link is invalid or has expired.', 'warning')
    return redirect(url_for('.index'))


@main.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', title='Login')
    username = request.form['username']
    password = request.form['password']
    registered_user = User.query.filter_by(username=username).first()
    if registered_user is None or check_password_hash(registered_user.password, password) is False:
        flash('Username or Password is invalid' , 'warning')
        return redirect(url_for('.login'))
    elif registered_user.confirmed == 0 and request.args.get('next').startswith('/confirm/'):
        login_user(registered_user)
        return redirect(request.args.get('next'))
    elif registered_user.activated == 0:
        flash('Your account still requires activation by the admins, they have already been notified' , 'info')
    else:
        login_user(registered_user)
        flash('Logged in successfully as %s' % username, 'info')
    return redirect(request.args.get('next') or url_for('.index'))

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('.index')) 

@main.before_request
def before_request():
        g.user = current_user


