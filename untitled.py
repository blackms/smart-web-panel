from flask import Flask, render_template, Response, request
from ArubaCloud.PyArubaAPI import CloudInterface

app = Flask(__name__)


@app.route('/')
def login():
    return render_template("login.html")

@app.route('/main')
def main():
    return render_template("main.html")

@app.route('/login', methods=['POST'])
def check_login():
    data = request.form
    ci = CloudInterface(1)
    ci.login(username=str(data['username']), password=str(data['password']), load=False)
    ci.get_servers()
    return Response(response="ok", status=200, mimetype="application/json")


if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')
