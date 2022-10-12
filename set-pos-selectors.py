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
    # save_gitfile_locally("pos_v2.yaml", pos_v2_content)
    # save_gitfile_locally("pos_v1.yaml", pos_v1_content)

    # Update the POS yamls based on chosen version
    nonchosen_selectors = get_nonchosen_pos_selectors(selectors)
    if(pos_version == "pos_v2"):
        print("VERSION 2")
        # Set POS v2 selectors
        set_pos_selectors("pos_v2.yaml", selectors)
        # Put all other selectors in POS v1
        set_pos_selectors("pos_v1.yaml", nonchosen_selectors)
    elif(pos_version == "pos_v1"):
        print("VERSION 1")
        # Set POS v1 selectors
        set_pos_selectors("pos_v1.yaml", selectors)
        # Put all other selectors in POS v2
        set_pos_selectors("pos_v2.yaml", nonchosen_selectors)

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

# List of all selectors
all_selectors = [   # Asia
                    'abm-asia-east1-sel', 
                    'abm-asia-northeast1-sel', 
                    'abm-asia-northeast2-sel', 
                    'abm-asia-northeast3-sel', 
                    'abm-asia-southeast1-sel', 
                    'abm-asia-southeast2-sel', 
                    'abm-asia-south1-sel', 
                    'abm-asia-south2-sel',
                    # Australia
                    'abm-australia-southeast1-sel',
                    'abm-australia-southeast2-sel',
                    # Europe 
                    'abm-europe-central2-sel', 
                    'abm-europe-north1-sel', 
                    'abm-europe-southwest1-sel', 
                    'abm-europe-west1-sel', 
                    'abm-europe-west2-sel', 
                    'abm-europe-west3-sel', 
                    'abm-europe-west4-sel', 
                    'abm-europe-west6-sel', 
                    'abm-europe-west8-sel', 
                    'abm-europe-west9-sel',
                    # Northamerica
                    'abm-northamerica-northeast1-sel',
                    'abm-northamerica-northeast2-sel',
                    # Southamerica
                    'abm-souththamerica-east1-sel',
                    'abm-souththamerica-west1-sel',
                    # US
                    'abm-us-central1-sel', 
                    'abm-us-east1-sel', 
                    'abm-us-east4-sel', 
                    'abm-us-south1-sel', 
                    'abm-us-west1-sel', 
                    'abm-us-west2-sel', 
                    'abm-us-west3-sel', 
                    'abm-us-west4-sel',
                    # Canary
                    'canary-50-sel', 
                    'canary-10-sel', 
                    'canary-100-sel', 
                    'canary-25-sel', 
                    # Continents
                    'continent-europe-sel', 
                    'continent-asia-sel', 
                    'continent-australia-sel', 
                    'continent-north-america-sel', 
                    'continent-south-america-sel',
                    'continent-usa-sel']

def get_nonchosen_pos_selectors(selectors):
    #set the array with other selectors
    return set(all_selectors) - set(selectors)

def set_pos_selectors(yaml_str, pos_selector):
    
    # Parse the YAML file
    yaml = ruamel.yaml.YAML()
    data = yaml.load(open(yaml_str))
    
    # Change value of the selectors
    data['metadata']['annotations']['configmanagement.gke.io/cluster-selector'] =  ",".join(pos_selector)
    
    #Write to file
    with open(yaml_str, 'w') as file:
        yaml.dump(data, file)

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


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


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

