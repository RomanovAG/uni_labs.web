from flask import Flask, request, jsonify, g
from flask_cors import CORS
from functools import wraps
import jwt
import sqlite3
import hashlib
import hmac
import os

ROLE_ADMIN  = 0
ROLE_CLIENT = 1

ADMIN_DEFAULT = {
    'id': 0,
    'email': 'admin@gmail.com',
    'hash': 0x6bd735c628c8fba78817f00ac4ce2ab4c1f98e589668023980350f8660cecbe7, # 123
    'role': ROLE_ADMIN
}
USER_DEFAULT = {
    'id': 100,
    'email': 'client@gmail.com',
    'hash': 0x6b1dbfdd5d5fc6ebc299ea1f2b820b7e48444252ecf8f4511d995289fb7842a9, # qwe
    'password': 'qwe',
    'role': ROLE_CLIENT,
    'name': 'Вася',
    'storeName': 'Пятёрочка'
}

DB_REL_PATH = '../database/db.db'
DB_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), DB_REL_PATH)

app = Flask(__name__)
app.config['SECRET_KEY'] = b'577dc65e3d182756827f1dcdd3db7cdfa70badddd4146e103f45e6d40aac9e36'
CORS(app)

def update_sqlite_sequence():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("SELECT name FROM sqlite_sequence")
    tables = cur.fetchall()

    for table in tables:
        table_name = table[0]
        cur.execute(f"UPDATE sqlite_sequence SET seq = (SELECT IFNULL(MAX(id), 0) FROM {table_name}) WHERE name = ?", (table_name,))

    con.commit()
    con.close()

def db_user_to_front(l: list) -> dict:
    if len(l) < 6:
        raise ValueError
    tmp = {
        'id': int(l[0]),
        # 'is_active': int(l[1]),
        'email': l[2],
        #'hash': int.from_bytes(l[3], 'big'),
        'role': 'admin' if l[4] == ROLE_ADMIN else 'client',
        'name': l[5]
    }
    return tmp

def db_mall_to_front(db_mall: list) -> dict:
    if len(db_mall) < 4:
        raise ValueError
    mall = {
        'id': int(db_mall[0]),
        'name': str(db_mall[1]),
        'floorsCount': int(db_mall[2]),
        'undergroundFloorsCount': int(db_mall[3]),
    }
    return mall

class EscapeAll(bytes):
    def __str__(self):
        return 'b\'{}\''.format(''.join('\\x{:02x}'.format(b) for b in self))
    
def check_jwt_token(auth_header: str) -> int:
    ''' Returns user_id if token is correct '''
    if auth_header is None:
        raise ValueError('auth header is none')
    if 'Bearer ' not in auth_header:
        raise ValueError('bad token form')
    
    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(jwt=token, key=app.config['SECRET_KEY'], algorithms=['HS256'])
        return int(payload['sub'])
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError

def generate_response_on_token(auth_header: str):
    try:
        return check_jwt_token(auth_header)
    except ValueError:
        return jsonify({'error': 'Token missing!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token!'}), 403

def check_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            auth_header = request.get_json().get('headers').get('Authorization')
        # app.logger.info(request)
 
        resp = generate_response_on_token(auth_header)
        if not isinstance(resp, int):
            return resp 
        
        g.user_id = resp
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/<string:user_role>s/<int:user_id>/data', methods=['GET'])
@check_auth
def get_user_data(user_role: str, user_id: int):
    if user_id != g.user_id and is_admin(g.user_id) == False:
        return jsonify({'error': 'Forbidden access (wrong account)'}), 403
    
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    db_user = cursor.fetchone()
    if not db_user:
        return jsonify({'error': 'No such user'}), 404
    user = db_user_to_front(db_user)
    return jsonify(user)
    
    cursor.execute('SELECT * FROM stores WHERE owner_id = ?', (user_id,))
    db_stores = cursor.fetchall()
    con.close()
    
    stores = []
    for store in db_stores:
        stores.append(db_store_to_front(store))
    return jsonify({'client': user, 'stores': stores})

@app.route('/api/malls', methods=['GET'])
@check_auth
def get_malls_list():
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM malls')
    db_malls = cursor.fetchall()

    malls = []
    for db_mall in db_malls:
        malls.append(db_mall_to_front(db_mall))
    return jsonify(malls)

@app.route('/api/request-create', methods=['POST'])
@check_auth
def create_request():
    data = request.get_json()
    topic = data['r']['topic']
    store = data.get('store')

    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    if topic == 'Запрос на выделение датчиков':
        quantity = data.get('quantity')
        cursor.execute('INSERT INTO requests (author_id, topic, quantity) VALUES (?, ?, ?)', (g.user_id, 1, quantity))
    elif topic == 'Запрос на обслуживание':
        description = data.get('description')
        cursor.execute('INSERT INTO requests (author_id, topic, description) VALUES (?, ?, ?)', (g.user_id, 2, description))
    elif topic == 'Общие вопросы':
        question = data.get('question')
        cursor.execute('INSERT INTO requests (author_id, topic, question) VALUES (?, ?, ?)', (g.user_id, 3, question))
    else:
        return jsonify({'error': 'Invalid topic'}), 403
    con.commit()
    con.close()
    return jsonify({'message': 'done'})

