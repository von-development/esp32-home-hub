# Picoweb utilities
import ure as re

def parse_qs(s):
    """Parse query string"""
    res = {}
    if s:
        pairs = s.split("&")
        for p in pairs:
            vals = p.split("=", 1)
            if len(vals) == 1:
                vals.append("")
            if vals[0] in res:
                if not isinstance(res[vals[0]], list):
                    res[vals[0]] = [res[vals[0]]]
                res[vals[0]].append(vals[1])
            else:
                res[vals[0]] = vals[1]
    return res

def unquote_plus(s):
    """URL decode with + to space conversion"""
    s = s.replace("+", " ")
    arr = s.split("%")
    res = arr[0]
    for i in range(1, len(arr)):
        if len(arr[i]) >= 2:
            res += chr(int(arr[i][:2], 16)) + arr[i][2:]
        else:
            res += "%" + arr[i]
    return res 