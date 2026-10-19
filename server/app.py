"""Civic demonstration biometric authority. Not a production election service."""
import base64
import hashlib
import hmac
import io
import os
from pathlib import Path
import re
import secrets
import sqlite3
from contextlib import contextmanager
import time
import numpy as np
from dotenv import load_dotenv
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_abi import encode
from eth_utils import is_address, keccak, to_checksum_address
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
load_dotenv(Path(__file__).with_name('.env'))
BASE = Path(__file__).resolve().parent
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
CORS(app, origins=os.getenv('ALLOWED_ORIGINS','http://localhost:5173,http://127.0.0.1:5173').split(','))
limiter = Limiter(get_remote_address, app=app, default_limits=['60 per minute'], storage_uri=os.getenv('RATE_LIMIT_STORAGE','memory://'))
DB = os.getenv('DATABASE_PATH', str(BASE/'voters.sqlite3'))
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN','')
SIGNER_KEY = os.getenv('VERIFIER_PRIVATE_KEY','')
IDENTITY_SECRET = os.getenv('IDENTITY_SECRET','')
CONTRACT = os.getenv('CONTRACT_ADDRESS','')
CHAIN_ID = int(os.getenv('CHAIN_ID','31337'))
TOLERANCE = .45

DATABASE_URL = os.getenv('DATABASE_URL', '')
if DATABASE_URL:
    import psycopg
    from psycopg.rows import dict_row
    INTEGRITY_ERRORS = (sqlite3.IntegrityError, psycopg.IntegrityError)
else:
    INTEGRITY_ERRORS = (sqlite3.IntegrityError,)

class PostgresConnection:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, sql, params=()):
        if sql == 'BEGIN IMMEDIATE':
            # Serialize enrollment scans and challenge consumption across all
            # processes. Transaction-scoped locks work with pooled connections.
            return self.connection.execute('SELECT pg_advisory_xact_lock(73491821)')
        return self.connection.execute(sql.replace('?', '%s'), params)

@contextmanager
def db():
    if DATABASE_URL:
        with psycopg.connect(DATABASE_URL, row_factory=dict_row, connect_timeout=15) as con:
            yield PostgresConnection(con)
    else:
        con = sqlite3.connect(DB, timeout=10)
        con.row_factory = sqlite3.Row
        try:
            with con:
                yield con
        finally:
            con.close()

# Versioned initial schema is checked in alongside the application. Hosted
# databases are migrated separately; local SQLite initializes for development.
if not DATABASE_URL:
    with db() as con:
        con.executescript('''CREATE TABLE IF NOT EXISTS voters (roll TEXT PRIMARY KEY, wallet TEXT UNIQUE NOT NULL, encoding BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS challenges (nonce TEXT PRIMARY KEY, roll TEXT NOT NULL, wallet TEXT NOT NULL, message TEXT NOT NULL, expires INTEGER NOT NULL);''')

def fail(message, status=400):
    return jsonify(status='error',message=message), status

def payload():
    data = request.get_json(silent=True)
    if not isinstance(data,dict): raise ValueError('Send a JSON object.')
    return data

def voter_fields(data):
    roll = str(data.get('roll_no',''))
    wallet = data.get('wallet','')
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,40}',roll) or not isinstance(wallet,str) or not is_address(wallet):
        raise ValueError('Enter a valid voter ID and Ethereum wallet address.')
    return roll,to_checksum_address(wallet)

def configured():
    return len(ADMIN_TOKEN)>=32 and len(IDENTITY_SECRET)>=32 and bool(SIGNER_KEY) and is_address(CONTRACT)

def decode_frame(value):
    import cv2
    from PIL import Image
    if not isinstance(value,str) or len(value)>700000: raise ValueError('Invalid camera frame.')
    try:
        raw = base64.b64decode(value.split(',')[-1],validate=True)
        with Image.open(io.BytesIO(raw)) as picture:
            if not (100<=picture.width<=1280 and 100<=picture.height<=960):
                raise ValueError('Invalid camera dimensions.')
        frame = cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
        if frame is None: raise ValueError('Invalid image.')
        return cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    except Exception as exc:
        raise ValueError('Unable to decode camera frame.') from exc

def face_sample(value):
    import face_recognition
    image = decode_frame(value)
    locations = face_recognition.face_locations(image)
    if len(locations)!=1: raise ValueError('Exactly one face must be visible in every frame.')
    encodings = face_recognition.face_encodings(image,known_face_locations=locations)
    if len(encodings)!=1: raise ValueError('Unable to encode face. Improve lighting and retry.')
    return encodings[0],face_recognition.face_landmarks(image,face_locations=locations)[0]

def verify_frames(frames,registered):
    if not isinstance(frames,list) or not 8<=len(frames)<=16:
        raise ValueError('Capture between 8 and 16 camera frames.')
    ratios=[]
    for frame in frames:
        encoding,landmarks=face_sample(frame)
        if np.linalg.norm(registered-encoding)>=TOLERANCE:
            raise ValueError('Identity did not match throughout the capture.')
        nose=np.mean(landmarks['nose_tip'],axis=0)
        left=np.mean(landmarks['left_eye'],axis=0)
        right=np.mean(landmarks['right_eye'],axis=0)
        distance=np.linalg.norm(left-right)
        if distance<1: raise ValueError('Face landmarks could not be measured.')
        ratios.append(float((np.linalg.norm(nose-left)-np.linalg.norm(nose-right))/distance))
    if max(ratios)-min(ratios)<.18:
        raise ValueError('Movement not detected. Slowly turn your head during capture.')

