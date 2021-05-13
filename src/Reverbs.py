import numpy as np

def Filter_AP(g,d,x,rate):
    y = []
    i = x.size
    step = int(round(d*rate))

    #condiciones iniciales
    for j in range(0,step):
        y.append(-g*x[j])

    for j in range(step,i):
        y.append((-g*x[j]) + x[j-step] + (g*y[j-step]))

    return np.array(y)

def Filter_COMB(g,d,x,rate):
    y = np.zeros(x.size)
    i = x.size
    step = int(round(d * rate))

    # condiciones iniciales
    for j in range(0, step):
        y[j] = 0

    for j in range(step,i):
        y[j] = x[j-step]+(g*y[j-step])

    return y

#g: vector de tamaño 6 con todos los coeficientes
#d: vector de tamaño 6 con todos los coeficientes

def REV_Schroeder(g,d,x,rate):

    C1 = Filter_COMB(g[0],d[0],x,rate)
    C2 = Filter_COMB(g[1],d[1],x,rate)
    C3 = Filter_COMB(g[2],d[2],x,rate)
    C4 = Filter_COMB(g[3],d[3],x,rate)

    Sum = np.add(np.add(np.array(C1), np.array(C2)),np.add(np.array(C3), np.array(C4)))

    AP1 = Filter_AP(g[4], d[4], Sum, rate)
    y = Filter_AP(g[5], d[5], AP1,rate)

    return y
