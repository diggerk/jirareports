#!/usr/bin/env python 
#-W ignore::DeprecationWarning
# Suppress all deprecation warnings (not recommended for development)
import warnings
warnings.simplefilter('ignore', DeprecationWarning)

import sys

from common import JiraConnection
import datetime as Datetime

def usage():
    print >> sys.stderr, "%s version [date]" % __file__

if len(sys.argv) < 2:
    usage()
    sys.exit(1)

jira = JiraConnection()
auth, client, project_name, to_datetime = (jira.auth, jira.client, jira.project_name, jira.to_datetime)

version = sys.argv[1]

release_date = None
if len(sys.argv) > 2:
    release_date = Datetime.datetime.strptime(sys.argv[2], '%Y-%m-%d')

print "Logs for version %s, after %s" % (version, release_date)

issues = jira.client.service.getIssuesFromJqlSearch(auth, 'project = %s and fixVersion = %s' % (jira.project_name, version),
                                                    1000)

logs = {} # user -> [date, issue, time]
stats = {} # user -> total hours
for issue in issues:
    worklogs = client.service.getWorklogs(auth, issue.key)
    for l in worklogs:
        if l.author not in logs:
            logs[l.author] = []
        wl_time = to_datetime(l.created)
        if not release_date or wl_time >= release_date:
            if l.author not in stats:
                stats[l.author] = 0
            stats[l.author] += l.timeSpentInSeconds / 3600.0
            logs[l.author].append( (wl_time, issue.key, l.timeSpentInSeconds / 3600.0) )

print "Work logged by engineer\ndev\t\tstarted\t\tissue\t\thours"

for author in logs:
    print "%s\t\t\t\t\t\t%s hours" % (author, stats[author])
    logs[author].sort()
    for entry in logs[author]:
        print "\t\t%s\t\t%s\t\t%s" % entry
