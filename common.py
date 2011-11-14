import os
import ConfigParser

class BaseJiraConnection(object):
    def __init__(self):
        config = ConfigParser.SafeConfigParser()
        config.read(os.path.expanduser('~/.jira'))
        self.jira_url = config.get('default', 'uri')
        self._jira_user = config.get('default', 'username')
        self._jira_pass = config.get('default', 'password')
        self.project_name = config.get('default', 'project')

class SudsJiraConnection(BaseJiraConnection):
    def __init__(self):
        super(SudsJiraConnection, self).__init__()

        from suds.client import Client
        self.client = Client(self.jira_url)
        self.auth = self.client.service.login(self._jira_user, self._jira_pass)

    def to_datetime(self, date):
        return date


class SoapPyJiraConnection(BaseJiraConnection):
    def __init__(self):
        super(SoapPyJiraConnection, self).__init__()

        import SOAPpy
        self.soap = SOAPpy.WSDL.Proxy(self.jira_url)
        self.auth = self.soap.login(self._jira_user, self._jira_pass)

    from datetime import datetime as Datetime
    def to_datetime(self, jira_date):
        date = list(jira_date)
        if date[5] is not None and type(date[5]) == float:
            f = float(date[5])
            import math
            date[5] = int(math.floor(f))
            if len(date) == 6:
                date.append(None)
            date[6] = int((f - date[5]) * 1000)
        return Datetime(*date)

def JiraConnection(provider='SUDS'):
    if provider == 'SUDS':
        # Suds version
        return SudsJiraConnection()
    else:
        #SOAPpy version
        return SoapPyJiraConnection()