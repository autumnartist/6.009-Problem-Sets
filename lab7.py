import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.
def tokenize(op):
    new_op = ""
    for i in op:
        if i == "(":
            new_op += i + " "
        elif i== ")":
            new_op += " " + i
        else:
            new_op += i
    return new_op.split(" ")

def parse(tokens):
    d = {"+": Add,
         "-": Sub,
         "*": Mul,
         "/": Div, 
         "**": Pow}
    def parse_expression(index):
        token = tokens[index]
        #check if its a number
        try:
            t = int(token)
            return Num(t), index+1
        except ValueError:
            pass
        
        #check if its a variable 
        if token.isalpha() and len(token) == 1:
            return (Var(token), index+1)
        
        #expression is left of operation
        #print("30", index+1, tokens[index+1])
        left_expression, new_index = parse_expression(index+1) 
        operand = tokens[new_index] 
        #print("33", new_index, tokens[new_index])
        right_expression, right_new_index = parse_expression(new_index+1)
                
        return d[operand](left_expression, right_expression), right_new_index+1

    parsed_expression, next_index = parse_expression(0)
    return parsed_expression
def expression(op):
    return parse(tokenize(op))
    

class Symbol():
    right_special_case = False
    left_special_case = False
    
    def __add__(self, other):
        return Add(self, other)
    
    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Sub(self, other)
    
    def __rsub__(self, other):
        return Sub(other, self)
    
    def __mul__(self, other):
        return Mul(self, other)
    
    def __rmul__(self, other):
        return Mul(other, self)
    
    def __truediv__(self, other):
        return Div(self, other)
    
    def __rtruediv__(self, other):
        return Div(other, self)
    
    def __pow__(self, other):
        return Pow(self, other)
    
    def __rpow__(self, other):
        return Pow(other, self)
    

        
    


class Var(Symbol):
    order = 5
    
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Var(" + repr(self.name) + ")"
    
    def deriv(self, x):
        if x in self.name:
            return Num(1)
        else:
            return Num(0)
    
    def simplify(self):
        return self
    
    def eval(self, mapping):
        try:
            val = mapping[self.name]
        except:
            return self
        return val
    
    

class Num(Symbol):
    order = 5
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return "Num(" + repr(self.n) + ")"
    
    def deriv(self, x):
        return Num(0)
    
    def simplify(self):
        return self
    
    def eval(self, mapping):
        return self.n
 

class BinOp(Symbol):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        
        #check if left is a number or string
        if isinstance(self.left, (int, float)):
            self.left = Num(left)
        if isinstance(self.left, str):
            self.left = Var(left)
            
        #check if right is a number or string
        if isinstance(self.right, (int, float)):
            self.right = Num(right)
        if isinstance(self.right, str):
            self.right = Var(right)
    
    def __str__(self):
        
        left = str(self.left)
        if self.left.order < self.order:
            left = "(" + left + ")"
            
        right = str(self.right)
        if self.right_special_case and self.right.order == self.order:
            right = "(" + right + ")"
        elif self.right.order < self.order:
            right = "(" + right + ")"
            
        return left + self.operator[1] + right
    
    def __repr__(self):
        return self.operator[0] + "(" + repr(self.left) + ", " + repr(self.right) + ")"
        
    
 
class Add(BinOp): 
    operator = ("Add", " + ")
    order = 1
    def deriv(self, x):
        derivative = self.left.deriv(x) + self.right.deriv(x)
        return derivative
    
    def simplify(self):
        left_simp = self.left.simplify()
        right_simp = self.right.simplify()
        zero = [0, 0.0]
        #two numbers
        left_is_number = isinstance(left_simp, Num)
        right_is_number = isinstance(right_simp, Num)
        if left_is_number and right_is_number:
            left = left_simp.n
            right = right_simp.n
            return Num(left+right)
        
        if left_is_number:
            #check if the left is 0
            if left_simp.n in zero :
                return right_simp 
            
        if right_is_number:
            if right_simp.n in zero:
                return left_simp 
            
            
        return Add(left_simp, right_simp)
    def eval(self, mapping):
        return self.left.eval(mapping) + self.right.eval(mapping)
       
