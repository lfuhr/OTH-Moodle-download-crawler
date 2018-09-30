import cookielib, urllib2, urllib, os, os.path, re
from ConfigParser import ConfigParser
from bs4 import BeautifulSoup

authentication_url = "https://elearning.uni-regensburg.de/login/index.php"
root_directory = "/Some/Directory/"
login = {
    'username': "",
    'password': "",
    'realm': "hs"
}

courses = [
    # ["NOP", "https://elearning.uni-regensburg.de/course/view.php?id=32759"],
    ["LaTex", "https://elearning.uni-regensburg.de/course/view.php?id=19442"],
    
    # Folders in courses are parsed automatically but can be added manually as well
    ["LaTexFolder", "https://elearning.uni-regensburg.de/mod/folder/view.php?id=837175"],
]


# Store the cookies and create an opener that will hold them
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

# Add our headers
opener.addheaders = [('User-agent', 'Moodle-Crawler')]

# Install our opener (note that this changes the global opener to the one
# we just made, but you can also just call opener.open() if you want)
urllib2.install_opener(opener)


# Use urllib to encode the payload
logindata = urllib.urlencode(login)

# Build our Request object (supplying 'logindata' makes it a POST)
req = urllib2.Request(authentication_url, logindata)

# Make the request and read the response
response = urllib2.urlopen(req)
contents = response.read()
# Ignore contents

def downloadThisPage(parentFolder, webpath, name):
    if not os.path.isdir(parentFolder + name):
        os.mkdir(parentFolder + name)
    response1 = urllib2.urlopen(webpath)
    scrap = response1.read()
    soup = BeautifulSoup(scrap, features="html.parser")
    current_dir = parentFolder + name + "/"
    filebuttons = soup.select(".fp-filename-icon > a, .resource a")

    for file_button in filebuttons :
        href = file_button.get('href')
        webFile = urllib2.urlopen(href)
        url = current_dir + webFile.geturl().split('/')[-1].split('?')[0]
        file_name = urllib.unquote(url).decode('utf8')
        pdfFile = open(file_name, 'wb')
        pdfFile.write(webFile.read())
        webFile.close()
        pdfFile.close()

    for folder_button in soup.findAll(class_="folder"):
        href = folder_button.find('a').get('href')
        foldername = folder_button.find(class_="instancename").getText()
        downloadThisPage(current_dir, href, foldername)

for course in courses:
    downloadThisPage(root_directory, course[1],course[0])

print "Download Complete"
