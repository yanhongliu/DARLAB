import sys
import code
print "Run"

def tree_repr(tree, indent):
	global tree_repr
	print (" " * indent) + repr(tree)
	if indent < 20:
		for name,attribute in tree.getattributes().iteritems():
			if isinstance(attribute, gcc.Tree):
				print (" " * (indent + 2)) + repr(name)
				tree_repr(attribute, indent + 4)
			else:
				print (" " * (indent + 2)) + repr(name) + "=" + repr(attribute)
		for operand in tree.getoperands():
			tree_repr(operand, indent + 2)

for block in gcc.getblocks():
	print repr(block)
	for statement in block.getstatements():
		tree_repr(statement.gettree(), 2)

def console_handler(string,local_stack={}): #local_stack is thus, in effect, static
	if (string) == "exit":
		return False
	else:
		try:
			exec string in globals(),local_stack
		except Exception,inst:
			print "Exception Encountered: %s"%str(inst)
	return True

#while(console_handler(raw_input("> "))):
#	pass 

code.interact("Welcome to InvTS/GCC!",raw_input,globals())
#res = InvTS.do_rules(*res)
