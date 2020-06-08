# Copyright 2019-2020 VMware, Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# you may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os, subprocess, json, tempfile

class ClusterManager:
    def __init__(self, cluster_namespace, cluster_name):
        self.namespace = cluster_namespace
        self.name = cluster_name

    # get configmap in dict
    def FetchConfigmap(self, component):
       args ="kubectl get configmap {} -n {} -o json".format(component, self.namespace).split(" ") 
       try:
           data, err = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
           return json.loads(data)
       except Exception as error:
           print(error)
    
    # get route table in dict
    def FetchRouteTable(self, configmap):
       route_table_json = json.loads(configmap["data"]["route_table.json"]) 
       return route_table_json 
    
    def UpdateConfigMap(self, configmap, route_table):
        configmap["data"]["route_table.json"] = json.dumps(route_table)
    
    def PatchConfigMap(self, configmap, component):
        args = "kubectl patch configmap {} -n {} --patch".format(component, self.namespace).split(" ")
        args.append(json.dumps(configmap))
        try:
            data, err = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
            print(data)
        except Execption as error:
            print(error)

    def GetRouteTable(self):
        # get configmap in dict
        configmap = self.FetchConfigmap("proxy-config")

        # get route table in dict
        route_table = self.FetchRouteTable(configmap)
        return route_table

    def SetRouteTable(self, route_table):
        # get configmap in dict
        configmap = self.FetchConfigmap("proxy-config")

        # paste upate to the configmap
        self.UpdateConfigMap(configmap, route_table)

        # patch config
        self.PatchConfigMap(configmap, "proxy-config")

    def GetEntrypoint(self):
        get_address = "kubectl get nodes -o jsonpath=\'{$.items[0].status.addresses[?(@.type==\'InternalIP\')].address}\'"
        get_port = "kubectl get service proxy -n {0} -o jsonpath=\'{{.spec.ports[0].nodePort}}\'".format(self.namespace)

        ip = ""
        port = ""

        try:
           ip, err = subprocess.Popen(get_address.split(" "), stdout=subprocess.PIPE).communicate()
           port, err = subprocess.Popen(get_port.split(" "), stdout=subprocess.PIPE).communicate()
        except Exception as error:
            print(error)

        if ip == "" or port == "":
            raise(Exception("Unable to get entrypoint"))
        return "{}:{}".format(ip.decode("utf-8").replace("'", ""), port.decode("utf-8").replace("'", ""))