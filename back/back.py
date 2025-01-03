from flask import Flask, request, jsonify, g
from flask_cors import CORS
from functools import wraps
import jwt
import sqlite3
import hashlib
import hmac
import os
import re

import datetime
from collections import defaultdict

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

MAC_REGEX = r'^([0-9a-fA-F]{2}[:]){5}([0-9a-fA-F]{2})$'

LOGS_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'input.txt')

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

        cur.execute(f"PRAGMA table_info({table_name})")
        columns = cur.fetchall()
        if columns:
            first_column_name = columns[0][1]

        cur.execute(f"UPDATE sqlite_sequence SET seq = (SELECT IFNULL(MAX({first_column_name}), 0) FROM {table_name}) WHERE name = ?", (table_name,))

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
        if not db_sensor:
            continue

        cursor.execute('SELECT * FROM sensor_of_user WHERE user_id = ? AND sensor_id = ?', (g.user_id, sensor_id))
        accessible = cursor.fetchone() is not None
        cursor.execute('SELECT * FROM requests WHERE author_id = ? AND sensor_mac = ?', (g.user_id, db_sensor[1]))
        request_created = cursor.fetchone() is not None
        sensor_in_mall = {
            'x': int(db_sensor_in_mall[3]),
            'y': int(db_sensor_in_mall[4]),
            'floor': int(db_sensor_in_mall[5]),
            'mac': db_sensor[1],
            'state': int(db_sensor[2]),
            'accessible': int(accessible),
            'requestCreated': int(request_created),
        }
        sensors_in_mall.append(sensor_in_mall)
    con.close()
    return jsonify({ 'mall': mall, 'sensors': sensors_in_mall})

