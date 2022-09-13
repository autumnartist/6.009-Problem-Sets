#!/usr/bin/env python3

import typing
from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}


DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}

      
def build_internal_representation(nodes_filename, ways_filename):
    """
    Create any internal representation you you want for the specified map, by
    reading the data from the given filenames (using read_osm_data)
    
    3 dictionaries 
    1. node: children
    2. node: (end, speed limit)
    3. node: (long, lat)
    
    """
    
    #dictionary of frozen sets
    #dictionary of nodes
    #node: which node they connect to
    
    '''
    for node in read_osm_data(nodes_filename):
        print(node)
    
    print()
    
    for way in read_osm_data(ways_filename):
        print(way)
    '''
    #DICTIONARY OF NODES:CHILDREN (route1)
    #id: set((lat,lon), (child, SL))
    #{id: {location: (lat, lon), child: {child1, child2}},}
    #creates a dictionary of nodes 
    nodesUsed = set()
    route = {}
    #route = {'id': {'location': (None,), 'child': set()}}
    #finds what each node is connected to
    #for loop instead
    for way in read_osm_data(ways_filename):
        
        #check highway
        try: 
            highway = way['tags']['highway']
        except:
            highway = None
        else:
            highway = way['tags']['highway']
        
        
        if highway in ALLOWED_HIGHWAY_TYPES:
            #check speed_limit
            try:
                speed_limit = way['tags']['maxspeed_mph']
            except:
                speed_limit = DEFAULT_SPEED_LIMIT_MPH[highway]
            else:
                speed_limit = way['tags']['maxspeed_mph']
            
            for i in range(len(way['nodes'])-1):
                
                id_start = way['nodes'][i]
                if id_start not in nodesUsed:
                    route[id_start] = {'coord': (), 'child': set()}
                    nodesUsed.add(id_start)
                             
                #add children
                id_end = way['nodes'][i+1]
                
                children = route[id_start]['child']
                children.add((id_end, speed_limit))
                route[id_start]['child'] = children

                
                #oneway street?
                try:
                    oneway = way['tags']['oneway']
                except:
                    oneway = None
                else:
                    oneway = way['tags']['oneway']
                    
                if id_end not in nodesUsed:
                    nodesUsed.add(id_end)
                    route[id_end] = {'coord': (), 'child': set()} 
                 
                if oneway == None or oneway == 'no':
                    
                    if id_end not in nodesUsed:
                        nodesUsed.add(id_end)
                        route[id_end] = {'coord': (), 'child': set()}
                    
                    children = route[id_end]['child']
                    children.add((id_start, speed_limit))
                    route[id_end]['child'] = children  
         
    #adding locations
    for nodes in read_osm_data(nodes_filename):
        if nodes['id'] in nodesUsed:
            route[nodes['id']]['coord'] = (nodes['lat'], nodes['lon'])
            
       
    return route

def findDistance(map_rep, node1, node2):
    '''
    Given a list of nodes and the map_rep, finds the distance in the list
    '''
    loc1 = map_rep[node1]['coord']
    loc2 = map_rep[node2]['coord']
    return great_circle_distance(loc1, loc2)
        
def find_short_path_nodes(map_rep, node1, node2):
    """
    Return the shortest path between the two nodes

    Parameters:
        map_rep: the result of calling build_internal_representation
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    """
    
    
    if node1 not in map_rep:
        return None

    
    #(distance, tuple_path)
    agenda = [(0, (node1,))]
    visited = set()
    #possible_paths = set()
    
    while agenda:
       
        current_cost, current_path  = min(agenda)
        #current_cost = min(agenda)[0]
        #current_path = min(agenda)[1]
        
        agenda.remove(min(agenda))
        #agenda.discard(min(agenda))
        
     
        vertex = current_path[-1]
        
        if vertex == node2:
            return current_path
        elif vertex in visited:
            continue
        
        visited.add(vertex)
        
        
        #vertex not in visited
        #find all children
        for child in map_rep[vertex]['child']:
            child = child[0]
            if child in visited or child not in map_rep:
                continue
    
            new_path = current_path + (child,)
            #find distance:
            distance = findDistance(map_rep, vertex, child)
            agenda.append((current_cost+distance, new_path))
        

    if agenda == []:
        return None
    
    return agenda

                    
                        

#helper function to convert locs to nodes
def find_closest_nodes(map_rep, loc1, loc2):
    '''
    Given a map_represtation and 2 locations, finds the closest nodes 
    for each given location
    
    Returns a tuple with the nodes corresponding to the order of the 
    locations put in the parameters
    '''
    
    #look through children too 
    
    distance1 = set()
    distance2 = set()
    
    for node in map_rep:
        #check node id
        loc = map_rep[node]['coord']
            
        distance1.add((great_circle_distance(loc1, loc), node))
        distance2.add((great_circle_distance(loc2, loc), node))
     
    node1 = min(distance1)[1]
    node2 = min(distance2)[1]
    
    return [node1, node2]

def convertToLocs(map_rep, path):
    '''
    Given a map representation and list of nodes (path), returns a 
    list of tuples representing the locations.
    '''
    locpath = []
    for i in path:
        locpath.append(map_rep[i]['coord'])
    return locpath

def find_short_path(map_rep, loc1, loc2):
    """
    Return the shortest path between the two locations

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
        
    #H
    g(n) = distance from node to its child
    h(n) = distance from node to end_node
    
    distance (in short_path_node) = g(n)+h(n)
    
    agenda = (real_theo, real, new_path)
    
    
    """
    node1, node2 = find_closest_nodes(map_rep, loc1, loc2)
    path = find_short_path_nodes(map_rep, node1, node2)
    
    if path == None:
        return None
    
    final_path = convertToLocs(map_rep, path)
    
    return final_path


