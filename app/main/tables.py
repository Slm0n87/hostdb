from flask_table import Table, Col, LinkCol, DatetimeCol
import markdown
from flask import Markup
import re

class MarkdownCol(Col):
    def td_format(self, content):
        # replace http:// with proper markdown link if not already markdown
        content = re.sub(r'(?<!\]\()(https?://\S+)', r'[\1](\1)', content)
        return Markup(markdown.markdown(content))

# Declare your table
class HostTable(Table):
        hostname = Col('Hostname')
        domain = Col('Domain')
        stage = Col('Stage')
        role = Col('Role')
        view = LinkCol('Edit', '.edit_host', url_kwargs=dict(host_id='id'))
        delete = LinkCol('Delete', '.delete_host', url_kwargs=dict(host_id='id'))

class HistoryTable(Table):
    date = DatetimeCol('Date')
    userid = Col('User')
    action = Col('Action')
    item_type = Col('Type')
    item_name = Col('Item')
    comment = MarkdownCol('Comment')
