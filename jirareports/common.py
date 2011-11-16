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

    def help(self):
        print self.client

    def int_arg(self, arg):
        return arg


class SoapPyJiraConnection(BaseJiraConnection):
    def __init__(self):
        super(SoapPyJiraConnection, self).__init__()

        import SOAPpy
        self.client = SOAPpy.WSDL.Proxy(self.jira_url)
        self.auth = self.client.login(self._jira_user, self._jira_pass)

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

    def help(self):
        for key in self.client.methods.keys():
            print key, ': '
            for param in self.client.methods[key].inparams:
                print '\t', param.name.ljust(10), param.type
            for param in self.client.methods[key].outparams:
                print '\tOut: ', param.name.ljust(10), param.type

    def int_arg(self, arg):
        return SOAPpy.Types.intType(arg)

def JiraConnection(provider='SUDS'):
    if provider == 'SUDS':
        # Suds version
        return SudsJiraConnection()
    else:
        #SOAPpy version
        return SoapPyJiraConnection()

