from flask import Flask, render_template, Response, request, redirect, url_for, session
from ArubaCloud.PyArubaAPI import CloudInterface
from ArubaCloud.base.Errors import RequestFailed
from ArubaCloud.objects.VmTypes import Smart, Pro
from ArubaCloud.objects import SmartVmCreator
from session_manager import RedisSessionInterface

import threading
import json

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


def run_in_thread(fn):
    def run(*k, **kw):
        t = threading.Thread(target=fn, args=k, kwargs=kw)
        t.start()
    return run


@app.route('/')
def login():
    return render_template("login.html")


@app.route('/main')
def main():
    return render_template("main.html", dc=session['dc'])


@app.route('/getservers', methods=['GET'])
def getservers():
    username = session['username']
    password = session['password']
    if request.args.get('dc') is not None:
        dc = request.args.get('dc')
    else:
        dc = request.cookies.get('dc')
    ci = CloudInterface(dc)
    try:
        ci.login(username=username, password=password, load=False)
        ci.get_servers()
    except RequestFailed:
        return Response(response='KO', status=401, mimetype="application/json")
    json_data = {'data': []}
    for element in ci.vmlist:
        if isinstance(element, Pro):
            ip = element.ip_addr.ip_addr
            vm_type = 'Pro'
        else:
            ip = element.ip_addr
            vm_type = 'Smart'
        if element.status == 3:
            state = 'PoweredOn'
        elif element.status == 2:
            state = 'PoweredOff'
        elif element.status == 1:
            state = 'InCreation'
        json_data['data'].append(
            {
                'recordsTotal': len(ci.vmlist),
                'recordsFiltered': len(ci.vmlist),
                'DT_RowId': element.sid,
                'name': '<span class="glyphicon glyphicon-tasks"></span>  {}'.format(element.vm_name),
                'type': vm_type,
                'ip': ip,
                'actions': '<button id="start" type="button" class="btn btn-primary">Start</button>'
                           '<button id="stop" type="button" class="btn btn-warning">Stop</button>'
                           '<button id="destroy" type="button" class="btn btn-danger">Destroy</button>',
                'state': state
            }
        )
    return Response(response=json.dumps(json_data), status=200, mimetype='application/json')


@run_in_thread
def execute_action(a, d):
    a(server_id=d)


@run_in_thread
def load_data_task():
    for dc in xrange(1, 6):
        ci = CloudInterface(session['dc'])
        ci.login(username=session['username'], password=session['password'], load=False)


@app.route('/action', methods=['POST'])
def action():
    data = request.form
    username = session['username']
    password = session['password']
    ci = CloudInterface(data['dc'])
    ci.login(username=username, password=password, load=False)
    if data['action'] == 'start':
        execute_action(ci.poweron_server, data['vm_id'])
    elif data['action'] == 'stop':
        execute_action(ci.poweroff_server, data['vm_id'])
    elif data['action'] == 'destroy':
        execute_action(ci.delete_vm, data['vm_id'])
    return Response(response=json.dumps({'data': 'OK'}), status=200, mimetype='application/json')


@app.route('/create_smart', methods=['POST'])
def create_smart():
    data = request.form
    username = session['username']
    password = session['password']
    ci = CloudInterface(data['dc'])
    ci.login(username=username, password=password, load=False)
    c = SmartVmCreator(name=data['server_name'],
                       admin_password=data['admin_password'],
                       template_id=data['template_id'],
                       auth_obj=ci.auth)
    c.set_type(size=data['size'])
    c.commit(url=ci.wcf_baseurl, debug=True)
    return Response(json.dumps({'data': 'OK'}), status=200, mimetype='application/json')


@app.route('/login', methods=['POST'])
def check_login():
    data = request.form
    username = data['aru'].encode('ascii', 'ignore')
    password = data['password'].encode('ascii', 'ignore')
    session['username'] = username
    session['password'] = password
    session['dc'] = 1
    ci = CloudInterface(1)
    try:
        ci.login(username=username, password=password, load=False)
        ci.get_servers()
    except RequestFailed:
        return Response(response='KO', status=401, mimetype="application/json")
    auth = {
        'username': username,
        'password': password
    }
    redirect_to_main = redirect(url_for('main'))
    response = app.make_response(redirect_to_main)
    return response


if __name__ == '__main__':
    app.run(debug=True)
