# -*- coding: utf-8 -*-
import re
import sympy

from colorama import Fore

from plugin import alias, plugin


@alias('calc', 'evaluate')
@plugin('calculate')
def calculate(ausis, s):
    """
    ausis will get your calculations done!
    -- Example:
        calculate 3 + 5
    """
    tempt = s.replace(" ", "")
    if len(tempt) > 1:
        calc(ausis, tempt, formatter=lambda x: x)
    else:
        ausis.say("Error: Not in correct format", Fore.RED)


@plugin('solve')
def solve(ausis, s):
    """
    Prints where expression equals zero
    -- Example:
        solve x**2 + 5*x + 3
        solve x + 3 = 5
    """
    x = sympy.Symbol('x')

    def _format(solutions):
        if solutions == 0:
            return "No solution!"
        ret = ''
        for count, point in enumerate(solutions):
            if x not in point:
                return "Please use 'x' in expression."
            x_value = point[x]
            ret += "{}. x: {}\n".format(count, x_value)
        return ret

    def _calc(expr):
        return sympy.solve(expr, x, dict=True)

    s = remove_equals(ausis, s)
    calc(ausis, s, calculator=_calc, formatter=_format, do_evalf=False)


@plugin('equations')
def equations(ausis, term):
    """
    Solves linear equations system

    Use variables: a, b, c, ..., x, y,z

    Example:

    ~> Hi, what can I do for you?
    equations
    1. Equation: x**2 + 2y - z = 6
    2. Equation: (x-1)(y-1) = 0
    3. Equation: y**2 - x -10 = y**2 -y
    4. Equation:
    [{x: -9, y: 1, z: 77}, {x: 1, y: 11, z: 17}]

    """
    a, b, c, d, e, f, g, h, i, j, k, l, m = sympy.symbols(
        'a,b,c,d,e,f,g,h,i,j,k,l,m')
    n, o, p, q, r, s, t, u, v, w, x, y, z = sympy.symbols(
        'n,o,p,q,r,s,t,u,v,w,x,y,z')

    equations = []
    count = 1
    user_input = ausis.input('{}. Equation: '.format(count))
    while user_input != '':
        count += 1
        user_input = format_expression(user_input)
        user_input = remove_equals(ausis, user_input)
        equations.append(user_input)
        user_input = ausis.input('{}. Equation: '.format(count))

    calc(
        ausis,
        term,
        calculator=lambda expr: sympy.solve(
            equations,
            dict=True))


@plugin('factor')
def factor(ausis, s):
    """
    ausis will factories
    -- Example:
        factor x**2-y**2
    """
    tempt = s.replace(" ", "")
    if len(tempt) > 1:
        calc(ausis, tempt, formatter=sympy.factor)
    else:
        ausis.say("Error: Not in correct format", Fore.RED)


@alias("curve plot")
@plugin('plot')
def plot(ausis, s):
    """
    Plot graph
    -- Example:
        plot x**2
        plot y=x(x+1)(x-1)
    """
    def _plot(expr):
        sympy.plotting.plot(expr)
        return ""

    if len(s) == 0:
        ausis.say("Missing parameter: function (e.g. call 'plot x**2')")
        return

    s = remove_equals(ausis, s)
    try:
        calc(ausis, s, calculator=solve_y, formatter=_plot, do_evalf=False)
    except ValueError:
        ausis.say("Cannot plot...", Fore.RED)
    except OverflowError:
        ausis.say("Cannot plot - values probably too big...")


@plugin('limit')
def limit(ausis, s):
    """
    Prints limit to +/- infinity or to number +-. Use 'x' as variable.
    -- Examples:
        limit 1/x
        limit @1 1/(1-x)
        limit @1 @2 1/((1-x)(2-x))
    """
    def try_limit(term, x, to, directory=''):
        try:
            return sympy.Limit(term, x, to, directory).doit()
        except sympy.SympifyError:
            return 'Error'
        except NotImplementedError:
            return "Sorry, cannot solve..."

    if s == '':
        ausis.say("Usage: limit TERM")
        return

    s_split = s.split()
    limit_to = []
    term = ""
    for token in s_split:
        if token[0] == '@':
            if token[1:].isnumeric():
                limit_to.append(int(token[1:]))
            else:
                ausis.say("Error: {} Not a number".format(
                    token[1:]), Fore.RED)
        else:
            term += token

    term = remove_equals(ausis, term)
    term = format_expression(term)

    try:
        term = solve_y(term)
    except (sympy.SympifyError, TypeError):
        ausis.say('Error, not a valid term')
        return

    x = sympy.Symbol('x')

    # infinity:
    ausis.say("lim ->  ∞\t= {}".format(try_limit(term,
                                                  x, +sympy.S.Infinity)), Fore.BLUE)
    ausis.say("lim -> -∞\t= {}".format(try_limit(term,
                                                  x, -sympy.S.Infinity)), Fore.BLUE)

    for limit in limit_to:
        limit_plus = try_limit(term, x, limit, directory="+")
        limit_minus = try_limit(term, x, limit, directory="-")

        ausis.say("lim -> {}(+)\t= {}".format(limit, limit_plus), Fore.BLUE)
        ausis.say("lim -> {}(-)\t= {}".format(limit, limit_minus), Fore.BLUE)


