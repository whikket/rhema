# -*- coding: utf-8 -*-
import sqlite3
import Tkinter as tk
import ConfigParser
import codecs
import sys 
import os

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

print dname

from HTMLParser import HTMLParser

class Parser(HTMLParser):
    
    def __init__(self, tk, root, label):
        self.tk = tk
        self.root = root
        self.box = label
        HTMLParser.__init__(self)
    
    def handle_starttag(self, tag, attrs):
        global showText
        global tags
        global link
        
        if tag == "j":
            tags.insert(0,"tagJ")
        
        if tag == "f":
            tags.insert(0,"tagNote")
            
        if tag == "t":
            tags.insert(0,"tagT")
            self.box.insert(self.tk.END, "\n     ", tuple(tags))

        if tag == "i":
            tags.insert(0,"tagT")
            
        if tag == "e":
            tags.insert(0,"tagT")
        if tag == "h":
            tags.insert(0,"tagHeading")
        if tag == 'a':
            for name, value in attrs:
                if name == 'tagRef':
                    tags.insert(0, 'tagRef')
                if name == 'href':
                    tags.insert(0, 'tagAHref:'+value)
                
            tags.insert(0, 'tagA')
        if tag == 's':
            showText = False
        if tag == 'm':
            showText = False
        
    def handle_endtag(self, tag):
        global showText
        global tags
        
        if tag == "i":
            if "tagT" in tags:
                tags.remove("tagT")
        if tag == "e":
            if "tagT" in tags:
                tags.remove("tagT")
        if tag == "f":
            if "tagNote" in tags:
                tags.remove("tagNote")
        if tag == 'j':
            if "tagJ" in tags:
                tags.remove("tagJ")
        if tag == "t":
            if "tagT" in tags:
                tags.remove("tagT")
        if tag == "h":
            if "tagHeading" in tags:
                tags.remove("tagHeading")
        if tag == 'a':
            if "tagA" in tags:
                tags.remove('tagA')
            if "tagRef" in tags:
                tags.remove('tagRef')
            tags = [x for x in tags if "Href" not in x]
        if tag == 's':
            showText = True
        if tag == 'm':
            showText = True
            
    def handle_data(self, data):
        global showText
        global currentVerse
        global bufferredVerse
        global tags
        
        if showText:
            if currentVerse != bufferredVerse:
                self.box.insert(self.tk.END, " " + str(currentVerse), "verseNo")
                self.box.insert(self.tk.END, ' ', tuple(tags))
                bufferredVerse = currentVerse
                
            data = data.replace("<", "")
            tags.insert(0, "verseStart"+str(currentVerse))
            self.box.insert(self.tk.END, data, tuple(tags))
            tags.remove("verseStart"+str(currentVerse))
        
    def handle_startendtag(self, tag, attrs):
        global textBox
        if tag == "pb":
            self.box.insert(self.tk.END, '\n \n', tuple(tags))
            
        if tag == "br":
            self.box.insert(self.tk.END, '\n', tuple(tags))
            
class History():
    def __init__(self):
        self.steps = 0
        self.places = []
    def go(self,place):
        if self.getPlace() == place:
            return 0
        if self.steps < len(self.places):
            del self.places[self.steps:]
        self.places.append(place)
        self.steps += 1
        if len(self.places) > 100:
            del self.places[:75]
            self.steps -= 75
    def goForward(self):
        self.steps += 1
        if self.steps > len(self.places):
            self.steps = len(self.places) 
        return self.getPlace()
        
    def goBack(self):
        self.steps -= 1
        if self.steps < 1:
            self.steps = 1
        return self.getPlace()
    def printplaces(self):
        print self.places
        print self.steps
    def getPlace(self):
        if self.steps < 1:
            return 1
        return self.places[self.steps-1]
    def save(self, config):
        config.read("bibles//config.ini")
        config.set('history', 'location', str(self.steps))
        config.set('history', 'nodes', ';'.join(self.places))
        with open("bibles//config.ini", "wb") as file:
            
            config.write(file)
            file.close()
    def load(self, config):
        self.steps  = int(ConfigSectionMap("history",config)['location'])
        self.places = ConfigSectionMap("history",config)['nodes'].split(";")
