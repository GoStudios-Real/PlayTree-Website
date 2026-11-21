#!/usr/bin/env python3
"""GoSD - a real bytecode-compiled programming language (embedded in PLAYTREE)."""
import sys, struct, json, os

# ===================== LEXER =====================
class Tok:
    __slots__ = ('kind','val','line','col')
    def __init__(self, kind, val, line, col):
        self.kind = kind; self.val = val; self.line = line; self.col = col
    def __repr__(self): return f"{self.kind}:{self.val!r}@{self.line}"

KEYWORDS = {'let','const','fn','if','else','while','for','in','return','true','false','null','break','continue'}

def tokenize(src):
    toks = []
    i = 0; n = len(src); line = 1; col = 1
    while i < n:
        c = src[i]
        if c == '\n':
            i += 1; line += 1; col = 1; continue
        if c in ' \t\r':
            i += 1; col += 1; continue
        if c == '#':
            while i < n and src[i] != '\n':
                i += 1; col += 1
            continue
        start_line, start_col = line, col
        if c in '{}()[];,':
            toks.append(Tok(c, c, start_line, start_col)); i += 1; col += 1; continue
        if c == '"':
            j = i+1; buf = ''
            while j < n and src[j] != '"':
                if src[j] == '\\' and j+1 < n:
                    esc = src[j+1]
                    buf += {'n':'\n','t':'\t','"':'"','\\':'\\','r':'\r'}.get(esc, esc)
                    j += 2; col += 2; continue
                if src[j] == '\n': line += 1; col = 1
                else: col += 1
                buf += src[j]; j += 1
            toks.append(Tok('STR', buf, start_line, start_col)); i = j+1; col += (j-i)+1; continue
        if c.isalpha() or c == '_':
            j = i
            while j < n and (src[j].isalnum() or src[j]=='_'): j += 1
            w = src[i:j]
            kind = w.upper() if w in KEYWORDS else 'IDENT'
            toks.append(Tok(kind, w, start_line, start_col))
            i = j; col += (j-i); continue
        if c.isdigit():
            j = i
            while j < n and (src[j].isdigit() or src[j]=='.'): j += 1
            toks.append(Tok('NUM', src[i:j], start_line, start_col))
            i = j; col += (j-i); continue
        two = src[i:i+2]
        if two in ('==','!=','<=','>=','&&','||','+=','-='):
            toks.append(Tok('OP', two, start_line, start_col)); i += 2; col += 2; continue
        if c in '+-*/%<>!=&|':
            toks.append(Tok('OP', c, start_line, start_col)); i += 1; col += 1; continue
        raise SyntaxError(f"Unexpected char {c!r} at line {line} col {col}")
    toks.append(Tok('EOF', None, line, col))
    return toks

