from symbol_library import generate_symbol_library, SymType
import numpy as np
from hvae_utils import load_config_file
from ProGED.generators import GeneratorGrammar
from tree import Node
from expression_set_generation import tokens_to_tree, generate_grammar
import json
from itertools import combinations

# NOTE!!!! This file ws not written in the original HVAE code. It was written by me to generate the rate laws for the HVAE model.

def generate_expressions(grammar, number_of_expressions, symbol_objects, has_constants=True, max_depth=7):
    generator = GeneratorGrammar(grammar)
    expression_set = set()
    expressions = []
    # output = "trees"
    attempt = 0
    while len(expression_set) < number_of_expressions:
        if len(expression_set) % 500 == 0:
            print(f"Unique expressions generated so far: {len(expression_set)}")
        expr = generator.generate_one()[0]
        if has_constants:
            pass
        
        
        if True:
            expr_str = " ".join(expr)
        else: 
            expr_str = "".join(expr)

        if attempt > 10000:
            # pass
            break

        if expr_str in expression_set:
            attempt += 1
            continue
        
      
        try:
            expr_tree = tokens_to_tree(expr, symbol_objects)
            if expr_tree.height() > max_depth:
                continue
            # print(expr_str)
            expressions.append(expr_tree)
            expression_set.add(expr_str)
            attempt = 0
        except:
            continue

    return expressions, expression_set


def generate_simple_rate_grammar(symbols, max_tree_height=7):
    grammar = ""
    operators = {}
    functions = []
    powers = []
    variables = []
    constants = False

    for symbol in symbols:
        if symbol["type"].value == SymType.Operator.value:
            if symbol["precedence"] in operators:
                operators[symbol["precedence"]].append(symbol["symbol"])
            else:
                operators[symbol["precedence"]] = [symbol["symbol"]]
        elif symbol["type"].value == SymType.Fun.value and symbol["precedence"] < 0:
            powers.append(symbol["symbol"])
        elif symbol["type"].value == SymType.Fun.value:
            functions.append(symbol["symbol"])
        elif symbol["type"].value == SymType.Var.value:
            variables.append(symbol["symbol"])
        elif symbol["type"].value == SymType.Const.value:
            constants = True
        else:
            raise Exception("Error during generation of the grammar")
    
    grammar += f"E0 -> 'C' '*' F0 [1.0]\n"

    # to accomdata a given max tree height and use the general form k * Ca ^Pa * Cb ^ Pb .....
    # we need to know how many times a concentration can be multipied and still be represented by at 
    # least the max tree height. This Number n is given by max_tree_height - 2 = 2*n + n-1     (because k, * are always there)
    ns = int((max_tree_height-2+1)/3)
    if len(variables) < ns:
        ns = len(variables)
    

    prob_n = 1/ns
    for n in range(ns):
        grammar +=f"F0 -> X{str(n+1)} [{prob_n}]\n"

        combs = list(combinations(variables, n+1))
        if len(combs) == 0:
            break
        prob_comb = 1/len(combs)
        for comb in combs:
            string = ""
            for var in comb:
                string += f"{var} "
                if var != comb[-1]:
                    string += f"'*' "  
            grammar += f"X{str(n+1)} -> {string}[{prob_comb}]\n"    
    
    for var in variables:
        grammar += f"{var} -> '{var}' [0.7]\n"
        grammar += f"{var} -> '{var}' P0 [0.3]\n"

    powers = sorted(powers)
    # decreasing probability for exponent. prob_i = 1/exponent_i. 
    power_probs = [1/(1+int(p[1:])) for p in powers]
    # and then normalized to be equal to 1 again at the end
    power_probs = np.array(power_probs) / sum(power_probs)
    for p, prob in zip(powers, power_probs):
        grammar += f"P0 -> '{p}' [{prob}]\n"
    
    return grammar 

