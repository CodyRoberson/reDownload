import json
import requests

import logging
logging.basicConfig( level=logging.INFO)
log = logging.getLogger("docs_py")
log.addHandler(logging.FileHandler("getdocs.log", 'w'))

def grab(path:str):
    req = requests.get("http://10.11.99.1/documents/"+path)
    if req.status_code == 200:
        data = req.json()
        return data
    else:
        log.error("Wasnt't able to grab requested document")
        raise Exception("Wasnt't able to grab requested document")

docs = []
def parse_filetree(lst: list, path:str):
    log.debug(f"parse_filetree: lst = {lst}")
    for i in range(0, len(lst)):
        log.debug(f"for {i} in range 0 to {len(lst)}")
        obj = lst[i]
        id = obj['ID']
        name = obj['VissibleName']
        # parent = obj['Parent']
        dtype = obj['Type']

        
        if dtype == "CollectionType":
            log.debug(f"{name} was a folder!")
            path = path + "/"+ name
            parse_filetree(grab(id+"/"), path)
        else:
            log.debug(f"{name} was a document!")
            docs.append((name, id, path+'/'+name))

def download(thruple: tuple):
    name, id, path = thruple
    log.info(name)
    
    url = f"http://10.11.99.1/download/{id}/rmdoc"
    req = requests.get(url)
    if req.status_code == 200:
        with open(f"{name}.zip", "wb") as file:
            for chunk in req.iter_content(chunk_size=8192):
                file.write(chunk)


def get_docs():
    # Get webinterface-Home
    parse_filetree(grab(""), "")
    
    for x in docs:
        download(x)