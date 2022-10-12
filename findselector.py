selectorList = {"continent": "asia", "loc" : "east"}
selects = []

def find_selector(selectorList):
    for key in selectorList:
        print(selectorList)
        res_str = selectorList.get(key).strip()
        print(selectorList.get(key))
        if (key=="loc"):
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
print(selects)