def is_admin(user_id: int) -> bool:
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    db_user = cursor.fetchone()
    con.close()
    if not db_user:
        raise ValueError
    user = db_user_to_front(db_user)
    return True if user['role'] == 'admin' else False

@app.route('/api/malls/<int:mall_id>/data', methods=['GET'])
@check_auth
def get_mall_data(mall_id: int):
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM malls WHERE mall_id = ?', (mall_id,))
    db_mall = cursor.fetchone()
    # user_id = int(request.args.get('id'))
    if not db_mall:
        con.close()
        return jsonify({'error': 'No mall info!'}), 404
    mall = db_mall_to_front(db_mall)

    cursor.execute('SELECT * FROM sensor_in_mall WHERE mall_id = ?', (mall_id,))
    db_sensors_in_mall = cursor.fetchall()

    sensors_in_mall = []
    for db_sensor_in_mall in db_sensors_in_mall:
        sensor_id = int(db_sensor_in_mall[1])
        cursor.execute('SELECT * FROM sensors WHERE sensor_id = ?', (sensor_id,))
        db_sensor = cursor.fetchone()

        cursor.execute('SELECT * FROM sensor_of_user WHERE user_id = ? AND sensor_id = ?', (g.user_id, sensor_id))
        accessible = cursor.fetchone() is not None
        sensor_in_mall = {
            'x': int(db_sensor_in_mall[3]),
            'y': int(db_sensor_in_mall[4]),
            'floor': int(db_sensor_in_mall[5]),
            'mac': db_sensor[1],
            'state': int(db_sensor[2]),
            'accessible': int(accessible),
        }
        sensors_in_mall.append(sensor_in_mall)
    con.close()
    return jsonify({ 'mall': mall, 'sensors': sensors_in_mall})

@app.route('/api/malls/<int:mall_id>/save', methods=['POST'])
@check_auth
def set_mall_data(mall_id: int):
    data = request.get_json()
    sensors = data['sensors']
    app.logger.info(sensors)
    #con = sqlite3.connect(DB_PATH)
    #cursor = con.cursor()
    return jsonify({'message': 'done'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    computed_hash = hmac.new(key=app.config['SECRET_KEY'], msg=str(email + ':' + password).encode(), digestmod=hashlib.sha256).hexdigest()
    blob_hash = bytes.fromhex(computed_hash)
    # app.logger.info(EscapeAll(blob_hash))

    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users WHERE hash = ?', (blob_hash,))
    result = cursor.fetchone()
    con.close()

    if not result:
        return jsonify({'error': 'Неверные учётные данные'}), 401
    if result[1] == 0: # is_active
        return jsonify({'error': 'Неверные учётные данные'}), 401
    
    user = db_user_to_front(result)
    token = jwt.encode(payload={'sub': user['id']}, key=app.config['SECRET_KEY'], algorithm='HS256')
    app.logger.info(user)
    return jsonify({'user': user, 'token': token})

@app.route('/api/register-create', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    store_name = data.get('storeName')

    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    u = cursor.fetchone()
    if u:
        return jsonify({'error': 'Клиент с таким почтовым адресом уже существует'}), 401

    computed_hash = hmac.new(key=app.config['SECRET_KEY'], msg=str(email + ':' + password).encode(), digestmod=hashlib.sha256).hexdigest()
    blob_hash = bytes.fromhex(computed_hash)

    cursor.execute('INSERT INTO users (is_active, email, hash, role, name) VALUES (?, ?, ?, ?, ?)', (0, email, blob_hash, ROLE_CLIENT, name))
    cursor.execute('SELECT user_id FROM users WHERE email = ?', (email,))
    user_id = cursor.fetchone()[0]
    cursor.execute('INSERT INTO stores (owner_id, store_name) VALUES (?, ?)', (user_id, store_name))
    con.commit()
    con.close()

    return jsonify({'status': 'Запрос на регистрацию отправлен'}), 201

@app.route('/api/pending-users', methods=['GET'])
@check_auth
def get_pending_users():
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users WHERE is_active = 0')
    results = cursor.fetchall()
    con.close()

    pending_users = []
    for res in results:
        tmp = db_user_to_front(res)
        pending_users.append(tmp)
    return jsonify(pending_users)

@app.route('/api/register-approve', methods=['POST'])
@check_auth
def approve_user():
    data = request.json
    email = data.get('email')

    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute('UPDATE users SET is_active = 1 WHERE email = ?', (email,))
    con.commit()
    con.close()
    return jsonify({'message': 'done'})

@app.route('/api/register-reject', methods=['POST'])
@check_auth
def reject_user():
    data = request.json
    email = data.get('email')
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute('SELECT user_id FROM users WHERE email = ?', (email,))
    p = cursor.fetchone()
    if not p:
        con.close()
        return jsonify({'error': 'Клиент не найден'}), 404
    
    user_id = p[0];    
    cursor.execute('DELETE FROM users  WHERE user_id  = ?', (user_id,))
    cursor.execute('DELETE FROM stores WHERE owner_id = ?', (user_id,))
    con.commit()
    con.close()
    update_sqlite_sequence()
    return jsonify({'message': 'done'})

def main():
    # app.run(host='192.168.90.203', debug=True)
    # app.run(host='192.168.88.137', debug=True)
    app.run(debug=True)

if __name__ == '__main__':
    main()
