#!/usr/bin/env python3

import json
from datetime import datetime

from flask import Flask, render_template


### Config

app = Flask(__name__)
CONFIG_FILE = 'content.json'

def load_config(fname=CONFIG_FILE):
    with open(fname, 'r') as f:
        lines = (l for l in f if not l.strip().startswith('//'))
        return json.loads('\n'.join(lines))

CONFIG = load_config(CONFIG_FILE)


### Routes

@app.route('/<name>.html')
def render_page(name):
    page = CONFIG['PAGES'][name]
    return render_template(page['template'], now=datetime.now(), **CONFIG, **page)

@app.route('/posts/<name>.html')
def render_posts(name):
    post = CONFIG['POSTS'][name]
    return render_template(post['template'], now=datetime.now(), **CONFIG, **post)


if __name__ == '__main__':
    app.run()
