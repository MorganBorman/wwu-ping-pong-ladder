import sqlalchemy.util._collections

def resultdict(result):
    if type(result) == list:
        return map(resultdict, result)
    elif type(result) == sqlalchemy.util._collections.NamedTuple:
        r = {}
        for key in result.keys():
            r[key] = result.__getattribute__(key)
        return r
    else:
        raise Exception("Invalid result type for resultdict.")
