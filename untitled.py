from flask import Flask, render_template, Response, request, redirect, url_for
from ArubaCloud.PyArubaAPI import CloudInterface
from ArubaCloud.base.Errors import RequestFailed
from ArubaCloud.objects.VmTypes import Smart, Pro
from ArubaCloud.objects import SmartVmCreator

import json

app = Flask(__name__)


@app.route('/')
def login():
    return render_template("login.html")


@app.route('/main')
def main():
    return render_template("main.html", dc=request.cookies.get('dc'))


@app.route('/getservers', methods=['GET'])
def getservers():
    data = json.loads(request.cookies.get('auth'))
    username = data['username'].encode('ascii', 'ignore')
    password = data['password'].encode('ascii', 'ignore')
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


@app.route('/action', methods=['POST'])
def action():
    data = request.form
    auth_data = json.loads(request.cookies.get('auth'))
    username = auth_data['username'].encode('ascii', 'ignore')
    password = auth_data['password'].encode('ascii', 'ignore')
    ci = CloudInterface(data['dc'])
    ci.login(username=username, password=password, load=False)
    if data['action'] == 'start':
        ci.poweron_server(server_id=data['vm_id'])
    elif data['action'] == 'stop':
        ci.poweroff_server(server_id=data['vm_id'])
    elif data['action'] == 'destroy':
        ci.delete_vm(server_id=data['vm_id'])
    return Response(response=json.dumps({'data': 'OK'}), status=200, mimetype='application/json')


@app.route('/create_smart', methods=['POST'])
def create_smart():
    data = request.form
    auth_data = json.loads(request.cookies.get('auth'))
    username = auth_data['username'].encode('ascii', 'ignore')
    password = auth_data['password'].encode('ascii', 'ignore')
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
    response.set_cookie('auth', value=json.dumps(auth))
    response.set_cookie('dc', value="1")
    return response


if __name__ == '__main__':
    app.run(debug=True)
