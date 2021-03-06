from bs4 import BeautifulSoup
from shutil import copyfile
import re
import os
import datetime

#print BeautifulSoup(open('workitem.xml', from_encoding='UTF-8'), 'html.parser').find(id="status").text
#print BeautifulSoup(open('workitem.xml', from_encoding='UTF-8'), 'html.parser').find("field", id="status").text

# globals
moduleDict = dict()              # dict for all documents in repo
workitemDict = dict()            # dict for all workitems in repo
imageDict = dict()               # dict for all images (*.png, *jpg)

imageDir = './img/'

TEXT_REMOVE_ATTRIBUTES = [
    'style','font','size','color','border-collapse']

TABLE_REMOVE_ATTRIBUTES = [
    'border-collapse']


def _analyseFolderStruct():
    numberOfDocuments = 1
    for root, dirs, files in os.walk("."):
        for file in files:
            # save all documents in dict
            if file.endswith("module.xml"):
                moduleDict[numberOfDocuments] = os.path.join(root, file)
                numberOfDocuments = numberOfDocuments + 1
            # safe all workitems in dict
            if file.endswith("workitem.xml"):
                id = re.search('\\\([a-zA-Z_]*-\d{1,6})', root)
                if id:
                    workitemDict[id.group(1)] = os.path.join(root, file)
                    #print id.group(1), os.path.join(root, file)
            # safe all images in dict
            if file.endswith(('jpg','png')):
                imageDict[file] = os.path.join(root, file)

def _getFieldByAttrName(soup, attrName):
    value = soup.find("field", id=attrName)
    if value:
        return value.text.encode('utf-8')
    else:
        return "id \"" + attrName + "\" not found"

def _getTitleFromId(id):
    workitemSoup = BeautifulSoup(open(workitemDict[id]), 'html.parser', from_encoding='UTF-8')
    return _getFieldByAttrName(workitemSoup, "title")


def _getIdFromString(string):
   id = re.search('([a-zA-Z]*-\d{1,6})', string)
   if id:
      return id.group(1)

def _printHeading(id, headingLevel):
    workitemSoup = BeautifulSoup(open(workitemDict[id]), 'html.parser', from_encoding='UTF-8')
    f.write("<"  + headingLevel + ">")
    f.write(_getFieldByAttrName(workitemSoup, "title"))
    f.write("</" + headingLevel + ">\n")

def _printWorkitem(id):
    workitemSoup = BeautifulSoup(open(workitemDict[id]), 'html.parser', from_encoding='UTF-8')
    f.write("<p>")
    f.write("<div style=\"border: thin solid black\">")
    f.write("<b>" + id + " - " + _getFieldByAttrName(workitemSoup, "title") + "</b></br>")       # id + title in bold

    descriptionSoup = BeautifulSoup(_getFieldByAttrName(workitemSoup, "description"), 'html.parser', from_encoding='UTF-8')
    descriptionSoup = _removeDefinedAttributes(descriptionSoup)

    for linkedWorkitem in descriptionSoup.find_all('span'):
        if linkedWorkitem.get('data-item-id'):
            # https://www.crummy.com/software/BeautifulSoup/bs4/doc/#replace-with
            new_tag = descriptionSoup.new_tag("font color=\"blue\"")
            new_tag.string = linkedWorkitem.get('data-item-id').encode('utf-8') + " - " +  _getTitleFromId(linkedWorkitem.get('data-item-id'))
            # print linkedWorkitem.get('data-item-id')
            linkedWorkitem.replace_with(new_tag)
        else:
            linkedWorkitem.replace_with(linkedWorkitem.getText())

    for attachment in descriptionSoup.find_all('img'):
        if attachment.get('src'):
            #print attachment.get('src')

            if not os.path.exists(imageDir):
                os.makedirs(imageDir)

            if attachment.get('src').startswith("attachment:"):
                copyfile(imageDict[attachment.get('src')[11:]], imageDir + attachment.get('src')[11:])
                new_tag = descriptionSoup.new_tag('img', src=imageDir + attachment.get('src')[11:], align="middle")
                attachment.replace_with(new_tag)
            elif attachment.get('src').startswith("workitemimg:"):
                #print "ID: " + id
                copyfile(imageDict['attachment' + attachment.get('src')[12:]], imageDir + attachment.get('src')[12:])
                new_tag = descriptionSoup.new_tag('img', src=imageDir + attachment.get('src')[12:], align="middle")
                attachment.replace_with(new_tag)
            else:
                pass

            #copy(imageDict[attachment.get('src').text[11:], '/img/'])

    f.write(descriptionSoup.prettify().encode('utf-8').replace('\r', '').replace('\n', ''))
    f.write("</div>")
    f.write("</p>\n")

def _parseModuleTag(moduleTag):
    # decide what type of workitem it is
    if str(moduleTag.name).startswith('h'):                 # heading
        id = _getIdFromString(str(moduleTag.get('id')))
        if id:
            _printHeading(id, str(moduleTag.name))
    elif str(moduleTag.name).startswith('div'):             # normal workitems
        id = _getIdFromString(str(moduleTag.get('id')))
        if id:
            _printWorkitem(id)
        else:
            #print moduleTag.text
            # https://github.com/purcell/airspeed
            pass
    else:                                                   # ignore these tags
        pass

def _removeDefinedAttributesFromText(tag):
    if hasattr(tag, 'attrs'):
        tag.attrs = {key:value for key,value in tag.attrs.iteritems() if key not in TEXT_REMOVE_ATTRIBUTES}
    return tag

def _removeDefinedAttributesFromTable(tag):
    if hasattr(tag, 'attrs'):
        tag.attrs = {key:value for key,value in tag.attrs.iteritems() if key not in TABLE_REMOVE_ATTRIBUTES}
    return tag

def _removeDefinedAttributes(soup):
    # https://stackoverflow.com/a/39976027
    for tag in soup.recursiveChildGenerator():
        if tag.name not in ['table','tbody','tr','th','td']:
            tag = _removeDefinedAttributesFromText(tag)
        else:
            tag = _removeDefinedAttributesFromTable(tag)
    return soup


##################################################################################
##################################################################################

# generate dicts
_analyseFolderStruct()

# print module dict
for module in moduleDict:
    print module, moduleDict[module]

#for img in imageDict:
#    #print img, imageDict[img], "\n"
#    if img.startswith('15'):
#        print img, imageDict[img], "\n"
#
#exit()

# ask user for a number
rawNumber = raw_input('Choose a number: ')

try:
    selectedModule = int(rawNumber)
except ValueError:
    print("Invalid number")
    exit()

if 0 < selectedModule < len(moduleDict):
    moduleSoup = BeautifulSoup(open(moduleDict[selectedModule]), 'html.parser', from_encoding='UTF-8')
    print "Author: " + _getFieldByAttrName(moduleSoup, "author")
    print "Created: " + _getFieldByAttrName(moduleSoup, "created")

    contentSoup = BeautifulSoup(_getFieldByAttrName(moduleSoup, "homePageContent"), 'html.parser', from_encoding='UTF-8')

    filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + _getFieldByAttrName(moduleSoup, "title").replace(" ", "_") + ".html"
    f = open(filename, 'w')

    for tag in contentSoup:
        _parseModuleTag(tag)

    f.close

    os.startfile(filename)

else:
    print "Input out of range - start again."