#
# Contain functions for pre-processing strings containing Python code.
#  


def extractFunctionBody(pythonStr:str) -> str :
    """
    This assumes the given txt contains the definition of a single function F.
    The body of F is extracted and returned. F's header and any leading lines
    before the header will be stripped off.
    """
    lines =  pythonStr.split('\n')
    body = []
    foundBody = False
    for z in lines:
        if foundBody:
            body.append(z)      
        elif z.strip().startswith('def'):
            foundBody = True

    if foundBody:
        return '\n'.join(body)
    else:
        return pythonStr
  

def extractPythonFunctionDef_fromMarkDownQuote(pythonStr:str) -> str :
    """
    To extract a Python function definition which is written inside a Markdown quote,
    e.g.:

    ```
    def foo(x): return x+1
    ```
    
    We then extract the code inside the quote.

    The same string is returned if there is no quotation in the string.
    """
    if pythonStr.find("```") < 0:
        # no quotation is found
        return pythonStr
    
    lines =  pythonStr.split('\n')
    functionDef = []
    startQuoteFound = False
    startFunctionFound = False
    for z in lines:
        if not startFunctionFound and z.strip().startswith('```'):
            # start quote found
            startQuoteFound = True
            # will assume that the next line is the start of the python-code
            startFunctionFound = True
            continue
        #if not startFunctionFound and z.strip().startswith('def'):
        #    if not startQuoteFound:
        #        # well then the function is not packed between quotes
        #        return pythonStr
        #    startFunctionFound = True
        #    functionDef.append(z)
        #    continue
        if startFunctionFound:
            if z.strip().startswith('```'):
                # end of quote is found
                break
            functionDef.append(z)

    return '\n'.join(functionDef)

def getColumnStart(z:str) -> int :
    """
    Given a string z, this gives the index of the first character in z
    which is not a space.
    """
    if z=='': return None
    k = 0
    for c in z:
        if c != ' ': break
        k = k+1
    return k

def split_Atcollon(pythonStr:str) -> str :
    """ 
    Split single-liners like if g : S into two lines (with S indented further than if)
    """
    lines = pythonStr.split('\n')
    newlines = []
    inMultiLineComment = False
    for z in lines:
        striped_z = z.strip()
        # dealing emtpy lines and comments:
        if striped_z == '' or striped_z.startswith('#'): 
            newlines.append(z)
            continue
        if not inMultiLineComment and striped_z.startswith('```'):
            inMultiLineComment = True
            newlines.append(z)
            continue
        if inMultiLineComment:
            if striped_z.startswith('```'): 
                # end of multi-line comment
                inMultiLineComment = False
            newlines.append(z)    
            continue

        k = z.find(':')
        if k>0 and not striped_z.endswith(':') :
            # split the line
            k = k+1
            newlines.append(z[0 : k])
            padding = ' ' * (getColumnStart(z) + 3)
            newlines.append(padding + z[k : ])
            continue
        
        newlines.append(z)
    
    return '\n'.join(newlines)

def fix_indentation(functionDefLine:str, body:str) -> str :
    """
    Try to fix the indentation of the given function body. The header-line
    is a single line of the header of a function definition.
    The fixer does a best approach. The resulting program is not guaranteed
    to represent its author intent (the problem of fixing is ambiguous).

    The fixer also assumes that both the given header and body contain
    no multi-line expression.
    """
    if functionDefLine.startswith('def ') :
        functionDefLine = functionDefLine[4 : ]
    
    fun0 = 'def xxx_' + functionDefLine + '\n' + body
    try:
        exec(fun0,globals())
        # the function can be executed
        print(">>> AI proposed function looks good.")
        return body
    except:
        print(">>> AI proposed function is not well defined. Trying to fix indentation.")
        body2 = fix_indentation_worker(body)
        if body2 == None:
            print("    Fixing FAILED.")
            return None
        try :
            fun1 = 'def yyy_' + functionDefLine + '\n' + body2
            exec(fun1,globals())
            print("    Indentation fixed.")
            return body2
        except :
            print("    Fixing FAILED.")
            return None


