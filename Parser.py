from bs4 import BeautifulSoup
import re
import os

#print BeautifulSoup(open('workitem.xml'), 'html.parser').find(id="status").text
#print BeautifulSoup(open('workitem.xml'), 'html.parser').find("field", id="status").text

# globals
moduleDict = dict()              # dict for all documents in repo
workitemDict = dict()            # dict for all workitems in repo

def _analyseFolderStruct():
    numberOfDocuments = 1
    for root, dirs, files in os.walk("."):
        for file in files:
            # save all documents in dict
            if file.endswith("module.xml"):
                moduleDict[numberOfDocuments] = os.path.join(root, file)
                numberOfDocuments =  numberOfDocuments + 1
            # safe all workitems in dict
            if file.endswith("workitem.xml"):
                id = re.search('\\\([a-zA-Z_]*-\d{1,6})', root)
                if id:
                    workitemDict[id.group(1)] = os.path.join(root, file)
                    #print id.group(1), os.path.join(root, file)

def _getFieldByAttrName(soup, attrName):
    value = soup.find("field", id=attrName)
    if value:
        return value.text.encode('utf-8')
    else:
        return "id \"" + attrName + "\" not found"

def _getTitleFromId(id):
    workitemSoup = BeautifulSoup(open(workitemDict[id]), 'html.parser')
    return _getFieldByAttrName(workitemSoup, "title")


def _getIdFromString(string):
   id = re.search('([a-zA-Z]*-\d{1,6})', string)
   if id:
      return id.group(1)

def _printHeading(id, headingLevel):
    workitemSoup = BeautifulSoup(open(workitemDict[id]), 'html.parser')
    f.write("<"  + headingLevel + ">")
    f.write(_getFieldByAttrName(workitemSoup, "title"))
    f.write("</" + headingLevel + ">")

def _printWorkitem(id):
    workitemSoup = BeautifulSoup(open(workitemDict[id]), 'html.parser')
    f.write("<p>")
    f.write("<div style=\"border: thin solid black\">")
    f.write("<b>" + id + " - " + _getFieldByAttrName(workitemSoup, "title") + "</b></br>")       # id + title in bold
    
    descriptionSoup = BeautifulSoup(_getFieldByAttrName(workitemSoup, "description"), 'html.parser')
    
    for linkedWorkitem in descriptionSoup.find_all('span'):
        if linkedWorkitem.get('data-item-id'):
           # https://www.crummy.com/software/BeautifulSoup/bs4/doc/#replace-with
           new_tag = descriptionSoup.new_tag("font color=\"blue\"")
           new_tag.string = linkedWorkitem.get('data-item-id') + " - " +  _getTitleFromId(linkedWorkitem.get('data-item-id'))
           #print linkedWorkitem.get('data-item-id')
           linkedWorkitem.replace_with(new_tag)
           
    f.write(descriptionSoup.prettify().encode('utf-8'))
    f.write("</div>")
    f.write("</p>")
    
def _parseWorkitem(tag):
    # decide what type of workitem it is
    if str(tag.name).startswith('h'):                   # heading
        id = _getIdFromString(str(tag.get('id')))
        if id:
            _printHeading(id, str(tag.name))
    elif str(tag.name).startswith('div'):               # normal workitems
        id = _getIdFromString(str(tag.get('id')))
        if id:
            _printWorkitem(id)
    else:                                               # ignore these tags
        pass
    
    
##################################################################################
##################################################################################

# generate dicts
_analyseFolderStruct()
  
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
    
if 0 < selectedModule < len(moduleDict):
    moduleSoup = BeautifulSoup(open(moduleDict[selectedModule]), 'html.parser')
    print "Author: " + _getFieldByAttrName(moduleSoup, "author")
    print "Created: " + _getFieldByAttrName(moduleSoup, "created")
    
    contentSoup = BeautifulSoup(_getFieldByAttrName(moduleSoup, "homePageContent"), 'html.parser')
    
    f = open("index.html", 'w')
    
    for tag in contentSoup:
        _parseWorkitem(tag)
        
    f.close

    os.startfile("index.html")
        
else:
    print "Input out of range - start again."