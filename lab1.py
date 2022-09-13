#!/usr/bin/env python3

import math

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, x, y):
    return image['pixels'][image['width']*y+x]


def set_pixel(image, x, y, c):
    image['pixels'][image['width']*y+x] = c


def apply_per_pixel(image, func):
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [],
    }
    for y in range(image['height']):
        for x in range(image['width']):
            result['pixels'].append(get_pixel(image, x, y))
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)
    return result


def inverted(image):
    return apply_per_pixel(image, lambda c: 255-c)


# HELPER FUNCTIONS

def get_pixel_bounds(image, x, y, boundary_behavior):
    if boundary_behavior == 'zero':
        if (x>=0 and y>= 0) and (x<image['width'] and y<image['height']):
            return get_pixel(image, x, y)
        return 0
    
    if boundary_behavior == 'extend':
        if (x<0 and y<0):
            return get_pixel(image,0,0)
        elif (x<0 and y>= image['height']):
            return get_pixel(image, 0, image['height']-1)
        elif (y<0 and x>= image['width']):
            return get_pixel(image, image['width']-1, 0)
        elif (x>=image['width'] and  y>=image['height']):
            return get_pixel(image, image['width']-1, image['height']-1)
        elif (x<0):
            return get_pixel(image, 0, y)
        elif (y<0):
            return get_pixel(image,x,0)
        elif (y>=image['height']):
            return get_pixel(image, x, image['height']-1)
        elif (x>= image['width']):
            return get_pixel(image, image['width']-1, y)
        else:
            return get_pixel(image, x, y)
    
    if boundary_behavior == 'wrap':        
        if (x<0 and y<0):
            return get_pixel(image, (image['width']-abs(x)%image['width']), image['height']-abs(y)%image['height'])
        
        elif (x>=image['width'] and y<0):
            return get_pixel(image, x%image['width'], image['height']-abs(y)%image['height'])
        
        elif (x<0 and y>= image['height']):
            return get_pixel(image, image['width']-abs(x)%image['width'], y%image['height'])
        
        elif (x>=image['width'] and y>=image['height']):
            return get_pixel(image, (x)%image['width'], y%image['height'])
        
        elif y<0:
            return get_pixel(image, x, image['height']-abs(y)%image['height'])
        
        elif y>=image['height']:
            return get_pixel(image, x, abs(y)%image['height'])
        
        elif x<0:
            return get_pixel(image, image['width']-abs(x)%image['width'], y)
        
        elif x>= image['width']:
            return get_pixel(image, x%image['width'], y)
        
        else:
            return get_pixel(image,x,y)
        

def apply_kernel(image, x, y, kernel, boundary_behavior):
    bound = int(len(kernel)**(1/2))
    num =0
    for j in range(bound):
        for i in range(bound):
            kernel_index = int(len(kernel)**(1/2))*j+i
            image_x = x-int(bound/2)+i
            image_y = y-int(bound/2)+j
            num += (get_pixel_bounds(image, image_x, image_y, boundary_behavior)*kernel[kernel_index])
    return num 


