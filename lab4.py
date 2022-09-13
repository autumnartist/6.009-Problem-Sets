#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

import typing
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION
def create_board(num_rows, num_cols, bombs):
    '''
    Parameters
    ----------
    num_rows : (int)
        number of rows in the game rep
    num_cols : (int)
        number of columns in the game rep
    bombs : (list)
        List of bombs, given in (row, column) pairs, which are tuples

    Returns
    -------
    dict
        comprised of the board and visibility of each tile on the 
        board (game rep)

    '''
    board = []
    visible = []
    for r in range(num_rows):
        row = []
        vis = []
        for c in range(num_cols):
            if [r, c] in bombs or (r, c) in bombs:
                row.append('.')
            else:
                row.append(0)
            vis.append(False)
        board.append(row)
        visible.append(vis)
    return {'board': board,
            'visible': visible}

def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """

    info = create_board(num_rows, num_cols, bombs)
    board = info['board']
    
    nums = [-1,0,1]
    for r in range(num_rows):
        for c in range(num_cols):
            if board[r][c] == 0:
                neighbor_bombs = 0
                for num in nums:
                    if 0<= r+num < num_rows:
                        for n in nums:
                            if 0<= c+n<num_cols and board[r+num][c+n] == ".":
                                neighbor_bombs+=1
                board[r][c] = neighbor_bombs
    return {
        'dimensions': (num_rows, num_cols),
        'board': board,
        'visible': info['visible'],
        'state': 'ongoing'}

def count_bombs(game):
    """
    Parameters
    ----------
    game : dict
        game representation with board, visible, dimensions and state

    Returns
    -------
    tuple
        containing the number of bombs revealed (bombs) and the number of 
        bombs not revealed (covered_squares)

    """
    bombs = 0
    covered_squares = 0
    #iterating through every coordinate
    for r in range(game['dimensions'][0]):
        for c in range(game['dimensions'][1]):
            #if there's a bomb 
            if game['board'][r][c] == '.':
                #if the bomb is revealed
                if game['visible'][r][c] == True:
                    bombs += 1
                #if the bomb is covered
            elif game['visible'][r][c] == False:
                covered_squares += 1
    return (bombs, covered_squares)
    
def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['visible'][bomb_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """
    #if game state isn't ongoing
    if game['state'] != 'ongoing': 
        return 0
    #if we reveal a bomb
    if game['board'][row][col] == '.':
        game['visible'][row][col] = True
        game['state'] = 'defeat'
        return 1

    bombs, covered_squares = count_bombs(game)
    #if a bomb is revealed
    if bombs != 0:
        # if bombs is not equal to zero, set the game state to defeat and
        # return 0
        game['state'] = 'defeat'
        return 0
 
    #revealing the first coordinate if it hasn't been already
    if game['visible'][row][col] != True:
        game['visible'][row][col] = True
        revealed = 1
    else:
        return 0
    
    #find all neighbors
    nums = [-1,0,1]    
    if game['board'][row][col] == 0:
        num_rows, num_cols = game['dimensions']
        for num in nums:
            if 0<= row+num < num_rows:
                for n in nums:
                    #recursive call if 
                    # 1. neighbor isn't a bomb
                    # 2. the neighbor isn't visible
                    if (0 <= col+n < num_cols) and game['board'][row+num][col+n] != "." and game['visible'][row+num][col+n] == False:
                        revealed += dig_2d(game,row+num, col+n)
    #go through changed game board and find boards and covered squares
    bombs, covered_squares = count_bombs(game)
    bad_squares = bombs + covered_squares
    if bad_squares > 0:
        game['state'] = 'ongoing'
        return revealed
    else:
        game['state'] = 'victory'
        return revealed


def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['visible'] indicates which squares should be visible.  If
    xray is True (the default is False), game['visible'] is ignored and all
    cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    board = []

    for y in range(game['dimensions'][0]):
        row = []
        for x in range(game['dimensions'][1]):
            #if xray is false - check visibility
            if xray == False and game['visible'][y][x] == False:
                row.append("_")
            else:
                #if the game is 0 add a blank space " "
                if str(game['board'][y][x]) == '0':
                    row.append(" ")
                else:
                    row.append(str(game['board'][y][x]))
        board.append(row)
            
    return board
      


def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    board = ""

    for y in range(game['dimensions'][0]):
        row = ""
        for x in range(game['dimensions'][1]):
            #if xray is false - check visibility
            if xray == False and game['visible'][y][x] == False:
                row += "_"
            else:
                #if the game is 0 add a blank space " "
                if str(game['board'][y][x]) == '0':
                    row += " "
                else:
                    row += str(game['board'][y][x])
        if y == game['dimensions'][0]-1:
            board += row
        else:
            board += row + "\n" 
          
    return board
    


