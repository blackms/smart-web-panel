from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def login():
    return render_template("login.html")

@app.route('/main')
def main():
    return render_template("main.html")

@app.route('/login')
def check_login():
    pass


if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')
