import getpass
import urllib
import urllib2
import itertools
import re

from bs4 import BeautifulSoup

def removeDuplicates(seq, idfun=None):
  # order preserving
 if idfun is None:
     def idfun(x): return x
 seen = {}
 result = []
 for item in seq:
     marker = idfun(item)
     if marker in seen: continue
     seen[marker] = 1
     result.append(item)
 return result

class CDTest:
  def __init__(self, machine, parms):
    self.Id = parms['id']
    self.Name = parms['name']
    self.Machine = machine

class CDMachine:
  def __init__(self, id, parms):

    def make_test(machine,parms):
      return CDTest(machine,parms)

    self.Id = id
    self.Name = parms['name']
    self.BuildName = parms['buildname']

    numFailedTests = len(parms['tests'])
    self.Tests = map(make_test,
                     itertools.repeat(self,numFailedTests),
                     parms['tests'])

    #empty list of devs, will be set by findUsersWhoeModifiedFiles
    self.Devs = []

  def __str__(self):
    return self.Name + ":  " + self.BuildName

class CDModifiedFile:
  def __init__(self, file, user):
    self.File = file
    self.User = user

  def ClassName(self):
    name = self.File
    name = name.split(".")[0]
    name = name.split("vtk")[-1] #get the last section, if no vtk does no split
    name = name.split("pq")[-1] #get the last section, if no vtk does no split
    name = name.split("itk")[-1] #get the last section, if no vtk does no split
    return name

def openCDash():
  return 'https://open.cdash.org'

def askForLogin():
  user = raw_input("User: ")
  passw = getpass.getpass(stream=sys.stderr)
  return (user,passw)

def queryCDash(url,getString):
  if(url[-1:] != '/'):
    url += '/'
  if(url[-4:] != 'api/v1/'):
    url += 'api/v1/'
  fullURL = url+getString

  request = urllib2.Request(fullURL)
  r = urllib2.urlopen(request)
  return r

def scrapeCDash(url,page, query):
  if(url[-1:] != '/'):
    url += '/'
  fullURL = url +  page + "?" + query
  print fullURL
  request = urllib2.Request(fullURL)
  r = urllib2.urlopen(request)
  return r


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

def extractModifiedFileNames(page):

  def make_CDModFile(tag):
    file =  tag.text.split("Revision")[0] #split on space and get first elment
    user = tag.next_sibling.split('by')[1]
    return CDModifiedFile(file,user)

  soup = BeautifulSoup(page)
  files = map(make_CDModFile,soup.find_all('a', text=re.compile("Revision")))
  return files

def extractDevNames(page):
  def extractNames(raw):
    s = raw.split(",")
    print s
    return s[0][1:-1] #first arg is name, remove quotes

  soup = BeautifulSoup(page)
  script = soup.find_all('script', text=re.compile("dbAdd"))
  try:
    rawModFiles = script.text.split('2,"","1",')
    return map(extractNames,rawModFiles)
  except Exception, e:
      return []


