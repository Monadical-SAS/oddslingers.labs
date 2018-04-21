from flask import Flask, render_template
app = Flask(__name__)


BASE_CONTEXT = {
    'SITE_TITLE': 'OddSlingers Labs',
    'a': 'b',
}


@app.route("/")
def home():
    return render_template('home.html', **BASE_CONTEXT)


@app.route("/team")
def team():
    return render_template('team.html', **BASE_CONTEXT)



@app.route("/code")
def code():
    return render_template('code.html', **BASE_CONTEXT)
