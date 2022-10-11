import ruamel.yaml
import sys

#set sample variables
all_selectors = "123", "234", "578"
selections = "123", "234"

def set_pos(selectors):
    #set new pos with listed selectors
    set_yaml("new_pos.yaml", selectors)
    #set the array with other selectors
    old_pos_selector = (set(all_selectors) - set(selectors))
    #set old pos
    set_yaml("old_pos.yaml", old_pos_selector)

def set_yaml(yaml_str, pos_selector):
    #Parse the YAML file
    yaml = ruamel.yaml.YAML()
    data = yaml.load(open(yaml_str))
    #change value of the selectors
    data['metadata']['annotations']['configmanagement.gke.io/cluster-selector'] =  ",".join(pos_selector)
    #Write to file
    with open(yaml_str, 'w') as file:
        yaml.dump(data, file)

#set new pos with listed selectors
set_pos(selections)