def multiFunction(*functions):
    def func(*args, **kwargs):
        return_value = None
        for function in functions:
            return_value = function(*args, **kwargs)
        return return_value
    return func
    
def showNote(event, tag):
    
    global configs
    global book
    global chapter
    global fontFace
    global fontSize
    global wojColor
    global fgColor
    global noteColor
    global verseColor
    global linkColor
    
    cfg = ConfigParser.ConfigParser()
    cfg.read('bibles//config.ini')
    conn2 = sqlite3.connect("bibles//"+ConfigSectionMap("current",cfg)['bible']+".commentaries.SQLite3")
    conn2.row_factory = sqlite3.Row
    cursor2 = conn2.cursor()
    
    sql = "SELECT * FROM commentaries WHERE book_number=?  and chapter_number_from=? and marker like ?;"
    
    index = event.widget.index("@%s,%s" % (event.x, event.y))
    
    ch = event.widget.get(index+ " wordstart - 5 chars", index + " wordend + 5 chars")
    num = ch[ch.find('['):ch.find(']')+1]
    if num == '':
        num = event.widget.get(index)
    
    
    for row in cursor2.execute(sql, [book, chapter, num]):
        note = num + ' ' +row['text']

    toplevel = tk.Toplevel()
    toplevel.title("Footnotes")
    toplevel.iconbitmap(r"bibles//bible.ico")
    label1 = tk.Text(toplevel,  fg = fgColor, bg = bgColor, wrap=tk.WORD)
    label1.config( font=fontFace+" "+fontSize, padx=15)
    
    label1.tag_configure("tagJ", foreground=wojColor, font=fontFace+" "+fontSize)
    label1.tag_configure("tagNormal", foreground=fgColor, font=fontFace+" "+fontSize)
    label1.tag_configure("tagT" , font=fontFace+" "+fontSize+' italic')
    label1.tag_configure("tagNote", foreground=noteColor, offset=4, font=fontFace+" "+str(int(fontSize)-6))
    label1.tag_configure("verseNo", foreground=verseColor, offset=4, font=fontFace+" "+str(int(fontSize)-4))
    label1.tag_configure("tagA" , foreground=linkColor, font=fontFace+" "+fontSize, underline=True)

    label1.tag_bind("tagA", "<Button-1>", lambda e:followLink(e))

    parser2 = Parser(tk, toplevel, label1)
    parser2.feed(note)
    label1.pack()
    
def scrollMe(event, box):
    
    box.yview_scroll(-1*(event.delta/120), "units")
    