# ===================== PARSER =====================
class Parser:
    def __init__(self, toks):
        self.toks = toks; self.i = 0
    def peek(self, k=0):
        idx = self.i + k
        return self.toks[idx] if idx < len(self.toks) else self.toks[-1]
    def next(self):
        t = self.toks[self.i]; self.i += 1; return t
    def expect(self, kind, val=None):
        t = self.next()
        if t.kind != kind or (val is not None and t.val != val):
            raise SyntaxError(f"Expected {kind} {val}, got {t.kind}:{t.val!r} at line {t.line}")
        return t
    def parse(self):
        stmts = []
        while self.peek().kind != 'EOF':
            stmts.append(self.stmt())
        return ('block', stmts, 1)
    def stmt(self):
        t = self.peek()
        line = t.line
        if t.kind in ('LET','CONST'):
            is_const = t.kind == 'CONST'; self.next()
            name = self.expect('IDENT').val
            init = None
            if self.peek().kind in ('=','OP') and (self.peek().val == '=' or self.peek().val == '='):
                self.next(); init = self.expr()
            elif self.peek().kind == 'OP' and self.peek().val in ('=','+=','-='):
                self.next(); init = self.expr()
            return ('let', name, init, is_const, line)
        if t.kind == 'FN':
            self.next()
            name = self.expect('IDENT').val
            self.expect('(')
            params = []
            if self.peek().kind != ')':
                params.append(self.expect('IDENT').val)
                while self.peek().kind == ',':
                    self.next(); params.append(self.expect('IDENT').val)
            self.expect(')')
            self.expect('{')
            body = self.block_until('}')
            self.expect('}')
            return ('fn', name, params, ('block', body, line), line)
        if t.kind == 'IF':
            self.next()
            cond = self.expr()
            self.expect('{'); body = self.block_until('}'); self.expect('}')
            else_body = None
            if self.peek().kind == 'ELSE':
                self.next()
                if self.peek().kind == 'IF':
                    else_body = self.stmt()
                else:
                    self.expect('{'); eb = self.block_until('}'); self.expect('}')
                    else_body = ('block', eb, self.peek().line)
            return ('if', cond, ('block', body, line), else_body, line)
        if t.kind == 'WHILE':
            self.next(); cond = self.expr()
            self.expect('{'); body = self.block_until('}'); self.expect('}')
            return ('while', cond, ('block', body, line), line)
        if t.kind == 'FOR':
            self.next()
            var = self.expect('IDENT').val
            self.expect('IN')
            iterable = self.expr()
            self.expect('{'); body = self.block_until('}'); self.expect('}')
            return ('for', var, iterable, ('block', body, line), line)
        if t.kind == 'RETURN':
            self.next()
            val = None
            if self.peek().kind not in ('}',';',) and self.peek().kind not in ('EOF',):
                val = self.expr()
            return ('return', val, line)
        if t.kind == 'PRINT':
            self.next(); return ('print', self.expr(), line)
        if t.kind == 'BREAK':
            self.next(); return ('break', line)
        if t.kind == 'CONTINUE':
            self.next(); return ('continue', line)
        if t.kind == 'IDENT':
            if self.i+1 < len(self.toks) and self.peek(1).kind in ('=','OP') and self.peek(1).val in ('=','+=','-='):
                name = self.next().val
                op = self.next().val
                val = self.expr()
                return ('assign', name, op, val, line)
            e = self.expr()
            return ('exprstmt', e, line)
        if t.kind == '{':
            self.next(); body = self.block_until('}'); self.expect('}')
            return ('block', body, line)
        e = self.expr()
        return ('exprstmt', e, line)
    def block_until(self, end):
        stmts = []
        while not (self.peek().kind == end):
            if self.peek().kind == 'EOF': break
            stmts.append(self.stmt())
        return stmts
    def expr(self): return self.or_expr()
    def or_expr(self):
        left = self.and_expr()
        while self.peek().kind == 'OP' and self.peek().val == '||':
            self.next(); right = self.and_expr(); left = ('or', left, right, self.peek().line)
        return left
    def and_expr(self):
        left = self.eq_expr()
        while self.peek().kind == 'OP' and self.peek().val == '&&':
            self.next(); right = self.eq_expr(); left = ('and', left, right, self.peek().line)
        return left
    def eq_expr(self):
        left = self.rel_expr()
        while self.peek().kind == 'OP' and self.peek().val in ('==','!='):
            op = self.next().val; right = self.rel_expr(); left = ('cmp', op, left, right, self.peek().line)
        return left
    def rel_expr(self):
        left = self.add()
        while self.peek().kind == 'OP' and self.peek().val in ('<','>','<=','>='):
            op = self.next().val; right = self.add(); left = ('cmp', op, left, right, self.peek().line)
        return left
    def add(self):
        left = self.mul()
        while self.peek().kind == 'OP' and self.peek().val in ('+','-'):
            op = self.next().val; right = self.mul(); left = ('bin', op, left, right, self.peek().line)
        return left
    def mul(self):
        left = self.unary()
        while self.peek().kind == 'OP' and self.peek().val in ('*','/','%'):
            op = self.next().val; right = self.unary(); left = ('bin', op, left, right, self.peek().line)
        return left
    def unary(self):
        if self.peek().kind == 'OP' and self.peek().val in ('-','!'):
            op = self.next().val; e = self.unary(); return ('unary', op, e, self.peek().line)
        return self.postfix()
    def postfix(self):
        e = self.primary()
        while True:
            if self.peek().kind == '[':
                self.next(); idx = self.expr(); self.expect(']'); e = ('index', e, idx, self.peek().line)
            elif self.peek().kind == '(':
                self.next()
                args = []
                if self.peek().kind != ')':
                    args.append(self.expr())
                    while self.peek().kind == ',':
                        self.next(); args.append(self.expr())
                self.expect(')')
                e = ('call', e, args, self.peek().line)
            elif self.peek().kind == '.':
                self.next(); name = self.expect('IDENT').val; e = ('attr', e, name, self.peek().line)
            else:
                break
        return e
    def primary(self):
        t = self.peek()
        if t.kind == 'NUM':
            self.next(); v = float(t.val) if '.' in t.val else int(t.val); return ('num', v, t.line)
        if t.kind == 'STR':
            self.next(); return ('str', t.val, t.line)
        if t.kind == 'TRUE':
            self.next(); return ('bool', True, t.line)
        if t.kind == 'FALSE':
            self.next(); return ('bool', False, t.line)
        if t.kind == 'NULL':
            self.next(); return ('null', t.line)
        if t.kind == 'IDENT':
            self.next(); return ('var', t.val, t.line)
        if t.kind == '(':
            self.next(); e = self.expr(); self.expect(')'); return e
        if t.kind == '[':
            self.next()
            items = []
            if self.peek().kind != ']':
                items.append(self.expr())
                while self.peek().kind == ',':
                    self.next(); items.append(self.expr())
            self.expect(']'); return ('arr', items, t.line)
        raise SyntaxError(f"Unexpected {t.kind}:{t.val!r} at line {t.line}")

