HOSTDB
======

flask app for small hostdb with roles and stages  

Fork from https://github.com/svenXY/hostdb

### Dependency and Setup

On Debian, do:  

```
apt-get install git python-virtualenv python-pip python-psycopg2 python-dev libpq-dev
```

Build venv:
```
git clone <URL> hostdb
cd hostdb
virtualenv -p python2.7 venv
. venv/bin/activate
pip install -r requirements.txt
```
Add DB-Config to class ProductionConfig in config.py  

