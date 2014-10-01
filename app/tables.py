from flask_table import Table, Col, LinkCol

# Declare your table
class HostTable(Table):
        hostname = Col('Hostname')
        domain = Col('Domain')
        stage = Col('Stage')
        role = Col('Role')
        view = LinkCol('Edit', 'edit_host', url_kwargs=dict(host_id='id'))
        delete = LinkCol('Delete', 'delete_host', url_kwargs=dict(host_id='id'))
