#!/usr/bin/env python -W ignore::DeprecationWarning
# Suppress all deprecation warnings (not recommended for development)
import warnings
warnings.simplefilter('ignore', DeprecationWarning)

import sys
from datetime import datetime

import SOAPpy

from common import JiraConnection


if len(sys.argv) < 2:
    print "Provide version name"
    sys.exit(1)

jira = JiraConnection()
(auth, soap, project_name) = (jira.auth, jira.soap, jira.project_name)
version = sys.argv[1]

if len(sys.argv) > 2:
    release_date = datetime.strptime(sys.argv[2], '%Y-%m-%d')
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
        wl_time = datetime(*l.created)
        if wl_time > release_date:
            print "Issue: ", issue
            print "Worklog: ", l
        if wl_time <= release_date or len(sys.argv) < 3:
            stats[l.author] += l.timeSpentInSeconds

print "Work logged by engineer"

for (author, time) in stats.items():
    print author, time / 3600.0