# N-D IMPLEMENTATION

def empty_nd_board(dim, value):
    """
    Parameters
    ----------
    dim : Tuple
        Dimensions of the board
    value : any - for the purposes of this lab, the values will be a 
                  list and a boolen
        Any type to create an n-dimensional list

    Returns
    -------
    list of list
        returns a n-d list of a specific value

    """
    board = []
    if len(dim) == 1:
        for i in range(dim[0]):
            board.append(value)
        return board
    
    if len(dim)>1:
        for i in range(dim[0]):
            board.append(empty_nd_board(dim[1:], value))
        return board
        
def get_coords(dim, foundPoints= False, currentPoints=False): 
    """
    Parameters
    ----------
    dim : tuple
        Dimensions of the board
    foundPoints : set (of tuples)
        set of tuples of possible coordinates within the dimensions of the board
    currentPoints : list(of tuples)
        list of coordinates of neighbors of a given point 

    Returns
    -------
    foundPoints : set
        Final set of tuples of all possible coordinates within the dimensions 
        of the board

    """
       
    #recursive call
    #find the neighbors of the given point then put call the function on 
    #the found neighbors
        
    #always start with all zeros
    #see if we can add the current point (if its in range)
    if foundPoints == False:
        foundPoints = set()
    if currentPoints == False:
        point = []
        for i in range(len(dim)):
            point.append(0)
        currentPoints = [tuple(point)]
            
    
    for point in currentPoints:
        if point in foundPoints:
            continue
        else:
            #check if we can add the point
            canAdd = False
            if point not in foundPoints:
                for j in range(len(point)):
                    if point[j]<dim[j]:
                        canAdd = True
                    else:
                        canAdd = False
                #if its within the dimensions add it to foundPoints
                if canAdd:
                    foundPoints.add(point)

            neighbors = set()
            point = list(point)
            for i in range(len(dim)):
                #check if its in dimension
                if point[i] +1 < dim[i]:
                    point[i] +=1
                else:
                    continue
                
                n =[]
                for x in point:
                    n.append(x)
                neighbors.add(tuple(n))
                point[i] -=1
            get_coords(dim, foundPoints, neighbors)
    
    #stopping case 
    #when the length of the foundPoints is == to the volume
    length = 1
    for i in dim:
        length *= i
    if len(foundPoints) == length:
        return foundPoints
    
def change_val(board, value, coord):
    '''
    Parameters
    ----------
    board : list of lists
        n-d array of the game rep
    value : any
        value to change the coord of the board to
    coord : tuple
        coordinate - coresponding to some point on the board

    Returns
    -------
    Nothing 
        only changes the board

    '''
    if len(coord) == 1:
        board[coord[0]] = value
        #return board
    if len(coord)>1:
        #newBoard = board[coord[0]]
        board = board[coord[0]]
        #coord.pop(0)
        #change_val(newBoard, value, coord)
        change_val(board, value, coord[1:])
        
        
def get_val(board, coord):
    '''
    Parameters
    ----------
    board : list of lists
        n-d array of the game rep
    coord : tuple
        coordinate - coresponding to some point on the board

    Returns
    -------
    any
        returns whatever value (int, string boolean) located at that
        specific coordinate in the board

    '''
    if len(coord) == 1:
        return board[coord[0]]
    else:
        newBoard = board[coord[0]]
        #coord.pop(0)
        return get_val(newBoard,coord[1:])
    
def get_neighbors(dim, coord, neighbors=False):
    """
    Parameters
    ----------
    dim : tuple
        Dimensions of game board
    coord : tuple
        tuple of length (dimensions) that corresponds to a specific place
        in the game board
    neighbors : list of tuples, optional
        combinations of all neighbors The default is False.

    Returns
    -------
    set of tuples
        Returns a list of all possible neighbors within the given
        dimensions of the game board

    """
    neighbor = set()
    nums = [-1,0,1]
    for i in nums:
        if 0<=coord[0]+i<dim[0]:
            n = (coord[0]+i,) #+ coord[1:]
            #print(tuple(n,))
            neighbor.add(n)
    
    if len(dim) == 1:
        neighs = set()
        for i in neighbors:
            for j in neighbor:
                neigh = i+j
                neighs.add(neigh)
        return neighs
    
    if neighbors == False:
        neighbors = set()
        #neighbors.append(neighbor)
    else:
        neighs = set()
        for i in neighbors:
            for j in neighbor:
                neigh = i+j
                neighs.add(neigh)
        neighbor = neighs    
    return get_neighbors(dim[1:], coord[1:], neighbor)

