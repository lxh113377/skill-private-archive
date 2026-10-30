
import json
d=json.load(open('06-benchmark/r275_three_channel_intersection.json',encoding='utf-8'))
def walk(o,path=''):
    if isinstance(o,dict):
        s=json.dumps(o,ensure_ascii=False)
        if 'mcp-builder' in s and len(s)<4000:
            print('=== HIT at',path);print(s);return
        for k,v in o.items(): walk(v,path+'/'+str(k))
    elif isinstance(o,list):
        for i,v in enumerate(o): walk(v,path+'/'+str(i))
walk(d)
