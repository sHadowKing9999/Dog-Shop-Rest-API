from flask import Flask, jsonify,abort,make_response,request,url_for
from flask_httpauth import HTTPBasicAuth
auth=HTTPBasicAuth()
app = Flask(__name__)
#creating users and assigning password
users=[
    {
        'user':'Reet',
        'password':'0123'
    },
    {
        'user':'Storm',
        'password':'1234'
    }
]
pups=[
    {
        'id':1,
        'name':'Bull Terrier',
        'male-weight':'23-32',
        'female-weight':'18-23',
        'available':True
    },
    {
        'id':2,
        'name':'Pug',
        'male-weight':'6-9',
        'female-weight':'6-8',
        'available':False
    },
    {
        'id':3,
        'name':'Golden Retriever',
        'male-weight':'31.7-36.3',
        'female-weight':'27.2-31.7',
        'available':True
    }
]
@auth.get_password  #check username return desired password
def get_password(username):
    for user in users:
        if username==user['user']:
            return user['password']
    return None
@auth.error_handler #unauthorized access handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)
def make_public_pup(pup):
    new_pup = {}
    for field in pup:
        if field == 'id':
            new_pup['uri'] = url_for('get_pup', pup_id=pup['id'], _external=True)
        else:
            new_pup[field] = pup[field]
    return new_pup
@app.route('/shop/api/v1.0/pups', methods=['GET'])
def get_pups():
    return jsonify({'Pups': [make_public_pup(pup) for pup in pups]})
@app.route('/shop/api/v1.0/pups/<int:pup_id>', methods=['GET'])
def get_pup(pup_id):
    pup = [pup for pup in pups if pup['id'] == pup_id]
    if len(pup) == 0:
        abort(404)
    return jsonify({'Pup': pup[0]})
@app.route('/shop/api/v1.0/pups/<pup_filter>', methods=['GET'])
def get_pup_filtered(pup_filter):
    pup = [pup for pup in pups if (pup['name'].upper()).find(pup_filter.upper())!=-1]
    if len(pup) == 0:
        abort(404)
    return jsonify({'Filtered Pups': pup})
#error response handlers
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error':'Bad Request'}),400)
@app.route('/shop/api/v1.0/pups', methods=['POST'])
@auth.login_required
def create_pup():
    if not request.json or not 'name' in request.json or not 'male-weight' in request.json or not 'female-weight' in request.json:
        abort(400)
    pup = {
        'id': pups[-1]['id'] + 1,
        'name': request.json['name'],
        'male-weight': request.json.get('male-weight'),
        'female-weight': request.json.get('female-weight'),
        'available': request.json.get('available',False)
    }
    pups.append(pup)
    return jsonify({'pup': pup}), 201
@app.route('/shop/api/v1.0/pups/<int:pup_id>', methods=['PUT'])
@auth.login_required
def update_pup(pup_id):
    pup = [pup for pup in pups if pup['id'] == pup_id]
    print(request.json)
    if len(pup) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'available' in request.json and type(request.json['available']) is not bool:
        abort(400)
    pup[0]['name'] = request.json.get('name', pup[0]['name'])
    pup[0]['male-weight'] = request.json.get('male-weight', pup[0]['male-weight'])
    pup[0]['female-weight'] = request.json.get('female-weight', pup[0]['female-weight'])
    pup[0]['available'] = request.json.get('available', pup[0]['available'])
    return jsonify({'Pup': pup[0]})

@app.route('/shop/api/v1.0/pups/<int:pup_id>', methods=['DELETE'])
@auth.login_required
def delete_pup(pup_id):
    pup = [pup for pup in pups if pup['id'] == pup_id]
    if len(pup) == 0:
        abort(404)
    pups.remove(pup[0])
    return jsonify({'result': True})
if __name__ == '__main__':
    app.run(debug=True)