def generate_rev_rate_grammar(symbols, max_tree_height=7):
    grammar = ""
    operators = {}
    functions = []
    powers = []
    variables = []
    constants = False

    for symbol in symbols:
        if symbol["type"].value == SymType.Operator.value:
            if symbol["precedence"] in operators:
                operators[symbol["precedence"]].append(symbol["symbol"])
            else:
                operators[symbol["precedence"]] = [symbol["symbol"]]
        elif symbol["type"].value == SymType.Fun.value and symbol["precedence"] < 0:
            powers.append(symbol["symbol"])
        elif symbol["type"].value == SymType.Fun.value:
            functions.append(symbol["symbol"])
        elif symbol["type"].value == SymType.Var.value:
            variables.append(symbol["symbol"])
        elif symbol["type"].value == SymType.Const.value:
            constants = True
        else:
            raise Exception("Error during generation of the grammar")
    
    grammar += f"E0 -> 'C' '*' '(' F0 '-' F0 '/' 'C' ')'  [1.0]\n"

    # to accomdata a given max tree height and use the general form k * Ca ^Pa * Cb ^ Pb .....
    # we need to know how many times a concentration can be multipied and still be represented by at 
    # least the max tree height. This Number n is given by max_tree_height - 2 = 2*n + n-1     (because k, * are always there)
    ns = int((max_tree_height-2+1)/3)
    if len(variables) < ns:
        ns = len(variables)
    
    prob_n = 1/ns
    for n in range(ns):
        grammar +=f"F0 -> X{str(n+1)} [{prob_n}]\n"

        combs = list(combinations(variables, n+1))
        if len(combs) == 0:
            break
        prob_comb = 1/len(combs)
        for comb in combs:
            string = ""
            for var in comb:
                string += f"{var} "
                if var != comb[-1]:
                    string += f"'*' "  
            grammar += f"X{str(n+1)} -> {string}[{prob_comb}]\n"    
    
    for var in variables:
        grammar += f"{var} -> '{var}' [0.7]\n"
        grammar += f"{var} -> '{var}' P0 [0.3]\n"

    powers = sorted(powers)
    # decreasing probability for exponent. prob_i = 1/exponent_i. 
    power_probs = [1/(1+int(p[1:])) for p in powers]
    # and then normalized to be equal to 1 again at the end
    power_probs = np.array(power_probs) / sum(power_probs)
    for p, prob in zip(powers, power_probs):
        grammar += f"P0 -> '{p}' [{prob}]\n"
    
    return grammar 

