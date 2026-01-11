from fastapi import APIRouter, UploadFile, Form
from Crypto.Cipher import AES
import secrets
from typing import  Optional
router_aes = APIRouter()

def check_key_mode(key: str, mode: str):
    if not len(key) in [16, 24, 32]:
        raise ValueError("Key must be either 16, 24, or 32 bytes long.")
    if mode.upper() not in ["EAX", "CBC", "CFB", "OFB", "CTR"]:
        raise ValueError("Invalid mode. Choose from EAX, CBC, CFB, OFB, CTR.")
    return key, mode.upper()

@router_aes.post("/aes/encrypt/")
async def encrypt_file(
    file: UploadFile,
    key: str = Form(...),
    mode: str = Form("EAX"),
    iv: Optional[str] = Form(None),
    nonce: Optional[str] = Form(None),
):
    key, mode = check_key_mode(key, mode)
    key_bytes = key.encode('utf-8')
    plaintext = await file.read()

    # convert hex strings to bytes if provided (use separate variables so types are bytes|None for cipher)
    if isinstance(iv, str):
        iv_bytes = bytes.fromhex(iv)
    else:
        iv_bytes = iv
    if isinstance(nonce, str):
        nonce_bytes = bytes.fromhex(nonce)
    else:
        nonce_bytes = nonce

    if mode == 'EAX':
        if nonce_bytes is None:
            nonce_bytes = secrets.token_bytes(16)
        cipher = AES.new(key=key_bytes, mode=AES.MODE_EAX, nonce=nonce_bytes)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        with open(f"file/encrypted_{file.filename}", "wb") as filea:
            filea.write(cipher.nonce + tag + ciphertext)
    elif mode == 'CBC':
        if iv_bytes is None:
            iv_bytes = secrets.token_bytes(16)
        # PKCS7 padding
        pad_len = 16 - (len(plaintext) % 16)
        padded = plaintext + bytes([pad_len]) * pad_len
        cipher = AES.new(key=key_bytes, mode=AES.MODE_CBC, iv=iv_bytes)
        ciphertext = cipher.encrypt(padded)
        with open(f"file/encrypted_{file.filename}", "wb") as filea:
            filea.write(iv_bytes + ciphertext)
    elif mode in ('CFB', 'OFB'):
        if iv_bytes is None:
            raise ValueError(f"Mode {mode} requires an 'iv' parameter.")
        cipher = AES.new(key=key_bytes, mode=getattr(AES, 'MODE_' + mode), iv=iv_bytes)
        ciphertext = cipher.encrypt(plaintext)
        with open(f"file/encrypted_{file.filename}", "wb") as filea:
            filea.write(iv_bytes + ciphertext)
    elif mode == 'CTR':
        if nonce_bytes is None:
            nonce_bytes = secrets.token_bytes(16)
        cipher = AES.new(key=key_bytes, mode=AES.MODE_CTR, nonce=nonce_bytes)
        ciphertext = cipher.encrypt(plaintext)
        with open(f"file/encrypted_{file.filename}", "wb") as filea:
            filea.write(cipher.nonce + ciphertext)
    else:
        raise ValueError('Unsupported mode')

    return {"message": f"File '{file.filename}' encrypted successfully as 'encrypted_{file.filename}'."}

@router_aes.post("/aes/decrypt/")
async def decrypt_file(
    file: UploadFile,
    key: str = Form(...),
    mode: str = Form("EAX"),
):
    key, mode = check_key_mode(key, mode)
    key_bytes = key.encode('utf-8')
    ciphertext_all = await file.read()

    # If user provided hex iv/nonce, convert

    if mode == 'EAX':
        # expect: nonce(16) + tag(16) + ciphertext
        nonce_in = ciphertext_all[:16]
        tag = ciphertext_all[16:32]
        ciphertext = ciphertext_all[32:]
        cipher = AES.new(key=key_bytes, mode=AES.MODE_EAX, nonce=nonce_in)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    elif mode == 'CBC':
        iv_in = ciphertext_all[:16]
        ciphertext = ciphertext_all[16:]
        cipher = AES.new(key=key_bytes, mode=AES.MODE_CBC, iv=iv_in)
        padded = cipher.decrypt(ciphertext)
        pad_len = padded[-1]
        if pad_len < 1 or pad_len > 16:
            raise ValueError('Invalid padding')
        plaintext = padded[:-pad_len]
    elif mode in ('CFB', 'OFB'):
        iv_in = ciphertext_all[:16]
        ciphertext = ciphertext_all[16:]
        cipher = AES.new(key=key_bytes, mode=getattr(AES, 'MODE_' + mode), iv=iv_in)
        plaintext = cipher.decrypt(ciphertext)
    elif mode == 'CTR':
        nonce_in = ciphertext_all[:16]
        ciphertext = ciphertext_all[16:]
        cipher = AES.new(key=key_bytes, mode=AES.MODE_CTR, nonce=nonce_in)
        plaintext = cipher.decrypt(ciphertext)
    else:
        raise ValueError('Unsupported mode')

    with open(f"file/decrypted_{file.filename}", "wb") as filea:
        filea.write(plaintext)
    return {"message": f"File '{file.filename}' decrypted successfully as 'decrypted_{file.filename}'."}