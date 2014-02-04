from pyparsing import Optional, Word, Literal, Forward, alphas, nums, Group, ZeroOrMore, oneOf, delimitedList, cStyleComment, restOfLine
import pprint

cstructBNF = None
def getCStructBNF():
	global cstructBNF
	if cstructBNF is None:
		structDecl = Forward()
		ident = Word( alphas+"_", alphas+nums+"_$" )
		integer = Word( nums )
		semi = Literal(";").suppress()

		typeName = ident
		varName = ident
		arraySizeSpecifier = integer | ident # <- should really support an expression here, but keep simple for now
		typeSpec = Optional("unsigned") + oneOf("int long short double char void")
		bitfieldspec = ":" + arraySizeSpecifier
		varnamespec = Group( Optional("*", default="") + varName + Optional( bitfieldspec | ( "[" + arraySizeSpecifier + "]" ) ) )
		memberDecl = Group( ( typeSpec | typeName ) + Group( delimitedList( varnamespec ) ) + semi ) | structDecl

		structDecl << Group( "struct" + Optional(ident) + "{" + ZeroOrMore( memberDecl ) + "}" + Optional(varnamespec) + semi )

		cstructBNF = structDecl

		cplusplusLineComment = Literal("//") + restOfLine

		cstructBNF.ignore( cStyleComment ) # never know where these will crop up!
		cstructBNF.ignore( cplusplusLineComment ) # or these either

	return cstructBNF

testData1 = """
a=b.c+d
"""

testData2 = """
struct {
long a;
struct {
int x;
int y;
} pt; // this is an embedded struct
struct {
int x,y;
} pt2;
struct {
int x;
int y;
}* coordPtr; /* this is just a pointer to a struct */
short b;
char c[32];
char d[MAX_LENGTH /* + 1 to make room for terminating null */ ];
char* name;
char *name2; /* no one can agree where the '*' should go */
int bitfield:5; /* this is rare, but not hard to add to parse
grammar */
int bitfield2:BIT2LEN;
void* otherData;
} a;
"""
for testdata in (testData1, testData2):
	pprint.pprint(getCStructBNF().parseString(testdata).asList())
	print
	