def fix_indentation_worker(pythonStr:str) -> str :
    def current(scopes:list):
        N = len(scopes)
        if N == 0 : return None
        return scopes[N-1]
    
    def pop(scopes:list):
        scopes.pop(len(scopes)-1)

    def popUntil(scopes:list, col:int):
        # pop the scope until the current scope starts at collumn
        # k <= col, or else until the scope only has one element
        while len(scopes) > 1 :
            S = current(scopes)
            if S['col'] <= col :
                break
            pop(scopes)

    
    
    def getStmtType(z:str):
        # SIMPLISTIC solution that assumes a structure header is coded in a single line!
        # similarly primitive stmt like assignments or calls are assumed to be coded in a single line.
        s = z.strip()
        # remove trailing comment too:
        i = s.find('#')
        if i > 0:
            s = s[0 : i]

        if not s.endswith(':'):
            return 'ordinary-stmt-line'
        # other cases are stmt that changes the scope-level
        if s.startswith('if '):
            return 'if'
        if s.startswith('for ') or s.startswith('while ') or s.startswith('def ') or s.startswith('with '):
            return 'stmt-struct-START'
        if s.startswith('else'):
            return 'else'
        if s.startswith('elif'):
            return 'elif'
        
        return None

    pythonStr2 = split_Atcollon(pythonStr)
    lines = pythonStr2.split('\n')
    fixed = []
    scopes = []
    inMultiLineComment = False

    for z in lines:
        striped_z = z.strip()
        # dealing emtpy lines and comments:
        if striped_z == '' or striped_z.startswith('#'): 
            fixed.append(z)
            continue
        if not inMultiLineComment and striped_z.startswith('```'):
            inMultiLineComment = True
            fixed.append(z)
            continue
        if inMultiLineComment:
            if striped_z.startswith('```'): 
                # end of multi-line comment
                inMultiLineComment = False
            fixed.append(z)    
            continue

        S = { 'col' : getColumnStart(z), 'ty' : getStmtType(z)}
        if S['ty'] == None:
            # something is wrong, can't fix the code
            return None
        if len(scopes) == 0:
            # the scope is still empty           
            scopes.append(S)
            fixed.append(z)
            continue

        Scurrent = current(scopes)

        if S['ty'] == 'else' or S['ty'] == 'elif' :
            # z should be indented as the matching if or elif that appears
            # previously
            n = len(scopes) - 1
            while n>=0 :
                T = scopes[n]
                if (T['ty'] == 'if' or T['ty'] == 'elif') and T['col'] == S['col'] :
                    # found a matching if/elif
                    break
                else: n = n - 1
            if n>=0:
                while len(scopes) > n: pop(scopes)
                scopes.append(S)
                fixed.append(z)
                continue
            else:
                # no matching if or elif found, we will pop until
                # the deepest one, then add z in that scope
                T = Scurrent
                while len(scopes) > 0 and T['ty'] != 'if' and T['ty'] != 'elif'  :
                    pop(scopes)
                    T = current(scopes)
                if len(scopes) == 0:
                    # something is wrong, cannot find a candidate if/elif
                    return None
                S['col'] = T['col']
                padding = ' ' * S['col']
                pop(scopes)
                scopes.append(S)
                fixed.append(padding + striped_z)
                continue

        else:
            if Scurrent['ty'] == 'ordinary-stmt-line' :
                # in the case z should be indented as far as the current scope
                if S['col'] == Scurrent['col']:
                    # good!
                    scopes.append(S)
                    fixed.append(z)
                    continue
                #print(f">>> {scopes}")
                popUntil(scopes,S['col'])
                Scurrent = current(scopes)
                #print(f">>> {scopes}")
                if S['col'] >=  Scurrent['col']:
                    # z is may be too much indentend, fix it:
                    k = S['col'] - Scurrent['col']
                    S['col'] = Scurrent['col']
                    scopes.append(S)
                    fixed.append(z[k : ])
                    continue
                if S['col'] <  Scurrent['col']:
                    # can only be the case if the scope has been poped until it
                    # only has one element remaining
                    # we indent z as much as the current scope
                    padding = ' ' * Scurrent['col']
                    S['col'] = Scurrent['col']
                    scopes.append(S)
                    fixed.append(padding + striped_z)
                    continue
            else:
                # the current scope is a structure
                # then z should be indented further than the current scope
                if  S['col'] >  Scurrent['col']:
                    # Good!
                    scopes.append(S)
                    fixed.append(z)
                else:
                    # z is wrongly indented; we indent it as far as the current-scope + 3
                    S['col'] = Scurrent['col'] + 3
                    padding = ' ' * S['col'] 
                    scopes.append(S)
                    fixed.append(padding + striped_z)
                    continue
    
    return '\n'.join(fixed)
  


if __name__ == '__main__':
    # some tests
    txt = """#some comment
#more comment
def foo(x):
  y = x+1
  return y
#trailing stuff
"""

    txt2 = """
```python
def foo(x):
  y = x+1
  return y
```
"""
    txt3 = """  
  if x>0 :
  x = x+1
      y = y+1
      if y>0 :
          y = 0
      x = 0
    elif x>-1 : x = 1  
   else: 
      y = 0
"""
    txt4 = """
    if x + y == 0 or x - y == 0 or z - x == 0:
    return True
    else:
    return False
"""
    print(extractFunctionBody(txt))
    print("====")
    print(extractPythonFunctionDef_fromMarkDownQuote(txt2))
    print("====")
    txt2b = extractFunctionBody(extractPythonFunctionDef_fromMarkDownQuote(txt2))
    print(txt2b)
    print("====")
    print("** fixing identation")
    print(fix_indentation_worker(txt2b))
    print("====")
    print(fix_indentation_worker(txt4))
    print("====")
    print(fix_indentation("def foo(x,y,z):", txt4))
 