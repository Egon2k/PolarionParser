import xml.etree.ElementTree as ET
import re
import os
import os.path
from bs4 import BeautifulSoup

# globals
moduleDict = dict()           # dict for all documents in repo
workitemDict = dict()         # dict for all workitems in repo

def analyseFolderStruct():
   numberOfDocuments = 1
   for root, dirs, files in os.walk("."):
      for file in files:
         # save all documents in dict
         if file.endswith("module.xml"):
            moduleDict[numberOfDocuments] = os.path.join(root, file)
            numberOfDocuments =  numberOfDocuments + 1
         # safe all workitems in dict
         if file.endswith("workitem.xml"):
            id = re.search('\\\([a-zA-Z]*-\d{1,6})', root)
            if id:
               workitemDict[id.group(1)] = os.path.join(root, file)
               #print id.group(1), os.path.join(root, file)

def getIdFromString(string):
   id = re.search('([a-zA-Z]*-\d{1,6})', string)
   if id:
      return id.group(1)
      
def getIdsFromString(string):
   return re.findall('([a-zA-Z]*-\d{1,6})', string)
   
   
def getTitleFromWorkitem(id):
   workitemTree = ET.parse(workitemDict[id])
   workitemRoot = workitemTree.getroot()
   
   for field in workitemRoot:
      if field.get('id') == "title":
         title = field.text.encode('utf-8')
         
   if title:
      return title
   else:
      return "WI not found"
      
def getDescriptionFromWorkitem(id):
   workitemTree = ET.parse(workitemDict[id])
   workitemRoot = workitemTree.getroot()
   
   for field in workitemRoot:
      if field.get('id') == "description":
         description = field.text.encode('utf-8')
         
   if description:
      return description
   else:
      return "WI not found"
   
########################################################################################
########################################################################################
########################################################################################

# generate dicts
analyseFolderStruct()

###for workitem in workitemDict:
###   print workitem, workitemDict[workitem]
###
###exit()   
   
# print module dict 
for module in moduleDict:
   print module, moduleDict[module]
   
# ask user for a number
rawNumber = raw_input('Choose a number: ')

try:
    selectedModule = int(rawNumber)
except ValueError:
    print("Invalid number")
    exit()

# parse selected module    
if selectedModule <= len(moduleDict):
   # https://docs.python.org/2/library/xml.etree.elementtree.html
   moduleTree = ET.parse(moduleDict[selectedModule])
   moduleRoot = moduleTree.getroot()

   # get through all fields and find specific ones
   for field in moduleRoot:
###      if field.get('id') == "author":
###         print "Author:\t\t" + field.text
###      if field.get('id') == "created":
###         print "Created:\t" + field.text
      if field.get('id') == "homePageContent":
         homePageContent = field.text
else:
   print("Number out of range")
   exit()

f = open("index.html", 'w')

soup = BeautifulSoup(homePageContent, 'html.parser')

for tag in soup:
   #print tag
   if str(tag.name).startswith('h'):                     # heading
      #print str(tag.name) + " " + str(tag.get('id'))    # print tag and attribute 'id'
      id = getIdFromString(str(tag.get('id')))
      if id:
         #print id.group(1)
         f.write("<"  + str(tag.name) + ">")
         f.write(getTitleFromWorkitem(id))
         f.write("</" + str(tag.name) + ">")
   if str(tag.name).startswith('div'):                    # workitem
      id = getIdFromString(str(tag.get('id')))
      if id:
         #description = getDescriptionFromWorkitem(id)
         #linkedIds = getIdsFromString(description)
         
         #for linkedId in linkedIds:
         #   #print description
         #   #a = '<span class="polarion-rte-link" data-type="workItem" id="fake" data-item-id="' + linkedId + '" data-option-id="long"></span>'
         #   #print description.replace(a,linkedId)
         #   print linkedId
         
         #description = getDescriptionFromWorkitem(id)
         #linkedIds = getIdsFromString(description)
         #
         #for linkedId in linkedIds:
         #   a = '<span class="polarion-rte-link" data-type="workItem" id="fake" data-item-id="' + linkedId + '" data-option-id="long"></span>'
         #   b = linkedId
         #   description.replace(a,b)
            
         
         #linkedId = re.search('<span class="polarion-rte-link" data-type="workItem" id="fake" data-item-id="(\w*-\d{1,6})" data-option-id="long"></span>', descriptionLines)
         #print linkedIds
         #
         #for linkedId in linkedIds:
         #   print linkedId
         
         f.write("<b>")
         f.write(id + " " + getTitleFromWorkitem(id))
         f.write("</b></br>")
         f.write(getDescriptionFromWorkitem(id))
         f.write("</br>")

f.close

os.startfile("index.html")
