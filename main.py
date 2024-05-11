from flask import Flask, render_template, request, jsonify
from fractions import Fraction
import sympy as sp
import IPython 
from IPython.display import Math
from sympy import *
import os
import math
import re
import sympy.plotting as sym_plot

app = Flask(__name__)
app.config['STATIC_FOLDER'] = '.'

init_printing()

def parse_trig(match):
    func, arg = match.groups()
    if func == 'sin':
        return f'math.sin({arg})'
    elif func == 'cos':
        return f'math.cos({arg})'
    elif func == 'tan':
        return f'math.tan({arg})'

def convert_equation(equation):
    equation = re.sub(r'\++', '+', equation)
    equation = re.sub(r'\+/', '/', equation)
    equation = re.sub(r'/+', '/', equation)
    equation = re.sub(r'\*+', '*', equation)
    equation = re.sub(r'\+\*', '*', equation)
    equation = re.sub(r'\*\+', '*', equation)
    equation = re.sub(r'\+\(', '(', equation)
    equation = re.sub(r'\(\+', '(', equation)
    equation = re.sub(r'\+\)', ')', equation)
    equation = re.sub(r'\)\+', ')', equation)
    equation = equation.replace("^", "**")
    equation = equation.replace("(", " ( ")  
    equation = equation.replace(")", " ) ")
    equation = equation.replace("÷", "/")
    equation = equation.replace("/", "/")

    equation = re.sub(r'(\d+)(\w)', r'\1*\2', equation)
    equation = re.sub(r'([^\+])\(', r'\1*\(', equation)
    equation = re.sub(r'(sin|cos|tan)\((.*?)\)', parse_trig, equation)

    print("equation3", equation)

    return equation

def parse_fraction(s):
    num, denom = s.split("/")
    return Fraction(int(num), int(denom))

def format_output(equation):
    equation_str = str(equation)
    equation_str = equation_str.replace("**", "^")
    equation_str = equation_str.replace("^0", "⁰")
    equation_str = equation_str.replace("^1", "¹")
    equation_str = equation_str.replace("^2", "²")
    equation_str = equation_str.replace("^3", "³")
    equation_str = equation_str.replace("^4", "⁴")
    equation_str = equation_str.replace("^5", "⁵")
    equation_str = equation_str.replace("^6", "⁶")
    equation_str = equation_str.replace("^7", "⁷")
    equation_str = equation_str.replace("^8", "⁸")
    equation_str = equation_str.replace("^9", "⁹")
    equation_str = re.sub(r'\(([^()]+)\)', r'\1', equation_str)
    equation_str = re.sub(r'(\d+)\*(\w)', r'\1\2', equation_str)
    equation_str = equation_str.replace("sqrt", "√")
    equation_str = re.sub(r'(\w+)\*I', r'i\1', equation_str)
    equation_str = re.sub(r'√\((\w+)\*I\)', r'i√(\1)', equation_str)
    equation_str = re.sub(r'(\d+)\s+(\d+)i', r'\1+\2i', equation_str)
    return equation_str

@app.route('/')
def index():
    return render_template('index.html')

def iflfactor(eq):
    e = Mul(*[horner(e) if e.is_Add else e for e in
        Mul.make_args(factor_terms(expand(eq)))])
    r, e = cse(e)
    s = [ri[0] for ri in r]
    e = Mul(*[collect(ei.expand(), s) if ei.is_Add else ei for ei in
        Mul.make_args(e[0])]).subs(r)
    return e

class Polynomial:
    def __init__(self,val):
        if type(val) == type([]):
            self.plist = val
        elif type(val) == type(''):
            self.plist = parse_string(val)
        else:
            raise "Unknown argument to Polynomial: %s" % val
        return
    
    def __neg__(self): return -1*self
    def __repr__(self): return tostring(self.plist)