def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings 'zero', 'extend', or 'wrap',
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of 'zero', 'extend', or 'wrap', return
    None.

    Otherwise, the output of this function should have the same form as a 6.009
    image (a dictionary with 'height', 'width', and 'pixels' keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    """
    pixels = []
    for y in range(image['height']):
        for x in range(image['width']):
            pixels.append(apply_kernel(image, x, y, kernel, boundary_behavior))

    new_image = {'height': image['height'],
                 'width': image['width'],
                 'pixels': pixels}
    return new_image


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    pix = image['pixels'].copy()
    for i in range(len(image['pixels'])):
        pix[i] = round(pix[i])
        if pix[i]>255:
            pix[i] = 255
        if pix[i]<0:
            pix[i] = 0
    new_image = {'height': image['height'],
                 'width': image['width'],
                 'pixels': pix}
    return new_image



# FILTERS
def findKernelN(n):
    kern = []
    for i in range(n):
        for j in range(n):
            kern.append(1/n**2)
    return kern

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    kernel = findKernelN(n)
    copy_image = image.copy()

    # then compute the correlation of the input image with that kernel using
    # the 'extend' behavior for out-of-bounds pixels
    blurred_image = correlate(copy_image, kernel, 'extend')
    #TESTING OTHER EDGE EFFECTS
    #blurred_image = correlate(image, kernel, 'zero')
    #blurred_image = correlate(image, kernel, 'wrap')

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    return round_and_clip_image(blurred_image)


def sharpened(image, n):
    sharp_pixs = []
    copied_image = image.copy()
    blurred_image = blurred(copied_image, n)
    
    for i in range(len(image['pixels'])):
        sharp_pixs.append(copied_image['pixels'][i]*2 - blurred_image['pixels'][i])

    sharp_image = {'height': copied_image['height'],
                   'width': copied_image['width'],
                   'pixels': sharp_pixs}
    
    finished_sharp_image = round_and_clip_image(sharp_image)
    return finished_sharp_image

def edges(image):
    kx = [-1, 0, 1, -2, 0, 2, -1, 0, 1]
    ky = [-1, -2, -1, 0, 0, 0, 1,  2,  1]
    
    ox = correlate(image, kx, 'extend')
    oy = correlate(image, ky, 'extend')

    edge_pixs = []
    for i in range(len(image['pixels'])):
        pix = (ox['pixels'][i]**2 + oy['pixels'][i]**2)**(1/2)
        edge_pixs.append(round(pix))
    
    edge_im = {'height': image['height'],
               'width': image['width'],
               'pixels': edge_pixs}
    finished_edge_image = round_and_clip_image(edge_im)
    return finished_edge_image

    
# COLOR FILTERS

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def filter_color(color_image):
        #splits each color its own image
        image_red = {'height': color_image['height'],
                     'width': color_image['width'],
                     'pixels': [0]*len(color_image['pixels'])}
        
        image_green = {'height': color_image['height'],
                     'width': color_image['width'],
                     'pixels': [0]*len(color_image['pixels'])}
        
        image_blue = {'height': color_image['height'],
                     'width': color_image['width'],
                     'pixels': [0]*len(color_image['pixels'])}
        #each color is only made up of that color (like greyscale)
        for i in range(len(color_image['pixels'])):
            image_red['pixels'][i] = color_image['pixels'][i][0]
            
            image_green['pixels'][i] = color_image['pixels'][i][1]
            
            image_blue['pixels'][i] = color_image['pixels'][i][2]
        #applies filter on each singlar color
        new_red = filt(image_red)
        new_green = filt(image_green)
        new_blue = filt(image_blue)
        
        final_pixs = []
        for i in range(len(color_image['pixels'])):
            final_color = (new_red['pixels'][i], new_green['pixels'][i], new_blue['pixels'][i])
            final_pixs.append(final_color)
            
        final_image = {'height': color_image['height'],
                       'width': color_image['width'],
                       'pixels': final_pixs}
        return final_image
    return filter_color


def make_blur_filter(n):
    def color_blur(image):
        return blurred(image, n)
    return color_blur


def make_sharpen_filter(n):
    def color_sharpen(image):
        return sharpened(image, n)
    return color_sharpen


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def final_filter(image):
        filter_image = image.copy()
        for filts in filters:
            filter_image = filts(filter_image)
        return filter_image
    return final_filter

import random
def randomize(image):
    random_image = image.copy()
    for i in range(len(random_image['pixels'])):
        #red = random.randint(0, 255)
        #green = random.randint(0, 255)
        #blue = random.randint(0, 255)
        pixel = random.randint(0, 255)
        random_image['pixels'][i] = pixel
    return random_image

# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_greyscale_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    
    #INVERTING IMAGES
    #image1 = load_greyscale_image('test_images/bluegill.png')
    #inverted_image1 = inverted(image1)
    #saved_inverted_image1 = save_greyscale_image(inverted_image1, 'invertbluegill.png')
    
    #TESTING CORRELATE
    #corr_kernel = []
    #for i in range(13):
    #    for j in range(13):
    #        corr_kernel.append(0)
    #corr_kernel[26] = 1
    
    #image_pig_bird = load_greyscale_image('test_images/pigbird.png')
    #cor_zero = correlate(image_pig_bird, corr_kernel, 'zero')
    #saved_coer_zero = save_greyscale_image(cor_zero, 'pig_bird_zero.png')
    
    #cor_extend = correlate(image_pig_bird, corr_kernel, 'extend')
    #saved_coer_extend = save_greyscale_image(cor_extend, 'pig_bird_extend.png')
    
    #cor_wrap = correlate(image_pig_bird, corr_kernel, 'wrap')
    #saved_coer_wrap = save_greyscale_image(cor_wrap, 'pig_bird_wrap.png')
    
    #BLURRED
    #blurred_im = load_greyscale_image('test_images/cat.png')
    #blurred_image1 = blurred(blurred_im, 13)
    #saved_blurred_image1 = save_greyscale_image(blurred_image1, 'blurredCat.png')
    
    #SHARPEN
    #sharp_im = load_greyscale_image('test_images/python.png')
    #sharp_image1 = sharpened(sharp_im, 11)
    #saved_sharp_image = save_greyscale_image(sharp_image1, 'sharpPython.png')
    
    #EDGE 
    #edge_im = load_greyscale_image('test_images/construct.png')
    #edge_image1 = edges(edge_im)
    #saved_edge_image = save_greyscale_image(edge_image1, 'constructEdge.png')
            
    #COLOR FILTER
    #inverted_cat = inverted(load_greyscale_image('test_images/cat.png'))
    #color_inverted = color_filter_from_greyscale_filter(inverted)
    #inverted_color_cat = color_inverted(load_color_image('test_images/cat.png'))
    #saved_cat = save_color_image(inverted_color_cat, 'colorCat.png')
    
    #COLOR BLUR
    #blur_python = blurred(load_greyscale_image('test_images/python.png'), 9)
    #color_blurred = color_filter_from_greyscale_filter(make_blur_filter(9))
    #blurred_color_python = color_blurred(load_color_image('test_images/python.png'))
    #saved_blurry_python = save_color_image(blurred_color_python, 'blurryPython.png')
    
    #COLOR SHARPEN
    #sharpen_chick = sharpened(load_greyscale_image('test_images/sparrowchick.png'), 7)
    #color_sharpened = color_filter_from_greyscale_filter(make_sharpen_filter(7))
    #sharp_color_chick = color_sharpened(load_color_image('test_images/sparrowchick.png'))
    #saved_sharp_chick = save_color_image(sharp_color_chick, 'sharpenedSparrowChick.png')
    
    #CASCADE 
    #filter1 = color_filter_from_greyscale_filter(edges)
    #filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    #filt = filter_cascade([filter1, filter1, filter2, filter1])
    
    #frog = load_color_image('test_images/frog.png')
    #filtered_frog = filt(frog)
    #saved_filtered_frog = save_color_image(filtered_frog, 'filteredFrog.png')
    
    #SOMETHING OF YOUR OWN - cascading + randomize - making TV static
    filter_random = color_filter_from_greyscale_filter(randomize)
    filter_edge = color_filter_from_greyscale_filter(edges)
    filter_blur = color_filter_from_greyscale_filter(make_blur_filter(7))
    filt2 = filter_cascade([filter_random, filter_blur, filter_edge, filter_blur])
    
    mushroom = load_color_image('test_images/mushroom.png')
    filtered_mushroom = filt2(mushroom)
    saved_filtered_mushrom = save_color_image(filtered_mushroom, 'filteredMushroom.png')
    
    pass
