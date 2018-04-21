#!/usr/bin/env python3

import json
from datetime import datetime

from flask import Flask, render_template


CONFIG_FILE = 'content.json'


def load_config(fname=CONFIG_FILE):
    with open(fname, 'r') as f:
        lines = (l for l in f if not l.strip().startswith('//'))
        return json.loads('\n'.join(lines))

def get_urls(config):
    return list(config['PAGES'].items()) + list(config['POSTS'].items())



app = Flask(__name__)
CONFIG = load_config(CONFIG_FILE)

def render_error(reason="That's an error.", status=404):
    return render_template('error.html', **CONFIG, status=status, reason=reason)

@app.route('/<name>.html')
def render_page(name):
    try:
        page = CONFIG['PAGES'][name]
    except KeyError:
        return render_error('No page with that title.')
    return render_template(page['template'], now=datetime.now(), **CONFIG, **page)

@app.route('/posts/<name>.html')
def render_posts(name):
    try:
        post = CONFIG['POSTS'][name]
    except KeyError:
        return render_error('No post with that title.')
    return render_template(post['template'], now=datetime.now(), **CONFIG, **post)


if __name__ == '__main__':
    app.run()
