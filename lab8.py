#!/usr/bin/env python3
"""6.009 Lab 8: Carlae (LISP) Interpreter"""

import doctest

# NO ADDITIONAL IMPORTS!


###########################
# Carlae-related Exceptions #
###########################


class CarlaeError(Exception):
    """
    A type of exception to be raised if there is an error with a Carlae
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class CarlaeSyntaxError(CarlaeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class CarlaeNameError(CarlaeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class CarlaeEvaluationError(CarlaeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    CarlaeNameError.
    """

    pass

class Environment:
    """
    Class for enviornment diagrams, to hold the parents of the current enviornments 
    and the bindings (dictionary) which holds the variable and its value
    """
    
    #parent and bindings 
    def __init__(self, parent, bindings):
        self.parent = parent
        self.bindings = bindings
    
    def get_var(self, var):
        """
        Parameters
        ----------
        var : str
            variable which is attached to a variable

        Raises
        ------
        CarlaeNameError
            Raised if theres not a parent and therefore the binding does not 
            exist

        Returns
        -------
        val
            the value of the var passed in if its within the enviornment 
        """
        if var in self.bindings:
            return self.bindings[var]
        else:
            if self.parent != None:
                return self.parent.get_var(var)
            else:
                raise CarlaeNameError("No parent, binding DNE")
                
    def __contains__(self, var):
        """
        Check if the enviornment contains the var passed in the parameter
        Takes in a symbol(variable)
        Returns True if the variable is in the enviornment and returns False
        otherwise
        """
        if var in self.bindings:
            return True
        else:
            if self.parent != None:
                return var in self.parent
            else:
                return False
                
    def set_var(self, var, val):
        """
        Sets the variable passed, in as the first parameter to the value passed
        into the second parameters
        Doesn't return anything
        """
        self.bindings[var] = val
        
class Function:
    def __init__(self, parameters, body, env):
        self.body = body
        self.parameters = parameters
        self.env = env
        
    
    def __call__(self, arguments):
        """
        Function to allow users to call functions other functions and pass in 
        arguments.
        Arguments : list
            Of numbers, not variables
        
        Raises a CarlaeEvaluationError if the length of the parameter is not 
        equal to the length of the arguments.
        
        Returns the evaluated function given the arguments given the new enviornment
        """
        #check if the parameters are the same length
        if len(arguments) != len(self.parameters):
            raise CarlaeEvaluationError
        
        #make a new env with the parent as the enclosing env
        new_env = Environment(self.env, {})
        
        #bind function's parameters to arguments
        for i in range(len(self.parameters)):
            new_env.set_var(self.parameters[i], arguments[i])
        
        #eval body of function
        return(evaluate(self.body, new_env))
            
        


############################
# Tokenization and Parsing #
############################


def number_or_symbol(x):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return x


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Carlae
                      expression
    """
    tokens = ""
    comments = False
    i = 0
    while i<len(source):
        if source[i] == "#":
            comments = True
        if source[i] == "\n":
            comments = False
        if not comments:
            if source[i] == "(":
                tokens += " " + source[i] + " "
            elif source[i] == ")":
                tokens += " " + source[i] + " "
            elif source[i] == "\n":
                tokens += " "
            else:
                tokens += source[i]
        i+=1 
    tokens = tokens.split(" ")
    #gets rid of all empty indices
    while '' in tokens:
        tokens.remove('')
    return tokens

def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    #count number of closed and open () and see if they are equal else through error
    #no () throughts error
    #if single number or variable returns just that 
    #mismatch and single character together (check using if statement)
    open_par = 0
    closed_par = 0
    for i in tokens:
        if i == "(":
            open_par += 1
        if i == ")":
            closed_par += 1
    
    if open_par != closed_par:
        raise CarlaeSyntaxError
    
    if len(tokens) ==1:
        #return number is num and str in string
        return number_or_symbol(tokens[0])
    
    if len(tokens) > 1 and tokens[-1] != ")":
        raise CarlaeSyntaxError
    
    def parse_expression(index):
        token = number_or_symbol(tokens[index])
        if token != "(":
            return token, index+1
        
        parsed = []
        exp, new_index = parse_expression(index+1)

        if exp != ")":
            parsed.append(exp)
            
            
            while new_index <len(tokens) and tokens[new_index] != ")":
                #parsed.append(exp)
                exp, new_index = parse_expression(new_index)
               
                parsed.append(exp)
        else:
            new_index-=1
        
        return parsed, new_index+1
    

    parsed_expression, next_index = parse_expression(0)

    return parsed_expression


    
            


######################
# Built-in Functions #
######################
def multiply(exp):
    """
    Given an expression, it returns the product 
    """
    total = exp[0]
    for i in exp[1:]:
        total *= i
    return total

def divide(exp):
    """
    Given an expression, it divides every number
    """
    total = exp[0]
    for i in exp[1:]:
        total /= i
    return total
        
    

carlae_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": multiply,
    "/": divide
}

default_env = Environment(None, carlae_builtins)

def REPL():
    """
    Allows user inputs
    """
    current_env = None
    exp = ""
    while exp != "EXIT":
        exp = input("enter an expression: ")
        try:
            tok = tokenize(exp)
            parsed = parse(tok)
            evaluated, current_env = result_and_env(parsed, current_env)
            print(evaluated)
        except Exception as e:
            print(str(type(e)))

        

##############
# Evaluation #
##############
def evaluate(tree, environment=None):
    """
    Evaluate the given syntax tree according to the rules of the Carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if environment == None:
        #if no parent
        environment = Environment(default_env, {})
    #check if its a symbol
    if isinstance(tree, str):
        if tree in environment:
            return environment.get_var(tree)
        else:
            raise CarlaeNameError
    #check if its a number
    if isinstance(tree, (int,float)):
        return tree
    
    #else its a list
    #if the first thing in the list isn't a valid operator
    if tree[0] == ":=":
        if isinstance(tree[1], list):
            name = tree[1][0:1]
            param = tree[1][1:]
            body = tree[2]
            
            environment.set_var(name[0], Function(param, body, environment))
            return environment.get_var(name[0])
            
        else:
            environment.set_var(tree[1], evaluate(tree[2], environment))
            return environment.get_var(tree[1])
    elif tree[0] == "function":
        par = tree[1]
        body = tree[2]
        return Function(par, body, environment)
               
    else:
        operand = evaluate(tree[0], environment)
        exp = []
        for i in tree[1:]:
            exp.append(evaluate(i, environment))
        #checks if you can call
        if callable(operand):
            return operand(exp)
        else:
            raise CarlaeEvaluationError
            
def result_and_env(exp, env=None):
    """
    Parameters
    ----------
    exp : list
        expression
    env : current enviornment, optional

    Returns
    -------
    eval_result : evaulated result of exp
    env : enviornment
    """
    if env == None:
        env = Environment(default_env, {})
    eval_result = evaluate(exp, env)
    return eval_result, env
    
    
    

if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()

    REPL()
    
   
    
    

    pass
