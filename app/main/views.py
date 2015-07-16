from flask import render_template, flash, redirect, url_for, session, g, request, current_app
from flask.ext.login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from .. import db
from ..email import send_email
from . import main
from ..models import Host, Role, Stage, Domain, User, History
from .tables import HostTable, HistoryTable
from .forms import FilterHostForm, NewHostForm, RoleForm, FilterHistoryForm
from .forms import DomainForm, StageForm
import re
from datetime import datetime, tzinfo
from pytz import timezone



@main.route('/', methods = ['GET', 'POST'])
@main.route('/index', methods = ['GET', 'POST'])
@main.route('/index/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    form = FilterHostForm()
    form.role.choices = [(h.id, h.name) for h in Role.query.order_by('name').all()]
    form.role.choices.insert(0, (0, 'all'))
    form.stage.choices = [(s.id, s.name) for s in Stage.query.order_by('name').all()]
    form.stage.choices.insert(0, (0, 'all'))
    form.domain.choices = [(d.id, d.name) for d in Domain.query.order_by('name').all()]
    form.domain.choices.insert(0, (0, 'all'))

    for key in ['namelike', 'role', 'stage', 'domain']:
        if not session.has_key(key):
            session[key] = None

    stage = session.get('stage', None)
    role = session.get('role', None)
    domain = session.get('domain', None)
    namelike = session.get('namelike', None)

    # Form was submitted ...
    if form.validate_on_submit():
        # 'Filter' clicked
        if request.form['submit'] == 'Filter':
            flash('Filtered data.', 'info')
            session['role'] = form.role.data
            session['domain'] = form.domain.data
            session['stage'] = form.stage.data
            session['namelike'] = form.namelike.data
            if len(session['namelike']) and not '%' in session['namelike']:
                session['namelike'] += '%'
        # 'Reset' clicked - reset all fields everywhere
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
            namelike = None
            form.namelike.data = None
            session['namelike'] = None
        # Post/Redirect/Get !!!
        return redirect(url_for('.index'))
    # set filter dropdowns to the values of the session
    else:
        form.role.data = session.get('role', None)
        form.stage.data = session.get('stage', None)
        form.domain.data = session.get('domain', None)
        form.namelike.data = session.get('namelike', None)


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
    if namelike:
        items = items.filter(Host.hostname.like(namelike))
        session['namelike'] = namelike
    items = items.order_by('hostname asc').paginate(page,
                                                    current_app.config['HOSTS_PER_PAGE'], False)
    table = HostTable(items.items, classes=['table', 'table-striped'])
    return render_template("index.html",
                           form = form,
                           table = table,
                           items=items,
                           title='Home')

@main.route('/host/new', methods = ['GET', 'POST'])
@main.route('/host/new/<clone_from>', methods = ['GET', 'POST'])
@login_required
def new_host(clone_from=None):

    if clone_from:
        host = Host.query.get(clone_from)
        if not host:
            flash('Host does not exist', 'warning')
            return redirect( url_for('.index'))
    else:
        host = None

    form = NewHostForm()
    form.role.choices = [(h.id, h.name) for h in Role.query.order_by('name').all()]
    form.stage.choices = [(s.id, s.name) for s in Stage.query.order_by('name').all()]
    form.domain.choices = [(d.id, d.name) for d in Domain.query.order_by('name').all()]

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
                comment = form.comment.data
                h = Host(hostname=hostname,
                         role=role,
                         domain=domain,
                         stage=stage,
                         comment=comment,
                         user = g.user.id)
                db.session.add(h)
                db.session.commit()
                if h.id:
                    history = History(
                            action='add',
                            item=h,
                            user=g.user.id
                            )
                    db.session.add(history)
                    db.session.commit()
                flash('Added new host: %s' % hostname, 'success')
        return redirect(url_for('.index'))
    elif host:
        form.hostname.data = host.hostname
        form.role.data = host.role_id
        form.stage.data = host.stage_id
        form.domain.data = host.domain_id
        form.comment.data = host.comment

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
    form.role.choices = [(h.id, h.name) for h in Role.query.order_by('name').all()]
    form.stage.choices = [(s.id, s.name) for s in Stage.query.order_by('name').all()]
    form.domain.choices = [(d.id, d.name) for d in Domain.query.order_by('name').all()]

    if form.validate_on_submit():
        if request.form['submit'] == 'Delete':
            return redirect(url_for('.delete_host', host_id=host_id))
        elif request.form['submit'] == 'Clone':
            return redirect(url_for('.new_host', clone_from=host_id))
        else:
            if current_app.config['TIMEZONE'] == 'NAIVE':
                tz=None
            else:
                tz = timezone(current_app.config['TIMEZONE'])
            host.hostname = form.hostname.data
            host.role_id = form.role.data
            host.domain_id = form.domain.data
            host.stage_id = form.stage.data
            host.modified_by = g.user.id
            host.last_modified = datetime.now(tz)
            host.comment = form.comment.data
            history = History(
                    action='change',
                    item=host,
                    user=g.user.id
                    )
            db.session.add(host)
            db.session.add(history)
            db.session.commit()
            flash('Changed host: %s' % host.hostname, 'success')
            return redirect(url_for('.index'))
    else:
        form.hostname.data = host.hostname
        form.role.data = host.role_id
        form.stage.data = host.stage_id
        form.domain.data = host.domain_id
        form.comment.data = host.comment

        # metadata
        by = User.query.get(host.modified_by).username
        when = host.last_modified
        when = when.strftime('%Y-%m-%d %H:%M:%S %z')

        return render_template("host.html",
                       form = form,
                       by = by,
                       when = when,
                       title='Change Host')

@main.route('/host/del/<host_id>', methods = ['GET', 'POST'])
@login_required
def delete_host(host_id):
    h = Host.query.get(host_id)
    if h:
        history = History(
                action='delete',
                item=h,
                user=g.user.id
                )
        db.session.add(history)
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
            if r.id:
                history = History(
                        action='add',
                        item=r,
                        user=g.user.id
                        )
                db.session.add(history)
                db.session.commit()
            flash('Added new role: %s' % form.name.data, 'success')
        return redirect(url_for('.index'))

    roles = Role.query.order_by('name').all()
    return render_template("admin.html",
                       form = form,
                       liste = roles,
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
            if r.id:
                history = History(
                        action='add',
                        item=r,
                        user=g.user.id
                        )
                db.session.add(history)
                db.session.commit()
            flash('Added new stage: %s' % form.name.data, 'success')
        return redirect(url_for('.index'))

    stages = Stage.query.order_by('name').all()
    return render_template("admin.html",
                       form = form,
                       liste = stages,
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
            if r.id:
                history = History(
                        action='add',
                        item=r,
                        user=g.user.id
                        )
                db.session.add(history)
                db.session.commit()
            flash('Added new domain: %s' % form.name.data, 'success')
        return redirect(url_for('.index'))

    domains = Domain.query.order_by('name').all()
    return render_template("admin.html",
                       form = form,
                       liste = domains,
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


@main.route('/history', methods = ['GET', 'POST'])
@login_required
def history(page=1):
    form = FilterHistoryForm()
    form.action.choices = [(h.action, h.action) for h in db.session.query(History.action).distinct().order_by(History.action)]
    form.action.choices.insert(0, ('all', 'all'))
    form.item_type.choices = [(h.item_type, h.item_type) for h in db.session.query(History.item_type).distinct().order_by(History.item_type)]
    form.item_type.choices.insert(0, ('all', 'all'))
    form.userid.choices = [(h.id, h.username) for h in User.query.order_by('username').all()]
    form.userid.choices.insert(0, (0, 'all'))

    for key in ['item_name', 'action', 'item_type', 'userid']:
        if not session.has_key(key):
            session[key] = None

    action = session.get('action', None)
    item_name = session.get('item_name', None)
    item_type = session.get('item_type', None)
    userid = session.get('userid', None)

    # Form was submitted ...
    if form.validate_on_submit():
        # 'Filter' clicked
        if request.form['submit'] == 'Filter':
            flash('Filtered data.', 'info')
            session['action'] = form.action.data
            session['item_name'] = form.item_name.data
            session['item_type'] = form.item_type.data
            session['userid'] = form.userid.data
            if len(session['item_name']) and not '%' in session['item_name']:
                session['item_name'] += '%'
        # 'Reset' clicked - reset all fields everywhere
        else:
            session['action'] = 'all'
            session['item_name'] = None
            session['item_type'] = 'all'
            session['userid'] = None
            action = None
            item_name = None
            item_type = None
            userid = None
        # Post/Redirect/Get !!!
        return redirect(url_for('.history', page=page))
    # set filter dropdowns to the values of the session
    else:
        form.action.data = session.get('action', None)
        form.item_name.data = session.get('item_name', None)
        form.item_type.data = session.get('item_type', None)
        form.userid.data = session.get('userid', None)

    items = History.query
    if action != 'all':
        items = items.filter(History.action==action)
        session['action'] = action
    if item_type != 'all':
        items = items.filter(History.item_type==item_type)
        session['item_type'] = item_type
    if userid:
        items = items.filter(History.userid==userid)
        session['userid'] = userid
    if item_name:
        items = items.filter(History.item_name.like(item_name))
        session['item_name'] = item_name
    items = items.order_by('date desc').paginate(page,
                                                 current_app.config['HOSTS_PER_PAGE'],
                                                 False)
    table = HistoryTable(items.items, classes=['table', 'table-striped'])
    return render_template("history.html",
                           form = form,
                           table = table,
                           items=items,
                           title='History')
