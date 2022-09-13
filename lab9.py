"""6.009 Lab 9: Carlae Interpreter Part 2"""

import sys
sys.setrecursionlimit(10_000)

# KEEP THE ABOVE LINES INTACT, BUT REPLACE THIS COMMENT WITH YOUR lab.py FROM
# THE PREVIOUS LAB, WHICH SHOULD BE THE STARTING POINT FOR THIS LAB.

##STARTING LAB8
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
    
    def update_var(self, var, val):
        """
        Finds the enviornment the variable is binding to, and changes the val to 
        a new val in that specific enviornment
        
        If no enviornment has the variable it raises a NameError 
        """
        if var in self.bindings:
            self.bindings[var] = val
            return val
        else:
            if self.parent != None:
                return self.parent.update_var(var, val)
            else:
                raise CarlaeNameError
    
    
                
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
    
class Pair:
    """
    For creating the linked list pairs with a head and tail
    """
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail
        
    def get_head(self):
        return self.head
    
    def get_tail(self):
        return self.tail
    
    def copy(self):
        """
        deep copies a pair
        """
        if isinstance(self.tail, Pair):
            return Pair(self.head, self.tail.copy())
        return Pair(self.head, self.tail)
    
    def set_tail(self, new_tail):
        self.tail = new_tail
    
    def __repr__(self):
        return repr(self.head) + " , " + repr(self.tail)
    
      
        


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

def all_equal(exp):
    """
    Given an expression, returns true if they are all equal, 
    otherwise false
    """
    check = exp[0]
    for i in exp[1:]:
        if i != check:
            return False
    return True

def all_decreasing(exp):
    """
    Given an expression, returns true if they are in decreasing 
    order, otherwise false
    """
    current_num = exp[0]
    for i in exp[1:]:
        if current_num<=i:
            return False
        current_num = i
    return True

def nonincreasing(exp):
    """
    Given an expression, returns true if nonincreasing order, 
    false otherwise
    """
    current_num = exp[0]
    for i in exp[1:]:
        if current_num<i:
            return False
        current_num = i
    return True

def all_increasing(exp):
    """
    Given an expression, returns true if in increasing order, 
    false otherwise
    """
    current_num = exp[0]
    for i in exp[1:]:
        if current_num>=i:
            return False
        current_num = i
    return True

def nondecreasing(exp):
    """
    Given an expression, returns true if nondecreasing order, 
    false otherwise
    """
    current_num = exp[0]
    for i in exp[1:]:
        if current_num>i:
            return False
        current_num = i
    return True


def not_func(exps):
    """
    Given an expression, returns true if the expression is false, 
    and false is expression is true
    """
    if len(exps)>1 or len(exps) ==0:
        raise CarlaeEvaluationError() 
    return not exps[0]

def pair(exps):
    """
    exps: list
    Given a head and tail, creates a new Pair object
    """
    if len(exps) != 2:
        raise CarlaeEvaluationError
    return Pair(exps[0], exps[1])

def get_head(pair):
    """
    Gets the head of a pair
    """
    if len(pair) != 1 or not isinstance(pair[0], Pair):
        raise CarlaeEvaluationError
    return pair[0].get_head()

def get_tail(pair):
    """
    Gets the tail of a pair
    """
    if len(pair) != 1 or not isinstance(pair[0], Pair):
        raise CarlaeEvaluationError
    return pair[0].get_tail()

def create_list(nums):
    """
    nums: list
    Given a list of numbers, creates a linked list usins
    the pair objects.
    """
    if len(nums) == 0:
        #evaulating nil
        return None
    else:
        return Pair(nums[0], create_list(nums[1:]))
    
def linked_list(obj):
    """
    obj: list
    Checks if the obj in the list is a linked list
    """
    if obj == [None]:
        return True
    
    try:
        tail = obj[0].get_tail()
    except:
        return False

    if tail == None:
        return True
    if isinstance(tail, Pair):
        return linked_list([tail])
    return False

def length(obj):
    """
    obj: list
    finds the length of the linked list past 
    in the paramaters
    """
    if not linked_list(obj):
        raise CarlaeEvaluationError
    if obj == [None]:
        return 0

    count = 1
    tail = obj[0].get_tail()
    while tail != None:
        count+=1
        tail = tail.get_tail()
    return count
        
def nth(obj):
    """
    obj: list
        obj[0]: linked list
        obj[1]: index
        
    Given a specific index, returns the value at the given
    index
    """
    l_list = obj[0]
    index = obj[1]
    
    if linked_list(obj):
        if index == 0:
            return l_list.get_head()
        tail = l_list.get_tail()
        count = 1
        while tail != None:
            if count == index:
                return tail.get_head()
            tail = tail.get_tail()
            count += 1
        raise CarlaeEvaluationError
        
    if isinstance(l_list, Pair) and index == 0:
        return l_list.get_head()
    else:
        raise CarlaeEvaluationError

def find_last_pair(obj):
    """
    helper function, given a list of a pair object, finds the last
    pair (num, nil)
    """
    if linked_list([obj]):
        tail = obj.get_tail()
        while tail!= None:
            next_tail = tail.get_tail()
            if next_tail == None:
                return tail
            tail = next_tail
    return obj
        
        
