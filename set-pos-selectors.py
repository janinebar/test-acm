from flask import Flask, request, Response
import sys
import json 
import base64
import requests
import ruamel.yaml

app = Flask(__name__)

######################## 
## CREATE NEW FILE TO GIT
########################
@app.route("/selector/create/", methods=['POST'])
def create_selector():
    
    # Get selectors from query
    params = request.get_json()
    labels = params['labels']
    selector_name = params['selector_name']
    yaml = create_cluster_selector_yaml(selector_name, labels)
    
    # Encode to base64
    yaml_bytes = yaml.encode("ascii")
    yaml_bytes = base64.b64encode(yaml_bytes)
    yaml_b64 = yaml_bytes.decode("ascii")

    # Push to github
    user = "janinebar"
    repo = "sample"
    url = f"https://api.github.com/repos/{user}/{repo}/contents/{selector_name}.yaml"
    message = f"new selector: {selector_name}"
    r = git_push_new_file(url, message, yaml_b64)
    

    return Response(r, status=200)

######################## 
## UPDATE POS YAMLS WITH CORRECT SELECTORS
########################
@app.route("/selector/pos/", methods=['POST'])
def update_selectors():

    # Pull params
    params = request.get_json()
    pos_version = params['pos_version'] 
    pos_version = "pos_v2"
    print(pos_version)
    policies = params['policies'] # array of string policies
    labels = params['labels']

    # Find selectors for params
    selectors = find_selector(labels)

    # Pull POS files from git
    user = "janinebar"
    repo = "test-acm"
    pos_v2_url = git_url(user, repo, "default/pos/pos_v2.yaml")    
    pos_v1_url = git_url(user, repo, "default/pos/pos_v1.yaml")    
    pos_v2_sha, pos_v2_content = git_pull_file(pos_v2_url)
    pos_v1_sha, pos_v1_content = git_pull_file(pos_v1_url)

    # Decode the content and save locally
    save_gitfile_locally("pos_v2.yaml", pos_v2_content)
    save_gitfile_locally("pos_v1.yaml", pos_v1_content)

    # Update the POS yamls based on chosen version
    selected_clusters, unselected_clusters = get_nonchosen_pos_selectors(labels)
    if(pos_version == "pos_v2"):
        print("VERSION 2")
        # Set POS v2 selectors
        set_pos_selectors("pos_v2.yaml", selected_clusters)
        # Put all other selectors in POS v1
        set_pos_selectors("pos_v1.yaml", unselected_clusters)
    elif(pos_version == "pos_v1"):
        print("VERSION 1")
        # Set POS v1 selectors
        set_pos_selectors("pos_v1.yaml", selected_clusters)
        # Put all other selectors in POS v2
        set_pos_selectors("pos_v2.yaml", unselected_clusters)

    # Encode yamls back to base64 
    pos_v2_yaml_encoded = encode_localfile_b64("pos_v2.yaml")
    pos_v1_yaml_encoded = encode_localfile_b64("pos_v1.yaml")

    # Push updated POS versions back to git
    message = f"updated {pos_version} with selectors: {selectors}"
    r = git_update_file(pos_v2_url, message, pos_v2_yaml_encoded, pos_v2_sha)
    r = git_update_file(pos_v1_url, message, pos_v1_yaml_encoded, pos_v1_sha)

    return "OK"


######################## 
## FORM GIT URL FOR REQUESTS
########################
def git_url(user, repo, filepath):
    return f"https://api.github.com/repos/{user}/{repo}/contents/{filepath}"

######################## 
## SAVE PULLED GIT FILE TO LOCAL DIR
########################
def save_gitfile_locally(filename, content):
    content = base64.b64decode(content)
    with open(filename, "wb") as text_file:
        text_file.write(content)