def parse_string(str=None):
    trigpat = re.compile('([a-z]{3})(\([^)]+\))')
    termpat = re.compile('([-+]?\s*\d*\.?\d*)(x?\^?\d?)')
    left, right = str.split("=") if "=" in str else str, ""
    res_dict = {}
    
    trig_matches = trigpat.findall(left)
    for func, arg in trig_matches:
        if func == 'sin':
            left = left.replace(f'{func}({arg})', f'math.sin({arg})')
        elif func == 'cos':
            left = left.replace(f'{func}({arg})', f'math.cos({arg})')
        elif func == 'tan':
            left = left.replace(f'{func}({arg})', f'math.tan({arg})')
    
    for n,p in termpat.findall(left):
        n,p = n.strip(),p.strip()
        if not n and not p: continue
        n,p = parse_n(n),parse_p(p)
        if p in res_dict: res_dict[p] += n
        else: res_dict[p] = n
    if right!= "":
        for n,p in termpat.findall(right):
            n,p = n.strip(),p.strip()
            if not n and not p: continue
            n,p = parse_n(n),parse_p(p)
            if p in res_dict: res_dict[p] -= n
            else: res_dict[p] = -n
    
    highest_order = max(res_dict.keys())
    res = [0]*(highest_order+1)
    for key,value in res_dict.items(): res[key] = value
    return res
def parse_n(str):
    if not str: return 1
    elif str == '-': return -1
    elif str == '+': return 1
    return eval(str)

def parse_p(str):
    pat = re.compile('x\^?(\d)?')
    if not str: return 0
    res = pat.findall(str)[0]
    if not res: return 1
    return int(res)

def strip_leading_zeros(p):
    for i in range(len(p)-1,-1,-1):
        if p[i]: break
    return p[:i+1]

def tostring(p):
    p = strip_leading_zeros(p)
    str = []
    for i in range(len(p)-1,-1,-1):
        if p[i]:
            if i < len(p)-1:
                if p[i] >= 0: str.append('+')
                else: str.append('-')
                str.append(tostring_term(abs(p[i]),i))
            else:
                str.append(tostring_term(p[i],i))
    return ' '.join(str)

def tostring_term(c,i):
    if i == 1:
        if c == 1: return 'x'
        elif c == -1: return '-x'
        return "%sx" % c
    elif i: 
        if c == 1: return "x^%d" % i
        elif c == -1: return "-x^%d" % i
        return "%sx^%d" % (c,i)
    return "%s" % c


