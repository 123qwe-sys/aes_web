from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse,FileResponse
from Crypto.Cipher import AES
import random
from typing import Any

def check_key_mode(key: str, mode: str,kwargs:dict):
    if not len(key) in [16, 24, 32]:
        raise ValueError("Key must be either 16, 24, or 32 bytes long.")
    if mode.upper() not in ["EAX", "CBC", "CFB", "OFB", "CTR"]:
        raise ValueError("Invalid mode. Choose from EAX, CBC, CFB, OFB, CTR.")
    if mode.upper() == "CTR" and "nonce" not in kwargs:
        kwargs["nonce"] = b''  # CTR mode requires a nonce; using empty bytes as default
    if mode.upper() in ["CBC", "CFB", "OFB"] and "iv" not in kwargs:
        raise ValueError(f"Mode {mode} requires an 'iv' parameter.")
    if mode.upper() == "EAX" and "nonce" not in kwargs:
        kwargs["nonce"] = random.randbytes(16)  # EAX mode requires a nonce
    return key, mode

app=FastAPI()

@app.get("/file/")
async def read_root():
    return {"file_name": "Please provide a file name in the URL."}


@app.get("/file_html/{file_name}", response_class=HTMLResponse)
async def read_html_file(file_name: str):
    return open(f"src/{file_name}",encoding="utf-8").read()

@app.get("/file/{file_name}")
async def read_file(file_name: str):
    return FileResponse(f"file/{file_name}",media_type='application/octet-stream',filename=file_name)

@app.post("/encrypt_file/")
async def encrypt_file(file: UploadFile, key: str,mode: str="EAX",iv: Any=None, nonce: Any=None):
    kwargs = {"iv": iv, "nonce": nonce}
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    key, mode = check_key_mode(key, mode,kwargs)
    cipher = AES.new(key=key.encode('utf-8'), mode=getattr(AES, "MODE_" + mode.upper()),**kwargs)
    plaintext = await file.read()
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    with open(f"file/encrypted_{file.filename}", "wb") as filea:
        [ filea.write(x) for x in (cipher.nonce, tag, ciphertext) ]
    return {"message": f"File '{file.filename}' encrypted successfully as 'encrypted_{file.filename}'."}