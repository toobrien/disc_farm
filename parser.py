from bs4 import BeautifulSoup as bs
from json import loads
import polars as pl
import re

HTML_SCHEMA = {
    'ts': pl.Datetime,
    'username': pl.String,
    'user_id': pl.String,
    'displayname': pl.String,
    'content': pl.String,
    'mentions': pl.String,
    'attachments': pl.String
}


# tree() helper

def tree_(root, pre):

    attrs = ''
    class_ = ''
    
    if hasattr(root, 'attrs'):
        
        attrs = ', '.join(root.attrs.keys())
        class_ = f'.{','.join(root.attrs['class'])}' if 'class' in root.attrs else ''
    
    print(f'{pre}{root.name}{class_}: {attrs}')
    pre += "    "

    if hasattr(root, 'children'):
        
        for child in root.children:
    
            tree_(child, pre)


# display tree with class and attributes for each tag

def tree(root):
    
    tree_(root, "")


# from document root, return dataframe summarizing messages i -> j

def read_html(path, i = 0, j = None):

    root = bs(open(path).read(), 'lxml')
    msgs = root.select('div.chatlog__message')[i:j]
    
    elems = [ 'div', 'span' ]
    atch_elems = [ 'img', 'source' ]
    ts_exp = re.compile('chatlog__(short-|system-notification-)*timestamp')
    author_exp = re.compile('chatlog__(system-notification-)*author')
    content_exp = re.compile('chatlog__(system-notification-)*content')
    
    ts = []
    username = []
    user_id = []
    displayname = []
    content = []
    mentions = []
    attachments = []

    i = 0
    
    for m in msgs:

        if m.select('.chatlog__author'):

            break

        i += 1

    for m in msgs[i:]:
        
        ts_i = m.find(elems, class_ = ts_exp)
        author_i = m.find(elems, class_ = author_exp)
        content_i = m.find(elems, class_ = content_exp)
        mentions_i = m.find_all(elems, class_ = 'chatlog__markdown-mention')
        attachments_i = m.find_all(elems, class_ = 'chatlog__attachment')
        
        if attachments_i:

            # temporary solution
            
            attachments_i = [ a.find(atch_elems) for a in attachments_i ]
            attachments_i = [ a for a in attachments_i if a and a.has_attr('src') ]
                
        ts_o = ts_i.attrs['title'] if ts_i else None
        username_o = author_i.attrs['title'] if author_i else username[-1]
        user_id_o = author_i.attrs['data-user-id'] if author_i else user_id[-1]
        displayname_o = author_i.get_text(strip = True) if author_i else displayname[-1]
        content_o = next(content_i.children).get_text(strip = True) if content_i else None
        mentions_o = '\n'.join([ mn.attrs['title'] if mn.has_attr('title') else mn.get_text(strip = True) for mn in mentions_i ]) if mentions_i else None
        attachments_o = '\n'.join([ a.attrs['src'] for a in attachments_i ]) if attachments_i else None
        
        ts.append(ts_o)
        username.append(username_o)
        user_id.append(user_id_o)
        displayname.append(displayname_o)
        content.append(content_o)
        mentions.append(mentions_o)
        attachments.append(attachments_o)

    return pl.DataFrame(
        {
            'ts': pl.Series(ts).str.to_datetime('%A, %B %-d, %Y %-I:%M %p'),
            'username': username,
            'user_id': user_id,
            'displayname': displayname,
            'content': content,
            'mentions': mentions,
            'attachments': attachments
        }, 
        schema = HTML_SCHEMA
    )


def read_json(path):

    msgs = loads(open(path).read())

    # TODO
    
    pass