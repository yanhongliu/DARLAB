import sys
import re
data = sys.stdin.readlines()
print len(data)
for d in data:
    try:
        f=open(d.strip(),'rb')
    except:
        pass
    s=f.read()
    if re.search(r"\n then",s):
        print "%s: FOUND \\r alone!"%(d.strip())
    
