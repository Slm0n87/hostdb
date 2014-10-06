#!/usr/bin/env python
# encoding: utf-8

import requests
import json
from argparse import ArgumentParser

parser =ArgumentParser(description='Get a list of hostnames')
parser.add_argument('--stage', '-s', metavar='STAGE',
                    help='the stage')
parser.add_argument('--domain', '-d', metavar='DOMAIN',
                    help='the domain')
parser.add_argument('--role', '-r', metavar='ROLE',
                    help='the role')
parser.add_argument('--delimiter', '-D', metavar='DELIM', default='\n',
                    help='the delimiter')
parser.add_argument('--fqdn', '-f', action='store_true',
                    help='output fqdn')
parser.add_argument('--url', '-u', default='http://127.0.0.1:5000', help='the hostname:port')
args = parser.parse_args()

url = ''.join([args.url, '/api/host'])
headers = {'Content-Type': 'application/json'}

filters = []

if args.stage:
    filters.append(dict(name='stage__name', op='has', val=args.stage))
if args.role:
    filters.append(dict(name='role__name', op='has', val=args.role))
if args.domain:
    filters.append(dict(name='domain__name', op='has', val=args.domain))

params = dict(q=json.dumps(dict(filters=filters)))

response = requests.get(url, params=params, headers=headers)
assert response.status_code == 200

data = response.text
stuff = json.loads(data)

#import pprint; pprint.pprint(stuff)

if args.fqdn:
    print(
        args.delimiter.join(
            ['.'.join(
                [o['hostname'], o['domain']['name']]
                     ) for o in stuff['objects']]))
else:
    print(args.delimiter.join([o['hostname'] for o in stuff['objects']]))

