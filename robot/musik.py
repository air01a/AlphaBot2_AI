from threading import Thread
import RPi.GPIO as GPIO
import time

GPIOBUZZER = 4

class Musik:

    def __init__(self):
        #Thread.__init__(self)
        self.up=True
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM) ## Use board pin numbering
        GPIO.setup(GPIOBUZZER, GPIO.OUT)


    def buzz(self,pitch, duration):
        if(pitch==0):
                time.sleep(duration)
                return
        period = 1.0 / pitch     #in physics, the period (sec/cyc) is the inverse of the frequency (cyc/sec)
        delay = period / 2     #calcuate the time for half of the wave  
        cycles = int(duration * pitch)   #the number of waves to produce is the duration times the frequency

        for i in range(cycles):    
                GPIO.output(GPIOBUZZER, True)   
                time.sleep(delay)    
                GPIO.output(GPIOBUZZER, False)    
                time.sleep(delay)    

    def play(self):
        timesleep = 0
        pitches=[392,294,0,392,294,0,392,0,392,392,392,0,1047,262]
        duration=[0.2,0.2,0.2,0.2,0.2,0.2,0.1,0.1,0.1,0.1,0.1,0.1,0.8,0.4]
        tempo=0
        i=0
        for p in pitches:
                self.buzz(p, duration[i])
                time.sleep(duration[i] *0.5)
                timesleep+=duration[i]*1500

                i+=1

                if timesleep>1000:
                     self.up=not self.up
                     timesleep=0
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)


#thread1=T_Disp()
#thread1.start()
#t = T_Disp()
#t.run()
