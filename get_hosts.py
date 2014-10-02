#!/usr/bin/env python

from app import app, db
from app.models import Host, Role, Stage, Domain

from argparse import ArgumentParser

parser =ArgumentParser(description='Get a list of hostnames')
parser.add_argument('--stage', '-s', metavar='STAGE',
                    help='the stage')
parser.add_argument('--domain', '-d', metavar='DOMAIN',
                    help='the domain')
parser.add_argument('--role', '-r', metavar='ROlE',
                    help='the role')
parser.add_argument('--delimiter', '-D', metavar='DELIM', default='\n',
                    help='the delimiter')
parser.add_argument('--fqdn', '-f', action='store_true',
                    help='output fqdn')
args = parser.parse_args()

h = Host.query

if args.stage:
    h = h.filter(Host.stage.has(name=args.stage))
if args.role:
    h = h.filter(Host.role.has(name=args.role))
if args.domain:
    h = h.filter(Host.domain.has(name=args.domain))

h = h.all()

if args.fqdn:
    print( args.delimiter.join(['.'.join([host.hostname, host.domain.name])  for host in h]))
else:
    print( args.delimiter.join([host.hostname for host in h]))