######################## 
## ENCODE LOCAL FILE TO BASE64
########################
def encode_localfile_b64(filename):
    with open(filename, "rb") as to_encode:
        encoded_file = base64.b64encode(to_encode.read())
        encoded_file = encoded_file.decode("ascii")
        print(encoded_file)
    return encoded_file

######################## 
## PULL FILE FROM GIT
########################
def git_pull_file(url):
    r = requests.get(
        url, 
        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        },
    )
    response = r.json()
    print(response['sha'])
    sha = response['sha']
    content = response['content']
    return sha, content
    
######################## 
## PUSH UPDATED FILE TO GIT
########################
def git_update_file(url, message, content, sha): 
    r = requests.put(
        url, 
        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        },
        data = json.dumps({
            "message": message,
            "content": content,
            "sha": sha
        })
    )
    return r

def git_push_new_file(url, message, content):
    r = requests.put(
        url, 
        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        },
        data = json.dumps({
            "message": message,
            "content": content
        })
    )
    return r


######################## 
## FIND SELECTED AND UNSELECTED CLUSTERS
########################
def get_nonchosen_pos_selectors(labels):
    
    selected_clusters = []
    unselected_clusters = []
    
    # Find the corresponding clusters for the desired labels
    for label in labels:
        print(label)
        label_values = labels[label]
        for value in label_values:
            print("------------- "+ label + ": " + value)

            for cluster in clusters: # For each cluster
                curr_cluster_labels = clusters[cluster] # Look at the cluster labels
                if(curr_cluster_labels[label] == value):  
                    print(cluster)
                    if(cluster not in selected_clusters): # Add the cluster name if it has the desired label:value 
                        selected_clusters.append(cluster) # Remove duplicates
    
    # Find the rest of the clusters that do not have the desired label:values
    for cluster in clusters:
        if(cluster not in selected_clusters):
            unselected_clusters.append(cluster)

    print(len(selected_clusters))
    print(len(unselected_clusters))

    return selected_clusters, unselected_clusters

######################## 
## UPDATE POS YAMLS WITH NEW CLUSTERS
########################
def set_pos_selectors(yaml_str, pos_selector):
    
    # Parse the YAML file
    yaml = ruamel.yaml.YAML()
    data = yaml.load(open(yaml_str))
    
    # Change value of the selectors
    data['metadata']['annotations']['configsync.gke.io/cluster-name-selector'] =  ",".join(pos_selector)
    
    #Write to file
    with open(yaml_str, 'w') as file:
        yaml.dump(data, file)


######################## 
## FORM SELECTOR NAME
########################
def find_selector(selectorList):
    selects = []
    # Iterate through the label:value dict
    for key in selectorList:
        print(selectorList)
        
        # Determine the kind of label being used
        if (key=="loc"):
            # Format the selector value, remove any whitespace
            for res_str in selectorList.get(key):
                print(res_str)
                selections = "abm-" + res_str + "-sel"
                print(selections)
                selects.append(selections)

        elif(key=="canary"):
            for res_str in selectorList.get(key):
                selections = "canary-" + res_str + "-sel"
                print(selections)
                selects.append(selections)

        else:
            for res_str in selectorList.get(key):
                selections = "continent-" + res_str + "-sel"
                print(selections)
                selects.append(selections)
        
    print(selects)
    return selects

