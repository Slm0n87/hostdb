from flask_table import Table, Col, LinkCol, DatetimeCol
import markdown
from flask import Markup
from ..models import User
import re

class MarkdownCol(Col):
    def td_format(self, content):
        # replace http:// with proper markdown link if not already markdown
        content = re.sub(r'(?<!\]\()(https?://\S+)', r'[\1](\1)', content)
        return Markup(markdown.markdown(content))

class UserCol(Col):
    def td_format(self, content):
        return User.query.get(int(content)).username

class HostTable(Table):
        hostname = Col('Hostname')
        domain = Col('Domain')
        stage = Col('Stage')
        role = Col('Role')
        view = LinkCol('Edit', '.edit_host', url_kwargs=dict(host_id='id'))
        delete = LinkCol('Delete', '.delete_host', url_kwargs=dict(host_id='id'))

class HistoryTable(Table):
    date = Col('Date')
    userid = UserCol('User')
    action = Col('Action')
    item_type = Col('Type')
    item_name = LinkCol('Item', '.edit_host', attr_list='item_name', url_kwargs=dict(host_id='item_id'))
    comment = MarkdownCol('Comment')

class AdminTable(Table):
    name = Col('Item')
    comment = MarkdownCol('Comment')
