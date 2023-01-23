import flet
from flet import (
    Page,
    ListView,
    ElevatedButton,
    Container,
    Row,
    Text,
    FilledButton,
    colors,
    ContainerTapEvent,
    View,
    Image,
    Column,
    FloatingActionButton
)
from bs4 import BeautifulSoup, Doctype
import textwrap
import re 
import requests
 

#Initializes the list of titles
novelTitles = [None] * 20

'''Sets up boxnovel specific parsing using the page numbers as well as what I am 
 going to use to hold positions in that list'''
fullScopeVar = {
'pagenum' : 0, 
'counter' : 0,
'pos' : 0,
'index' : 0,
'arr': [6,12,8,14,14]}


# Scrapes the page (10 items) returns a list of titles in searchable format
def stack_push():
    books = []
    nav_link = requests.get(f'https://boxnovel.com/novel/page/{fullScopeVar["pagenum"]}/?m_orderby=rating').text
    soup = BeautifulSoup(nav_link, 'html.parser')
    searchquery = soup.find_all('div', attrs= {'class':'post-title font-title'})
    for div in searchquery:
        title = div.find('a').text
        stripped = re.sub('[^A-Za-z0-9-\s]+', '', title)
        hyphenated = re.sub('[\s]+', '-', stripped)
        if hyphenated not in books:
            books.append(hyphenated)

    return books

# This manages the windows length as well as the the pages position in the list
def windowCycle():
    # 6 items in the list so everytime cycle is called increase the counter  
    global novelTitles
    global fullScopeVar
    fullScopeVar['counter'] += 6
    '''if the window has only just been initialized set the pos variable to 1
        and the pagenumber to 1 while clearing the list
        append all the items in the list of books
        sets the page number to the next page and adds those books too
        sets the index of what book is last in the viewer to a preselected list
    '''
    '''
    If the window has things in it already add 1 to the position holder

    if that position holder is 3 (The button has been hit 2 times)
    add a page to the page number delete the first ten books
    then add the 10 books from the current page number

    If that position is at 5 do the same thing 
    
    If the position is at 1,2 or 4 just increment the index

    If the position is at 6 reset the index to the first value in the
    preselected array

    Window logic is index goes from 6 -> 12 -> 18 then it deletes first 10
    setting the index to -> 8 -> 14 deletes first 10 to -> 4 while adding 10 -> 14
    then deletes first 10 again setting 20 -> 0 retrns a list
    '''
    if novelTitles.count(None) == 20:
        fullScopeVar['pos'] += 1
        fullScopeVar['pagenum'] += 1
        novelTitles.clear()
        for book in stack_push():
            novelTitles.append(book)
        fullScopeVar['pagenum'] += 1
        for book in stack_push():
            novelTitles.append(book)
        
    else:
        fullScopeVar['pos'] += 1
        if fullScopeVar['pos'] == 3:
            
            fullScopeVar['pagenum'] += 1
            del novelTitles[0:10]
            for book in stack_push():
                novelTitles.append(book)

        elif fullScopeVar['pos'] == 5:
            
            fullScopeVar['pagenum'] += 1
            for book in stack_push():
                novelTitles.append(book)
            
        elif fullScopeVar['pos'] == 6:
            fullScopeVar['pos'] = 1
            del novelTitles[0:11]
            
    fullScopeVar['index'] = fullScopeVar['arr'][fullScopeVar['pos'] - 1]
    return novelTitles

#Splices that list into 6 displaying titles

#Makes a TOC grabs image
def get_image(link):
    toc_page = requests.get(f'https://boxnovel.com/novel/{link}/').text
    soup = BeautifulSoup(toc_page, 'html.parser')
    img = soup.select_one('img[data-src]').get('data-src')
    return img

#Uses a different site to check the most recent chapter to make a Table of Contents
def get_chapter_list(link):
    link = link.lower()
    nav_Page = requests.get(f'https://full-novel.com/nb/{link}/').text
    soup = BeautifulSoup(nav_Page, 'html.parser')
    searchquery = soup.find('div', attrs= {'class':'item-value'})
    fulltitle = searchquery.a.text.strip().partition('-')
    # recent_no = fulltitle[0].replace('Chapter ', '').rstrip()
    recent_no = ''.join(c for c in fulltitle[0] if c.isdigit())
    recent_tit = fulltitle[2]
    return int(recent_no)

