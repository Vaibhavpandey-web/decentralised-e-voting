import importlib.util
import os
import uuid
from pathlib import Path
import numpy as np
import pytest
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_abi import encode
from eth_utils import keccak
@pytest.fixture
def api(tmp_path,monkeypatch):
    test_url = os.getenv('TEST_DATABASE_URL')
    if test_url:
        from urllib.parse import urlsplit, urlunsplit
        parts = urlsplit(test_url)
        test_url = urlunsplit(parts._replace(netloc=parts.netloc.replace('-pooler.', '.')))

    monkeypatch.delenv('DATABASE_URL', raising=False)
    schema = None
    if test_url:
        import psycopg
        from psycopg.conninfo import make_conninfo
        schema = 'test_' + uuid.uuid4().hex
        with psycopg.connect(test_url) as con:
            con.execute(f'CREATE SCHEMA {schema}')
            con.execute(f'SET search_path TO {schema}')
            con.execute((Path(__file__).parents[1]/'migrations/001_initial.sql').read_text())
        monkeypatch.setenv('DATABASE_URL', make_conninfo(test_url, options=f'-c search_path={schema}'))
    for key,value in {'CHAIN_ID':'31337','DATABASE_PATH':str(tmp_path/'test.sqlite3'),'ADMIN_TOKEN':'a'*40,'IDENTITY_SECRET':'i'*40,'VERIFIER_PRIVATE_KEY':'0x'+'11'*32,'CONTRACT_ADDRESS':'0x'+'22'*20}.items():monkeypatch.setenv(key,value)
    spec=importlib.util.spec_from_file_location('civic_api',Path(__file__).parents[1]/'app.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.app.config['TESTING']=True;module.limiter.enabled=False
    monkeypatch.setattr(module,'face_sample',lambda frame:(np.ones(128),{}))
    try:
        yield module,module.app.test_client()
    finally:
        if schema:
            with psycopg.connect(test_url) as con:
                con.execute(f'DROP SCHEMA {schema} CASCADE')
def enroll(client,voter,roll='CSE001'):
    return client.post('/register',json={'roll_no':roll,'wallet':voter.address,'image':'mock','consent':True},headers={'Authorization':'Bearer '+'a'*40})
def test_enrollment_requires_admin(api):
    _,client=api
    assert client.post('/register',json={}).status_code==401
def test_enrollment_validation_and_duplicates(api):
    _,client=api;voter=Account.create()
    assert enroll(client,voter,'../escape').status_code==400
    assert enroll(client,voter).status_code==200
    assert enroll(client,voter).status_code==409
    assert enroll(client,Account.create(),'OTHER').status_code==409
def test_no_destructive_or_client_ledger_routes(api):
    _,client=api
    for route in ['/wipe_data','/clear_data','/resetElection','/mark_voted']:assert client.post(route,json={}).status_code==404
def test_wallet_bound_signed_permit_and_single_use_challenge(api,monkeypatch):
    module,client=api;voter=Account.create();assert enroll(client,voter).status_code==200
    challenge=client.post('/challenge',json={'roll_no':'CSE001','wallet':voter.address}).get_json()
    monkeypatch.setattr(module,'verify_frames',lambda frames,registered:None)
    signature='0x'+voter.sign_message(encode_defunct(text=challenge['message'])).signature.hex()
    body={'nonce':challenge['nonce'],'signature':signature,'frames':[]}
    response=client.post('/verify',json=body);assert response.status_code==200
    permit=response.get_json();digest=keccak(encode(['uint256','address','address','bytes32','uint256'],[31337,module.CONTRACT,voter.address,bytes.fromhex(permit['identity'][2:]),permit['deadline']]))
    assert Account.recover_message(encode_defunct(primitive=digest),signature=permit['signature'])==Account.from_key(module.SIGNER_KEY).address
    assert client.post('/verify',json=body).status_code==401
def test_wrong_wallet_and_expired_challenge(api):
    module,client=api;voter=Account.create();enroll(client,voter)
    assert client.post('/challenge',json={'roll_no':'CSE001','wallet':Account.create().address}).status_code==403
    challenge=client.post('/challenge',json={'roll_no':'CSE001','wallet':voter.address}).get_json();signature='0x'+Account.create().sign_message(encode_defunct(text=challenge['message'])).signature.hex()
    assert client.post('/verify',json={'nonce':challenge['nonce'],'signature':signature}).status_code==401
    challenge=client.post('/challenge',json={'roll_no':'CSE001','wallet':voter.address}).get_json()
    with module.db() as con:con.execute('UPDATE challenges SET expires=0')
    assert client.post('/verify',json={'nonce':challenge['nonce']}).status_code==401
def test_movement_check_matches_each_frame(api,monkeypatch):
    module,_=api
    def sample(frame):return np.ones(128),{'nose_tip':[(5+frame/10,5)],'left_eye':[(0,0)],'right_eye':[(10,0)]}
    monkeypatch.setattr(module,'face_sample',sample)
    with pytest.raises(ValueError,match='Movement'):module.verify_frames([0]*8,np.ones(128))
    module.verify_frames([0,10,20,30,40,30,20,10],np.ones(128))
    monkeypatch.setattr(module,'face_sample',lambda _:(np.zeros(128),{}))
    with pytest.raises(ValueError,match='Identity'):module.verify_frames([0]*8,np.ones(128))
