import os

import numpy as np
import json
import subprocess
import os

def get_data(name):
    return subprocess.check_output(f'.\\read_wav.exe {name}').decode("utf-8").split("\r\n")[:-1]

def read_file(name):
    DATA=get_data(name)
    print(DATA[:3])
    np.seterr(divide='raise')

    header1 = json.loads(DATA[0].replace(",",".",1))
    header2 = json.loads(DATA[1])
    bit_depth = header1["bit depth"]
    sample_amount = header2["Sample amount"]
    duration = header1["Duration"]
    sample_rate = header1['Sample Rate']

    dtype = f"int{bit_depth}"
    max_abs_val = 30000

    full_sample = np.array(list(map(int,DATA[2:])))

    N = 2000
    n = N//2

    window = 1 - np.abs(np.linspace(-1,1,N))

    if full_sample.size % N != 0:
        full_sample = np.append(full_sample, np.zeros(N - full_sample.size % N))

    output = np.zeros(full_sample.size, dtype=dtype)
    Gs = np.zeros(full_sample.size // n, dtype=dtype)

    for i in range(full_sample.size // n):
        samp = np.array(full_sample[n * i:n * (i + 2)], dtype=dtype)
        m = np.abs(samp).max()
        try:
            g = max_abs_val // m
        except FloatingPointError:
            g = 1
        Gs[i] = g

    for i in range(full_sample.size // n - 1):
        samp = np.array(full_sample[n * i:n * (i + 1)], dtype = dtype)
        samp = samp*(window[:n]*Gs[i+1] + (window[n:]*Gs[i]))
        samp = np.clip(samp, a_min=-max_abs_val, a_max=max_abs_val)

        output[n * i:n * (i + 1)] = np.array(samp).astype(dtype)
    samp = np.array(full_sample[-n:], dtype = dtype)
    samp = samp*(window[:n]*Gs[-1] + (window[n:]*Gs[-1]))
    samp = np.clip(samp, a_min=-max_abs_val, a_max=max_abs_val)
    output[-n:] = np.array(samp).astype(dtype)
    output2 = np.zeros(output.size, dtype=dtype)

    for i in range(output.size // n - 1):
        output2[n * i:n * (i + 1)] = (output[n * i:n * (i + 1)])//(window[n:]*(Gs[i] - Gs[i+1]) + Gs[i+1])

    output2[-n:] = (output[-n:])//(Gs[-1])

    dif=full_sample - output2
    L_time=np.linspace(0,duration,output.size)
    return [header1,[[L_time,full_sample],[L_time,output],[L_time,output2],[L_time,dif]]]

if __name__=="__main__":
    print(read_file("C:\\Users\\Всеволод\\Desktop\\Код_С++\\done\\sample32bit8.wav"))
