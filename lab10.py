"""6.009 Lab 10: Snek Is You Video Game"""

import doctest

# NO ADDITIONAL IMPORTS!

# All words mentioned in lab. You can add words to these sets,
# but only these are guaranteed to have graphics.
NOUNS = {"SNEK", "FLAG", "ROCK", "WALL", "COMPUTER", "BUG"}
PROPERTIES = {"YOU", "WIN", "STOP", "PUSH", "DEFEAT", "PULL"}
WORDS = NOUNS | PROPERTIES | {"AND", "IS"}
EVERYTHING = NOUNS | PROPERTIES | WORDS

# Maps a keyboard direction to a (delta_row, delta_column) vector.
direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}
class Items():
    def __init__(self, name, loc):
        self.name = name
        self.loc = loc
        
    def get_name(self):
        return self.name
    
    def get_loc(self):
        return self.loc
    
    def update_loc(self, new_loc):
        self.loc = new_loc
    
    def set_name(self, new_name):
        self.name = new_name
  
    
                     
def set_rules(game):
    """
    Parameters
    ----------
    game : Game class
        DESCRIPTION.
    noun : string
        a possible noun in the game
    loc : tuple
        locaton of the given nouns
    direction : tuple
        where (in relation to the noun) to look for the next words

    Updates the rules(dict)
    """
    #empty rule book
    rule = {"snek": [],
             "wall": [],
             "rock": [],
             "computer": [],
             "bug": [],
             "flag": [],
             "empty": [None]}

    for i in EVERYTHING:
        rule[i] = ["PUSH"]
        
    #find where every "IS" is located
    is_objs = game.find_obs("IS")
    #for each location
    for i in is_objs:
        #check if there's something above and below
        whats_around(game, ("up", "down"), i, rule)
        #check if theres something left or right
        whats_around(game, ("left", "right"), i, rule)
    return rule

def whats_around(game, direction, location, rule):
    """
    Finds whats around the location given and updates the
    rules as accordingly.
    """
    def sub_pred(direct, word_list):
        subjects = set()
        count = 1

        #location of the subject
        loc = (direct[0]*count+location[0], direct[1]*count+location[1])
        #is this location in bounds and is the obj at this location a nouns
        poss_subs = []
        for i in game.obj_at_loc(loc):
            if i.name != "empty":
                poss_subs.append(i.name)
        if len(poss_subs) != 0 and in_bounds(game, loc) and poss_subs[0] in word_list:
            subjects.add(poss_subs[0])
            #check if theres an and
            and_loc = (loc[0]+direct[0], loc[1]+direct[1])
            if in_bounds(game, and_loc) and len(game.obj_at_loc(and_loc)) != 0 and game.obj_at_loc(and_loc)[0].name == "AND":
                count+=2
                #is there a noun next to the and
                loc = (direct[0]*count+location[0], direct[1]*count+location[1])
                while in_bounds(game, loc) and len(game.obj_at_loc(loc)) != 0 and game.obj_at_loc(loc)[0].name in word_list:
                    subjects.add(game.obj_at_loc(loc)[0].name)
                    and_loc = (loc[0]+direct[0], loc[1]+direct[1])
                    if len(game.obj_at_loc(and_loc)) != 0 and game.obj_at_loc(and_loc)[0].name == "AND":
                        count+=2
                        loc = (direct[0]*count+location[0], direct[1]*count+location[1])
                    else:
                        break
        return subjects
        

    sub_direct = direction_vector[direction[0]]
    subjects = sub_pred(sub_direct, NOUNS)
          
      
    #if we have a subject
    if len(subjects)!=0:
        pred_direct = direction_vector[direction[1]]
        preds = PROPERTIES | NOUNS
        predicates = sub_pred(pred_direct, preds)
        
        
        for sub in subjects:
            for pred in predicates:
                rule[sub.lower()] += [pred]
  