# ===================== COMPILER =====================
class Compiler:
    def __init__(self):
        self.code = []
        self.consts = []
        self.names = []
    def emit(self, op, arg=None):
        self.code.append((op, arg))
    def const_index(self, v):
        for i, c in enumerate(self.consts):
            if c == v and type(c) is type(v):
                return i
        self.consts.append(v)
        return len(self.consts)-1
    def name_index(self, n):
        if n not in self.names:
            self.names.append(n)
        return self.names.index(n)
    def compile(self, node):
        k = node[0]
        if k == 'block':
            for s in node[1]:
                self.compile(s)
            return
        if k == 'let':
            if node[2] is not None:
                self.compile(node[2])
            else:
                self.emit('PUSH_NULL')
            self.emit('STORE', self.name_index(node[1]))
            if node[3]:
                self.emit('MARK_CONST', self.name_index(node[1]))
            return
        if k == 'fn':
            sub = Compiler()
            sub.emit('ENTER_SCOPE')
            for p in node[2]:
                sub.emit('PARAM', p)
            sub.compile(node[3])
            sub.emit('PUSH_NULL')
            sub.emit('RETURN')
            codeobj = (sub.code, sub.consts, sub.names, node[2])
            idx = self.const_index(('fn', codeobj))
            self.emit('MAKE_FUNC', idx)
            self.emit('STORE', self.name_index(node[1]))
            return
        if k == 'if':
            self.compile(node[1])
            jf = len(self.code); self.emit('JUMP_IF_FALSE', None)
            self.compile(node[2])
            if node[3] is not None:
                j = len(self.code); self.emit('JUMP', None)
                self.code[jf] = ('JUMP_IF_FALSE', len(self.code))
                self.compile(node[3])
                self.code[j] = ('JUMP', len(self.code))
            else:
                self.code[jf] = ('JUMP_IF_FALSE', len(self.code))
            return
        if k == 'while':
            start = len(self.code)
            self.compile(node[1])
            jf = len(self.code); self.emit('JUMP_IF_FALSE', None)
            self.compile(node[2])
            self.emit('JUMP', start)
            self.code[jf] = ('JUMP_IF_FALSE', len(self.code))
            return
        if k == 'for':
            self.compile(node[2])
            self.emit('ITER_START')
            return
        if k == 'return':
            if node[1] is not None:
                self.compile(node[1])
            else:
                self.emit('PUSH_NULL')
            self.emit('RETURN')
            return
        if k == 'print':
            self.compile(node[1]); self.emit('PRINT'); return
        if k == 'break':
            self.emit('BREAK'); return
        if k == 'continue':
            self.emit('CONTINUE'); return
        if k == 'assign':
            if node[2] == '+=':
                self.emit('LOAD', self.name_index(node[1])); self.compile(node[3]); self.emit('ADD')
            elif node[2] == '-=':
                self.emit('LOAD', self.name_index(node[1])); self.compile(node[3]); self.emit('SUB')
            else:
                self.compile(node[3])
            self.emit('STORE', self.name_index(node[1]))
            return
        if k == 'exprstmt':
            self.compile(node[1]); self.emit('POP'); return
        if k in ('num','str','bool'):
            self.emit('PUSH_CONST', self.const_index(node[1])); return
        if k == 'null':
            self.emit('PUSH_NULL'); return
        if k == 'var':
            self.emit('LOAD', self.name_index(node[1])); return
        if k == 'arr':
            for it in node[1]:
                self.compile(it)
            self.emit('BUILD_LIST', len(node[1])); return
        if k == 'bin':
            self.compile(node[2]); self.compile(node[3])
            self.emit({'+':'ADD','-':'SUB','*':'MUL','/':'DIV','%':'MOD'}[node[1]]); return
        if k == 'cmp':
            self.compile(node[2]); self.compile(node[3])
            self.emit({'==':'EQ','!=':'NE','<':'LT','>':'GT','<=':'LE','>=':'GE'}[node[1]]); return
        if k == 'and':
            self.compile(node[1]); self.emit('JUMP_IF_FALSE', None); self.compile(node[2]); return
        if k == 'or':
            self.compile(node[1]); self.emit('JUMP_IF_TRUE', None); self.compile(node[2]); return
        if k == 'unary':
            self.compile(node[2]); self.emit('NEG' if node[1]=='-' else 'NOT'); return
        if k == 'index':
            self.compile(node[1]); self.compile(node[2]); self.emit('INDEX'); return
        if k == 'attr':
            self.compile(node[1]); self.emit('ATTR', node[2]); return
        if k == 'call':
            self.compile(node[1])
            for a in node[2]:
                self.compile(a)
            self.emit('CALL', len(node[2])); return
        if k == 'condexpr':
            self.compile(node[1])
            jf = len(self.code); self.emit('JUMP_IF_FALSE', None)
            self.compile(node[2])
            j = len(self.code); self.emit('JUMP', None)
            self.code[jf] = ('JUMP_IF_FALSE', len(self.code))
            self.compile(node[3])
            self.code[j] = ('JUMP', len(self.code))
            return
        raise RuntimeError(f"Unknown node {k}")

