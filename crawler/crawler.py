#!/usr/bin/env python -W ignore::DeprecationWarning

import sys
from datetime import datetime

import SOAPpy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import Base, Version, Issue, Worklog, Status
from common import JiraConnection


engine = create_engine('mysql://root:@localhost/xcom_jira', echo=True)
engine.connect()

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


jira = JiraConnection()
(auth, soap, project_name) = (jira.auth, jira.soap, jira.project_name)

project = soap.getProjectByKey(auth, project_name)

issue_types = {}
for t in soap.getSubTaskIssueTypesForProject(auth, project.id):
    issue_types[t.id] = t
for t in soap.getIssueTypesForProject(auth, project.id):
    issue_types[t.id] = t

def build_tasks_hierarchy():
    issues = soap.getIssuesFromJqlSearch(auth, 'project = %s and fixVersion = %s' % (project_name, version),
        SOAPpy.Types.intType(1000))
    hierarchy = {}
    for issue in issues:
        if not issue_types[issue.type].subTask:
            children = soap.getIssuesFromJqlSearch(auth, 'parent = "%s"' % issue.key, SOAPpy.Types.intType(100))
            for child in children:
                hierarchy[child.key] = issue
                if child.fixVersions[0].name != version:
                    print "Warning: Sub-task %s (%s) is not assigned to version %s" % (child.key, child.summary, version)
    return hierarchy

def get_top_level_issue(issue):
    return issues_hierarchy[issue.key] if issue.key in issues_hierarchy else issue

#issues_hierarchy = build_tasks_hierarchy()

session = Session()

statuses = {}
for status in soap.getStatuses(auth):
    s = Status(id=int(status.id), name=status.name)
    s = session.merge(s)
    statuses[s.id] = s

for version in soap.getVersions(auth, project_name):
    release_date = datetime(*version.releaseDate) if version.releaseDate is not None else None

    print "Cloning issues for version", version.name

    existing_versions = session.query(Version).filter(Version.id == version.id).all()
    if existing_versions:
        version_model = existing_versions[0]
        if version_model.archived:
            continue
        if version.archived:
            version_model.archived = True
    else:
        version_model = Version(id=version.id, name=version.name,
            release_date=release_date, archived=version.archived)
        session.add(version_model)
        session.flush()

    existing_issues = session.query(Issue.id).filter(Issue.fix_version == version_model).all()

    issues = soap.getIssuesFromJqlSearch(auth,
        "project = %s and fixVersion = '%s'" % (project_name, version.name),
        SOAPpy.Types.intType(1000))

    for issue in issues:
        #top_level_issue = get_top_level_issue(issue)

        existing_issue = issue.id in existing_issues

        issue_model = Issue(id=issue.id, key=issue.key, type=issue_types[issue.type].name,
            subtask=issue_types[issue.type].subTask,
            summary=issue.summary, assignee=issue.assignee,
            created_at=datetime(*issue.created))
        issue_model.status = statuses[int(issue.status)]
        if len(issue.fixVersions) > 0:
            issue_model.fix_version = version_model
        if issue.duedate:
            issue_model.due_date = datetime(*issue.duedate)
        if existing_issue:
            session.merge(issue_model)
        else:
            session.add(issue_model)

        for worklog in soap.getWorklogs(auth, issue.key):
            worklog_model = Worklog(id=worklog.id, date=datetime(*worklog.created), author=worklog.author,
                time_spent=worklog.timeSpentInSeconds, issue=issue_model)
            if existing_issue:
                session.merge(worklog_model)
            else:
                session.add(worklog_model)

session.commit()
