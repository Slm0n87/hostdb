from flask_table import Table, Col

# Declare your table
class HostTable(Table):
        hostname = Col('Hostname')
        domain = Col('Domain')
        stage = Col('Stage')
        role = Col('Role')