class Game():
    def __init__(self, level_description):
        self.things = []
        self.dims = (len(level_description), len(level_description[0]))
        self.players = set()
        for y in range(len(level_description)):
            for x in range(len(level_description[0])):
                items = level_description[y][x]
                if len(items)>=1:
                    for name in items:
                        self.things.append(Items(name, (y,x)))
                        self.players.add(name)
                else:
                    self.things.append(Items("empty", (y,x)))
                    self.players.add("empty")
        self.rules = set_rules(self)
     
    def update_rules(self, new_rules):
        self.rules = new_rules
                
    def obj_at_loc(self, loc):
        """
        Returns all the objects (items) at a given location
        """
        objs = []
        for i in self.things:
            if loc == i.get_loc():
                objs.append(i)
        return objs
    
    
    def get_all_behav(self, prop):
        """
        returns all the objs that have a certain property
        """
        objs = []
        for i in self.things:
            if prop in self.rules[i.name]:
                objs.append(i)
        return objs
    
    def find_obs(self, name):
        """
        Finds all the objs locations that have a specific name
        """
        objs = []
        for obj in self.things:
            if obj.name == name:
                objs.append(obj.loc)
        return objs
                
    def is_obj_there(self, name, loc):
        """
        Returns true if there is an object with the given name at the 
        given location, false otherwise
        """
        objs = self.obj_at_loc(loc)
        for i in objs:
            if i.name == name:
                return True
        return False
    
    def num_objs_there(self, loc):
        """
        Returns the amount of objects at a given location
        """
        count = 0
        for i in self.things:
            if loc == i.loc:
                count+=1
        return count
    
    def find_all_obj_name(self, name):
        """
        Returns all objects with a given name
        """
        objs =[]
        for obj in self.things:
            if obj.name == name:
                objs.append(obj)
        return objs
    
    
                
