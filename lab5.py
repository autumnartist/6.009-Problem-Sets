#!/usr/bin/env python3
"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys
import typing
import doctest
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

def copy_formula(formula):
    copied_formula = []
    for i in formula:
        row = []
        for j in i:
            row.append(j)
        copied_formula.append(row)
    return copied_formula 

def update_expression(formula, first_variable, bol):
    '''
    Parameters
    ----------
    formula : list
        2D list of tuples in a CNF formula
    first_variable : string
        first variable in the tuple, that we can assume to be true/false
        
    bol: Boolean
        checks whether true or false works
    Returns
    -------
    formula : list
        simplified version of the 2d list, if we assume the first_variable
        is true or false
        will also return None if the first variable makes the statment false
    '''
    i = 0
    formula = copy_formula(formula)
    #assuming the variable is true
    if bol:
        condition1 = True
        condition2 = False
        #finding any unit case
        if [(first_variable, False)] in formula:
            return None
    #assumes variable is false
    else:
        condition1 = False
        condition2 = True
        if [(first_variable, True)] in formula:
            return None
    
    while i<len(formula):
        #assume its true
        if (first_variable, condition1) in formula[i]:
            formula.remove(formula[i])
            #assume its false
        elif (first_variable, condition2) in formula[i]:
            for j in formula[i]:
                if j == (first_variable, condition2):
                    #removes only that part of the list
                    formula[i].remove(j)   
                    if formula[i] == []:
                        return None
        else:
            i+=1
                       
    return formula

def find_unit_case(formula):
    '''
    Parameters
    ----------
    formula : list
        2D list of tuples in a CNF formula

    Returns
    -------
    i: tuple
        first list found that's length 1 - unit case
    '''
    for i in formula:
        if len(i) == 1:
            return i
    return None


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    #first time run through
    if formula == []:
        return {}
    
    #find unit case:
    #if theres no unit case
    if find_unit_case(formula) == None:
        first_variable = formula[0][0][0]
        #checking if true or false work
        formula1 = update_expression(formula, first_variable, True)
        #if true works
        if formula1 != None:
            try_formula = satisfying_assignment(formula1)
            if isinstance(try_formula, dict):
                try_formula[first_variable] = True
                return try_formula
        #checks if false works
        formula2 = update_expression(formula, first_variable, False)
        #if false works
        if formula2 != None:
            try_formula = satisfying_assignment(formula2)
            if isinstance(try_formula, dict):
                try_formula[first_variable] = False
                return try_formula    
        
    #in the case where we have a unit case 
    else:
        #assign that variable to what it says
        first_variable, bol = find_unit_case(formula)[0]
        formula = update_expression(formula, first_variable, bol)
        #if assigning it to what it says works
        if formula != None:
            try_formula = satisfying_assignment(formula)
            if isinstance(try_formula, dict):
                try_formula[first_variable] = bol
                return try_formula
        
    return None



def rule1(student_preferences, room_capacities):
    '''
    Parameters
    ----------
    student_preferences : dict
        a dictionary mapping a student name (string) to a list
        of room names (strings) that work for that student
    room_capacities : dict
        a dictionary mapping each room name to a positive integer
        for how many students can fit in that room
        
    Returns
    -------
    rule1 : 2d list
        CNF formula using rule 1 

    '''
    
    rule1 = []
    for student in student_preferences:
        pref = []
        for location in student_preferences[student]:
            #creates the function names 
            s = student + "_" + location
            #sets all preferneces to be true
            pref.append((s, True))
        rule1.append(pref)
    return rule1

def rule2(student_preferences, room_capacities):
    '''
    Parameters
    ----------
    student_preferences : dict
        a dictionary mapping a student name (string) to a list
        of room names (strings) that work for that student
    room_capacities : dict
        a dictionary mapping each room name to a positive integer
        for how many students can fit in that room
        
    Returns
    -------
    rule1 : 2d list
        CNF formula using rule 2

    '''
    rule2 = []
    for student in student_preferences:
        stud_locs = []
        for location in room_capacities:
            s = student + "_" + location
            stud_locs.append(s)
        #finds each combo of length 2
        combos = create_combos(stud_locs,2)
        for combo in combos:
            #print(combo)
            com = []
            for i in combo:
                #sets all combos to be not_ or not_
                p1 = (i, False)
                
                com.append(p1)
            rule2.append(com)
        
    return rule2

def create_combos(values, k):
    '''
    Parameters
    ----------
    values : list
        list of values that we are finding the combos for
    k : int
        length of the sets of combos

    Returns
    -------
    list (of sets)
        list of sets which show each possible combination

    '''
    #base case
    if k == 1:
        return [{val} for val in values]
    else:
        i = 0
        val_list = []
        for val in values:
            #list of sets of k-1
            combos = create_combos(values[i+1:], k-1)
            i+=1
            #goes through eat set
            for c in combos:
                #adds our starting variable
                val_list.append({val}|c)
        return val_list

def rule3(student_preferences, room_capacities):
    '''
    Parameters
    ----------
    student_preferences : dict
        a dictionary mapping a student name (string) to a list
        of room names (strings) that work for that student
    room_capacities : dict
        a dictionary mapping each room name to a positive integer
        for how many students can fit in that room
        
    Returns
    -------
    rule1 : 2d list
        CNF formula using rule 3 

    '''
    #rule3
    rule3 = []
    for location in room_capacities:
        #if there's no need to test combos 
        #because the room can have everyone inside
        if room_capacities[location] >= len(student_preferences):
            continue
        
        #room capacity --> N+1
        length = room_capacities[location]+1
        combos = []
        for student in student_preferences:
            s = student + "_" + location
            combos.append(s)
        #find every combo of the room capacity+1
        combo = create_combos(combos, length)
        for c in combo:
            com = []
            for i in c:
                #sets each item in the combo to False
                com.append((i, False))
            rule3.append(com)
            
    return rule3
    
def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz room scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a list
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    
    rule_1 = rule1(student_preferences, room_capacities)
    rule_2 = rule2(student_preferences, room_capacities)
    rule_3 = rule3(student_preferences, room_capacities)
    #CNF is the summation of every rule
    
    return rule_1+rule_2+rule_3



if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
    print("console:")
    r = rule3({'Alice': ['basement', 'penthouse'],
                            'Bob': ['kitchen'],
                            'Charles': ['basement', 'kitchen'],
                            'Dana': ['kitchen', 'penthouse', 'basement']},
                           {'basement': 1,
                            'kitchen': 2,
                            'penthouse': 4})
    print(r)
