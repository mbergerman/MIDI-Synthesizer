import numpy as np

# Para que salga el efecto hay que crear la clase con los parametros deseados y llamar a output con la senial de entrada
# Nose si se interfasea bien con lo demas. Sino veo de hacerlo estilo funcion como el reverb

class Vibrato:
    def __init__(self,maxPitchShift,fs,fLFO = 2,buffer_length= 1024):
        #Parametros
        # maxPitchShift = Maxima variacion en frecuencia de la salida respecto a la frec de entrada (cociente directo)
        #fs = self explanatory
        #fLFO varia delay time, no suele ser mas de 20Hz
        self.bufferLength = buffer_length
        self.inBuffer = np.array([])
        self.outBuffer = np.array([])
        self.prevOutput = np.zeros(buffer_length)
        self.fs = fs
        self.fLFO = fLFO
        self.W = (maxPitchShift-1)/(2*np.pi*self.fLFO)     # Variacion maxima el delay (En segundos)
        self.avgDelay = self.W*(1.01)   #SACAR MAGIC NUMBER

    def set_delay(self,t):
        self.currDelay = (self.avgDelay + self.W*np.sin(2*np.pi*self.fLFO*t/self.fs))*self.fs     # Cuenta para M{n} [en muestras]
                         #Delay Promedio Muestras   Delay acorde a LFO


    def output(self,inputBuffer):
        self.inBuffer = np.concatenate(self.prevOutput,inputBuffer)
        #LEN = self.inBuffer.size
        self.outBuffer = np.zeros(self.bufferLength)      #Inicializo el array de salida en 0
        # PAD = round((self.W + self.avgDelay)*self.fs)
        # for w in range(0,PAD-1):
        #     self.inBuffer = np.insert(self.inBuffer,0,0)

        for n in range(self.bufferLength, self.inBuffer.size):
            self.set_delay(n)
            i = int(np.floor(n-self.currDelay))         #Calculo de valores enteros de indice de muestra a tomar
            j = int(np.ceil(n-self.currDelay))
            interSample = ((j-(n-self.currDelay))*self.inBuffer[i] )+ (((n-self.currDelay) - i)*self.inBuffer[j]) #Interpolador Libro

            self.outBuffer[n-(self.bufferLength)] = interSample
        self.prevOutput = self.outBuffer
        return self.outBuffer

class Flanger:

    def __init__(self,flanger_depth,fs,fb_ammount,delay,sweep_width,fLFO=5):
        #Parametros
        # flanger depth = g (que tanto se mezcla la senial orig con delay) marca la profundidad del notch
        # delay = delay minimo. Varia el punto maximo del primer notch de la resp frec
        # sweep_width = amplitud del lfo(varia ubicacion del notch)
        # fLFO = tasa de variacion de ubicacion de notch (entr 0.1 y 10 Hz)
        # fb_ammount =agrega color, tiene que ser menor a 1. Sino la cosa no es estable
        self.g = flanger_depth
        self.fs = fs
        self.gfb = fb_ammount
        self.delay_SAMPLE = delay * self.fs
        self.sweepWidth_SAMPLE = sweep_width*self.fs
        self.fLFO = fLFO
        self.inBuffer = np.array([])
        self.outBuffer = np.array([])
        self.currDelay = 0


    def set_delay(self,t):
        self.currDelay = self.delay_SAMPLE + (self.sweepWidth_SAMPLE/2)*(1+np.sin(2*np.pi*self.fLFO*(t)/self.fs))

    def output(self,input_buffer):
        self.inBuffer = input_buffer
        LEN = self.inBuffer.size

        PAD = int(self.delay_SAMPLE + self.sweepWidth_SAMPLE)  #Me fijo cuanto tengo que paddear el inBuffer
        for l in (range(0,PAD)):
            self.inBuffer = np.insert(self.inBuffer,0,0)
        self.outBufferINTER = np.zeros(LEN + PAD)  # creo arreglo de salida vacio (ahorra tiempo) tambien tiene que estar paddeado
        self.outBuffer = np.zeros(LEN)
        for n in range(PAD-1, self.inBuffer.size):
            self.set_delay(n)
            i = int(np.floor(n - self.currDelay))  #Piso y techo de delay actual
            j = int(np.ceil(n - self.currDelay))
            #INTERPOLO PARA ENCONTRAR LA MUESTRA CORRESPONDIENTE
            interSample_IN=((j -(n-self.currDelay)) * self.inBuffer[i])+ (((n- self.currDelay)- i)* self.inBuffer[j])
            interSample_OUT = ((j- (n-self.currDelay))*self.outBufferINTER[i])+ (((n-self.currDelay)- i) * self.outBufferINTER[j])

            outSample = self.gfb*interSample_OUT + self.inBuffer[n] + (self.g - self.gfb) * interSample_IN #Ecuacion caracteristica del Flanger
            self.outBuffer[n - PAD] = outSample
            self.outBufferINTER[n] = outSample
        return self.outBuffer

class MultiChorus:
    #esencialmente muchos flangers juntos sin FB y hay que ponerle un delay mayor

    def __init__(self,chorus_number,fs,depth,delay,sweep_width,fLFO,delay_inter_chorus):
        #Parametros idem flanger
        # delay es mayor por que quiero que haya una diferencia audible
        # fLFO suele ser mas chica
        self.g = depth
        self.fs = fs
        self.delay_SAMPLE = delay * self.fs
        self.sweepWidth_SAMPLE = sweep_width * self.fs
        self.fLFO = fLFO
        self.inBuffer = np.array([])
        self.outBuffer = np.array([])
        self.currDelay = 0
        self.chorus_number = chorus_number
        self.delayInter_SAMPLES = delay_inter_chorus * self.fs

    def set_delay(self,t):
        self.currDelay = self.delay_SAMPLE + (self.sweepWidth_SAMPLE / 2) * (
                          1 + np.sin(2 * np.pi * self.fLFO * (t) / self.fs))

    def output(self,input_buffer):
        self.inBuffer = input_buffer
        LEN = self.inBuffer.size

        PAD = int(self.delay_SAMPLE + self.sweepWidth_SAMPLE)  # Me fijo cuanto tengo que paddear el inBuffer
        for l in (range(0, PAD)):
            self.inBuffer = np.insert(self.inBuffer, 0, 0)

        self.outBuffer = np.zeros(LEN)
        self.Chorus = np.zeros(shape=(self.chorus_number,LEN))
        for n in range(PAD - 1, self.inBuffer.size):    #Busco la respuesta para cada uno de los coros
            for m in range(0,self.chorus_number):
                self.set_delay(n - m*self.delayInter_SAMPLES)
                i = int(np.floor(n - self.currDelay))  # Piso y techo de delay actual
                j = int(np.ceil(n - self.currDelay))
                # INTERPOLO PARA ENCONTRAR LA MUESTRA CORRESPONDIENTE
                interSample_IN = ((j - (n - self.currDelay)) * self.inBuffer[i]) + (
                            ((n - self.currDelay) - i) * self.inBuffer[j])
                self.Chorus[m][n-PAD] = interSample_IN
        for w in range(0,self.chorus_number):
            self.outBuffer = self.outBuffer + (1/self.chorus_number)*self.Chorus[w]  #Multiplico por constante para normalizar
        return self.outBuffer