def find_short_path_heuristic(map_rep, loc1, loc2):
    '''
    heuistic approach to short_path, to compare run times
    '''
    node1, node2 = find_closest_nodes(map_rep, loc1, loc2)
        
    #(real + theoretical distance, real_distance, tuple_path)
    agenda = [(0, 0, (node1,))]
    visited = set()
    #possible_paths = set()
    
    while agenda:
       
        current_totalcost, current_realcost, current_path  = min(agenda)
        #current_cost = min(agenda)[0]
        #current_path = min(agenda)[1]
        
        agenda.remove(min(agenda))
        #agenda.discard(min(agenda))
        
     
        vertex = current_path[-1]
        
        if vertex == node2:
            #convert path to tuple of locs
            path = convertToLocs(map_rep, current_path)
            return path
        elif vertex in visited:
            continue
        
        visited.add(vertex)
        
        
        #vertex not in visited
        #find all children
        for child in map_rep[vertex]['child']:
            child = child[0]
            if child in visited or child not in map_rep:
                continue
    
            new_path = current_path + (child,)
            #find distance:
            realDistance = findDistance(map_rep, vertex, child) 
            fakeDistance = findDistance(map_rep, child, node2)
            total_distance = realDistance + fakeDistance
            agenda.append((total_distance, current_realcost+realDistance, new_path))
        

    if agenda == []:
        return None
    
    return agenda


def find_fast_path(map_rep, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
        
    """
    
    node1, node2 = find_closest_nodes(map_rep, loc1, loc2)
    
    if node1 not in map_rep:
        return None

    
    #(time, tuple_path)
    agenda = [(0, (node1,))]
    visited = set()
    #possible_paths = set()
    
    while agenda:
        current_time, current_path  = min(agenda)
        #current_cost = min(agenda)[0]
        #current_path = min(agenda)[1]
        
        agenda.remove(min(agenda))
        #agenda.discard(min(agenda))
        
     
        vertex = current_path[-1]
        
        if vertex == node2:
            path = convertToLocs(map_rep, current_path)
            #print(path)
            return path
        elif vertex in visited:
            continue
        
        
        
        #vertex not in visited
        #find all children
        for child in map_rep[vertex]['child']:
            children = child[0]
            speed_limit = child[1]
            if children in visited or children not in map_rep:
                continue
    
            new_path = current_path + (children,)
            #find distance:
            distance = findDistance(map_rep, vertex, children)
            time = distance/speed_limit
            agenda.append((current_time+time, new_path))
        visited.add(vertex)
    
    if agenda == []:
        return None
    
    return agenda



if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    
    waltham = (42.376485, -71.235611)
    salem = (42.519539,-70.896713)
    map1 = build_internal_representation('resources/cambridge.nodes', 'resources/cambridge.ways')
    #print(to_local_kml_url(find_short_path(map1, waltham, salem)))
    print(to_local_kml_url(find_fast_path(map1, waltham, salem)))
    
    
    #map_rep = build_internal_representation('resources/midwest.nodes', 'resources/midwest.ways')
    #map_rep = build_internal_representation('resources/mit.nodes', 'resources/mit.ways')
    #print(map_rep)
    #loc1 = (42.3576, -71.0952) # Kresge
    #loc2 = (42.355, -71.1009) # New House
    
    #print(find_fast_path(map_rep, loc1, loc2))
    
    
    #print(map_rep)
    #loc1 = (41.4452463, -89.3161394)
    #distances = set()
    
    #for node in map_rep:
    #    loc2 = map_rep[node]['coord']
    #    dis = great_circle_distance(loc1, loc2)
        
    #    distances.add((dis, node))
    
    
    #print(distances)
    #print()
    #print(min(distances))
    #print(min(distances)[1])
    
    
    
    #finding total nodes
    #counter = 0
    #for node in read_osm_data('resources/cambridge.nodes'):
    #    counter+=1
    #print(counter)
    
    #number of nodes with names
    #counter=0
    #for node in read_osm_data('resources/cambridge.nodes'):
    #    if 'name' in node['tags']:
    #        counter+=1
    #print(counter)
    
    #finding ID number
    #for node in read_osm_data('resources/cambridge.nodes'):
    #    if 'name' in node['tags']:
    #        if node['tags']['name'] == '77 Massachusetts Ave':
    #            print(node)
    #            print(node['id'])
                
    #number of ways
    #counter = 0
    #for way in read_osm_data('resources/cambridge.ways'):
    #    counter+=1
    #print(counter)
            
    #number of one way street
    #counter = 0
    #for way in read_osm_data('resources/cambridge.ways'):
    #    if 'oneway' in way['tags']:
    #        if way['tags']['oneway'] == 'yes':
    #            counter+= 1
    #print(counter)
    
    #number of 'valid' ways 
    #nodes = set()
    #for way in read_osm_data('resources/cambridge.ways'):
    #    if 'highway' in way['tags']:
    #        if way['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
    #            for node in way['nodes']:
    #                if node not in nodes:
    #                    nodes.add(node)               
    #print(len(nodes))
    
    #distance with lon, lat
    #loc1 = (42.363745, -71.100999)
    #loc2 = (42.361283, -71.239677)
    #print(great_circle_distance(loc1, loc2))
    
    #route = build_internal_representation('resources/midwest.nodes', 'resources/midwest.ways')
    #loc3 = route[233941454]
    #loc4 = route[233947199]
    #print(great_circle_distance(loc3, loc4))
    
    
    #for way in read_osm_data('resources/midwest.ways'):
    #    if way['id'] == 21705939:
    #        nodes = way['nodes']
            
    #distance = 0
    #for i in range(len(nodes)-1):
    #    distance+= great_circle_distance(route[nodes[i]], route[nodes[i+1]])
    #print(distance)
    pass