def desugar(node):
    if not isinstance(node, tuple): return node
    k = node[0]
    if k == 'block':
        return ('block', [desugar(s) for s in node[1]], node[2])
    if k == 'for':
        var = node[1]
        itname = '__it_' + str(id(node))
        iname = '__i_' + str(id(node))
        body = node[3]
        new_body = [('let', var, ('index', ('var', itname, 0), ('var', iname, 0), 0), False, 0)] + list(body[1]) + [('assign', iname, '=', ('bin','+',('var',iname,0),('num',1,0),0),0)]
        while_node = ('while', ('cmp','<',('var',iname,0),('call',('var','len',0),[('var',itname,0)],0),0), ('block', new_body, 0), 0)
        setup = [('let', itname, desugar(node[2]), False, 0), ('let', iname, ('num',0,0), False, 0)]
        return ('block', [desugar(s) for s in setup] + [desugar(while_node)], 0)
    if k == 'fn':
        return ('fn', node[1], node[2], desugar(node[3]), node[4])
    if k == 'while':
        return ('while', desugar(node[1]), desugar(node[2]), node[3])
    if k == 'if':
        eb = desugar(node[3]) if node[3] is not None else None
        return ('if', desugar(node[1]), desugar(node[2]), eb, node[4])
    if k == 'let':
        return ('let', node[1], desugar(node[2]) if node[2] is not None else None, node[3], node[4])
    if k == 'assign':
        return ('assign', node[1], node[2], desugar(node[3]), node[4])
    if k == 'return':
        return ('return', desugar(node[1]) if node[1] is not None else None, node[2])
    if k == 'print':
        return ('print', desugar(node[1]), node[2])
    if k == 'exprstmt':
        return ('exprstmt', desugar(node[1]), node[2])
    if k in ('bin','cmp'):
        return (k, node[1], desugar(node[2]), desugar(node[3]), node[4])
    if k == 'and':
        return ('condexpr', desugar(node[1]), desugar(node[2]), ('bool', False, 0), node[3])
    if k == 'or':
        return ('condexpr', desugar(node[1]), desugar(node[1]), desugar(node[2]), node[3])
    if k == 'unary':
        return ('unary', node[1], desugar(node[2]), node[3])
    if k == 'index':
        return ('index', desugar(node[1]), desugar(node[2]), node[3])
    if k == 'call':
        return ('call', desugar(node[1]), [desugar(a) for a in node[2]], node[3])
    if k == 'arr':
        return ('arr', [desugar(x) for x in node[1]], node[2])
    if k == 'condexpr':
        return ('condexpr', desugar(node[1]), desugar(node[2]), desugar(node[3]), node[4])
    return node

def desugar_logic(node):
    return desugar(node)  # already handled in desugar

