import rsa
from fastapi import APIRouter, UploadFile, Form
from base64 import b64encode, b64decode
from typing import Annotated
from Crypto.Cipher import AES
import secrets
import struct

router_rsa = APIRouter()


def check_key_length(key_size: int):
    if key_size not in [1024, 2048, 3072, 4096]:
        raise ValueError("Key size must be one of the following: 1024, 2048, 3072, 4096 bits.")
    return key_size

@router_rsa.post("/rsa/generate_keys/")
async def generate_rsa_keys(key_size: int = Form(2048)):
    key_size = check_key_length(key_size)
    (public_key, private_key) = rsa.newkeys(key_size)
    public_key_pem = public_key.save_pkcs1(format='PEM')
    private_key_pem = private_key.save_pkcs1(format='PEM')
    return {"message": f"RSA keys of size {key_size} bits generated successfully.",
            "public_key_file": f"{b64encode(public_key_pem)}",
            "private_key_file": f"{b64encode(private_key_pem)}"}
    
@router_rsa.post("/rsa/encrypt/")
async def rsa_encrypt(
    file: UploadFile,
    public_key: UploadFile,
):
    public_key_pem = rsa.PublicKey.load_pkcs1(b64decode(await public_key.read()), format='PEM')
    plaintext = await file.read()

    # RSA 最大可加密长度（PKCS#1 v1.5）
    key_len = public_key_pem.n.bit_length() // 8
    max_rsa_plain = key_len - 11

    # 若明文较小，直接用 RSA 加密（保持原行为）
    if len(plaintext) <= max_rsa_plain:
        ciphertext = rsa.encrypt(plaintext, public_key_pem)
        with open(f"file/encrypted_{file.filename}", "wb") as filea:
            filea.write(ciphertext)
        return {"message": f"File '{file.filename}' encrypted successfully as 'encrypted_{file.filename}'."}

    # 明文过大，使用混合加密：生成对称 AES key，用 AES 加密文件，然后用 RSA 加密 AES 密钥
    sym_key = secrets.token_bytes(32)  # 256-bit AES key
    cipher_aes = AES.new(key=sym_key, mode=AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(plaintext)

    # RSA 加密对称密钥
    rsa_encrypted_key = rsa.encrypt(sym_key, public_key_pem)

    # 输出格式： b'HYB' + 2字节(rsa_key_len) + rsa_encrypted_key + nonce(16) + tag(16) + ciphertext
    out = b'HYB' + struct.pack('>H', len(rsa_encrypted_key)) + rsa_encrypted_key + cipher_aes.nonce + tag + ciphertext
    with open(f"file/encrypted_{file.filename}", "wb") as filea:
        filea.write(out)

    return {"message": f"File '{file.filename}' hybrid-encrypted successfully as 'encrypted_{file.filename}'."}

@router_rsa.post("/rsa/decrypt/")
async def rsa_decrypt(
    file: UploadFile,
    private_key: UploadFile,
):
    private_key_pem = rsa.PrivateKey.load_pkcs1(b64decode(await private_key.read()), format='PEM')
    ciphertext_all = await file.read()

    # 检查是否为混合加密格式
    if ciphertext_all.startswith(b'HYB'):
        idx = 3
        rsa_len = struct.unpack('>H', ciphertext_all[idx:idx+2])[0]
        idx += 2
        rsa_encrypted_key = ciphertext_all[idx:idx + rsa_len]
        idx += rsa_len
        nonce = ciphertext_all[idx:idx+16]
        idx += 16
        tag = ciphertext_all[idx:idx+16]
        idx += 16
        ciphertext = ciphertext_all[idx:]

        # 使用 RSA 解密对称密钥
        sym_key = rsa.decrypt(rsa_encrypted_key, private_key_pem)

        # 使用 AES 解密
        cipher_aes = AES.new(key=sym_key, mode=AES.MODE_EAX, nonce=nonce)
        plaintext = cipher_aes.decrypt_and_verify(ciphertext, tag)
    else:
        # 尝试按原有方式直接 RSA 解密（对小文件）
        try:
            plaintext = rsa.decrypt(ciphertext_all, private_key_pem)
        except Exception as e:
            raise

    with open(f"file/decrypted_{file.filename}", "wb") as filea:
        filea.write(plaintext)
    return {"message": f"File '{file.filename}' decrypted successfully as 'decrypted_{file.filename}'."}