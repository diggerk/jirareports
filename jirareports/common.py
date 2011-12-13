import os
import ConfigParser

class BaseJiraConnection(object):
    def __init__(self, profile_name=None):
        config = ConfigParser.SafeConfigParser()
        config.read(os.path.expanduser('~/.jira'))
        if not profile_name:
            profile_name = os.environ['JIRA_PROFILE'] if 'JIRA_PROFILE' in os.environ else 'default'
        self.jira_url = config.get(profile_name, 'uri')

        self._jira_user = config.get(profile_name, 'username')
        self._jira_pass = config.get(profile_name, 'password')
        self.project_name = config.get(profile_name, 'project')

        self.config = {}
        for (key, value) in config.items(profile_name):
            self.config[key] = value

class SudsJiraConnection(BaseJiraConnection):
    def __init__(self, profile_name=None):
        super(SudsJiraConnection, self).__init__(profile_name)

        from suds.client import Client
        self.client = Client(self.jira_url)
        self.auth = self.client.service.login(self._jira_user, self._jira_pass)
        self.service = self.client.service

    def to_datetime(self, date):
        return date

    def help(self):
        print self.client

    def int_arg(self, arg):
        return arg


class SoapPyJiraConnection(BaseJiraConnection):
    def __init__(self, profile_name=None):
        super(SoapPyJiraConnection, self).__init__(profile_name)

        import SOAPpy
        self.service = SOAPpy.WSDL.Proxy(self.jira_url)
        self.auth = self.service.login(self._jira_user, self._jira_pass)

    def to_datetime(self, jira_date):
        from datetime import datetime as Datetime
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
        for key in self.service.methods.keys():
            print key, ': '
            for param in self.service.methods[key].inparams:
                print '\t', param.name.ljust(10), param.type
            for param in self.service.methods[key].outparams:
                print '\tOut: ', param.name.ljust(10), param.type

    def int_arg(self, arg):
        import SOAPpy
        return SOAPpy.Types.intType(arg)

def JiraConnection(provider='SUDS', profile_name=None):
    if provider == 'SUDS':
        # Suds version
        return SudsJiraConnection(profile_name)
    else:
        #SOAPpy version
        return SoapPyJiraConnection(profile_name)

