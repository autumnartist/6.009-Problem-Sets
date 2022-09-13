# 6.009 Lab 2: Snekoban

import json
import typing

# NO ADDITIONAL IMPORTS!

#(height, width)
direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    
    #Objects in the game
    computer = []
    player = None
    target = []
    wall = []
    
    #loops through each coordinate in the game
    for y in range(len(level_description)):
        for x in range(len(level_description[0])):
            #adds the coordinate to what is located in that square
            if "computer" in level_description[y][x]:
                computer.append((y,x))
            if "player" in level_description[y][x]:
                player = (y,x)
            if "target" in level_description[y][x]:
                target.append((y,x))
            if "wall" in level_description[y][x]:
                wall.append((y,x))
    #game representation = dictionary of sets of tuples/ of tuples
    game = {"wall": set(wall),
            "computer": set(computer),
            "player": tuple(player),
            "target": set(target),
            "dimensions": (len(level_description), len(level_description[0]))
            }
    
    return game
      

def isValidPlace(y, x, game, direction, mover):
    '''
    Given the new location (y,x), game (of the form returned from new_game), 
    direction and object that moves.
    Returns true if the object is able to move, returns false otherwise
    '''
    direct = direction_vector[direction]
    if (y,x) in game['wall']:
        return False
    if mover == 'player':
        if (y,x) in game["computer"] and ((y+direct[0], x+direct[1]) in game['wall'] or (y+direct[0], x+direct[1]) in game['computer']):
            return False
    if mover == 'computer':
        if (y,x) in game['computer']:
            return False
    return True

def nearWhat(y, x, game, direction):
    '''
    Given the (y,x) coordinate, game (of the form returned from new_game), and 
    direction.
    Returns a list of what objects are near (in the direction of variable
    direction) the given coordinates
    '''
    direct = direction_vector[direction]
    near = []
    if (y+direct[0],x+direct[1]) in game['wall']:
        near.append('wall')
    if (y+direct[0],x+direct[1]) in game['computer']:
        near.append('computer')
    if (y+direct[0],x+direct[1]) in game['target']:
        near.append('target')
    return near

def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    if game['target'] == set():
        return False
    for coord in game['computer']:
        if coord not in game['target']:
            return False
    return True
  

def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    #y,x
    playerLoc = game['player']
    
    
    #copy game
    copyWall = []
    for wall in game['wall']:
         copyWall.append(wall)
    
    copyComputer = []
    for comp in game['computer']:
        copyComputer.append(comp)
        
    copyPlayer = game['player']
    
    copyTarget  =[]
    for target in game['target']:
        copyTarget.append(target)
        
    copyGame = {"wall": set(copyWall),
                "computer": set(copyComputer),
                "player": tuple(copyPlayer),
                "target": set(copyTarget),
                "dimensions": game['dimensions']}
    
    
    direct = direction_vector[direction]
    
    near = nearWhat(playerLoc[0], playerLoc[1], copyGame, direction)
    #if player is pushing the computer
    #only really care about computer and player since they are the only things that move
    if "computer" in near:
        #check if computer can move
        if isValidPlace(playerLoc[0]+direct[0]*2, playerLoc[1]+direct[1]*2, copyGame, direction, "computer"):
            #move computer
            copyGame['computer'].remove((playerLoc[0]+direct[0], playerLoc[1]+direct[1]))
            copyGame['computer'].add((playerLoc[0]+direct[0]*2, playerLoc[1]+direct[1]*2))
            #move player
            copyGame['player'] = (playerLoc[0]+direct[0], playerLoc[1]+direct[1])
    else:
        #check if player can move
        if isValidPlace(playerLoc[0]+direct[0], playerLoc[1]+direct[1], copyGame, direction, "player"):
            #move player
            copyGame['player'] = (playerLoc[0]+direct[0], playerLoc[1]+direct[1])
  
    return copyGame
    
    
    


def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    #OG game rep
    level_description = []
    
    #loops through 2d array spaces
    for y in range(game['dimensions'][0]):
        level = []
        for x in range(game['dimensions'][1]):
            if (y,x) in game['wall']:
                level.append(['wall'])
                
            #computers can either be alone or with the target
            elif (y,x) in game['computer']:
                if (y,x) in game['target']:
                    level.append(['target', 'computer'])
                else:
                    level.append(['computer'])
            
            #player can either be alone or with the target
            elif y == game['player'][0] and x == game['player'][1]:
                if (y,x) in game['target']:
                    level.append(['target', 'player'])
                else:
                    level.append(['player'])
            
            elif (y,x) in game['target']:
                level.append(['target'])
            
            else:
                level.append([])
        level_description.append(level)

    return level_description

def converter(game):
    '''
    Given a game representation (of the form returned from new game)
    
    Return a tuple of tuples that consists of the location (y,x) of the 
    player and computer so it can be put into sets 
    '''
    loc = []
    for x in game['computer']:
        loc.append(tuple(x))
        
    loc.append(tuple(game['player']))
    
    return tuple(loc)
        
def getChildren(game):
    '''
    Given a game set (of the form returned from new game) 
    
    Return a tuple of tuples, with possible game sets with direction
    (((gameset, direction), (gameset2, direction2))
    '''
    directions = ['up', 'down', 'left', 'right']
    children = []
    for direction in directions:
        child = (step_game(game[0],direction), direction)
        children.append(child)
    
    return tuple(children)
        

def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    
    if victory_check(game):
        return []
    
    #list of tuple tuples with (gamestate, direction)
    agenda = [((game, "initialPos"),)]
    #set of tuples
    visited = {converter(game)}
    
    while agenda:
        
        current_path = agenda.pop(0)
        vertex = current_path[-1]
        
        #produces the list of tuples with possible game states and their corresponding
        #direction ['up', 'down', 'left', 'right']
        children = getChildren(vertex)
        
        for child in children:
            #keeps track of path, from current to its child
            new_path = current_path + (child,)
            if victory_check(child[0]):
                final_path = []
                for direct in new_path:
                    final_path.append(direct[1])
                #getting rid of "initialPos"
                final_path.pop(0)
                return final_path
            elif converter(child[0]) not in visited:
                agenda.append(new_path)
                visited.add(converter(child[0]))
    return None
 

if __name__ == "__main__":

    pass
