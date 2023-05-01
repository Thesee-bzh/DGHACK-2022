import sys

tab  = 0; glob = list(); curr = list(); is_fun = False

def eval_var(s):
    l = s.split(); out = s
    for m in l:
        if m[0] == '$':
            var = m[1:]
            exp = '", ' + var + ',"'
            out = s.replace(m, exp)
    return out
            
    
def parse_message(m):
    i = 0; out = ''; space = True; start = True
    while i < len(m):
        if m[i] == '"':
            # Found quote: parse string
            s = m[i:].split('"')[1]
            if space and not start:
                out += ' '
            # out += ',"' + s + '",'
            out += s
            i += len(s) + 2
            space = False; start = False
        else:
            # Parse until next string (starting with quote), if any
            s = m[i:].split('"')[0]; l = len(s); var = False
            if '$' in s:
                var = True
                s = eval_var(s)
            if s:
                s_ = ' '.join([x for x in s.split(' ') if x != '']).replace('  ', ' ')
                if s_ != '':
                    if not start and not var:
                        out += ' ' # ???????
                    out += s_
                    if space and not var:
                        out += ' '
                    if not var:
                        space = True
                i += l
            else:
                i += 1
            start = False
    if out != ' ':
        out = out.strip()
    out = 'print("' + out + '", sep=\'\')\n'
    return out

def handle_scope(var):
    global tab, glob, curr, is_fun
    g = ''
    if not is_fun:
        # Global
        if var not in glob:
            g = 'global ' + var + '\n'
            glob.append(var)
    else:
        # Local ?
        if var not in curr:
            g = 'global ' + var + '\n'
            curr.append(var)
    return g

def parse_var(n):
    l = n.split()
    var = l[0]; val = l[1]; g = ''
    exp = var + ' = ' + val + '\n'
    g = handle_scope(var)
    return g, exp
    
def parse_function(f):
    global tab
    name = f.split(':')[0]
    out = 'def ' + name + '():\n'
    tab = 1
    return out

def parse_call(c):
    out = c.strip() + '()\n'
    return out

def parse_increment(i):
    l = i.split()
    var = l[0]; val = l[1]; g = ''
    exp = var + ' += ' + val + '\n'
    return handle_scope(var), exp
    
def parse_if(c):
    l = c.split()
    var = l[0].split('$')[1]; op = l[1]; val = l[2]; g = ''
    exp = 'if(' + var + op + val + '):\n'
    return handle_scope(var), exp
    
def parse(f):
    global tab, is_fun
    out = ''; main = ''; fun = ''
    with open(f) as file:
        while line := file.readline():
            line = line.strip()
            m = line.split()
            if not m:
                out = '\n'
            elif m[0] == 'message':
                # Message
                out = tab * '\t' + parse_message(line[len('message '):])
            elif m[0] == 'nombre':
                # Variable
                g, exp = parse_var(line[len('nombre '):])
                out = ''
                if g != '':
                    out = tab * '\t' + g
                out += tab * '\t' + exp
            elif m[0][-1] == ':':
                # Function start:
                out = '\n' + parse_function(line)
                curr.clear()
                is_fun = True
            elif m[0] == 'retour':
                # Function end
                tab = 0; out = ''
                is_fun = False
            elif m[0] == 'appel':
                # Function call:
                out = tab * '\t' + parse_call(line[len('appel '):])
            elif m[0] == 'incrementer':
                # Increment variable:
                g, exp = parse_increment(line[len('incrementer '):])
                out = ''
                if g != '':
                    out = tab * '\t' + g
                out += tab * '\t' + exp
            elif m[0] == 'si':
                # Condition start:
                g, exp = parse_if(line[len('si '):])
                out = ''
                if g != '':
                    out = tab * '\t' + g
                out += tab * '\t' + exp
                tab += 1
            elif m[0] == 'finsi':
                # Condition end:
                tab -= 1
                out = '\n'
            elif m[0] == ';':
                # Comment
                out = ''
            if not is_fun:
                if out != '\n':
                    main += out
            else:
                fun += out
    # Add the main part to the prog
    decl_glob = ''
    #if glob:
    #    decl_glob = 'global ' + ', '.join([x for x in glob]) + '\n' 
    prog = 'p = """' + decl_glob + fun + '\n' + main + '"""\n' + 'exec(p)\n'
    return prog

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 " + sys.argv[0] + " <filename>")
        sys.exit(1)
    prog = parse(sys.argv[1])
    #print(prog)
    exec(prog, globals())

if __name__ == "__main__":
    main()
