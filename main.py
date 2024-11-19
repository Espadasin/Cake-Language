from sly import *


#Callbacks for check if exist a way for show the code result
callbacks = [
    'write'
]

#Lexer
class IntrepeterLexer(Lexer):
    tokens = {
        ID,
        STRING,
        INTEGER,
        PLUS,
        MINUS,
        TIMES,
        FAC,
        POW,
        DIVIDE,
        ASSIGN,
        WRITE,  
        IF,
        ELSE,
        WHILE
    }
    literals = ['{','}','(',')']

    ignore = ' \t'

    #OBJECT NAME
    ID = r'[a-zA-Z_][a-zA-Z0-9]*'

    #ARITMATICS SYMBOLS
    PLUS = r'\+'
    MINUS = r'-'
    DIVIDE = r'/'
    TIMES = r'\*'
    FAC = r'!'
    POW = r'\^'

    #BASE METHODS
    ID['WRITE'] = WRITE
    ID['IF'] = IF
    ID['ELSE'] = ELSE
    ID['WHILE'] = WHILE

    #COMMUM SYMBOLS
    ASSIGN = r':'

    #DATATYPES
    INTEGER = r"\d+"
    STRING = r'\".*?\"'

    @_(r'\n+')
    def ignore_newlines(self, t):
        self.lineno += len(t.value)

    @_(r'\#.*')
    def ignore_comments(self, t):
        pass

    #Error handling
    def error(self, t):
        print('Ilegal character "%s"' % t.value[0])

#Parser
class IntrepeterParser(Parser):
    tokens = IntrepeterLexer.tokens

    precedence = (
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE),
        ('left', POW, FAC),
        ('right', UMINUS),
    )

    #Sintax rules
    @_('ID ASSIGN expr')
    def statement(self, p):  
        return ('var_assign', p.ID  ,p.expr)

    @_('expr')
    def statement(self, p):
        return p.expr

    @_('ID')
    def expr(self, p):
        return ('var', p.ID)

    @_('expr PLUS expr',
       'expr MINUS expr')
    def expr(self,p):
        return (p[1], p.expr0, p.expr1)

    @_('expr TIMES expr',
       'expr DIVIDE expr')
    def expr(self,p):
        return (p[1], p.expr0, p.expr1)

    
    @_('expr FAC')
    def expr(self,p):
        return ('!', p.expr)
    
    @_('"(" expr ")"')
    def expr(self,p):
        return ('paren', p.expr)

    @_('expr POW expr')
    def expr(self, p):
        return ('^', p.expr0, p.expr1)

    @_('MINUS expr %prec UMINUS')
    def expr(self,p):
        return -p.expr

    @_('INTEGER')
    def expr(self, p):
        return ('int', int(p.INTEGER))

    @_('STRING')
    def expr(self, p):
        return ('str', str(p.STRING))

    @_('WRITE ASSIGN expr')
    def statement(self, p):
        return ('write', p.expr)

    @_('IF "(" expr ")" "{" statement "}"')
    def statement(self, p):
        return ('if', p.expr, p.statement)
        
    @_('IF "(" expr ")" "{" statement "}" ELSE "{" statement "}"')
    def statement(self, p):
        return ('if_and_else', p.expr, p.statement0, p.statement1)
        
    @_('WHILE "(" expr ")" "{" statement "}"')
    def statement(self, p):
        return ('while_loop', p.expr, p.statement)

#Intrepeter   
class BasicInterpreter:
    

    def __init__(self, tree, env):
        self.env = env
    
        result = self.walkTree(tree)
        
        if tree[0] in callbacks:
            if result != None and isinstance(result, int):
                print(result)
            if isinstance(result, str) and result[0] == '"':
                print(result)

    #Check the syntax and if is correct return the expected result, else this is just broken ;)
    def walkTree(self, node):

        if isinstance(node, int):
            return node
        if isinstance(node, str):
            return node
        
        if node is None:
            return None
        
        if node[0] == 'program':
            if node[1] == None:
                self.walkTree(node[2])
            else:
                self.walkTree(node[2])
                self.walkTree(node[3])

        #CHECK VALUE
        match node[0]:
            case "write":
                return self.walkTree(node[1])
            case "int":
                return node[1]
            case "str":
                return node[1]
            case "var":
                return self.walkTree(self.env[node[1]])

        #ARITIMETIC OPERATIONS
        match node[0]:
            case '+':
                return self.walkTree(node[1]) + self.walkTree(node[2])
            case '-':
                return self.walkTree(node[1]) - self.walkTree(node[2])
            case '*':
                return self.walkTree(node[1]) * self.walkTree(node[2])
            case '/':
                return self.walkTree(node[1]) / self.walkTree(node[2])
            case '!':
                n = node[1][1]
                fact = 1

                if node[1][1] < 10000:
                    for i in range(1, n+1):
                        fact = fact * i
                
                    return fact
                else:
                    print('This factorial is too BIG!')
            case '^':
                return node[1] ** node[1]
            case '>':
                return node[1] > node[2]
            case '<':
                return node[1] < node[2]
            case 'paren':
                return self.walkTree(node[1])
            case 'equal':
                return node[1] == node[2]
            

        #VARIABLES 
        if node[0] == 'var_assign':
            self.env[node[1]] = self.walkTree(node[2])
            return node[1]

        elif node[0] == 'var':
            try:
                return self.env[node[1]]
            except LookupError:
                print("The %r variable don't exist" % node[1])
                return 0
            
        #LOOPS
        match node[0]:
            case 'while_loop':
                while node[1]:
                    print(self.walkTree(node[2])) 

        #STATES

        #DEFINITIONS

        #CLASSES

#The final result
if __name__ == '__main__':
    lexer = IntrepeterLexer()
    parser = IntrepeterParser()    
    env = { }

    with open("init.txt", "r") as file:
        data = file.readlines()

        for line in data:

            tree = parser.parse(lexer.tokenize(line))
            BasicInterpreter(tree, env)