######################## 
## ALL CLUSTERS WITH LABELS
########################
clusters = {
    'abm-asia-east1': {"canary": "100", "loc": "asia-east1", "continent": "asia"},
    'abm-asia-east2': {"canary": "50", "loc": "asia-east2", "continent": "asia"},
    'abm-asia-northeast1': {"canary": "10", "loc": "asia-northeast1", "continent": "asia"},
    'abm-asia-northeast2': {"canary": "50", "loc": "asia-northeast2", "continent": "asia"},
    'abm-asia-northeast3': {"canary": "25", "loc": "asia-northeast3", "continent": "asia"},
    'abm-asia-south1': {"canary": "100", "loc": "asia-south", "continent": "asia"},
    'abm-asia-south2': {"canary": "10", "loc": "asia-south1", "continent": "asia"},
    'abm-asia-southeast1': {"canary": "100", "loc": "asia-southeast1", "continent": "asia"},
    'abm-asia-southeast2': {"canary": "100", "loc": "asia-southeast1", "continent": "asia"},
    'abm-australia-southeast1': {"canary": "50", "loc": "australia-southeast1", "continent": "australia"},
    'abm-australia-southeast2': {"canary": "100", "loc": "australia-southeast2", "continent": "australia"},
    'abm-europe-central2': {"canary": "100", "loc": "europe-central2", "continent": "europe"},
    'abm-europe-north1': {"canary": "100", "loc": "europe-north1", "continent": "europe"},
    'abm-europe-southwest1': {"canary": "10", "loc": "europe-southwest1", "continent": "europe"},
    'abm-europe-west1': {"canary": "50", "loc": "europe-west1", "continent": "europe"},
    'abm-europe-west2': {"canary": "25", "loc": "europe-west1", "continent": "europe"},
    'abm-europe-west3': {"canary": "100", "loc": "europe-west1", "continent": "europe"},
    'abm-europe-west4': {"canary": "25", "loc": "europe-west1", "continent": "europe"},
    'abm-europe-west6': {"canary": "10", "loc": "europe-west1", "continent": "europe"},
    'abm-europe-west8': {"canary": "50", "loc": "europe-west1", "continent": "europe"},
    'abm-europe-west9': {"canary": "100", "loc": "europe-west1", "continent": "europe"},
    'abm-northamerica-northeast1': {"canary": "10", "loc": "northamerica-northeast1", "continent": "northamerica"},
    'abm-northamerica-northeast2': {"canary": "50", "loc": "northamerica-northeast2", "continent": "northamerica"},
    'abm-southamerica-east1': {"canary": "25", "loc": "southamerica-east1", "continent": "southamerica"},
    'abm-southamerica-west1': {"canary": "100", "loc": "southamerica-west1", "continent": "southamerica"},
    'abm-us-central1': {"canary": "25", "loc": "us-central1", "continent": "us"},
    'abm-us-east1': {"canary": "50", "loc": "us-east1", "continent": "us"},
    'abm-us-east4': {"canary": "10", "loc": "us-east4", "continent": "us"},
    'abm-us-south1': {"canary": "10", "loc": "us-south1", "continent": "us"},
    'abm-us-west1': {"canary": "10", "loc": "us-west1", "continent": "us"},
    'abm-us-west2': {"canary": "50", "loc": "us-west2", "continent": "us"},
    'abm-us-west3': {"canary": "100", "loc": "us-west3", "continent": "us"},
    'abm-us-west4': {"canary": "50", "loc": "us-west4", "continent": "us"},
}

######################## 
## GENERATE CLUSTERSELECTOR YAML 
########################
def create_cluster_selector_yaml(filename, selectors):

    labels = ""
    for label in selectors:
        print(label)
        print(selectors[label])

    # YAML ClusterSelector contents
    yaml = {
        "kind": "ClusterSelector",
        "apiVersion": "configmanagement.gke.io/v1",
        "metadata": {
            "name": "hello",
            "spec": {
                "selector": {
                    "matchLabels": selectors
                } 
            }
        }
    }

    print(yaml)

    # Format into YAML string
    formatted_yaml = json.dumps(yaml, indent=2)
    print(formatted_yaml)
    formatted_yaml = formatted_yaml.replace('{', '')
    formatted_yaml = formatted_yaml.replace('}', '')
    formatted_yaml = formatted_yaml.replace('"', '')
    formatted_yaml = formatted_yaml.replace(',', '')
    formatted_yaml = formatted_yaml.split("\n", 1)[1]
    print(type(formatted_yaml))
    print(formatted_yaml)
                
    return formatted_yaml
