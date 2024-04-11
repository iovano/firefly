def dictMerge(dict1, dict2):
    for key, val in dict1.items():
        if type(val) == dict:
            if key in dict2 and type(dict2[key] == dict):
                dictMerge(dict1[key], dict2[key])
        else:
            if key in dict2:
                dict1[key] = dict2[key]

    for key, val in dict2.items():
        if not key in dict1:
            dict1[key] = val

    return dict1