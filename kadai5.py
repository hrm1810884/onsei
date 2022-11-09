import scipy
from scipy.io.wavfile import read
import numpy as np
import matplotlib.pyplot as plt
import glob

framelen = 512
dim = 15


def FFT(xr, xi, Xr, Xi, N):
    bufsize = 0
    if (bufsize != N):
        bufsize = N
    i = j = 0
    rbuf = [0]*N
    ibuf = [0]*N
    rbuf[j] = xr[j]
    ibuf[j] = xi[j]
    for j in range(1, N-1):
        k = int(N/2)
        while (k <= i):
            i -= k
            k = int(k/2)
        i += k
        rbuf[j] = xr[i]
        ibuf[j] = xi[i]
    rbuf[j] = xr[j]
    ibuf[j] = xi[j]

    theta = -2.0*np.pi
    n = 1
    while (n*2 <= N):
        theta *= 0.5
        for i in range(n):
            wr = np.cos(theta*i)
            wi = np.sin(theta*i)
            for j in range(i, N, n*2):
                k = j+n
                Xr[j] = rbuf[j] + wr*rbuf[k] - wi*ibuf[k]
                Xi[j] = ibuf[j] + wi*rbuf[k] + wr*ibuf[k]
                Xr[k] = rbuf[j] - wr*rbuf[k] + wi*ibuf[k]
                Xi[k] = ibuf[j] - wi*rbuf[k] - wr*ibuf[k]
        for i in range(N):
            rbuf[i] = Xr[i]
            ibuf[i] = Xi[i]
        n = n*2


def IFFT(Xr, Xi, xr, xi, N):
    bufsize = 0
    if (bufsize != N):
        bufsize = N
    i = j = 0
    rbuf = [0.0]*bufsize
    ibuf = [0.0]*bufsize
    rbuf[j] = float(Xr[j]/N)
    ibuf[j] = float(Xi[j]/N)
    for j in range(1, N-1):
        k = int(N/2)
        while (k <= i):
            i -= k
            k = int(k/2)
        i += k
        rbuf[j] = float(Xr[i]/N)
        ibuf[j] = float(Xi[i]/N)
    rbuf[j] = float(Xr[j]/N)
    ibuf[j] = float(Xi[j]/N)

    theta = 2.0*np.pi
    n = 1
    while (n*2 <= N):
        theta *= 0.5
        for i in range(n):
            wr = np.cos(theta*i)
            wi = np.sin(theta*i)
            for j in range(i, N, n*2):
                k = j+n
                xr[j] = rbuf[j] + wr*rbuf[k] - wi*ibuf[k]
                xi[j] = ibuf[j] + wr*ibuf[k] + wi*rbuf[k]
                xr[k] = rbuf[j] - wr*rbuf[k] + wi*ibuf[k]
                xi[k] = ibuf[j] - wr*ibuf[k] - wi*rbuf[k]
        for i in range(N):
            rbuf[i] = xr[i]
            ibuf[i] = xi[i]
        n = n*2


def trim(data):
    length = 1000
    count = len(data)//length
    lim_min = 0
    lim_max = len(data)
    threshhold = 500
    for i in range(count):
        sum = 0
        for j in range(length):
            sum += abs(data[length*i + j])
        ave = sum/length
        if (ave <= threshhold):
            lim_min = length*(i+1)
        else:
            break
    for i in range(count-1, -1, -1):
        sum = 0
        for j in range(length):
            sum += abs(data[length*i + j])
        ave = sum/length
        if (ave <= threshhold):
            lim_max = length*i
        else:
            break
    return data[lim_min:lim_max]


def cepstrum(data, head):
    x = data[head:head+framelen]
    window_func = np.hamming(framelen)
    x_w = window_func * x
    X = np.fft.fft(x_w)
    power_r = np.log10((X.real**2 + X.imag**2)/framelen)
    x_ = np.fft.ifft(power_r)
    return x_.real[1:1+dim]


def calc(filename):
    ave = np.zeros(dim)
    rate, data = read(filename)
    sound = trim(data)
    head = 0
    count = (len(sound)-framelen)//(framelen//2)
    for i in range(count):
        ave += cepstrum(sound, head)
        head += framelen//2
    ave /= count
    return ave


def train(spk):
    ceps = np.zeros(dim)
    folda = glob.glob("../new_vowels/train/"+spk+"/*.wav")
    for file in folda:
        ceps += calc(file)
    ceps /= len(folda)
    return ceps


def comp(data_test, data_train):
    euclid = 0
    for i in range(dim):
        euclid += (data_test[i] - data_train[i])**2
    return euclid


def test(trains):
    spks = ["spk1", "spk2", "spk3", "spk4"]
    test_num = 0
    success_num = 0
    f = open("test.txt", 'w')
    for spk in spks:
        success_num_spk = 0
        test_num_spk = 0
        folda = glob.glob("../new_vowels/test/"+spk+"/*.wav")
        for file in folda:
            test_num += 1
            test_num_spk += 1
            rate, data = read(file)
            sound = trim(data)
            head = 0
            count = (len(sound)-framelen)//(framelen//2)
            spk_point = [0, 0, 0, 0]
            for i in range(count):
                test_data = cepstrum(sound, head)
                if("spk4_aeiou_05.wav" in file):
                    print(test_data)
                for j, train_data in enumerate(trains):
                    euclid = comp(test_data, train_data)
                    if("spk4_aeiou_05.wav" in file):
                        print(euclid)
                    spk_point[j] += euclid
                head += framelen//2
            spk_min = spk_point.index(min(spk_point))
            f.write(spk+" "+spks[spk_min]+" ")
            if (spk == spks[spk_min]):
                success_num += 1
                success_num_spk += 1
                f.write("succeed!")
            else:
                f.write("failed...")
            f.write("\n")
        f.write("accuracy for " + spk + " : " +
                str(float(success_num_spk/test_num_spk)*100) + "\n")
    f.write("accuracy for all : " + str(float(success_num/test_num)*100))
    f.close()


def main():
    train_data1 = train("spk1")
    train_data2 = train("spk2")
    train_data3 = train("spk3")
    train_data4 = train("spk4")
    trains = [train_data1, train_data2, train_data3, train_data4]
    test(trains)


main()
