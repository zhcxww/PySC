from pymongo import MongoClient
import tqdm
client=MongoClient("localhost",27017)
db=client["SC"]
pkg_repo=db['pkg_repo']
pkg_import=db['pkg_import_2']
dependencies=db['dependencies']
name=set()
for i in tqdm.tqdm(dependencies.find(),total=157247908):
    name.add(i['from'])
file=open("project_unique","w")
for n in tqdm.tqdm(sorted(list(name))):
    file.write(n+"\n")
