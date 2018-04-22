#!/usr/bin/env python3

import sys
import json
from datetime import datetime

from flask import Flask, render_template


### Config

app = Flask(__name__)
CONFIG_FILE = 'content.json'
HOST = 'http://127.0.0.1:5000'

def load_config(fname=CONFIG_FILE):
    with open(fname, 'r') as f:
        lines = (l for l in f if not l.strip().startswith('//'))
        return json.loads('\n'.join(lines))

CONFIG = load_config(CONFIG_FILE)

PAGES = {page['url']: page for page in  list(CONFIG['PAGES'].values())}
POSTS = {post['url']: post for post in  list(CONFIG['POSTS'].values())}

### Routes

@app.route('/<path>')
def render_page(path):
    page = PAGES[f'/{path}']
    return render_template(page['template'], now=datetime.now(), **CONFIG, **page)

@app.route('/posts/<path>')
def render_post(path):
    print(path)
    post = POSTS[f'/posts/{path}']
    return render_template('post.html', now=datetime.now(), **CONFIG, **post)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--pages':
        print('\n'.join(HOST + url for url in PAGES.keys()))
    elif len(sys.argv) > 1 and sys.argv[1] == '--posts':
        print('\n'.join(HOST + url for url in POSTS.keys()))
    else:
        app.run()