class Sub(BinOp):
    operator = ("Sub", " - ")
    right_special_case = True
    order = 1
    def deriv(self, x):
        derivative = self.left.deriv(x) - self.right.deriv(x)
        return derivative
    
    def simplify(self):
        left_simp = self.left.simplify()
        right_simp = self.right.simplify()
        zero = [0, 0.0]
        #first check if both arguments are numbers 
        left_is_number = isinstance(left_simp, Num)
        right_is_number = isinstance(right_simp, Num)
        if left_is_number and right_is_number:
            left = left_simp.n 
            right = right_simp.n
            return Num(left-right)
        
        #check if the right is 0
        if right_is_number:
            if right_simp.n in zero:
                return left_simp
            
        return Sub(left_simp, right_simp)
    
    def eval(self, mapping):
        return self.left.eval(mapping) - self.right.eval(mapping)
        
        

class Mul(BinOp):
    operator = ("Mul", " * ")
    order = 2
    def deriv(self, x):
        derivative = self.left*self.right.deriv(x) + self.right*self.left.deriv(x)
        return derivative 
    def simplify(self):
        #start with simp
        left_simp = self.left.simplify()
        right_simp = self.right.simplify()
    
        zero = [0, 0.0]
        one = [1, 1.0]
        #first check if both arguments are numbers 
        left_is_number = isinstance(left_simp, Num)
        right_is_number = isinstance(right_simp, Num)
        if left_is_number and right_is_number:
            left = left_simp.n
            right = right_simp.n
            return Num(left*right)
        
        if left_is_number:
            if left_simp.n in one: 
                return right_simp
            if left_simp.n in zero: 
                return Num(0)
            
        if right_is_number:
            if right_simp.n in one: 
                return left_simp
            if right_simp.n in zero: 
                return Num(0)
        return Mul(left_simp, right_simp)
    
    def eval(self, mapping):
        return self.left.eval(mapping) * self.right.eval(mapping)
     


class Div(BinOp):
    operator = ("Div", " / ")
    right_special_case = True
    order = 2
    def deriv(self, x):
        derivative = (self.right*self.left.deriv(x) - self.left*self.right.deriv(x)) / (self.right*self.right)
        return derivative
    def simplify(self):
        left_simp = self.left.simplify()
        right_simp = self.right.simplify()
        zero = [0, 0.0]
        one = [1, 1.0]
        #first check if both arguments are numbers 
        left_is_number = isinstance(left_simp, Num)
        right_is_number = isinstance(right_simp, Num)
        if left_is_number and right_is_number:
            left = left_simp.n
            right = right_simp.n
            return Num(left/right)
        
        if left_is_number:
            if left_simp.n in zero: 
                return Num(0)
        
        if right_is_number:
            if right_simp.n in one: 
                return left_simp
        
        return Div(left_simp, right_simp)
    
    def eval(self, mapping):
        return self.left.eval(mapping) / self.right.eval(mapping)
        
class Pow(BinOp):
    operator = ("Pow", " ** ")
    left_special_case = True
    order = 4
    
    def __str__(self):
        left = str(self.left)
        if self.left.order <= self.order:
            left = "(" + left + ")"
            
        right = str(self.right)
        if self.right.order < self.order:
            right = "(" + right + ")"
        return left + self.operator[1] + right
    
    def deriv(self, x):
        if isinstance(self.right, Num):
            derivative = self.right*self.left**(self.right-1)*self.left.deriv(x)
            return derivative
        else:
            raise TypeError("Right argument is not an instance of Num")
    
    def simplify(self):
        left_simp = self.left.simplify()
        right_simp = self.right.simplify()
        
        left_is_number = isinstance(left_simp, Num)
        right_is_number = isinstance(right_simp, Num)
        if left_is_number and right_is_number:
            left = left_simp.n
            right = right_simp.n
            return Num(left**right)
        
        zero = [0, 0.0]
        one = [1, 1.0]
  
        
        if right_is_number:
            if right_simp.n in zero:
                return Num(1)
            if right_simp.n in one:
                return left_simp
     
        if left_is_number and left_simp.n in zero:
            if right_is_number:
                if right_simp.n>0:
                    return Num(0)
            else:
                return Num(0)
  
            
        return Pow(left_simp, right_simp)
    
    def eval(self, mapping):
        return self.left.eval(mapping)**self.right.eval(mapping)
    
    
        

    
if __name__ == "__main__":
    doctest.testmod()
    x = Var('x')
    y = Var('y')
    z = 3*x + x*y + y**2 - 18 / 6
    print(repr(z))
    print(z.deriv('x').simplify())
   
    