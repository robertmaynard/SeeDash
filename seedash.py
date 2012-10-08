#!/usr/bin/python
import urllib
import urllib2
from base64 import *
import argparse
import getpass
import sys


def openCDash():
  return 'http://open.cdash.org'

def askForLogin():
  user = raw_input("User: ")
  passw = getpass.getpass(stream=sys.stderr)
  return (user,passw)

def queryCDash(url,getString):
  if(url[-1:] != '/'):
    url += '/'
  if(url[-4:] != 'api/'):
    url += 'api/'
  fullURL = url+getString
  print fullURL
  request = urllib2.Request(fullURL)
  r = urllib2.urlopen(request)
  return r.readlines()


#Todo args really need to become full class types
#that self encode
def createGetString(args):
  getString = '?'
  getString += 'method='+args['method']
  getString += '&'
  getString += 'task='+args['task']
  getString += '&'
  if('project' in args):
    getString += 'project='+args['project']
    getString += '&'
  if('group' in args):
    getString += 'group='+args['group']
  return getString


def listProjects(url):
  args = { 'method' : 'project' , 'task' : 'list'}
  getString = createGetString(args)
  result = queryCDash(url,getString)
  submissions = eval(result[0]) #ugggggh
  for i in submissions:
    print i['name']


#groups need to become class types
def listErrors(url,project,group):
  args = { 'method' : 'build' , 'task' : 'sitetestfailures'}
  args['project']=project
  args['group']=group
  getString = createGetString(args)
  result = queryCDash(url,getString)
  submissions = eval(result[0]) #ugggggh
  tfails = dict()
  print "-"*20, "ANALYZING", "-"*20
  if(len(submissions) == 0):
    print "No Results."
    return

  for skey in submissions.keys():
    submission = submissions[skey]
    bname = submission['buildname']
    bfails = submission['tests']
    if len(bfails) > 100:
      print "WARNING IGNORING ", bname, len(bfails)
      continue
    print bname, ",", len(bfails)
    for tnum in range(0, len(bfails)):
      test = bfails[tnum]
      tname = test['name']
      if not tname in tfails:
         tfails[tname] = list()
      tfails[tname].append(bname)

  print "-"*20, "REPORT", "-"*20
  print len(tfails)," FAILURES"
  failcounts = map(lambda x: (x,len(tfails[x])), tfails.keys())
  sortedfails = sorted(failcounts, key=lambda fail: fail[1])
  for test in sortedfails:
    tname = test[0]
    print tname, ",", len(tfails[tname]), ",", tfails[tname]


def seeDat(settings):
  #user,passw = askForLogin()
  #buildRequest(user,passw)
  project = urllib.quote(settings.project[0])

  if(project == "dashboards"):
    listProjects(openCDash())
  else:
    group = urllib.quote(settings.group)
    listErrors(openCDash(),project,group)

def main():
  parser = argparse.ArgumentParser(description='SeeDash a CLI to CDash.')
  parser.add_argument('project', nargs=1,
                      help='project name you want to list')
  parser.add_argument('--group', dest='group',
                      default='Nighly',
                      help="CDash build group to operate on. Examples are Nightly, Experimental, Continous")

  args = parser.parse_args()

  #get settings
  seeDat(args)

if __name__ == '__main__':
  main()