@app.route('/calculate', methods=['POST'])
def calculate():
    print(request.form["equation"])
    equation_str = request.form['equation']

    equation_str = str(Polynomial(parse_string(equation_str)))
    equation_str = convert_equation(equation_str)
    fractions = re.findall(r"(\d+)/(\d+)", equation_str)
    for num, denom in fractions:
        fraction = parse_fraction(f"{num}/{denom}")
        equation_str = equation_str.replace(f"{num}/{denom}", str(fraction))

    equation = sp.sympify(equation_str, evaluate=False)
    var_set = set(equation.free_symbols)
    decimal = False
    if request.form.get('show_decimal') == 'on':
        decimal = True
    print(decimal)
        
    if len(var_set) == 1:
        var = list(var_set)[0]
    else:
        var = list(var_set)[0]
    result = ""
    if request.form['button'] == 'Solve using Quadratic Formula':
        sol = sp.solve(equation, var, quadratic=True)
        if decimal == True:
            sol = [s.evalf() for s in sol]
        sol = sp.latex(sol)
        
        result = sol
    elif request.form['button'] == 'Solve using Isolation [x]':
        var_str = request.form['var']
        if var_str!= "":
            var = sp.Symbol(var_str)
        sol = sp.solve(equation, var)
        if decimal == True:
            sol = [s.evalf() for s in sol]
        sol = sp.latex(sol)
        
        result = sol
    elif request.form['button'] == 'Solve using Factorization':
        sol = iflfactor(equation)
        sol = factor(sol)
        sol = sp.latex(sol)
        result = sol    
    elif request.form['button'] == 'Simplify':
        sol = sp.simplify(equation)
        sol = sp.latex(sol)
        
        result = sol
    elif request.form['button'] == 'Find Max/Min':
        der = sp.diff(equation, var)
        crit_pts = sp.solve(der, var)
        if decimal == True:
            crit_pts = [s.evalf() for s in crit_pts]
        sec_der = sp.diff(der, var)
        max_min = []
        for pt in crit_pts:
            func_val = equation.subs(var, pt)
            sec_der_val = sec_der.subs(var, pt)
            kind = ""
            try:
                if sec_der_val > 0:
                    kind = 'min'
                elif sec_der_val < 0:
                    kind = 'max'
                else:
                    third_der = sp.diff(der, var, 3)
                    if third_der.subs(var, pt)!= 0:
                        kind = 'absolute'
                    else:
                        epsilon = 0.001
                        left_val = equation.subs(var, pt - epsilon)
                        right_val = equation.subs(var, pt + epsilon)
                        if left_val < func_val and right_val < func_val:
                            kind = 'min'
                        elif left_val > func_val and right_val > func_val:
                            kind = 'max'
                        else:
                            kind = 'local'
            except:
                kind = "NaN"
            pt = sp.latex(pt)
            func_val = sp.latex(func_val)
            if kind == 'absolute':
                kind = f"x={pt} ({kind}), f({pt}) = {func_val}"
            else:
                sec_der_val = sp.latex(sec_der_val)
                kind = f"x={pt} ({kind}), f({pt}) = {func_val}, f''({pt}) = {(sec_der_val)}"
            max_min.append(kind)
        to_print = ", and ".join(max_min)
        if to_print.startswith(', and '):
            to_print = to_print[6:]
        to_print = to_print + "." 
        print(to_print)
        result = to_print
    elif request.form['button'] == 'Find Inflexion Points': 
        der = sp.diff(equation, var)
        sec_der = sp.diff(der, var)
        inflexion_pts = sp.solve(sec_der, var)
        if decimal == True:
            inflexion_pts = [s.evalf() for s in inflexion_pts]

        y_coords = [equation.subs(var, pt) for pt in inflexion_pts]
        amountofcoords = len(inflexion_pts)
        print(inflexion_pts, amountofcoords)
        inflexion_pts = str(inflexion_pts)
        new_coords = []
        for i in range(amountofcoords):
            new_coords.append(f"({sp.latex(inflexion_pts[i])}, {y_coords[i]}) ")
            print(new_coords)
        all_points = "".join(new_coords)
        result = all_points
    elif request.form['button'] == 'Find Derivative [#]':
        varse = "".join(str(key) for key in var_set)
        try: 
            num_derivatives = int(request.form['var'])
            derivatives = {}
            for i, var in enumerate(var_set):
                der = sp.diff(equation, var, num_derivatives)
                der = format_output(der)
                deri = r'\frac{d^{' + str(num_derivatives) + r'}y}{d' + str(var) + r'^{' + str(num_derivatives) + r'}}'
                if i == 0:
                    derivatives[var] = f"{deri}={der}"
                else:
                    derivatives[var] = f"+{der}"
                print(i, var, deri, der)
            result = "".join(derivatives[var] for var in var_set)
        except:
            num_derivatives = 1
            derivatives = {}
            for i, var in enumerate(var_set):
                der = sp.diff(equation, var, num_derivatives)
                der = format_output(der)
                deri = r'\frac{dy}{d' + str(var) + r'}'
                if i == 0:
                    derivatives[var] = f"{deri}={der}"
                else:
                    derivatives[var] = f"+{der}"
                print(i, var, deri, der)
            result = "".join(derivatives[var] for var in var_set)

    elif request.form['button'] == 'Find Zeroes':
        x_vals = sp.solve(equation, var)
        if decimal == True:
            x_vals = [s.evalf() for s in x_vals]
        x_vals = sp.latex(x_vals)
        
        result = x_vals

    elif request.form['button'] == 'Limits [x=#]':
        
        vare = request.form['var']
        if not vare:
            vare = 1
        if vare in ["inf", "infinity", "∞", "-inf", "-infinity", "-∞"]:
            valueini, value2ini = ("∞", "-∞") if "-" not in vare else ("-∞", "∞")
            value, value2 = float('inf'), -float('inf')
        else:
            value = int(vare) if type(vare) == str else float(vare)
            valueini, value2ini = str(value), str(-value)
            value2 = -value

        limplus = sp.limit(equation, var, value)
        limminus = sp.limit(equation, var, value2)

        if decimal:
            try:
                limplus, limminus = [s.evalf() for s in limplus], [s.evalf() for s in limminus]
            except:
                limplus, limminus = limplus, limminus

        limplus, limminus = sp.latex(limplus), sp.latex(limminus)
        lim = limplus if limminus == limplus else "None"

        equation = sp.latex(equation)
        response = fr"\underset{{x \to {valueini}}}{{\lim}}f({equation})={limplus}, \underset{{x \to {value2ini}}}{{\lim}}f({equation})={limminus}, \underset{{x \to \pm {valueini}}}{{\lim}}f({equation})={lim}"
        result = response

    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
