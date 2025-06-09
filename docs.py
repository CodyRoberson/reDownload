import requests
import os

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
        parent = obj['Parent']
        dtype = obj['Type']

        
        if dtype == "CollectionType":
            log.debug(f"{name} was a folder!")
            newpath = path + "/"+ name
            log.debug(f"parse_filetree({id + '/' + name}, {newpath})")
            parse_filetree(grab(id+"/"), newpath)
        else:
            log.debug(f"{name} was a document!")
            docs.append((name, id, path+'/',parent))

def download(thruple: tuple):
    name, id, _, _ = thruple
    log.info(name)
    
    os.makedirs("./downloads", exist_ok=True)
    headers = {
        'Accept': "*/*",
        'Accept-Encoding': "gzip,deflate",
        'Accept-Language': "en-US,en;q=0.9"
    }
    url = f"http://10.11.99.1/download/{id}/rmdoc"
    req = requests.get(url, headers=headers)
    if req.status_code == 200:
        with open(f"./downloads/{name}.rmdoc", "wb") as file:
            for chunk in req.iter_content(chunk_size=8192):
                file.write(chunk)

def get_docs():
    # Get webinterface-Home
    parse_filetree(grab(""), "")
    
    log.info(f"\nFound the following files:\n")
    for doc in docs:
        log.info(f"{doc}")

    log.info(f"Downloading...\n")
    for x in docs:
        download(x)
        pass

    log.info("\nWriting metadata")
    with open("./downloads/metainf.txt", 'w') as fh:
        fh.write("name,uuid,folder,parent\n")
        for obj in docs:
            name, id, path, parent = obj
            fh.write(f"{name},{id},{path},{parent}\n")


    log.info("Operation Complete")


if __name__ == "__main__":
    get_docs()