def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, where UPPERCASE
    strings represent word objects and lowercase strings represent regular
    objects (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['snek'], []],
        [['SNEK'], ['IS'], ['YOU']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """

    return Game(level_description)               

def in_bounds(game, loc):
    """
    Given a game and location, checks if the location is within the 
    bounds of the game
    """
    if loc[0]<game.dims[0] and loc[1]<game.dims[1]:
        if loc[0]>=0 and loc[1]>=0:
            return True
    return False

def check_prop(game, new_loc):
    """
    Given a game and a location, returns a list of every 
    property at that location
    """
    #what if there are multiple different things - return a list of properities
    prop = []
    for obj in game.things:
        if obj.get_loc() == new_loc:
            prop+= game.rules[obj.name]
    return prop

#property functions
def move(game, player, og_loc, direct, movers=None):
    """
    Parameters
    ----------
    game : Game 
        Game class
    player : what is moving 
        Items class
    og_loc : original location of the player 
        tuple
    direct : how the player will be moving
        tuple
    movers : everything that is moving with the player, optional
        list The default is None.

    Returns
    -------
    boolean
        can the player move?
    movers
        what ends up moving (possibly with the player)
    """
    #returns if you can move and everything that can move
    #player = object
    #each object has to be its own instance
    
    if movers == None:
        movers = []
        
    new_loc = (og_loc[0]+direct[0], og_loc[1]+direct[1])
    #every obj at loc
    obs = game.obj_at_loc(new_loc)
    prop = []
    for i in obs:
        prop += game.rules[i.name]
        if "STOP" in game.rules[i.name] and "PUSH" not in game.rules[i.name]:
            return False, movers
 
    if not in_bounds(game, new_loc): 
        return False, movers
    
    #if we can push the object
    if "PUSH" in prop:       
        if isinstance(player, list):
            for i in player:
                movers.append(i)
        else:
            movers.append(player)
        players = []
        all_players = game.obj_at_loc(new_loc)
        for i in all_players:
            if "PUSH" in game.rules[i.name]:
                players.append(i)
        return move(game, players, new_loc, direct, movers)
    
    
    #just moving
    if isinstance(player, list):
        for i in player:
            movers.append(i)
    else:
        movers.append(player)
    return True, movers
        
def pull(game, player, og_loc, direct, movers=None):
    """
    Parameters
    ----------
    game : Game 
        Game class
    player : what is moving 
        Items class
    og_loc : original location of the player 
        tuple
    direct : how the player will be moving
        tuple
    movers : everything that is moving with the player, optional
        list The default is None.

    Returns
    -------
    movers: what ends up moving (possibly with the player)
        list
    """
    #just return things you have to pull
    if movers== None:
        movers = []

    new_loc = (og_loc[0]-direct[0], og_loc[1]-direct[1])
    prop = check_prop(game, new_loc)
    
    if not in_bounds(game, new_loc):
        return movers
    
    if "PULL" in prop:
        #player = object at new_loc
        all_players = game.obj_at_loc(new_loc)
        #only want the objects that have the property of pull
        player = []
        for p in all_players:
            if "PULL" in game.rules[p.name]:
                player.append(p)
   

        can_move = move(game, player, new_loc, direct)
        if can_move[0]:
            for i in player:
                movers.append(i)
          
            return pull(game, player, new_loc, direct, movers)
    return movers
    
              
def step_game(game, direction):
    """
    Given a game representation (as returned from new_game), modify that game
    representation in-place according to one step of the game.  The user's
    input is given by direction, which is one of the following:
    {'up', 'down', 'left', 'right'}.

    step_game should return a Boolean: True if the game has been won after
    updating the state, and False otherwise.
    """
    #MOVING OBJECTS
    direct = direction_vector[direction]
    
    #get current player (list of item objects)
    current_player = game.get_all_behav("YOU")
    
    movers = set()
  
    for player in current_player:
        loc = player.get_loc()
        #can we move? / is anything moving with us i.e - push
        can_move = move(game, player, loc, direct) #returns if we can move, and what we are moving (list)
        if can_move[0]:
            for obj in can_move[1]:
                movers.add(obj)
                old_loc = obj.get_loc()
                #what can be moved by the current mover from can_move
                #objects that push can also pull
                for i in pull(game, obj, old_loc, direct):
                    movers.add(i)
                    loc = i.loc
                    #but can what we are pulling, also push something?
                    mover = move(game, i, loc, direct)
                    if mover[0]:
                        for j in mover[1]:
                            movers.add(j)
    #update all movers
    for moving in movers:
        old_loc = moving.loc
        moving.update_loc((old_loc[0]+direct[0], old_loc[1]+direct[1])) 
    
    
    #update the rules
    game.update_rules(set_rules(game))
    
    visited = set()
    for i in game.rules:
        for noun in NOUNS:
            if noun in game.rules[i]:
                for obj in game.find_all_obj_name(i):
                    if obj not in visited:
                        obj.set_name(noun.lower())
                        visited.add(obj)
                game.rules[i].remove(noun)

    current_player = game.get_all_behav("YOU")
    
 
    #HANDELING DEFEAT
    #check for defeat
    defeat_objs = game.get_all_behav("DEFEAT")
    players_to_delete = []
    for defeat in defeat_objs:
        for player in current_player:
            if player.loc == defeat.loc:
                players_to_delete.append(player)
                
    #delete all the players that have run into something with defeat           
    for player in players_to_delete:
        current_player.remove(player)
        game.things.remove(player)
                
    current_player = game.get_all_behav("YOU")
    #HANDELING WIN
    #check for win
    win_objs = game.get_all_behav("WIN")
    for wins in win_objs:
        win_loc = wins.get_loc()
        for player in current_player:
            if player.loc == win_loc:
                return True
    return False
                      
def dump_game(game):
    """
    Given a game representation (as returned from new_game), convert it back
    into a level description that would be a suitable input to new_game.

    This function is used by the GUI and tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    #OG game rep
    level_description = []
    
    #loops through 2d array spaces
    for y in range(game.dims[0]):
        row = []
        for x in range(game.dims[1]):
            l = game.obj_at_loc((y,x))
            level = []
            for obj in l:
                if obj.get_name() == ["empty"]:
                    pass
                else:
                    level.append(obj.get_name())
            if "empty" in level and len(level)!= 1:
                while "empty" in level:
                    level.remove("empty")
            if level == ['empty']:
                level = []
            row.append(level)
        level_description.append(row)
    

    return level_description


    

