Couple of scripts which generate reports out of JIRA worklogs.
[JIRA SOAP API](http://docs.atlassian.com/rpc-jira-plugin/latest/com/atlassian/jira/rpc/soap/JiraSoapService.html) is used to gather data. 

Before using the scripts create ~/.jira file with content like this:

    [default]
    username=aklochkov
    password=secret
    uri=https://issues.yourcompany.net/rpc/soap/jirasoapservice-v2?wsdl
    project=PRJ