def neighbor_bombs(board, dim, coord):
    """
    Parameters
    ----------
    board : list
        n-d list representing the game board
    dim : tuple
        Dimensions of game board
    coord : tuple
        tuple of length (dimensions) that corresponds to a specific place
        in the game board
    Returns
    -------
    neighbor_bombs : int
        Number of bombs in the neighbor of the given coordinates

    """
    neighbors = get_neighbors(dim, coord)
    
    #return neighbors
    #find if they have bombs using get_val
    neighbor_bombs = 0
    for neighbor in neighbors:
        if get_val(board, neighbor) == ".":
            #add 1 each time you find a bomb
            neighbor_bombs+=1
    return neighbor_bombs
    
def new_game_nd(dimensions, bombs, board=False):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
        
    """    

    if board == False:
        board = empty_nd_board(dimensions, 0)
    #adding the bombs
    for bomb in bombs:
        change_val(board, ".", bomb)
        #neighbors of each bomb
        neighborBombs = get_neighbors(dimensions, bomb)
        for neighbor in neighborBombs:
            if get_val(board, neighbor) != ".":
                val = neighbor_bombs(board, dimensions, neighbor)
                change_val(board, val, neighbor)
            
     
    
    visible = empty_nd_board(dimensions, False)
    game = {"board": board,
            "dimensions": dimensions,
            "state": "ongoing",
            "visible": visible}
    return game
    
    
    

def count_nd_squares(game):
    """
    Parameters
    ----------
    game : dict 
        dictionary with the board, visible, dimensions and state
        
    Returns
    -------
    tuple
        containing the number of bombs revealed (bombs) and the number of 
        bombs not revealed (covered_squares)
    """
    bombs = 0
    covered_squares = 0
    coords = get_coords(game['dimensions'])
    for coord in coords:
        boardVal = get_val(game['board'], coord)
        visVal = get_val(game['visible'], coord)
        if boardVal == ".":
            if visVal == True:
                bombs+=1
        elif visVal == False:
            covered_squares += 1
    return (bombs, covered_squares)    
    
def dig_nd(game, coordinates, recursive=False):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
     
    2d instructions
    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['visible'][bomb_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are visible, and 'ongoing' otherwise.
    """
    revealed =0

    #if game state isn't ongoing
    if game['state'] != 'ongoing': 
        return 0
    
    #if we reveal a bomb
    if get_val(game['board'], coordinates) == '.':
        change_val(game['visible'], True, coordinates)
        game['state'] = 'defeat'
        return 1
    
    if recursive == False:
        bombs, covered_squares = count_nd_squares(game)
        #if a bomb is revealed
        if bombs != 0:
            # if bombs is not equal to zero, set the game state to defeat and
            # return 0
            game['state'] = 'defeat'
            return 0
        
        if covered_squares == 0:
            game['state'] = 'victory'
            return revealed
 
    #revealing the first coordinate if it hasn't been already
    if get_val(game['visible'], coordinates) != True:
        change_val(game['visible'], True, coordinates)
        revealed += 1
    else:
        return 0

    
    #find all neighbors
    if get_val(game['board'], coordinates) == 0:
        neighbors = get_neighbors(game['dimensions'], coordinates)
        #print(neighbors)
        for neighbor in neighbors:
            if get_val(game['board'], neighbor) != "." and get_val(game['visible'], neighbor) == False:
                revealed += dig_nd(game, neighbor, True)
    
    #go through changed game board and find boards and covered squares
    if recursive == False:
        bombs, covered_squares = count_nd_squares(game)
        bad_squares = bombs + covered_squares
        if bad_squares > 0:
            game['state'] = 'ongoing'
            return revealed
        else:
            game['state'] = 'victory'
            return revealed
        
    return revealed


def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  The game['visible'] array indicates which squares should be
    visible.  If xray is True (the default is False), the game['visible'] array
    is ignored and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """

    renderedBoard = empty_nd_board(game['dimensions'], 0)
    coords = get_coords(game['dimensions'])
    for coord in coords:
        val = str(get_val(game['board'], coord))
        
        if xray == False and get_val(game['visible'], coord) == False:
            change_val(renderedBoard, "_", coord)
        else:
            if get_val(game['board'], coord) == 0:
                change_val(renderedBoard, " ", coord)
            else:
                change_val(renderedBoard, val, coord)
    return renderedBoard
    

if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests
    '''
    g = {'dimensions': (2, 4, 2),
          'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
                    [['.', 3], [3, '.'], [1, 1], [0, 0]]],
          'visible': [[[False, False], [False, True], [False, False],
                    [False, False]],
                   [[False, False], [False, False], [False, False],
                    [False, False]]],
          'state': 'ongoing'}
    print(dig_nd(g, (0, 3, 0)))
    '''
    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    # doctest.run_docstring_examples(
    #    render_2d_locations,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
