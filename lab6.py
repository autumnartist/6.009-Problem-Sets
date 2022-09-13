import sys
from http009 import http_response

import typing
import doctest

sys.setrecursionlimit(10000)

# NO ADDITIONAL IMPORTS!


# custom exception types for lab 6


class HTTPRuntimeError(Exception):
    pass


class HTTPFileNotFoundError(FileNotFoundError):
    pass


# functions for lab 6
def get_redirect_url(url):
    redirect = [301, 302, 307]
    try:
        r = http_response(url)
    except ConnectionError:
        raise HTTPRuntimeError()
    else:
        stat = r.status
        #print(stat)
        if stat == 404:
            raise HTTPFileNotFoundError()
        elif stat == 500:
            raise HTTPRuntimeError()
        elif stat in redirect:
            new_url = r.getheader('location')
            #print(new_url)
            #print()
            return get_redirect_url(new_url)
    return (r, url)     

def download_file(url, chunk_size=8192, cache_dict=None):
    """
    Yield the raw data from the given URL, in segments of at most chunk_size
    bytes (except when retrieving cached data as seen in section 2.2.1 of the
    writeup, in which cases longer segments can be yielded).

    If the request results in a redirect, yield bytes from the endpoint of the
    redirect.

    If the given URL represents a manifest, yield bytes from the parts
    represented therein, in the order they are specified.

    Raises an HTTPRuntimeError if the URL can't be reached, or in the case of a
    500 status code.  Raises an HTTPFileNotFoundError in the case of a 404
    status code.
    """
    if cache_dict == None:
        cache_dict = {}
    #what happens when url is bad????
    r, url_manifest = get_redirect_url(url)

    #if NOT manifest
    if ('.parts' != url_manifest[-6:]) and http_response(url_manifest).getheader('content-type') != 'text/parts-manifest':
        #check status code and update URL
        chunk = r.read(chunk_size)
        while chunk != b'':
            yield chunk
            chunk = r.read(chunk_size)
        
    #if manifest
    else:
        url_line = r.readline().decode('utf-8').strip()
        #creates the cache dict
            
            
        #creates lists of clusters of URLs
        while url_line != "":
            #print(url_line)
            lines = []
            #checks if all url don't work
            works = False
            while url_line != '--':
                lines.append(url_line)
                url_line = r.readline().decode('utf-8').strip()
             
                if url_line == '':
                    break
            #to skip b'--' 
            url_line = r.readline().decode('utf-8').strip()
            
            #goes through the clusters of urls as they are being made
            cacheable = '(*)' in lines
            #print("new group")
            for j in lines:
                #print(j)
                # check if cache
                if cacheable: 
                    #print("caching")
                #check if in cache_dict
                #if it is in dict - yeild
                    if j == '(*)':
                        continue
                    else:
                        if j in cache_dict:
                            #print("in dict.")
                            works = True
                            yield cache_dict[j]
                            break
                        else:
                            try:
                                gen = download_file(j, chunk_size, cache_dict)
                            except:
                                continue
                            
                            #if gen works - add to dict - call download_file
                            works = True
                            cache_dict[j] = bytearray()
                            for chunk in gen:
                                cache_dict[j].extend(chunk)
                            yield cache_dict[j]
                            break
                #if its not cacheable
                else:
                    try:
                        yield from download_file(j, chunk_size)
                        #for chunk in download_file(i.decode()):
                        #    yield chunk
                        works = True
                        #print('true')
                        break
                    except:
                        continue
                #print(works)
                if not works:
                    raise HTTPFileNotFoundError()   
            

def split_chunk(byte):
    length = int.from_bytes(byte[:4], 'big')
    yield byte[4:length+4]
    
    
def files_from_sequence(stream):
    """
    Given a generator from download_file that represents a file sequence, yield
    the files from the sequence in the order they are specified.
    """
    #byte length
    length = 0
    byte = b''
    chunk = next(stream)
    #4 byte length

    while chunk != b'':
        byte+= chunk
        
        #finds the byte with the length
        while len(byte)<=4:
            try:
                chunk = next(stream)
            except:
                break
            byte+=chunk
        
        length = int.from_bytes(byte[:4], 'big')
        byte = byte[4:]
        
        #find the file
        while len(byte)<=length:
            try:
                chunk = next(stream)
            except:
                    break
            byte+=chunk
        
      
        yield byte[:length]
        byte = byte[length:]
        try:
            chunk = next(stream)
        except: 
            break
    #if there's leftover bytes
        
    while len(byte) != 0:
        length = int.from_bytes(byte[:4], 'big')
        yield byte[4:length+4]
        byte = byte[length+4:]
        
        
    
    


if __name__ == "__main__":
    
    #print(sys.argv)
    lab = sys.argv[0]
    url = sys.argv[1]
    file_name = sys.argv[2]
    g = download_file(url)
    h = files_from_sequence(g)
    file = open(file_name, 'wb') 
    for i in h:
        file.write(i)
    

    
    #url = 'http://scripts.mit.edu/~6.009/lab6/redir.py/0/cat_poster.jpg.parts'
    #print(http_response(url).status)
    #print(get_redirect_url(url))
    #if ('.parts' not in url) and http_response(url).getheader('content-type') != 'text/parts-manifest':
    #    print('hi')
    #print(download_file('http://mit.edu/6.009/www/lab6_examples/yellowsub.txt.parts '))
    
    pass
    
    
