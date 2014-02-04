import sys
from analysis.plugins.simplify import simplify

s=simplify(sys.argv[1])
print s
sys.exit(0)