# Scrapes text from page and returns the chapter content and its title
def Chapget(title,slcted):
    if requests.get(f'https://boxnovel.com/novel/{title}-boxnovel/chapter-{slcted}/').status_code != 200:
        bnovel = requests.get(f'https://boxnovel.com/novel/{title}/chapter-{slcted}/').text
    else:  
        bnovel = requests.get(f'https://boxnovel.com/novel/{title}-boxnovel/chapter-{slcted}/').text
    final = ''
    soup = BeautifulSoup(bnovel, 'html.parser')
    for paragraph in soup.div.findAll('p'):
        final += paragraph.text + '\n'*2

    return final

windowCycle()
displayed = novelTitles[fullScopeVar['index'] - 6: fullScopeVar['index']]
numba = None
slctd = None
get_img = lambda num: Image(src = get_image(displayed[num]))



def main(page: Page):
    page.window_width = 450
    page.window_height = 900
    page.window_resizable = False
    page.horizontal_alignment = 'center'
    def imageContainer_Clicked(e: ContainerTapEvent):
        global numba
        numba = e.control.data
        page.go('/table')
        page.update()

    def fabClicked(e: ContainerTapEvent):
        windowCycle()
        displayed = novelTitles[fullScopeVar['index'] - 6: fullScopeVar['index']]
        
        
        



    def lv_clicked(e):
        global slctd
        slctd = e.control.data
        page.go('/book')

    def toc_list(book):
        lv = ListView(expand=1, spacing=10, padding=20, auto_scroll=True)

        count = 1


        for i in range(0, 60):
            eb = ElevatedButton(
                text= f'Chapter {count}',
                data=count,
                on_click= lambda count :lv_clicked(count))
            lv.controls.append(eb)
            count += 1
        return lv


    class img_container(Container):
            def __init__(self, num):
                super().__init__()
                self.content = get_img(num)
                self.on_click = imageContainer_Clicked
                self.data = num
                self.image_fit = 'scaleDown'




    def change_route(route):
        page.views.clear()
        page.views.append(
            View(
            route = '/',
            controls = [
                Container(bgcolor = colors.BLACK,
                content = 
                        Column(controls=[
                            Row(controls=[
                                img_container(0),
                                img_container(1)
                                ], alignment= 'center'),
                            Row(controls=[
                                img_container(2),
                                img_container(3)
                                ], alignment= 'center'),
                            Row(controls=[
                                img_container(4),
                                img_container(5)
                                ], alignment= 'center')
            ])
            ),  FloatingActionButton(text = 'Next', on_click = fabClicked)]
                ))       
        if page.route == '/table':
            page.views.append(
                    View(
                        '/table',
                        [
                            Row([FilledButton(text='Back', on_click= lambda x: page.go('/'))]),
                            Row([get_img(numba)], alignment= 'center'),
                            Row([Text(displayed[numba].replace('-', ' ').title())], alignment='center'),
                            Row([toc_list(displayed[numba])])
                        ]
                        )
                            )
        page.update()


        if page.route == '/book':
            chapterinfo = Chapget(displayed[numba], slctd)
            page.views.append(
                View(
                    route='/book',
                    scroll='always',
                    controls=[
                        Row([FilledButton(text='Back', on_click= lambda x: page.go('/table')),Text(displayed[numba].replace('-', ' ').title(), text_align='center', expand=True)]),
                        Text(chapterinfo, text_align='center')
                        
                    ]))
    
    
    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
        print(page.route)
    # page.update()
    page.on_route_change = change_route
    page.on_view_pop = view_pop
    page.go(page.route)
flet.app(target=main, view = flet.FLET_APP)









# if soup.find('div', attrs={'class' : 'dib pr'}):
    #     body = soup.findAll('div', attrs={'class' : 'dib pr'})
    #     for source_paragraph in body:
    #         paragraph = source_paragraph.find('p').text
    #         final += paragraph
    # elif soup.find('div', attrs={'class' : 'cha-words'}):
    #     body = soup.find('div', attrs={'class' : 'cha-words'})
    #     for source_paragraph in body.findAll('p'):
    #         paragraph = source_paragraph.text
    #         final += paragraph
    #         final += '\n'*4
    # else:
    #     assert 'Neither dib-pr or cha-words'
    
        # final += textwrap.fill(paragraph, width= 50, subsequent_indent='\n')
        # final += '\n'*4
    # Fulltitle = str(soup.find('title'))[7:-8].split('-')