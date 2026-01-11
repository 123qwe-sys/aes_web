from fastapi import FastAPI
from encrypt.aes import router_aes,encrypt_file
from file_service import router_file,read_file,read_html_file,src_file
from encrypt.rsa import router_rsa,rsa_encrypt,rsa_decrypt,generate_rsa_keys
import cleaner

cleaner.clean_temp_files()
app=FastAPI()
app.include_router(router_aes)
app.include_router(router_file)
app.include_router(router_rsa)

