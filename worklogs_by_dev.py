#!/usr/bin/env python 
#-W ignore::DeprecationWarning
# Suppress all deprecation warnings (not recommended for development)
import warnings
warnings.simplefilter('ignore', DeprecationWarning)

import sys

import SOAPpy

from common import JiraConnection
import datetime as datetime_m

def usage():
    print >> sys.stderr, "%s version [date]" % __file__

if len(sys.argv) < 2:
    usage()
    sys.exit(1)

jira = JiraConnection()
(auth, soap, project_name, to_datetime) = (jira.auth, jira.client, jira.project_name, jira.to_datetime)
version = sys.argv[1]

if len(sys.argv) > 2:
    release_date = datetime_m.datetime.strptime(sys.argv[2], '%Y-%m-%d')
else:
    versions = soap.getVersions(auth, project_name)
    release_date = None
    for v in versions:
        if v.name == version:
            release_date = jira.to_datetime(*v.releaseDate)
            break
    if not release_date:
        print "Can not find version", version
        exit(1)

print "Release date:", release_date

issues = soap.getIssuesFromJqlSearch(auth, 'project = %s and fixVersion = %s' % (project_name, version),
    SOAPpy.Types.intType(1000))

print "Worklogs done after sprint is finished:"

stats = {}
for issue in issues:
    worklogs = soap.getWorklogs(auth, issue.key)
    for l in worklogs:
        if l.author not in stats:
            stats[l.author] = 0
        wl_time = jira.to_datetime(*l.created)
        if wl_time > release_date:
            print "Issue: ", issue
            print "Worklog: ", l
        if wl_time <= release_date or len(sys.argv) < 3:
            stats[l.author] += l.timeSpentInSeconds

print "Work logged by engineer"

for (author, time) in stats.items():
    print author, time / 3600.0
