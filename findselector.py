def find_selector(selectorList):
    selectorList = "continent: 10"
    print(selectorList)
    res_str = selectorList.partition(":")[2]
    print(res_str.strip())
    selects = []
    if (selectorList.partition(":")[0]=="loc"):
        selections = "abm-" + res_str.strip() + "-sel"
        print(selections)
        selects.append(selections)

    elif(selectorList.partition(":")[0]=="canary"):
        selections = "canary-" + res_str.strip() + "-sel"
        print(selections)
        selects.append(selections)
    else:
        selections = "continent-" + res_str.strip() + "-sel"
        print(selections)
        selects.append(selections)

    print(selects)