#!/usr/bin/python

from base64 import *
import argparse
import sys
import urllib
import itertools

from operator import itemgetter, attrgetter

from queryCDash import *

def perMachineResults(machineResults):

  def machine_info(m):
    return str(m.Machine)

  #flatten all tests from each machine into a ist
  allTests = [test for machine in machineResults for test in machine.Tests]

  #test ids are unique, can't use them as unique identifiers
  keyFunc = attrgetter('Name')
  allTests = sorted(allTests, key=keyFunc)
  for k, g in itertools.groupby(allTests, keyFunc):
    machineNames = map(machine_info,g)
    print k + " Failed on machines:\n\t" + "\n\t".join(machineNames)

    devs = [d for m in g for d in m.Devs]
    if(len(devs) > 0):
      devs = removeDuplicates(devs)
      print "Developers :\n\t" + "\n\t".join(devs)

    print "\n"


def listProjects(url):
  args = { 'method' : 'project' , 'task' : 'list'}
  getString = createGetString(args)
  print "Getting projects from CDash"
  result = queryCDash(url,getString)
  lines = result.readlines()
  print "Parsing projects from CDash"
  submissions = eval(lines[0]) #ugggggh
  for i in submissions:
    print i['name']

#groups need to become class types
def findErrorsByMachine(url,project,group):

  def make_machine(items):
    machineId, parameters = items
    return CDMachine(machineId,parameters)

  args = { 'method' : 'build' , 'task' : 'sitetestfailures'}
  args['project']=project
  args['group']=group
  getString = createGetString(args)

  print "Getting projects from CDash"
  result = queryCDash(url,getString)
  lines = result.readlines()

  print "Parsing projects from CDash"
  submissions = eval(lines[0]) #ugggggh
  machines = map(make_machine, submissions.iteritems())
  print  "Determined failures per machine"
  return machines


def findDevsPerMachine(machines):

  def unique_by_name(x):
    return x.File

  def test_contains(test,files):
    for f in files:
      if f in test.Name:
        return True
    return False

  #For each machine uery the update page to see what files have changed.
  for machine in machines:
    query = 'buildid=' + str(machine.Id)
    page = scrapeCDash(openCDash(),'viewUpdate.php', query)
    print 'Getting names of people that contributed code to machine: ' + str(machine)
    machine.Devs = extractDevNames(page)

  print machines[0].Devs
  return machines

#This doesn't work as well as I expected
def subsetFailuresByUser(machines,userName):

  def unique_by_name(x):
    return x.File

  def test_contains(test,files):
    for f in files:
      if f in test.Name:
        return True
    return False

  #For each machine uery the update page to see what files have changed.
  files = [] #use set to remove duplicates
  for machine in machines:
    query = 'buildid=' + str(machine.Id)
    page = scrapeCDash(openCDash(),'viewUpdate.php', query)
    print 'Getting modified files for machine: ' + str(machine)
    modifiedFiles = extractModifiedFileNames(page)
    for f in modifiedFiles:
      #find only files that the user might have modified
      if(userName in f.User):
        files.append(f)

  #remove duplicate files, use the file names as the unique identifier
  #as the hash of an object is unique
  files = removeDuplicates(files, unique_by_name)
  files = [ f.ClassName() for f in files ] #convert files to import class name section

  #update machines to only store tests that match a file the user
  #has modified
  for machine in machines:
    size = len(machine.Tests)
    machine.Tests = [test for test in machine.Tests  if test_contains(test,files)]

  return machines


def seeDat(settings):
  #user,passw = askForLogin()
  #buildRequest(user,passw)
  project = urllib.quote(settings.project[0])

  if(project == "dashboards"):
    listProjects(openCDash())
  else:
    group = urllib.quote(settings.group)
    results = findErrorsByMachine(openCDash(),project,group)

    if(settings.devs != None):
      results = findDevsPerMachine(results)

    perMachineResults(results)

def main():
  parser = argparse.ArgumentParser(description='SeeDash a CLI to CDash.')
  parser.add_argument('project', nargs=1,
                      help='project name you want to list')
  parser.add_argument('--group',
                      '-g',
                      dest='group',
                      default='Nightly',
                      help="CDash build group to operate on. Examples are Nightly, Experimental, Continous")
  parser.add_argument('--devs',
                      '-d',
                      action='store_true',
                      dest='devs',
                      help="find devs that might have caused each test failure")

  args = parser.parse_args()

  #get settings
  seeDat(args)

if __name__ == '__main__':
  main()
