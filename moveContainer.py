#!/usr/bin/env python
#
from cvprac.cvp_client import CvpClient
from cvprac.cvp_api import CvpApi
import urllib3
import ssl
import argparse
from getpass import getpass
from treelib import Node, Tree

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

parser = argparse.ArgumentParser()
parser.add_argument('--username', required=True)
parser.add_argument('--cvpIP', required=True)
parser.add_argument('--containertobemoved', required=True)
parser.add_argument('--targetcontainer', required=True)
parser.add_argument('--suffixremove', required=True)

args = parser.parse_args()
switchuser = args.username
cvpIP = args.cvpIP
switchpass = getpass()
containertobemoved = args.containertobemoved
targetcontainer = args.targetcontainer
suffixremove = args.suffixremove

clnt = CvpClient()
clnt.connect([cvpIP], switchuser, switchpass)
clntapi = CvpApi(clnt)
app_name=""

getContainers = clntapi.get_containers()["data"]

tree = Tree()
tree.create_node("Tenant","Tenant") #root

for container in getContainers:
    containername = container["name"]
    parentName = container["parentName"]
    parentId = container["parentId"]
    if containername != "Tenant":
        if tree.contains(parentName):
            if tree.contains(containername) is False:
                tree.create_node(containername,containername,parent=parentName)
        else:
            getcontainerbyid = clntapi.get_container_by_id(parentId)
            parent_parentname= getcontainerbyid["parentName"]
            tree.create_node(parentName,parentName,parent=parent_parentname)
            tree.create_node(containername,containername,parent=parentName)       
    if containername == targetcontainer:
        targetcontainerkey = container["key"]

sub_t = tree.subtree(containertobemoved)
sub_t.show()
paths_to_leaves = sub_t.paths_to_leaves()

movedcontainers = []

for paths in paths_to_leaves:
    if suffixremove == "n":
        parentname = paths[0]+"_temp"
        for container in paths:
            if container == containertobemoved:
                if container not in movedcontainers:
                    addContainer = clntapi.add_container(container+"_temp",targetcontainer,targetcontainerkey)
                    getcontainerbyname = clntapi.get_container_by_name(container+"_temp")
                    getcontainerbyname_old = clntapi.get_container_by_name(container)
                    getconfigletsbycontainerid = clntapi.get_configlets_by_container_id(getcontainerbyname_old["key"])["configletList"]
                    applyconfigletstocontainer = clntapi.apply_configlets_to_container(app_name,getcontainerbyname,getconfigletsbycontainerid)
                    movedcontainers.append(container)
            else:
                getcontainerbyname = clntapi.get_container_by_name(parentname)
                parentkey =  getcontainerbyname["key"]
                addContainer = clntapi.add_container(container+"_temp",parentname,parentkey)
                getcontainerbyname = clntapi.get_container_by_name(container+"_temp")
                getcontainerbyname_old = clntapi.get_container_by_name(container)
                getconfigletsbycontainerid = clntapi.get_configlets_by_container_id(getcontainerbyname_old["key"])["configletList"]
                applyconfigletstocontainer = clntapi.apply_configlets_to_container(app_name,getcontainerbyname,getconfigletsbycontainerid)
                parentname = container+"_temp"
    if suffixremove == "y":
        parentname = paths[0][:-5]
        for container in paths:
            if container == containertobemoved:
                if container not in movedcontainers:
                    addContainer = clntapi.add_container(container[:-5],targetcontainer,targetcontainerkey)
                    getcontainerbyname = clntapi.get_container_by_name(container[:-5])
                    getcontainerbyname_old = clntapi.get_container_by_name(container)
                    getconfigletsbycontainerid = clntapi.get_configlets_by_container_id(getcontainerbyname_old["key"])["configletList"]
                    applyconfigletstocontainer = clntapi.apply_configlets_to_container(app_name,getcontainerbyname,getconfigletsbycontainerid)
                    movedcontainers.append(container)
            else:
                getcontainerbyname = clntapi.get_container_by_name(parentname)
                parentkey =  getcontainerbyname["key"]
                addContainer = clntapi.add_container(container[:-5],parentname,parentkey)
                getcontainerbyname = clntapi.get_container_by_name(container[:-5])
                getcontainerbyname_old = clntapi.get_container_by_name(container)
                getconfigletsbycontainerid = clntapi.get_configlets_by_container_id(getcontainerbyname_old["key"])["configletList"]
                applyconfigletstocontainer = clntapi.apply_configlets_to_container(app_name,getcontainerbyname,getconfigletsbycontainerid)
                parentname = container[:-5]

if suffixremove == "n":
    for paths in paths_to_leaves:
        for container in paths:
            get_devices_in_container = clntapi.get_devices_in_container(container)
            get_container_by_name = clntapi.get_container_by_name(container+"_temp")
            for device in get_devices_in_container:
                move_device_to_container = clntapi.move_device_to_container(app_name,device,get_container_by_name)
if suffixremove == "y":
    for paths in paths_to_leaves:
        for container in paths:
            get_devices_in_container = clntapi.get_devices_in_container(container)
            get_container_by_name = clntapi.get_container_by_name(container[:-5])
            for device in get_devices_in_container:
                move_device_to_container = clntapi.move_device_to_container(app_name,device,get_container_by_name)


deletedcontainers = []
for paths in paths_to_leaves:
    for container in reversed(paths):
        if container != containertobemoved and container not in deletedcontainers:
            get_container_by_name = clntapi.get_container_by_name(container)
            container_key = get_container_by_name["key"]
            get_container_by_id = clntapi.get_container_by_id(container_key)
            parentname = get_container_by_id["parentName"]
            get_container_by_name = clntapi.get_container_by_name(parentname)
            parent_key = get_container_by_name["key"]
            delete_container = clntapi.delete_container(container,container_key,parentname,parent_key)
            deletedcontainers.append(container)

get_container_by_name = clntapi.get_container_by_name(containertobemoved)
container_key = get_container_by_name["key"]
get_container_by_id = clntapi.get_container_by_id(container_key)
parentname = get_container_by_id["parentName"]
get_container_by_name = clntapi.get_container_by_name(parentname)
parent_key = get_container_by_name["key"]
delete_container = clntapi.delete_container(container,container_key,parentname,parent_key)