# ===================== VM =====================
class VM:
    def __init__(self, compiler, output=None):
        self.code = compiler.code
        self.consts = compiler.consts
        self.names = compiler.names
        self.stack = []
        self.envs = [{}]
        self.call_stack = []
        self.ip = 0
        self.output = output if output is not None else print
        self.builtins = {
            'print': lambda *a: self.output(' '.join(str(x) for x in a)),
            'len': lambda x: len(x),
            'push': lambda arr, v: (arr.append(v), arr)[1],
            'pop': lambda arr: arr.pop(),
            'range': lambda *a: list(range(*a)),
            'str': lambda x: str(x),
            'int': lambda x: int(x),
            'float': lambda x: float(x),
            'type': lambda x: type(x).__name__,
        }
        for k, v in self.builtins.items():
            self.envs[0][k] = v
    def run(self):
        while self.ip < len(self.code):
            op, arg = self.code[self.ip]
            self.ip += 1
            if op == 'PUSH_CONST': self.stack.append(self.consts[arg])
            elif op == 'PUSH_NULL': self.stack.append(None)
            elif op == 'POP': self.stack.pop()
            elif op == 'ADD':
                b = self.stack.pop(); a = self.stack.pop()
                self.stack.append(str(a)+str(b) if isinstance(a,str) or isinstance(b,str) else a+b)
            elif op == 'SUB':
                b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a-b)
            elif op == 'MUL':
                b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a*b)
            elif op == 'DIV':
                b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a/b)
            elif op == 'MOD':
                b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a%b)
            elif op == 'NEG': self.stack.append(-self.stack.pop())
            elif op == 'NOT': self.stack.append(not self._truthy(self.stack.pop()))
            elif op == 'EQ':
                b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a==b)
            elif op == 'NE':
                b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a!=b)
            elif op == 'LT':
                b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a<b)
            elif op == 'GT':
                b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a>b)
            elif op == 'LE':
                b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a<=b)
            elif op == 'GE':
                b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a>=b)
            elif op == 'JUMP': self.ip = arg
            elif op == 'JUMP_IF_FALSE':
                if not self._truthy(self.stack.pop()): self.ip = arg
            elif op == 'JUMP_IF_TRUE':
                v = self.stack.pop()
                if self._truthy(v): self.ip = arg; self.stack.append(v)
                else: self.stack.append(v)
            elif op == 'LOAD': self.stack.append(self._get(self.names[arg]))
            elif op == 'STORE': self._set(self.names[arg], self.stack.pop())
            elif op == 'MAKE_FUNC':
                co = self.consts[arg]; self.stack.append(('func', co[1], self.envs[-1]))
            elif op == 'ENTER_SCOPE': self.envs.append({})
            elif op == 'BUILD_LIST': self.stack.append([self.stack.pop() for _ in range(arg)][::-1])
            elif op == 'INDEX':
                idx=self.stack.pop(); obj=self.stack.pop(); self.stack.append(obj[idx])
            elif op == 'CALL':
                argc=arg; args=[self.stack.pop() for _ in range(argc)][::-1]; callee=self.stack.pop()
                if isinstance(callee, tuple) and callee[0]=='func':
                    _, codeobj, closure = callee
                    ccode, cconsts, cnames, params = codeobj
                    self.call_stack.append((self.code,self.consts,self.names,self.ip))
                    self.code, self.consts, self.names, self.ip = ccode, cconsts, cnames, 0
                    new_env = dict(closure)
                    for p,a in zip(params,args): new_env[p]=a
                    self.envs.append(new_env)
                elif callable(callee):
                    self.stack.append(callee(*args))
                else:
                    raise RuntimeError(f"Not callable: {callee}")
            elif op == 'RETURN':
                val = self.stack.pop() if self.stack else None
                if len(self.envs)>1: self.envs.pop()
                if self.call_stack:
                    self.code,self.consts,self.names,self.ip = self.call_stack.pop()
                self.stack.append(val)
            elif op == 'PRINT': self.output(str(self.stack.pop()))
            elif op == 'HALT': break
            else: raise RuntimeError(f"Unknown op {op}")
    def _truthy(self, v):
        if v is None: return False
        if isinstance(v,bool): return v
        if isinstance(v,(int,float)): return v!=0
        if isinstance(v,(str,list)): return len(v)>0
        return True
    def _get(self, name):
        for env in reversed(self.envs):
            if name in env: return env[name]
        if name in self.builtins: return self.builtins[name]
        raise NameError(f"Undefined variable '{name}'")
    def _set(self, name, val):
        for env in reversed(self.envs):
            if name in env: env[name]=val; return
        self.envs[0][name]=val

def compile_source(src):
    toks = tokenize(src)
    ast = Parser(toks).parse()
    ast = desugar(ast)
    comp = Compiler()
    comp.compile(ast)
    comp.emit('HALT')
    return comp, ast

def run_source(src, output=None):
    comp, ast = compile_source(src)
    vm = VM(comp, output=output)
    vm.run()
    return vm

def check_source(src):
    Parser(tokenize(src)).parse()
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: gosd.py <run|check> [file]"); sys.exit(1)
    cmd = sys.argv[1]
    if cmd in ('run','check') and len(sys.argv) >= 3:
        with open(sys.argv[2], encoding='utf-8') as f:
            src = f.read()
        if cmd == 'check':
            check_source(src); print("OK: syntax valid")
        else:
            run_source(src)
