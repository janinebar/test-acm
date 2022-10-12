# Dict of list passed to the method from frontend (label:value)
selectorList = {"continent": "asia", "loc" : "east"}
# List of selectors to enable
selects = []

def find_selector(selectorList):
    # Iterate through the label:value dict
    for key in selectorList:
        print(selectorList)
        # Get the value and remove any whitespaces
        res_str = selectorList.get(key).strip()
        print(selectorList.get(key))

        # Determine the kind of label being used
        if (key=="loc"):
            # Format the selector value
            selections = "abm-" + res_str + "-sel"
            print(selections)
            selects.append(selections)

        elif(key=="canary"):
            selections = "canary-" + res_str + "-sel"
            print(selections)
            selects.append(selections)

        else:
            selections = "continent-" + res_str + "-sel"
            print(selections)
            selects.append(selections)


find_selector(selectorList)
# Print the list of selectors
print(selects)