@app.route('/api/malls/<int:mall_id>/save', methods=['POST'])
@check_auth
def set_mall_data(mall_id: int):
    if not is_admin(g.user_id):
        return jsonify({'error': 'not an admin'}), 403
    data = request.get_json()
    sensors = data['sensors']

    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute('DELETE FROM sensor_in_mall WHERE mall_id = ?', (mall_id,))
    con.commit()
    con.close()
    update_sqlite_sequence()

    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    for sensor_front in sensors:
        if re.match(MAC_REGEX, sensor_front['mac']) is None:
            continue
        cursor.execute('SELECT * FROM sensors WHERE mac = ?', (sensor_front['mac'],))
        sensor = cursor.fetchone()
        if not sensor:
            cursor.execute('INSERT INTO sensors (mac, state) VALUES (?, ?)', (sensor_front['mac'], sensor_front['state']))
            cursor.execute('SELECT * FROM sensors WHERE mac = ?', (sensor_front['mac'],))
            sensor = cursor.fetchone()
        else:
            cursor.execute('UPDATE sensors SET state = ? WHERE mac = ?', (sensor_front['state'], sensor_front['mac']))

        cursor.execute('INSERT INTO sensor_in_mall (sensor_id, mall_id, x, y, floor, date_start, date_end) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       (int(sensor[0]), int(mall_id), int(sensor_front['x']), int(sensor_front['y']), int(sensor_front['floor']), '-', '-'))

    con.commit()
    con.close()
    return jsonify({'message': 'done'})

def parse_file(file_path):
    """ Парсит входной файл и возвращает список записей. """
    records = []
    current_ap = None
    current_time = None

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            if line.startswith("AP:"):
                current_ap = line.split()[1]
            elif len(line.split()) == 2 and ":" in line.split()[1]:
                try:
                    current_time = datetime.datetime.strptime(line, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    print(f"Ошибка преобразования времени: {line}")
            else:
                # Предполагаем, что это MAC клиента и RSSI
                try:
                    client_mac, rssi = line.split()
                    records.append((current_time, current_ap, client_mac, int(rssi)))
                except ValueError:
                    print(f"Ошибка обработки строки: {line} (AP: {current_ap}, Time: {current_time})")

    return records

def transform_records(records):
    """ Преобразует записи в необходимую структуру. """
    delta_time = datetime.timedelta(seconds=240)
    transformed = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    start_time = records[0][0]
    for timestamp, radar_mac, client_mac, rssi in records:
        if timestamp - start_time > delta_time:
            start_time = timestamp

        transformed[start_time][client_mac][radar_mac].append(rssi)

    return transformed

def write_output(transformed):
    список = []
    for timestamp, clients in transformed.items():
        unit = {}
        unit['timestamp'] = timestamp
        unit['devices'] = []

        for client, radars in clients.items():
            device = {}
            device['mac'] = client
            device['sensors'] = []

            for radar_mac, rssi_list in radars.items():
                avg_rssi = sum(rssi_list) // len(rssi_list) # Средний RSSI
                sensor = {}
                sensor['mac'] = radar_mac
                sensor['rssi'] = avg_rssi
                device['sensors'].append(sensor)
            device['sensors'] = sorted(device['sensors'], key=lambda sensor: -sensor['rssi'])[:3]
            max_rssi = max(sensor['rssi'] for sensor in device['sensors'])
            for sensor in device['sensors']:
                if sensor['rssi'] == 0:
                    sensor['normalized_rssi'] = 1
                else:
                    sensor['normalized_rssi'] = abs(max_rssi / sensor['rssi'])**2
            unit['devices'].append(device)
        список.append(unit)
    return список

@app.route('/api/malls/<int:mall_id>/devices', methods=['GET'])
@check_auth
def get_detected_devices(mall_id: int):
    records = parse_file(LOGS_FILE)
    transformed = transform_records(records)
    output = write_output(transformed)
    # app.logger.info()
    return jsonify(output) 

@app.route('/api/sensors/<string:sensor_mac>/request-create', methods=['POST'])
@check_auth
def create_sensor_request(sensor_mac: str):
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    if re.match(MAC_REGEX, sensor_mac) is None:
        con.close()
        return jsonify({'error': 'No mac provided'}), 403
    cursor.execute('INSERT INTO requests (author_id, sensor_mac) VALUES (?, ?)', (g.user_id, sensor_mac))
    con.commit()
    con.close()
    return jsonify({'status': 'Запрос создан'}), 201

@app.route('/api/sensors/<string:sensor_mac>/request-approve', methods=['POST'])
@check_auth
def approve_sensor_request(sensor_mac: str):
    data = request.json
    email = data.get('email')
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    if re.match(MAC_REGEX, sensor_mac) is None:
        con.close()
        return jsonify({'error': 'No mac provided'}), 403
    
    cursor.execute('SELECT sensor_id FROM sensors WHERE mac = ?', (sensor_mac,))
    sensor_id = cursor.fetchone()
    cursor.execute('SELECT user_id FROM users WHERE email = ?', (email,))
    user_id = cursor.fetchone()
    if not sensor_id or not user_id:
        con.close()
        return jsonify({'error': 'Wrong sensor_id or user_id'}), 404
    
    cursor.execute('INSERT INTO sensor_of_user VALUES (?, ?)', (sensor_id[0], user_id[0]))
    cursor.execute(f'DELETE FROM requests WHERE author_id = ? AND sensor_mac = ?', (user_id[0], sensor_mac))
    con.commit()
    con.close()
    return jsonify({'status': 'Одобрено'}), 201

@app.route('/api/sensors/<string:sensor_mac>/request-reject', methods=['POST'])
@check_auth
def reject_sensor_request(sensor_mac: str):
    data = request.json
    email = data.get('email')
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    if re.match(MAC_REGEX, sensor_mac) is None:
        con.close()
        return jsonify({'error': 'No mac provided'}), 403
    
    cursor.execute('SELECT sensor_id FROM sensors WHERE mac = ?', (sensor_mac,))
    sensor_id = cursor.fetchone()
    cursor.execute('SELECT user_id FROM users WHERE email = ?', (email,))
    user_id = cursor.fetchone()
    if not sensor_id or not user_id:
        con.close()
        return jsonify({'error': 'Wrong sensor_id or user_id'}), 404

    cursor.execute(f'DELETE FROM requests WHERE author_id = ? AND sensor_mac = ?', (user_id[0], sensor_mac))
    con.commit()
    con.close()
    return jsonify({'status': 'Одобрено'}), 201

@app.route('/api/sensors/requests', methods=['GET'])
@check_auth
def get_sensor_requests():
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM requests')
    results = cursor.fetchall()

    requests = []
    for res in results:
        cursor.execute('SELECT email, name FROM users WHERE user_id = ?', (res[1],))
        user = cursor.fetchone()
        if not user:
            continue
        tmp = {
            'author_name': user[1],
            'author_email': user[0],
            'sensor_mac': res[2]
        }
        requests.append(tmp)

    con.close()
    return jsonify(requests)

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

    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    u = cursor.fetchone()
    if u:
        con.close()
        return jsonify({'error': 'Клиент с таким почтовым адресом уже существует'}), 401

    computed_hash = hmac.new(key=app.config['SECRET_KEY'], msg=str(email + ':' + password).encode(), digestmod=hashlib.sha256).hexdigest()
    blob_hash = bytes.fromhex(computed_hash)

    cursor.execute('INSERT INTO users (is_active, email, hash, role, name) VALUES (?, ?, ?, ?, ?)', (0, email, blob_hash, ROLE_CLIENT, name))

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
    host = '192.168.90.203'
    local = True

    if local:
        app.run(debug=True)
    else:
        app.run(host=host, debug=True)

if __name__ == '__main__':
    main()