def concat(obj, new_list=None): 
    """
    obj: list of linked lists
    
    Finds the last pair of the first linked list and makes that tail
    the next linked list, then does the same but the new list is the 
    connection of the first two linked lists
    """

    if len(obj) == 0:
        return None

    if len(obj) == 1:
        if not linked_list([obj[0]]):
            raise CarlaeEvaluationError 
        return obj[0].copy()
    


    if not linked_list([obj[0]]) or not linked_list([obj[1]]):
        raise CarlaeEvaluationError
        
    start_list = obj[0]
    end_list = obj[1]

    new_list = None
    
    if start_list == None and end_list == None:
        new_list = None
    elif start_list == None and end_list != None:
        new_list = end_list.copy()
    elif start_list != None and end_list == None:
        new_list = start_list.copy()
    else:
        new_list = start_list.copy()
        last_pair = find_last_pair(new_list)
        last_pair.set_tail(end_list.copy())
    
    if len(obj) == 2:
        return new_list
    return concat([new_list] + obj[2:])


def map_list(obj):
    """
    obj: list
        obj[0]: function
        obj[1]: linked_list
        
    Returns a new list comprised of the new elemtns which are each 
    element of the given list applied to the given function
    """
    func = obj[0]
    if not callable(func):
        raise CarlaeEvaluationError
    link_list = obj[1]
    index = 0
    leng = length([link_list])
    new_list = None
    while index<leng:
        num = nth([link_list, index])
        new_list = concat([new_list, create_list([func([num])])])
        index+=1
    return new_list

def filter_list(obj):
    """
    obj: list
        obj[0]: function
        obj[1]: linked list
    
    Returns a new list containing only the elements, when applied to 
    the given function result in True
    """
    func = obj[0]
    if not callable(func):
        raise CarlaeEvaluationError
    link_list = obj[1]
    index = 0
    leng = length([link_list])
    new_list = None
    while index<leng:
        num = nth([link_list, index])
        check = func([num])
        if check:
            new_list = concat([new_list, create_list([num])])
        index+=1
    return new_list
    
def reduce(obj):
    """
    obj: list
        obj[0]: function
        obj[1]: linked list
        obj[2]: initial value
        
    Returns a value that applies each value in the linked_list 
    to the function starting with the initial value
    """
    func = obj[0]
    if not callable(func):
        raise CarlaeEvaluationError
    link_list = obj[1]
    val = obj[2]
    index = 0
    leng = length([link_list])
    while index<leng:
        num = nth([link_list, index])
        val = func([val, num])
        index +=1
    return val
    
def begin(args):
    """
    returns the last index in the list
    """
    return args[-1]

def evaluate_file(file, env=None):
    """
    Given a file, evaluates that file with the given enviornmnet
    """
    exp = open(file).read()
    tok = tokenize(exp)
    par = parse(tok)

    return evaluate(par, env)


    

    

carlae_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": multiply,
    "/": divide,
    "@t": True,
    "@f": False,
    "=?": all_equal,
    ">": all_decreasing,
    ">=": nonincreasing,
    "<": all_increasing,
    "<=": nondecreasing,
    "not": not_func,
    "pair": pair,
    "head": get_head,
    "tail": get_tail,
    "nil": None,
    "list": create_list,
    "list?": linked_list,
    'length': length,
    "nth": nth,
    "concat": concat,
    "map": map_list,
    "filter": filter_list,
    "reduce": reduce,
    "begin": begin,
}

default_env = Environment(None, carlae_builtins)

def REPL():
    """
    Allows user inputs
    """
    current_env = Environment(default_env, {})
    files = sys.argv[1:]
    for file in files:
        evaluate_file(file, current_env)
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
    if tree == []:
        raise CarlaeEvaluationError() 
    elif tree[0] == ":=":
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
    
    elif tree[0] == "if":
        condition = tree[1]
        true_exp = tree[2]
        false_exp = tree[3]
        
        #checks the condition
        if evaluate(condition, environment):
            #if condition is true evaluates the true exp
            return evaluate(true_exp, environment)
        else:
            #if condition is false, evaluates the false exp
            return evaluate(false_exp, environment)
        
    elif tree[0] == "and":
        #as soon as one of the expressions is false, everything is false
        for exp in tree[1:]:
            if not evaluate(exp, environment):
                return False
        return True
    
    elif tree[0] == "or":
        #as soon as one exp is true, everything is true
        for exp in tree[1:]:
            if evaluate(exp, environment):
                return True
        return False
    
    elif tree[0] == "del":
        #trys to find the var in the enviornment
        try:
            return environment.bindings.pop(tree[1])
        except:
            #if var isn't in the enviornment or parents
            raise CarlaeNameError
            
    elif tree[0] == "let":
        new_env = Environment(environment, {})
        #goes through each exp, evaluating it with the current enviornment
        for exp in tree[1]:
            #adds the evaluated exp to the new env
            new_env.set_var(exp[0], evaluate(exp[1], environment))
        return evaluate(tree[2], new_env)
    
    elif tree[0] == "set!":
        #updates the enviornment 
        return environment.update_var(tree[1], evaluate(tree[2],environment))
        
           
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
