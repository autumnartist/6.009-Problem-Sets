# No Imports Allowed!


def backwards(sound):
    s = list(sound.values())
    rate = s[0]
    given_sample = s[1]
    sample = given_sample.copy()
    #reverses list
    sample.reverse()
    #creates new sound
    new_sound = {'rate': rate, 'samples': sample}
    return new_sound
    

def mix(sound1, sound2, p):
    '''ADD DOC STRINGS FOR EACH COMMENT: tell what functions can do'''
    #check if don't have same sample rate 
    rate1 = list(sound1.values())[0]
    rate2 = list(sound2.values())[0]
    #checks if they have the same rate
    if rate1 != rate2:
        return None
    #scale sample 1
    given_sample1= list(sound1.values())[1]
    sample1 = given_sample1.copy()
    for i in range(len(sample1)):
        sample1[i] = sample1[i]*p
    #scale sample 2
    given_sample2 = list(sound2.values())[1]
    sample2 = given_sample2.copy()
    for i in range(len(sample2)):
        sample2[i] = sample2[i]*(1-p)
    #check for which is shorter
    final_sample_len = min(len(sample1), len(sample2))
    if len(sample1)<len(sample2):
        final_sample = sample1.copy()
    else:
        final_sample = sample2.copy()
    #add both lists together
    for i in range(final_sample_len):
        final_sample[i] = sample1[i] + sample2[i]
        
    final_sound = {'rate': rate1, 'samples': final_sample}
    return final_sound
 

def convolve(sound, kernel):
    #return dictionary
    sample = sound['samples'].copy()
    length = len(sample) + len(kernel) -1
    final_sample = []
    for i in range(len(kernel)):
        changed_sample = []
        #multiply
        for j in sample:
            changed_sample.append(j*kernel[i])
        #shift
        for k in range(i):
            changed_sample.insert(0,0)
            
        #check length
        if len(changed_sample) < length:
            add_nums = length-len(changed_sample)
            for l in range(add_nums):
                changed_sample.append(0)
        final_sample.append(changed_sample)
    #adding each list together
    samples = []
    for i in range(length):
        s=0
        for j in range(len(final_sample)):
            s+=final_sample[j][i]
        samples.append(s)
    final_sound = {'rate': list(sound.values())[0], 'samples': samples}
    return final_sound
      


def echo(sound, num_echoes, delay, scale):
    final_samples = []
    sam = []
    sample_delay = round(delay*sound['rate']) #add resources (given in write-up)
    length = num_echoes*sample_delay+len(sound['samples'])
    #iterate through each echo +1
    for i in range(num_echoes+1):
        samples = []
        for j in sound['samples']:
            samp = j*(scale**i)
            samples.append(samp)
        #adding the delay
        for x in range(sample_delay*i):
            samples.insert(0,0)
        #add zeros at the end 
        if samples != length :
            diff = length - len(samples)
            for k in range(diff):
                samples.append(0)
        sam.append(samples)
        
        #adding
    for i in range(length):
        s = 0
        for j in range(len(sam)):
            s += sam[j][i]
        final_samples.append(s)
        
    final_sound = {'rate': sound['rate'], 'samples': final_samples}
    return final_sound
        
    

def pan(sound):
    length = len(sound['left'])
    left_sample = sound['left'].copy()
    right_sample = sound['right'].copy()
    #scaling the both siddes
    for i in range(length):
        if i == length-1:
            right_sample[i] *= 1
            left_sample[i] *= 0
        else:
            right_sample[i] *= (i/(length-1))
            left_sample[i] *= (1-(i/(length-1)))
            
    final_sound = {'rate': sound['rate'], 'left': left_sample, 'right': right_sample}
    return final_sound


def remove_vocals(sound):
    removed_samples = []
    for i in range(len(sound['right'])):
        #different between each side sample
        sample = sound['left'][i] - sound['right'][i]
        removed_samples.append(sample)
    final_sound = {'rate': sound['rate'], 'samples': removed_samples}
    return final_sound


def bass_boost_kernel(N, scale=0):
    """
    Construct a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ N

    Then we scale that piece up and add a copy of the original signal back in.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {'rate': 0, 'samples': [0.25, 0.5, 0.25]}
    kernel = {'rate': 0, 'samples': [0.25, 0.5, 0.25]}
    for i in range(N):
        kernel = convolve(kernel, base['samples'])
    kernel = kernel['samples']

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel)//2] += 1

    return kernel


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
import wave
import struct

def load_wav(filename, stereo=False):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, 'r')
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {'rate': sr}

    if stereo:
        left = []
        right = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left.append(struct.unpack('<h', frame[:2])[0])
                right.append(struct.unpack('<h', frame[2:])[0])
            else:
                datum = struct.unpack('<h', frame)[0]
                left.append(datum)
                right.append(datum)

        out['left'] = [i/(2**15) for i in left]
        out['right'] = [i/(2**15) for i in right]
    else:
        samples = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left = struct.unpack('<h', frame[:2])[0]
                right = struct.unpack('<h', frame[2:])[0]
                samples.append((left + right)/2)
            else:
                datum = struct.unpack('<h', frame)[0]
                samples.append(datum)

        out['samples'] = [i/(2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, 'w')

    if 'samples' in sound:
        # mono file
        outfile.setparams((1, 2, sound['rate'], 0, 'NONE', 'not compressed'))
        out = [int(max(-1, min(1, v)) * (2**15-1)) for v in sound['samples']]
    else:
        # stereo
        outfile.setparams((2, 2, sound['rate'], 0, 'NONE', 'not compressed'))
        out = []
        for l, r in zip(sound['left'], sound['right']):
            l = int(max(-1, min(1, l)) * (2**15-1))
            r = int(max(-1, min(1, r)) * (2**15-1))
            out.append(l)
            out.append(r)

    outfile.writeframes(b''.join(struct.pack('<h', frame) for frame in out))
    outfile.close()

if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    #hello = load_wav('sounds/hello.wav')
    #write_wav(backwards(hello), 'hello_reversed.wav')
    
    #Backwards
    #mystery = load_wav('sounds/mystery.wav')
    #write_wav(backwards(mystery), 'mystery.wav')
    
    #Mixing Audio
    #synth = load_wav('sounds/synth.wav')
    #water = load_wav('sounds/water.wav')
    #write_wav(mix(synth, water, 0.2), 'mixedAudio.wav')

    #Convolutional Filters
    #kernel = bass_boost_kernel(1000, 1.5)
    #ice = load_wav('sounds/ice_and_chilli.wav')
    #write_wav(convolve(ice, kernel), 'ice_and_chilli_test.wav')
    
    #Echo
    chord = load_wav('sounds/chord.wav')
    write_wav(echo(chord, 5, 0.3, 0.6), 'chord_test.wav')
                     
    #Pan
    #car = load_wav('sounds/car.wav', True)
    #write_wav(pan(car), 'car_test.wav')
    
    #Removing vocals
    #lookout = load_wav('sounds/lookout_mountain.wav', True)
    #write_wav(remove_vocals(lookout), 'lookout.wav')