def generate_cplx_rate_grammar(symbols, max_tree_height=7):
    grammar = ""
    operators = {}
    functions = []
    powers = []
    variables = []
    constants = False

    for symbol in symbols:
        if symbol["type"].value == SymType.Operator.value:
            if symbol["precedence"] in operators:
                operators[symbol["precedence"]].append(symbol["symbol"])
            else:
                operators[symbol["precedence"]] = [symbol["symbol"]]
        elif symbol["type"].value == SymType.Fun.value and symbol["precedence"] < 0:
            powers.append(symbol["symbol"])
        elif symbol["type"].value == SymType.Fun.value:
            functions.append(symbol["symbol"])
        elif symbol["type"].value == SymType.Var.value:
            variables.append(symbol["symbol"])
        elif symbol["type"].value == SymType.Const.value:
            constants = True
        else:
            raise Exception("Error during generation of the grammar")
    
    grammar += f"E0 -> 'C' '*' F0 '/' '(' 'C' '+' A0 ')' [0.5]\n"
    grammar += f"E0 -> 'C' '*' F0 '/' '(' 'C' '+' B0 ')' [0.5]\n"

    grammar += f"A0 -> A1 [0.5]\n"
    grammar += f"A0 -> A1 '/' A1 [0.5]\n"
    grammar += f"A1 -> V0 '*' A1 [0.2]\n"
    grammar += f"A1 -> V0 [0.8] \n"
    
    grammar += f"B0 -> 'C' '*' V0 '+' B0 [0.2]\n"
    grammar += f"B0 -> 'C' '*' V0 [0.8]\n"

    prob_var = 1/len(variables)
    for var in variables:
        grammar += f"V0 -> '{var}' [{prob_var}]\n"

    # to accomdata a given max tree height and use the general form k * Ca ^Pa * Cb ^ Pb .....
    # we need to know how many times a concentration can be multipied and still be represented by at 
    # least the max tree height. This Number n is given by max_tree_height - 2 = 2*n + n-1     (because k, * are always there)
    ns = int((max_tree_height-2+1)/3)
    if len(variables) < ns:
        ns = len(variables)

        
    prob_n = 1/ns
    for n in range(ns):
        grammar +=f"F0 -> X{str(n+1)} [{prob_n}]\n"

        combs = list(combinations(variables, n+1))
        if len(combs) == 0:
            break
        prob_comb = 1/len(combs)
        for comb in combs:
            string = ""
            for var in comb:
                string += f"{var} "
                if var != comb[-1]:
                    string += f"'*' "  
            grammar += f"X{str(n+1)} -> {string}[{prob_comb}]\n"    
    
    for var in variables:
        grammar += f"{var} -> '{var}' [0.7]\n"
        grammar += f"{var} -> '{var}' P0 [0.3]\n"

    powers = sorted(powers)
    # decreasing probability for exponent. prob_i = 1/exponent_i. 
    power_probs = [1/(1+int(p[1:])) for p in powers]
    # and then normalized to be equal to 1 again at the end
    power_probs = np.array(power_probs) / sum(power_probs)
    for p, prob in zip(powers, power_probs):
        grammar += f"P0 -> '{p}' [{prob}]\n"
    
    return grammar 

def create_rate_law(type = None, num_expressions = 1000,):
    # define hyperparamters for the equation generation
    
    symbols = ["-", "+", "/", "*", "^2", "^3", "^4", "^5"]
    num_variables = 3
    has_constants = True
    # num_expressions = 1000
    max_tree_height = 7

    # possible to also inlcude "^" symbol. I bet we could make "^"N where N -> "1", "2" etc...
    sy_lib = generate_symbol_library(num_variables, symbols, has_constants)
    
    # add symbols to Node so that when a tree is created later, that the Node knows what is possible
    Node.add_symbols(sy_lib)
    # Create a symbol object dicitonary (why?)HVAEcond
    so = {s["symbol"]: s for s in sy_lib}

    if "sim" in type:
        grammar = generate_simple_rate_grammar(sy_lib, max_tree_height)
    elif "rev" in type:
        grammar = generate_rev_rate_grammar(sy_lib, max_tree_height)
    elif "cplx" in type:
        grammar = generate_cplx_rate_grammar(sy_lib, max_tree_height)
    # print(grammar)

    expressions, expression_strs = generate_expressions(grammar, num_expressions, so, has_constants, 
                                                        max_depth=max_tree_height)
    # print(expression_strs)
    return expressions

def create_rnd_math(num_expressions = 3000):
    symbols = ["-", "+", "/", "*", "^2", "^3", "^4", "^5",  "sin", "cos", "sqrt"]
    num_variables = 3
    has_constants = True
    # num_expressions = 3000
    max_tree_height = 20
    sy_lib = generate_symbol_library(num_variables, symbols, has_constants)
    
    # add symbols to Node so that when a tree is created later, that the Node knows what is possible
    Node.add_symbols(sy_lib)
    # Create a symbol object dicitonary (why?)
    so = {s["symbol"]: s for s in sy_lib}
    grammar = generate_grammar(sy_lib)
    expressions, expression_strs = generate_expressions(grammar, num_expressions, so, has_constants, max_depth=max_tree_height)
    return expression_strs

if __name__ == "__main__":
    expressions = create_rate_law('sim')
    expr_dict = [tree.to_dict() for tree in expressions]

    save_path = "./HVAE/data/expression_sets/sim_rate_laws.json"
    if save_path != "":
        with open(save_path, "w") as file:
            json.dump(expr_dict, file)


    print("done")

