from flask import render_template
from flask import request
from app import app
from app.generate_sc import generate_sc
from app.evolution import get_layer_evolution
from app.network_analysis import get_net_metrics
import io
import base64
import json
from pymongo import MongoClient

client=MongoClient("localhost",27017)
db=client["SC"]
init=db['init_net']
pkg_import=db['pkg_import_2']
sc_tree=db["sc_tree"]

def get_net(time):
    x=init.find_one({"flag":2})
    
    return {"nodes":x["nodes"],"edges":x["edges"]}

def is_pkg(pkgname):
    if pkgname =="":
        return {"r":0}
    else:
        if pkg_import.find_one({"pkg":pkgname}):
            return {"r":1}
    return {"r":0}
# 主页面
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/pynet', methods=["POST"])
def net():
    time = request.json.get("time")
    res = get_net(time)
    return res
@app.route('/ispkg',methods=['POST'])
def ispkg():
    pkg = request.json.get("pkg")
    res= is_pkg(pkg)
    return res

@app.route('/gettree',methods=['POST'])
def get_tree():
    pkg = request.json.get("pkg")
    time=request.json.get("time")
    evolution=get_layer_evolution(pkg)
    net_res=get_net_metrics(pkg,time)
    if sc_tree.find_one({"pkg":pkg,"time":time}):
        res = sc_tree.find_one({"pkg":pkg,"time":time})
        return {"pkg":res["pkg"],"time":res["time"],"tree":res["tree"],"package_number":res["package_number"],"project_number":res["project_number"],"layer":res["layer"],"degree":res["degree"],"max_layer":res["max_layer"],"evolution":evolution,"between_degree":net_res["between_degree"],"indegree_pagerank":net_res["indegree_pagerank"]}
    else:
        supplychain=generate_sc(pkg,time) 
        supplychain.get_parents()
        supplychain.get_node_main_parent_and_layer()
        tree=supplychain.generate_tree()
        layer_number=supplychain.get_layer_number()
        degree=supplychain.get_degree()
        sc_tree.insert_one({"pkg":pkg,"time":time,"tree":tree,"package_number":len(supplychain.node_index),"project_number":len(supplychain.project),"layer":layer_number,"degree":degree,"max_layer":supplychain.max_layer})
        return {"pkg":pkg,"time":time,"tree":tree,"package_number":len(supplychain.node_index),"project_number":len(supplychain.project),"layer":layer_number,"degree":degree,"max_layer":supplychain.max_layer,"evolution":evolution,"between_degree":net_res["between_degree"],"indegree_pagerank":net_res["indegree_pagerank"]}