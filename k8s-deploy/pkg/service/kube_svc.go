/*
 * Copyright 2019-2020 VMware, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://www.apache.org/licenses/LICENSE-2.0
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */
package service

import (
	"context"
	"fmt"

	v1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

func GetProxySvcNodePorts(name, namespace string) ([]int32, error) {
	var labelSelector string
	labelSelector = fmt.Sprintf("name=%s", name)
	svcs, err := GetServices(namespace, labelSelector)
	if err != nil {
		return nil, err
	}

	var nodePorts []int32

	//svcs.Items[0].GetName()
	for _, v := range svcs.Items {
		if v.GetName() == "proxy" {
			for _, vv := range v.Spec.Ports {
				nodePorts = append(nodePorts, vv.NodePort)
			}
		}
	}
	return nodePorts, nil
}

func GetServices(namespace, LabelSelector string) (*v1.ServiceList, error) {
	clientset, err := getClientset()
	if err != nil {
		return nil, err
	}

	svcs, err := clientset.CoreV1().Services(namespace).List(context.Background(), metav1.ListOptions{LabelSelector: LabelSelector})
	return svcs, err
}

func GetServiceStatus(Services *v1.ServiceList) map[string]string {
	status := make(map[string]string)
	for _, v := range Services.Items {
		status[v.Name] = v.Status.String()
	}
	return status
}

func GetClusterServiceStatus(name, namespace string) (map[string]string, error) {
	var labelSelector string
	labelSelector = fmt.Sprintf("name=%s", name)
	list, err := GetServices(namespace, labelSelector)
	if err != nil {
		return nil, err
	}

	return GetServiceStatus(list), nil
}