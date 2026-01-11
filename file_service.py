from fastapi import APIRouter
from fastapi.responses import HTMLResponse,FileResponse

router_file = APIRouter()
@router_file.get("/file/")
async def read_root():
    return {"file_name": "Please provide a file name in the URL."}

@router_file.get("/file_src/{ways}/{file_name}")
async def src_file(file_name: str, ways: str):
    return FileResponse(f"src/{ways}/{file_name}", filename=file_name)

@router_file.get("/file_html/{ways}/{file_name}", response_class=HTMLResponse)
async def read_html_file(file_name: str, ways: str):
    return open(f"src/{ways}/{file_name}",encoding="utf-8").read()

@router_file.get("/file/{file_name}")
async def read_file(file_name: str):
    return FileResponse(f"file/{file_name}",media_type='application/octet-stream',filename=file_name)

