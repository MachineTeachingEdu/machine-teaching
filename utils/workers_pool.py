import multiprocessing
import time

data = (
    ['a', '2'], ['b', '4'], ['c', '6'], ['d', '8'],
    ['e', '1'], ['f', '3'], ['g', '5'], ['h', '7']
) 

def mp_worker(data):
    inputs, the_time = data
    output = " Processs %s\tWaiting %s seconds" % (inputs, the_time)
    time.sleep(int(the_time))
    output += " Process %s\tDONE" % inputs
    print(output)
    return output

def mp_handler():
    p = multiprocessing.Pool(2)
    output = p.map(mp_worker, data)
    return output
    
if __name__ == '__main__':
    print('oi')
    outs = mp_handler()
    print(outs)