@app.errorhandler(ValueError)
def invalid(exc): return fail(str(exc))
@app.errorhandler(413)
def too_large(_): return fail('Camera upload is too large.',413)
@app.errorhandler(429)
def limited(_): return fail('Too many attempts. Wait a minute and try again.',429)
@app.errorhandler(Exception)
def unexpected(exc):
    from werkzeug.exceptions import HTTPException
    if isinstance(exc,HTTPException): return fail(exc.description,exc.code)
    app.logger.exception('Verification service error')
    return fail('Verification service error. Contact the election administrator.',500)
@app.get('/health')
def health(): return jsonify(status='ready' if configured() else 'configuration_required')

@app.post('/register')
@limiter.limit('10 per minute')
def register():
    if len(ADMIN_TOKEN)<32: return fail('Enrollment is not configured.',503)
    if not hmac.compare_digest(request.headers.get('Authorization',''),'Bearer '+ADMIN_TOKEN):
        return fail('Administrator enrollment authorization required.',401)
    data=payload();roll,wallet=voter_fields(data)
    if data.get('consent') is not True: return fail('Biometric enrollment consent is required.')
    encoding,_=face_sample(data.get('image'))
    try:
        with db() as con:
            con.execute('BEGIN IMMEDIATE')
            if con.execute('SELECT 1 FROM voters WHERE roll=? OR wallet=?',(roll,wallet)).fetchone():
                return fail('This voter ID or wallet is already enrolled.',409)
            for row in con.execute('SELECT encoding FROM voters'):
                if np.linalg.norm(np.frombuffer(row['encoding'],dtype=np.float64)-encoding)<TOLERANCE:
                    return fail('This face is already enrolled. Contact the administrator.',409)
            con.execute('INSERT INTO voters VALUES (?,?,?)',(roll,wallet,encoding.astype(np.float64).tobytes()))
    except INTEGRITY_ERRORS: return fail('This voter ID or wallet is already enrolled.',409)
    return jsonify(status='success')

@app.post('/challenge')
@limiter.limit('10 per minute')
def challenge():
    if not configured(): return fail('Verification service configuration is incomplete.',503)
    roll,wallet=voter_fields(payload())
    with db() as con:
        row=con.execute('SELECT wallet FROM voters WHERE roll=?',(roll,)).fetchone()
        if not row or row['wallet']!=wallet: return fail('No matching voter enrollment. Contact your administrator.',403)
        nonce=secrets.token_hex(32);expires=int(time.time())+180
        message=f'Civic identity verification\nWallet: {wallet}\nChain: {CHAIN_ID}\nContract: {CONTRACT}\nNonce: {nonce}\nExpires: {expires}\nThis is not a vote or a transfer.'
        con.execute('DELETE FROM challenges WHERE expires < ?',(int(time.time()),))
        con.execute('INSERT INTO challenges VALUES (?,?,?,?,?)',(nonce,roll,wallet,message,expires))
    return jsonify(nonce=nonce,message=message,expires=expires)

@app.post('/verify')
@limiter.limit('6 per minute')
def verify():
    if not configured(): return fail('Verification service configuration is incomplete.',503)
    data=payload();nonce=data.get('nonce')
    if not isinstance(nonce,str) or not re.fullmatch(r'[0-9a-f]{64}',nonce): return fail('Invalid verification challenge.')
    # Consume challenges atomically, including failed attempts.
    with db() as con:
        con.execute('BEGIN IMMEDIATE')
        row=con.execute('SELECT * FROM challenges WHERE nonce=?',(nonce,)).fetchone()
        con.execute('DELETE FROM challenges WHERE nonce=?',(nonce,))
    if not row or row['expires']<int(time.time()): return fail('Challenge expired or already used. Start verification again.',401)
    try: recovered=Account.recover_message(encode_defunct(text=row['message']),signature=data.get('signature',''))
    except Exception: return fail('Invalid wallet signature.',401)
    if recovered.lower()!=row['wallet'].lower(): return fail('Wallet signature does not match enrollment.',401)
    with db() as con:
        registered=con.execute('SELECT encoding FROM voters WHERE roll=?',(row['roll'],)).fetchone()
    verify_frames(data.get('frames'),np.frombuffer(registered['encoding'],dtype=np.float64))
    identity=hmac.new(IDENTITY_SECRET.encode(),row['roll'].encode(),hashlib.sha256).digest()
    deadline=int(time.time())+300
    digest=keccak(encode(['uint256','address','address','bytes32','uint256'],[CHAIN_ID,to_checksum_address(CONTRACT),row['wallet'],identity,deadline]))
    signature=Account.sign_message(encode_defunct(primitive=digest),private_key=SIGNER_KEY).signature
    return jsonify(status='success',identity='0x'+identity.hex(),deadline=deadline,signature='0x'+signature.hex())

# No client-controlled vote ledger or destructive reset endpoints.
if __name__=='__main__': app.run(host='127.0.0.1',port=5000,debug=False)