def remove_equals(ausis, equation):
    """
    User should be able to input equations like x + y = 1.
    SymPy only accepts equations like: x + y - 1 = 0.
    => This method Finds '=' and move everything beyond to left side
    """
    split = equation.split('=')
    if len(split) == 1:
        return equation
    if len(split) != 2:
        ausis.say("Warning! More than one = detected!", Fore.RED)
        return equation

    return "{} - ({})".format(split[0], split[1])


def format_expression(s):
    s = str.lower(s)
    s = s.replace("power", "**")
    s = s.replace("plus", "+")
    s = s.replace("minus", "-")
    s = s.replace("dividedby", "/")
    s = s.replace("by", "/")
    s = s.replace("^", "**")

    # Insert missing * commonly omitted
    # 2x -> 2*x
    p = re.compile('(\\d+)([abcxyz])')
    s = p.sub(r'\1*\2', s)

    # x(... -> x*(...
    p = re.compile('([abcxyz])\\(')
    s = p.sub(r'\1*(', s)

    # (x-1)(x+1) -> (x-1)*(x+1)
    # x(... -> x*(...
    s = s.replace(")(", ")*(")

    return s


def solve_y(s):
    if 'y' in s:
        y = sympy.Symbol('y')
        try:
            results = sympy.solve(s, y)
        except NotImplementedError:
            return 'unknown'
        if len(results) == 0:
            return '0'
        else:
            return results[0]
    else:
        return solve_y("({}) -y".format(s))


def calc(ausis, s, calculator=sympy.sympify, formatter=None, do_evalf=True):
    s = format_expression(s)
    try:
        result = calculator(s)
    except sympy.SympifyError:
        ausis.say("Error: Something is wrong with your expression", Fore.RED)
        return
    except NotImplementedError:
        ausis.say("Sorry, cannot solve", Fore.RED)
        return

    if formatter is not None:
        result = formatter(result)

    if do_evalf:
        result = result.evalf()

    ausis.say(str(result), Fore.BLUE)


@alias("curve sketch")
@plugin('curvesketch')
def curvesketch(ausis, s):
    """
    Prints useful information about a graph of a function.
    * Limit
    * Intersection x/y axis
    * Derivative and Integral
    * Minima / Maxima / Turning point
    -- Example:
        curve sketch y=x**2+10x-5
        curve sketch y=sqrt((x+1)(x-1))
        curve sketch y=1/3x**3-2x**2+3x
    """
    if len(s) == 0:
        ausis.say(
            "Missing parameter: function (e.g. call 'curve sketch y=x**2+10x-5')")
        return

    def section(ausis, headline):
        ausis.say("\n{:#^50}".format(" {} ".format(headline)), Fore.MAGENTA)

    term = remove_equals(ausis, s)
    term = format_expression(term)
    term = solve_y(term)

    def get_y(x_val, func=term):
        x = sympy.Symbol('x')
        return func.evalf(subs={x: x_val})

    section(ausis, s)

    section(ausis, "Graph")
    ausis.eval('plot {}'.format(s))

    section(ausis, "Limit")
    ausis.eval('limit {}'.format(term))

    section(ausis, "Intersection x-axis")
    ausis.eval('solve {}'.format(term))

    section(ausis, "Intersection y-axis")
    ausis.say(str(get_y(0).round(9)), Fore.BLUE)

    section(ausis, "Factor")
    ausis.eval('factor {}'.format(term))

    section(ausis, "Derivative")
    x = sympy.Symbol('x')
    derivative_1 = sympy.Derivative(term, x).doit()
    derivative_2 = sympy.Derivative(derivative_1, x).doit()
    derivative_3 = sympy.Derivative(derivative_2, x).doit()
    ausis.say("1. Derivative: {}".format(derivative_1), Fore.BLUE)
    ausis.say("2. Derivative: {}".format(derivative_2), Fore.BLUE)
    ausis.say("3. Derivative: {}".format(derivative_3), Fore.BLUE)

    section(ausis, "Integral")
    ausis.say("F(x) = {} + t".format(sympy.Integral(term, x).doit()), Fore.BLUE)

    section(ausis, "Maxima / Minima")
    try:
        critical_points = sympy.solve(derivative_1)
    except NotImplementedError:
        ausis.say("Sorry, cannot solve...", Fore.RED)
        critical_points = []

    for x in critical_points:
        y = str(get_y(x).round(9))

        try:
            isminmax = float(get_y(x, func=derivative_2))
        except ValueError:
            isminmax = None
        except TypeError:
            # probably complex number
            isminmax = None

        if isminmax is None:
            minmax = "unknown"
        elif isminmax > 0:
            minmax = "Minima"
        elif isminmax < 0:
            minmax = "Maxima"
        else:
            minmax = "/"

        ausis.say("({}/{}) : {}".format(x, y, minmax), Fore.BLUE)

    section(ausis, "Turning Point")
    try:
        critical_points = sympy.solve(derivative_2)
    except NotImplementedError:
        ausis.say("Sorry, cannot solve...", Fore.RED)
        critical_points = []

    for x in critical_points:
        y = get_y(x)

        try:
            is_turning_point = float(get_y(x, func=derivative_3))
        except ValueError:
            is_turning_point = -1

        if is_turning_point != 0:
            ausis.say("({}/{})".format(x, y.round(9)), Fore.BLUE)

    section(ausis, "")
