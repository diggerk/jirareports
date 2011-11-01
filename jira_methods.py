#!/usr/bin/python

from common import JiraConnection

jira = JiraConnection()
(auth, soap, project_name) = (jira.auth, jira.soap, jira.project_name)

print 'Available methods: ', soap.methods.keys()

def listSOAPmethods():
    for key in soap.methods.keys():
        print key, ': '
        for param in soap.methods[key].inparams:
          print '\t', param.name.ljust(10), param.type
        for param in soap.methods[key].outparams:
          print '\tOut: ', param.name.ljust(10), param.type
listSOAPmethods()
