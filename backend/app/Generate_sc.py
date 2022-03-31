from pymongo import MongoClient
import numpy
import logging
from joblib import Parallel, delayed
import tqdm
from typing import Any, Dict, Generator, Iterable, Iterator, List, Tuple, TypeVar
import pickle
import os


T = TypeVar('T')
def chunks(lst: Iterable[T], n: int) -> Generator[List[T], None, None]:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

logging.basicConfig(
    filename=f"/data/xww/SC/Python-SC/web/flask-vue-word-cloud/backend/app/logging/backend.log",
    filemode='a',
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)
class sc:
    def __init__(self):
        self.node_lst=[]
        self.node_index={}
        self.head=None
        self.max_layer=0
        self.project=set()
        
    #@profile
    def get_parents(self):
        for node in self.node_lst:
            for c in node.children:
                self.node_lst[self.node_index[c[0]]].parents.append((node.name,c[1]))
        
        self.head.parents=[]

    #@profile
    def get_node_main_parent_and_layer(self,timestamp:str="1648121399"):
        
        for node in self.node_lst:
            if node.isroot:
                continue
            for p in node.parents:
                if p[1] == node.import_time:
                    node.main_parent=p[0]
                    self.node_lst[self.node_index[p[0]]].main_children.append(node.name)
                    break
        def  _layer(node):         
            for c in node.main_children:
                self.node_lst[self.node_index[c]].layer=node.layer+1
                _layer(self.node_lst[self.node_index[c]])
        
        _layer(self.head)



    def get_layer_number(self):
        dic={}
        for node in self.node_lst:
            dic[node.layer]=dic.get(node.layer,0)+1
        lst=[]
        self.max_layer=max(dic.keys())
        for i in sorted(dic.items(),key=lambda e:e[0]):
            lst.append({"layer":i[0],"number":i[1]})
        return lst

    def get_degree(self):
        lst=[]
        for node in self.node_lst:
            lst.append([len(node.parents),node.indegree,node.layer,node.name])#出度，入度，层数
        return lst
    #@profile
    def _tree(self,tree):
        node=self.node_lst[self.node_index[tree["name"]]]
        for i in node.main_children:
            dic1={"name":i,"import_time":self.node_lst[self.node_index[i]].import_time,"children":[]}
            tree["children"].append(dic1)
            self._tree(dic1)
    #@profile
    def generate_tree(self):
        tree={}
        root=self.head
        tree["name"]=root.name
        tree["import_time"]=root.import_time
        tree["children"]=[]
        self._tree(tree)
        return tree

class sc_node:
    #@profile
    def __init__(self,pkg,pkg_repo,pkg_import):
        self.import_time=""
        self.indegree=0
        self.isroot=False
        self.parents=[]
        self.children=[]
        self.main_parent=""
        self.main_children=[]
        self.name=pkg
        self.layer=-1
        self.repo=pkg_repo.find_one({"pkg":pkg})["repo"]
        self.import_name=pkg_import.find_one({"pkg":pkg})["import_name"]
    #@profile
    def get_children(self,dependencies,pkg_repo,project):
        count=0
        self.indegree=0
        logging.info(f"searhing {self.name} dependents")
        print(f"searhing {self.name} dependents")
        if self.import_name not in ['app', 'to', 'mxnet', 'paddle', 'all']:
            for i in dependencies.find({"to":self.import_name}):
                if i["timestamp"] > self.import_time:
                    count+=1
                    self.indegree+=1
                    project.add(i["from"])
                    res=pkg_repo.find_one({"repo":i["from"]})
                    if res:
                        pkg=res["pkg"]
                        if pkg != self.name:
                            self.children.append((str(pkg),str(i["timestamp"])))  # only append downstream packages
        logging.info(f"find {self.name} {count} dependents")
        print(f"find {self.name} {count} dependents")

#@profile 
def generate_sc(pkg):
    client=MongoClient("localhost",27017)
    db=client["SC"]
    pkg_repo=db['pkg_repo']
    pkg_import=db['pkg_import_2']
    dependencies=db['dependencies']
    pkg_sc=sc()
    root=sc_node(pkg,pkg_repo,pkg_import)
    root.isroot=True
    root.layer=0
    root.import_time="0"
    pkg_sc.head=root
    pkg_sc.node_lst.append(root)
    pkg_sc.node_index[root.name]=0
 
    def append_c(children_lst,project):
        for c in children_lst:
            if pkg_sc.node_index.get(c[0],-1) == -1:
                x=sc_node(c[0],pkg_repo,pkg_import)
                x.import_time=c[1]
                pkg_sc.node_lst.append(x)
                pkg_sc.node_index[c[0]]=len(pkg_sc.node_lst)-1
            else:
                if c[1] >= pkg_sc.node_lst[pkg_sc.node_index[c[0]]].import_time:#当前依赖 是晚于 当前导入时间的 不变
                    pass
                else:
                    pkg_sc.node_lst[pkg_sc.node_index[c[0]]].import_time = c[1]
                    pkg_sc.node_lst[pkg_sc.node_index[c[0]]].get_children(dependencies,pkg_repo,project)
                    append_c(pkg_sc.node_lst[pkg_sc.node_index[c[0]]].children,project)

    for node in pkg_sc.node_lst:
        node.get_children(dependencies,pkg_repo,pkg_sc.project)
        append_c(node.children,pkg_sc.project)

    return pkg_sc

#@profile
def main():
    client=MongoClient("localhost",27017)
    db=client["SC"]
    sc_tree=db["sc_tree"]
    pkg="torch"
    time="1648121399"
    if sc_tree.find_one({"pkg":pkg,"time":time}):
        pass
    else:
        if os.path.exists(f"{pkg}.pkl"):
            with open (f"{pkg}.pkl", 'rb') as f: 
                supplychain=pickle.load(f)
        else:    
            supplychain=generate_sc(pkg)
            with open (f"{pkg}.pkl", 'wb') as f: 
                pickle.dump(supplychain, f)
        supplychain.get_parents()

        supplychain.get_node_main_parent_and_layer()
        tree=supplychain.generate_tree()
        layer_number=supplychain.get_layer_number()
        degree=supplychain.get_degree()
        sc_tree.insert_one({"pkg":pkg,"time":time,"tree":tree,"package_number":len(supplychain.node_index),"project_number":len(supplychain.project)+1,"layer":layer_number,"degree":degree,"max_layer":supplychain.max_layer})
        print(tree)

if __name__ == "__main__":
    main()