def ConfigSectionMap(section, iniFile):
    dict1 = {}
    options = iniFile.options(section)
    for option in options:
        try:
            dict1[option] = iniFile.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def getText(bible, book, chapter):
    file = "bibles//"+bible+".SQLite3"
    conn = sqlite3.connect(file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor3 = conn.cursor()

    text = []
    sql = "SELECT * FROM verses WHERE book_number=? and chapter=?;"
    headingsSql = "SELECT * FROM stories WHERE exists (select count(*) from sqlite_master where type='table' and name='stories') and book_number=? and chapter=? and verse = ?"
    headingsExist = False
    for e in cursor3.execute("select name from sqlite_master where type='table' and name='stories'"):
        headingsExist = True
    for row in cursor.execute(sql, [book,chapter]):
        if headingsExist:
            for heading in cursor3.execute(headingsSql, [book, row["chapter"], row['verse']]):
                text.append(('h',"\n\n<h>"+heading['title']+ "</h>"))

        verse = row["text"]
        currentVerse = row['verse']
        verse = verse.replace("<<", "<")
        text.append((row['verse'], verse))
        
    return text
        
def displayChapter(newBible, newBook, newChapter, tk, root, box, v=0):
    global currentVerse
    global bufferredVerse
    global bible
    bible = newBible
    global book
    global chapter
    global tags 
    global history
    tags = []
    v = int(v)
    if book != newBook or chapter != newChapter :
        history.go("B:"+str(newBook)+" "+str(newChapter)+":0")
    
    book = newBook
    chapter = newChapter
    parser = Parser(tk, root, box)
    verses = getText(newBible, book, chapter)
    bufferredVerse = 0
    currentVerse = 0
    box.config(state=tk.NORMAL)
    box.delete('1.0', tk.END)
    marks = getBookmarks(book, chapter)
    for verse in verses:
        if(verse[0] != 'h'):
            currentVerse = verse[0]
        
        parser.feed(verse[1])
        
    if v > 0:
        hilightVerse(v)
    
    for mark in marks:
        hilightVerse(mark)

    box.config(state=tk.DISABLED)
    

def getBookName(bible, bookNo):
    conn = sqlite3.connect("bibles//"+bible+".SQLite3")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor3 = conn.cursor()

    text = []
    sql = "SELECT * FROM books WHERE book_number=?;"
    
    for row in cursor.execute(sql, [bookNo]):
        return row['long_name']
    
def setBible():
    global bible
    global book
    global chapter
    global root
    global textBox
    biblesWindow = tk.Toplevel()
    biblesWindow.title("Versions")
    biblesWindow.iconbitmap(r"bibles//bible.ico")
    biblesList = tk.Frame(biblesWindow)
    for file in os.listdir("bibles//"):
        if not file.endswith('SQLite3'):
            continue
        if 'commentaries' in file:
            continue
        if 'bookmarks' in file:
            continue
        newBible = file.split('.')
        
        bButton = tk.Button(biblesList, text=newBible[0], command=lambda nb=newBible[0]: multiFunction(displayChapter(nb, book, chapter, tk, root, textBox), biblesWindow.destroy(), setConfig("current", "bible", nb), updateHeaderButtons()))
        bButton.config(width=15)
        bButton.pack()
    biblesList.pack()
    
def setBook():
    global bible
    global book
    global chapter
    global root
    global textBox
    file = "bibles//"+bible+".SQLite3"
    conn = sqlite3.connect(file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sql = "select * from books order by book_number"
    
    booksWindow = tk.Toplevel()
    booksWindow.title("Books")
    booksWindow.iconbitmap(r"bibles//bible.ico")
    booksList = tk.Frame(booksWindow)
    i = 0
    j = 0
    for row in cursor.execute(sql):
        bookName = row["short_name"]
        bButton = tk.Button(booksList, text=bookName, command=lambda nb=row["book_number"]: multiFunction(updateBook(nb),setChapter(), booksWindow.destroy(), setConfig("current", "book", nb), updateHeaderButtons()))
        bButton.config(width=5)
        bButton.grid(column = i, row=j)
        i += 1
        if i % 6 == 0:
            i =  0
            j += 1
    booksList.grid(column=0, row=0)
def updateBook(b):
    global book
    book = b
    
def setChapter():
    global bible
    global book
    global chapter
    global root
    global textBox
    
    chaptersWindow = tk.Toplevel()
    chaptersWindow.title("Chapters")
    chaptersWindow.iconbitmap(r"bibles//bible.ico")
    chaptersList = tk.Frame(chaptersWindow)
    i = 0
    j = 0
    numChapters = getNumChapters()
    for k in range(1, int(numChapters) + 1):
        bButton = tk.Button(chaptersList, text=k, command=lambda nb=k: multiFunction(displayChapter(bible, book, nb, tk, root, textBox), chaptersWindow.destroy(), setConfig("current", "chapter", nb), updateHeaderButtons()))
        bButton.config(width=5)
        bButton.grid(column = i, row=j)
        i += 1
        if i % 10 == 0:
            i =  0
            j += 1
    chaptersList.grid(column=0, row=0)

def getNumChapters():
    global bible
    global book
    file = "bibles//"+bible+".SQLite3"
    conn = sqlite3.connect(file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sql = "select * from verses where book_number=? order by chapter desc limit 1;"
    for row in cursor.execute(sql, [book]):
        numChapters = row["chapter"]
    return numChapters
    
def setNextChapter():
    global bible
    global book
    global chapter
    global root
    global textBox
    c = int(chapter)
    if c < getNumChapters():
        c += 1
        chapter = str(c)
        displayChapter(bible, book, chapter, tk, root, textBox)
        setConfig("current", "chapter", chapter)
        updateHeaderButtons()
    
def setPrevChapter():
    global bible
    global book
    global chapter
    global root
    global textBox
    c = int(chapter)
    if c > 1:
        c -= 1
        chapter = str(c)
        displayChapter(bible, book, chapter, tk, root, textBox)
        setConfig("current", "chapter", chapter)
        updateHeaderButtons()

def followLink(event):
    w = event.widget
    x, y = event.x, event.y
    tags = w.tag_names("@%d,%d" % (x,y))
    for t in tags:
        if "Href" in t:
            items = t.split(":")
            location = items[2].split(" ")
            displayChapter(bible, location[0], location[1], tk, root, textBox, items[3])
            updateHeaderButtons()
            setConfig("current", "book", location[0])
            setConfig("current", "chapter", location[1])
            w.master.destroy()

def hilightVerse(v):
    if v == 0:
        return
    global textBox
    global verseColor
    range = textBox.tag_ranges("verseStart"+str(v))
    textBox.tag_add("tagBookmark", range[0], range[1])

def getBookmarks(book, chapter):
    file = "bibles/bookmarks.SQLite3"
    conn = sqlite3.connect(file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    marks = []
    sql = "select * from bookmarks where book=? and chapter=? order by verse;"
    for row in cursor.execute(sql, [book, chapter]):
        marks.append(row["verse"])
    return marks
    
def setConfig(section, option, value):
    config = ConfigParser.SafeConfigParser()
    config.read("bibles/config.ini")
    config.set(section, option, str(value))
    with open("bibles/config.ini", "wb") as file:
        
        config.write(file)
        file.close()

def updateHeaderButtons():
    global bibleButton
    global bible
    global bookButton
    global book
    global chapter
    
    bibleButton.config(text=bible)
    bookButton.config(text=getBookName(bible, book))
    chapterButton.config(text=chapter)
        
def updateBookmark(event):
    global book
    global chapter
    
    index = event.widget.index("@%s,%s" % (event.x, event.y))
    
    file = "bibles/bookmarks.SQLite3"
    conn = sqlite3.connect(file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    isBookmarked = False
    
    ch = event.widget.get(index+ " wordstart", index + " wordend")
    range = textBox.tag_ranges("verseStart"+str(ch))
    
    
    sql = "select * from bookmarks where book=? and chapter=? and verse=?;"
    for row in cursor.execute(sql, [int(book), int(chapter), int(ch)]):
        isBookmarked = True
        
    if not isBookmarked:
        sql = "insert into bookmarks (book, chapter, verse) values (?, ?, ?);"
        textBox.tag_add("tagBookmark", range[0], range[1])
    else:
        sql = "delete from bookmarks where book=? and chapter=? and verse=?"
        textBox.tag_remove("tagBookmark", range[0], range[1])
        
    
    cursor.execute(sql, [int(book), int(chapter), int(ch)])
    conn.commit()
    
def showBookmarks():
    global bible
    global book
    global chapter
    global root
    global textBox
    global configs
    global book
    global chapter
    global fontFace
    global fontSize
    global wojColor
    global fgColor
    global noteColor
    global verseColor
    global linkColor
    
    file = "bibles/"+bible+".SQLite3"
    conn = sqlite3.connect(file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('attach database "bibles/bookmarks.SQLite3" as marks;')
    marksWindow = tk.Toplevel()
    marksWindow.title("Bookmarks")
    marksWindow.iconbitmap(r"bibles/bible.ico")
    scrollBar = tk.Scrollbar(marksWindow)
    marksList = tk.Text(marksWindow,  fg = fgColor, bg = bgColor, wrap=tk.WORD)
    scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
    scrollBar.config(command=marksList.yview)
    marksList.config(yscrollcommand=scrollBar.set, bg=bgColor, fg=fgColor, font=fontFace+" "+fontSize, padx=15)
    marksList.bind_all("<MouseWheel>", lambda e,b=marksList:scrollMe(e,b))

    marks = ''
    sql = "select * from marks.bookmarks, books, verses where bookmarks.book=books.book_number and verses.verse = bookmarks.verse and verses.book_number=bookmarks.book and verses.chapter=bookmarks.chapter;"
    for row in cursor.execute(sql):
        mark = '<a href="B:'+str(row['book_number'])+' '+str(row['chapter'])+':'+str(row['verse'])+'" tag="tagRef">'+row['short_name']+' '+str(row['chapter'])+':'+str(row['verse']) + '</a> '+row['text']
        mark = mark.replace('<pb/>', " ").replace("<br/>", ' ')
        marks = marks + mark + "\n"
    marksList.config( font=fontFace+" "+fontSize, padx=15)
    
    marksList.tag_configure("tagJ", foreground=wojColor, font=fontFace+" "+fontSize)
    marksList.tag_configure("tagNormal", foreground=fgColor, font=fontFace+" "+fontSize)
    marksList.tag_configure("tagT" , font=fontFace+" "+fontSize+' italic')
    marksList.tag_configure("tagNote", foreground=noteColor, offset=4, font=fontFace+" "+str(int(fontSize)-6))
    marksList.tag_configure("verseNo", foreground=verseColor, offset=4, font=fontFace+" "+str(int(fontSize)-4))
    marksList.tag_configure("tagA" , foreground=linkColor, font=fontFace+" "+fontSize+' bold', underline=True)
    marksList.tag_configure("tagRef" , font=fontFace+" "+fontSize+'  italic')
    
    marksList.tag_bind("tagA", "<Button-1>", lambda e:followLink(e))
    marksList.tag_bind("tagNote", "<Button-1>", lambda e:showNote(e, "tagNote"))

    parser2 = Parser(tk, marksWindow, marksList)
    parser2.feed(marks)
    marksList.pack()
    updateHeaderButtons()
    
def goBack():
    history.goBack()
    
    items = history.getPlace().split(":")
    location = items[1].split(" ")
    print items[2]
    displayChapter(bible, location[0], location[1], tk, root, textBox, items[2])
    updateHeaderButtons()
    setConfig("current", "book", location[0])
    setConfig("current", "chapter", location[1])
    
def goForward():
    history.goForward()
    
    items = history.getPlace().split(":")
    location = items[1].split(" ")
    displayChapter(bible, location[0], location[1], tk, root, textBox, items[2])
    updateHeaderButtons()
    setConfig("current", "book", location[0])
    setConfig("current", "chapter", location[1])
    

configs = ConfigParser.ConfigParser()
configs.read('bibles/config.ini')
themeConfigs = ConfigParser.ConfigParser()
themeConfigs.read('bibles/'+ConfigSectionMap("style", configs)['theme']+'.ini')
bible = ConfigSectionMap("current",configs)['bible']
book = ConfigSectionMap("current",configs)['book']
chapter = ConfigSectionMap("current",configs)['chapter']
fgColor = ConfigSectionMap("style",themeConfigs)['foreground']
bgColor = ConfigSectionMap("style",themeConfigs)['background']
wojColor = ConfigSectionMap("style",themeConfigs)['woj']
headingColor = ConfigSectionMap("style",themeConfigs)['heading']
noteColor = ConfigSectionMap("style",themeConfigs)['note']
verseColor = ConfigSectionMap("style",themeConfigs)['verse']
linkColor = ConfigSectionMap("style",themeConfigs)['link']
currentVerseColor = ConfigSectionMap("style", themeConfigs)['current']
fontFace = ConfigSectionMap("style",themeConfigs)['font']
fontSize = ConfigSectionMap("style",themeConfigs)['font-size']
link = ''
history = History()
history.load(configs)

root = tk.Tk()
scrollBar = tk.Scrollbar(root)
textBox = tk.Text(root, height=30, width=100, wrap=tk.WORD, pady=15)

textBox.tag_configure("tagJ", foreground=wojColor, font=fontFace+" "+fontSize)
textBox.tag_configure("tagNormal", foreground=fgColor, font=fontFace+" "+fontSize)
textBox.tag_configure("tagT" , font=fontFace+" "+fontSize+' italic')
textBox.tag_configure("tagNote", foreground=noteColor, offset=4, font=fontFace+" "+str(int(fontSize)-6))
textBox.tag_configure("verseNo", foreground=verseColor, offset=4, font=fontFace+" "+str(int(fontSize)-4))
textBox.tag_configure("tagHeading", foreground=headingColor, font=fontFace+" "+str(int(fontSize)+4) +' bold')
textBox.tag_configure("tagA" , foreground=linkColor,underline=True, font=fontFace+" "+fontSize)
textBox.tag_configure("tagVerse", background=currentVerseColor, foreground=bgColor)
textBox.tag_configure("tagBookmark", underline=True)

tags = []

textBox.tag_bind("tagNote", "<Button-1>", lambda e:showNote(e, "tagNote"))
textBox.tag_bind("tagA", "<Button-1>", lambda e:followLink(e))
textBox.tag_bind("verseNo", "<Button-1>", lambda e:updateBookmark(e))

showText = True
buttons = tk.Frame(root)
root.title("Rhema")
root.iconbitmap(r"bibles/bible.ico")
buttons.pack(side=tk.TOP)
bibleButton = tk.Button(buttons, text=bible, command=lambda: setBible())
bibleButton.pack(side=tk.LEFT, padx=5, pady=5)

bookButton = tk.Button(buttons, text=getBookName(bible, book), command=lambda: setBook())
bookButton.pack(side=tk.LEFT, padx=5, pady=5)
chapterButton = tk.Button(buttons, text=str(chapter), command=lambda: setChapter())
chapterButton.pack(side=tk.LEFT)

l1 = tk.Label(buttons, text=" ", width=2)
l1.pack(side=tk.LEFT)

prevButton = tk.Button(buttons, text=str("«"), command=lambda: setPrevChapter())
prevButton.pack(side=tk.LEFT, padx=5, pady=5)
nextButton = tk.Button(buttons, text=str("»"), command=lambda: setNextChapter())
nextButton.pack(side=tk.LEFT)

l2 = tk.Label(buttons, text=" ", width=5)
l2.pack(side=tk.LEFT)

markButton = tk.Button(buttons, text=unicode('🔖', 'utf-8'), command=lambda: showBookmarks())
markButton.pack(side=tk.LEFT, padx=25)

hisPrevButton = tk.Button(buttons, text=unicode("⤺", 'utf-8'), command=lambda: goBack())
hisPrevButton.pack(side=tk.LEFT, padx=5, pady=5)
hisNextButton = tk.Button(buttons, text=unicode("⤻", 'utf-8'), command=lambda: goForward())
hisNextButton.pack(side=tk.LEFT)

scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
textBox.pack(side=tk.LEFT, fill=tk.Y)
scrollBar.config(command=textBox.yview)
textBox.config(yscrollcommand=scrollBar.set, bg=bgColor, fg=fgColor, font=fontFace+" "+fontSize, padx=15)
textBox.bind_all("<MouseWheel>", lambda e, b=textBox:scrollMe(e, b))

bufferredVerse = 0
currentVerse = 0

displayChapter(bible, book, chapter, tk, root, textBox)

root.protocol("WM_DELETE_WINDOW", lambda: multiFunction(history.save(configs), root.destroy() ))

tk.mainloop()
