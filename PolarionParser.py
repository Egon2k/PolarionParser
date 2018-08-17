import xml.etree.ElementTree as ET
import re
import os
from bs4 import BeautifulSoup

# globals
moduleDict = dict()           # dict for all documents in repo
workitemDict = dict()         # dict for all workitems in repo

REMOVE_ATTRIBUTES = [
    'style','font','size','color']
    
EXCLUDE_FROM_ATTRIBUTE_REMOVAL = [
    'table','tbody','tr','th','td']


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
      
      
def getIdAndTitleFromRegex(match):
   workitemTree = ET.parse(workitemDict[match.group(1)])
   workitemRoot = workitemTree.getroot()
   
   for field in workitemRoot:
      if field.get('id') == "title":
         idTitle = "<font color=\"blue\">" + match.group(1) + " - " + field.text.encode('utf-8') + "</font>"
         
   if idTitle:
      return idTitle
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

      
def removeDefinedAttributes(soup):
   ##https://stackoverflow.com/a/39976027
   for tag in soup.recursiveChildGenerator():
      if tag.name not in EXCLUDE_FROM_ATTRIBUTE_REMOVAL:
         if hasattr(tag, 'attrs'):
            tag.attrs = {key:value for key,value in tag.attrs.iteritems() if key not in REMOVE_ATTRIBUTES}
   return soup
      
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
         description = getDescriptionFromWorkitem(id)
         
         subsoup = BeautifulSoup(description, 'html.parser')
         #removeDefinedAttributes(subsoup)
         
         #for subtag in subsoup:
         #   if subtag.name == "span":
         #      print "span found"
         #      if hasattr(subtag, 'attrs'):
         #         for subtag.attrs in subtag.attrs:
         #           if subtag.attrs == "class":
         #               print type(subtag.attrs)
         #               print subtag.attrs
         #               exit()

         #print subsoup.find_all('span')
         for span in subsoup.find_all('span'):
            if span.get('data-item-id'):
               # https://www.crummy.com/software/BeautifulSoup/bs4/doc/#replace-with
               new_tag = soup.new_tag("font color=\"blue\"")
               new_tag.string = span.get('data-item-id') + " - " +  getTitleFromWorkitem(span.get('data-item-id'))
               #print span.get('data-item-id')
               span.replace_with(new_tag)
         
     
         ## https://stackoverflow.com/questions/17136127/calling-a-function-on-captured-group-in-re-sub
         #description = re.sub(r'<span class="polarion-rte-link" data-type="workItem" id="fake" data-item-id="([a-zA-Z]*-\d{1,6})" data-option-id="long"></span>', r'\1' + " - WI Title" , description)
         #description = re.sub(r'<span class="polarion-rte-link" data-type="workItem" id="fake" data-item-id="([a-zA-Z]*-\d{1,6})" data-option-id="long"></span>', getIdAndTitleFromRegex , subsoup.encode('utf-8'))
         
         f.write("<b>")
         f.write(id + " " + getTitleFromWorkitem(id))
         f.write("</b></br>")
         f.write(subsoup.prettify().encode('utf-8'))
         f.write("</br>")

f.close

os.startfile("index.html")
