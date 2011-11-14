#!/usr/bin/env python 
#-W ignore::DeprecationWarning
# Suppress all deprecation warnings (not recommended for development)
import warnings
warnings.simplefilter('ignore', DeprecationWarning)

import sys
import SOAPpy

from common import JiraConnection, datetime
import datetime as Datetime

def usage():
    print >> sys.stderr, "%s version [date]" % __file__

if len(sys.argv) < 2:
    usage()
    sys.exit(1)

jira = JiraConnection()
(auth, soap, project_name) = (jira.auth, jira.soap, jira.project_name)
version = sys.argv[1]

if len(sys.argv) > 2:
    release_date = Datetime.datetime.strptime(sys.argv[2], '%Y-%m-%d')
else:
    versions = soap.getVersions(auth, project_name)
    release_date = None
    for v in versions:
        if v.name == version:
            release_date = datetime(*v.releaseDate)
            break
    if not release_date:
        print "Can not find version", version
        exit(1)

print "Logs for version %s, after %s" % (version, release_date)

issues = soap.getIssuesFromJqlSearch(auth, 'project = %s and fixVersion = %s' % (project_name, version),
    SOAPpy.Types.intType(1000))

stats = {} # user -> [date, issue, time]
for issue in issues:
    worklogs = soap.getWorklogs(auth, issue.key)
    for l in worklogs:
        if l.author not in stats:
            stats[l.author] = []
        wl_time = datetime(*l.created)
        if not release_date or wl_time >= release_date:
#            print "Issue: ", issue.key
#            print "Worklog: ", l
        #if wl_time <= release_date or len(sys.argv) < 3:
        #    stats[l.author] += l.timeSpentInSeconds
            stats[l.author].append( (wl_time, issue.key, l.timeSpentInSeconds / 3600.0) )

print "Work logged by engineer\ndev\t\tstarted\t\tissue\t\thours"

for author in stats:
    print author
    for entry in stats[author]:
        print "\t\t%s\t\t%s\t\t%s" % entry
