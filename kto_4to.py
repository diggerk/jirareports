#!/usr/bin/env python 
#-W ignore::DeprecationWarning
# Suppress all deprecation warnings (not recommended for development)
import warnings
warnings.simplefilter('ignore', DeprecationWarning)

import sys

from jirareports.common import JiraConnection
import datetime as Datetime

def usage():
    print >> sys.stderr, "%s version [date]" % __file__

if len(sys.argv) < 2:
    usage()
    sys.exit(1)

jira = JiraConnection()
auth, client, project_name, to_datetime = (jira.auth, jira.client, jira.project_name, jira.to_datetime)

version = sys.argv[1]

if len(sys.argv) > 2:
    release_date = Datetime.datetime.strptime(sys.argv[2], '%Y-%m-%d')
else:
    versions = client.service.getVersions(auth, jira.project_name)
    release_date = None
    for v in versions:
        if v.name == version:
            release_date = to_datetime(v.releaseDate)
            break
    if not release_date:
        print "Can not find version", version
        exit(1)

print "Logs for version %s, after %s" % (version, release_date)

issues = jira.client.service.getIssuesFromJqlSearch(auth, 'project = %s and fixVersion = %s' % (jira.project_name, version),
                                                    1000)

stats = {} # user -> [date, issue, time]
for issue in issues:
    worklogs = client.service.getWorklogs(auth, issue.key)
    for l in worklogs:
        if l.author not in stats:
            stats[l.author] = []
        wl_time = to_datetime(l.created)
        if not release_date or wl_time >= release_date:
#            print "Issue: ", issue.key
#            print "Worklog: ", l
        #if wl_time <= release_date or len(sys.argv) < 3:
        #    stats[l.author] += l.timeSpentInSeconds
            stats[l.author].append( (wl_time, issue.key, l.timeSpentInSeconds / 3600.0) )

print "Work logged by engineer\ndev\t\tstarted\t\tissue\t\thours"

for author in stats:
    print author
    stats[author].sort()
    for entry in stats[author]:
        print "\t\t%s\t\t%s\t\t%s" % entry
