import os
import ConfigParser
import SOAPpy

from datetime import datetime as Datetime

class JiraConnection(object):
    def __init__(self):
        config = ConfigParser.SafeConfigParser()
        config.read(os.path.expanduser('~/.jira'))
        jira_url = config.get('default', 'uri')
        jira_user = config.get('default', 'username')
        jira_pass = config.get('default', 'password')
        self.project_name = config.get('default', 'project')
        self.soap = SOAPpy.WSDL.Proxy(jira_url)
        self.auth = self.soap.login(jira_user, jira_pass)

def datetime(*jira_date):
    date = list(jira_date)
    if date[5] is not None and type(date[5]) == float:
        f = float(date[5])
        import math
        date[5] = int(math.floor(f))
        if len(date) == 6:
            date.append(None)
        date[6] = int((f - date[5]) * 1000)
    return Datetime(*date)