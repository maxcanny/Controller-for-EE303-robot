import time
import numpy as np
import requests

pins = np.memmap("bots/001/pins.dat", dtype=np.uint32, mode="r+", shape=(41,))
ins=135
outs=300 
inl=75 
outl=300
inxl=30 
outxl=300
mline=225
forward=300
backward=200
low=25
mid=100
high=150
stro=300
stri=0
combinthres=500
crossthres=700
outthres=600
inthres=150
count=0
pos=0
poscount=0
oldpos=0
setup=1
farright=0
right=0
middle=0
left=0
farleft=0
combinR=0
combinL=0
state=0
orient="anti"
one=""
execute="no"
nin=1
tabout=2

#Reading + Writing functions
def analogRead(pin):
    return pins[pin]

def analogWrite(pin, value):
    if value < 0 or value > 1023:
        raise ValueError
    pins[pin] = value
    pins.flush()

def digitalRead(pin):
    return pins[pin]

def digitalWrite(pin, value):
    if value not in (0, 1):
        raise ValueError
    pins[pin] = value
    pins.flush()

def GetSensor():
    global farright,right,middle,left,farleft,combinL,combinR,distance
    farright = analogRead(8)
    right = analogRead(9)
    middle = analogRead(11)
    left = analogRead(13)
    farleft = analogRead(14)
    combinR = right + farright
    combinL = farleft + left
    distance = analogRead(1)
    
def NextPosition():
    global count,oldpos
    oldpos=pos
    Position()
    Stop(2)
    count=0
    CrossLine()
    
def Position():
    global pos, poscount,count
    payload = {'position': pos}
    r = requests.post('http://54.78.246.30:8081/api/arrived/c5de420d', data=payload)
    print(r.status_code)
    print(r.text)
    pos=r.text
    #print("This is pos: "+str(pos))
    poscount=poscount+1


#Routing Functions
def CrossLine():
    global count, setup, orient, execute
    count=count+1
    execute="no"
    if setup==1:
        Position()
        Stop(2)
        Continue(0.5)
        setup=0
    
    #print(count)
    #print(orient)
    if pos=="1":
        One()
        return
    if pos=="2":
        Two()
        return
    if pos=="3":
        Three()
        return
    if pos=="4":
        Four()
        return
    if pos=="0":
        Zero()
        return
    if pos=="5":
        Five()
        return
    if pos=="undefined":
        exit(0)
 
#oreint updates after each change in direction
#updates at out of turn 1
def One():
    global orient, one, execute
    #print("in one")
    if poscount==1:
        if count==2:
            Left(nin)
            one="fromright"
        if count==3 and pos=="1":
            NextPosition()
    elif poscount>=2:
        #2-1
        if oldpos=="2" and orient=="anti": 
            if count==1:
                ChangeOrientation("clock")#continues in clock for old=2
        if oldpos=="2" and orient=="clock":
            if count==1 and execute=="no":
                Continue(0.5)
            if count==2:
                Right(nin)
                one="fromright"
            if count==3:
                NextPosition()
                
        #3-1        
        if oldpos=="3" and orient=="anti": 
            if count==1 and execute=="no":
                Continue(0.5)
            if count==2:
                Left(nin)
                one="fromleft"
            if count==3:
                NextPosition()
        if oldpos=="3" and orient=="clock":
            if count==1:
                ChangeOrientation("anti")#continues in anti 
                
        #4-1        
        if oldpos=="4" and orient=="clock": 
            if count==1 and execute=="no":
                Continue(0.5)
            if count==2:
                Right(nin)
                one="fromleft"
            if count==3:
                NextPosition()
        if oldpos=="4" and orient=="anti":
            if count==1:
                ChangeOrientation("clock") #continues in clockwise 
                
        #0-1        
        if oldpos=="0" and orient == "anti":
            if count==1 and execute=="no":
                Continue(0.5)
            if count==2:
                Left(nin)
                one="fromright"
            if count==3:
                NextPosition()
        if oldpos=="0" and orient == "clock":
            if count==1:
                ChangeOrientation("anti") # continues in anti
                
#if anti coming in on left side, if clock coming on right
    

def Two():
    #print("in 2")
    global orient,one,execute
    if poscount==1:
        if count==2:
            FixL()
        if count==3 and pos=="2":
            NextPosition()        
        if count==3 and pos=="3":
            FixL() 
    elif poscount>=2:
        #1-2
        if oldpos=="1" and orient=="anti" and one=="fromleft": #come from left
            if count==1:
                ChangeDirection()
            if count==2 and execute=="no":
                Left(nin)
            if count==3 and pos=="2":
                NextPosition()
            if count==3 and pos=="3":
                FixL()
        if oldpos=="1" and orient=="clock" and one=="fromleft": #come from right
            if count==1:
                ChangeDirection()
            if count==2:
                Left(nin)
                orient="anti"
                execute="yes"
        if oldpos=="1" and orient=="anti" and one=="fromright":
            if count==1:
                Continue(0.5)
            if count==2 and execute=="no": #variable to stop a double call at this point
                Left(nin)
            if count==3 and pos=="2":
                NextPosition()
            if count==3 and pos=="3":
                FixL()
        if oldpos=="1" and orient=="clock" and one=="fromright":
            if count==1:
                Continue(0.5)
            if count==2:
                Left(nin)
                orient="anti"
                execute="yes"
                
        #3-2        
        if oldpos=="3" and orient=="clock": 
            if count==1 and execute=="no":
                Continue(0.5)
            if count==2:
                NextPosition()
        if oldpos=="3" and orient=="anti":
            if count==1:
                ChangeOrientation("clock")
                
        #4-2        
        if oldpos=="4" and orient=="clock": 
            Three()
            if count==4:
                NextPosition()
        if oldpos=="4" and orient=="anti":
            if count==1:
                ChangeOrientation("clock")
                
        #0-2
        if oldpos=="0" and orient=="anti":
            if count==1 and execute=="no":
                Continue(0.5)
            if count==2:
                FixL()
            if count==3 and pos=="2":
                NextPosition()
            if count==3 and pos=="3":
                FixL()
        if oldpos=="0" and orient=="clock":
            if count==1:
                ChangeOrientation("anti")
        
def Three():
    global orient,execute
    #print("in 3")    
    global oldpos,count
    if poscount==1:
        Two()
        if count==4:
            NextPosition()
    elif poscount>=2:
        #2-3
        if oldpos=="2" and orient=="anti": 
            if count==1 and execute=="no":
                Continue(0.5)
            if count==2:
                NextPosition()
        if oldpos=="2" and orient=="clock":
            if count==1:
                ChangeOrientation("anti")
                
        #1-3        
        if oldpos=="1" and orient=="anti" and one=="fromleft": 
            if count==1:
                ChangeDirection()
            if count==2:
                Right(nin)
                orient="clock"
                execute="yes"
        if oldpos=="1" and orient=="clock" and one=="fromleft": 
            if count==1:
                ChangeDirection()
            if count==2 and execute=="no":
                Right(nin)
            if count==3:
                NextPosition()
        if oldpos=="1" and orient=="anti" and one=="fromright": 
            if count==1:
                Continue(0.5)
            if count==2:
                Right(nin)
                orient="clock"
                execute="yes"
        if oldpos=="1" and orient=="clock" and one=="fromright": 
            if count==1:
                Continue(0.5)
            if count==2 and execute=="no":
                Right(nin)
            if count==3:
                NextPosition()
                
        #4-3        
        if oldpos=="4" and orient=="clock": 
            if count==1 and execute=="no":
                Continue(0.5)
            if count==2:
                FixL()
            if count==3 and pos=="3":
                NextPosition()
            if count==3 and pos=="2":
                Continue(0.5)
        if oldpos=="4" and orient=="anti":
            if count==1:
                ChangeOrientation("clock")
                
        #0-3
        if oldpos=="0" and orient=="anti":
            Two()
            if count==4:
                NextPosition()
        if oldpos=="0" and orient=="clock":
            if count==1:
                ChangeOrientation("anti")
        
                
def Four():
    global orient,execute
    if poscount==1:
        if count==1:
            ChangeOrientation("clock")
        if count==2:
            NextPosition()
    elif poscount>=2:
        #1-4
        if oldpos=="1" and orient=="anti" and one=="fromleft": 
            if count==1:
                ChangeDirection()
            if count==2 and execute=="no":
                Left(nin)
            if count==3:
                NextPosition()
        if oldpos=="1" and orient=="clock" and one=="fromleft": 
            if count==1:
                ChangeDirection()
            if count==2:
                Left(nin)
                orient="anti"
                execute="yes"
        if oldpos=="1" and orient=="anti" and one=="fromright": 
            if count==1:
                Continue(0.5)
            if count==2 and execute=="no":
                Left(nin)
            if count==3:
                NextPosition()
        if oldpos=="1" and orient=="clock" and one=="fromright": 
            if count==1:
                Continue(0.5)
            if count==2:
                Left(nin)
                orient="anti"
                execute="yes"
                
        #2-4
        if oldpos=="2" and orient=="clock": 
            if count==1 and execute=="no":
                Continue(0.5)
                #print("count 1")
            if count==2:
                FixR()
                #print("count 2")
            if count==3 and pos=="4":
                FixR()
                #print("count 3")
            if count==3 and pos=="0":
                NextPosition()
            if count==4:
                #print("count 4")
                NextPosition()
        if oldpos=="2" and orient=="anti":
            if count==1:
                #print("count 1")
                ChangeOrientation("clock")
                
        #3-4
        if oldpos=="3" and orient=="anti":
            if count==1 and execute=="no":
                Continue(0.5)
            if count==2:
                FixR()
            if count==3 and pos=="4":
                NextPosition()
            if count==3 and pos=="0":
                FixR()
        if oldpos=="3" and orient=="clock":
            if count==1:
                ChangeOrientation("anti")
                
        #0-4
        if oldpos=="0" and orient=="clock":
            if count==1 and execute=="no":
                Continue(0.5)
            if count==2:
                NextPosition()
        if oldpos=="0" and orient=="anti":
            if count==1:
                ChangeOrientation("clock")
                
                
def Zero():
    global orient,execute
    if poscount>=2:
        #1-0
        if oldpos=="1" and orient=="anti" and one=="fromleft": #come from left
            if count==1:
                Continue(0.5)
            if count==2:
                Right(nin)
                orient="clock"
                execute="yes"
        if oldpos=="1" and orient=="clock" and one=="fromleft": #come from right
            if count==1:
                Continue(0.5)
            if count==2 and execute=="no":
                Right(nin)
            if count==3:
                NextPosition()
        if oldpos=="1" and orient=="anti" and one=="fromright": #come from left
            if count==1:
                ChangeDirection()
            if count==2:
                Right(nin)
                orient="clock"
                execute="yes"
        if oldpos=="1" and orient=="clock" and one=="fromright": #come from right
            if count==1:
                ChangeDirection()
            if count==2 and execute=="no":
                Right(nin)
            if count==3:
                NextPosition()
                
        #2-0
        if oldpos=="2":
            Four()
            
        #3-0
        if oldpos=="3":
            Four()
            if count==4:
                NextPosition()
                
        #4-0
        if oldpos=="4" and orient=="clock":
            if count==1:
                ChangeOrientation("anti")
        if oldpos=="4" and orient=="anti":
            if count==1 and execute=="no":
                Continue(0.5)
            if count==2:
                NextPosition()
        
def Five():
    print("in five")
    global orient, execute
    if poscount==1:
        if count==1 and execute=="no":
            Continue(0.5)
        if count==2:
            Left(nin)
        if count==3:
            Continue(0.5)
        if count==4:
            GoTo5()
    if poscount>=2:
        #print("in five, oldpos = "+str(oldpos))
        #1-5
        if oldpos=="1" and one=="fromleft":
            if count==1:
                ChangeDirection()
            if count==2:
                GoTo5()
        if oldpos=="1" and one=="fromright":
            if count==1:
                Continue(0.5)
            if count==2:
                GoTo5()
        
        #2-5
        if oldpos=="2" and orient=="clock":
            if count==1 and execute=="no":
                FixR()
            if count==2:
                Right(nin)
            if count==3:
                Continue(0.5)
            if count==4:
                GoTo5()
        if oldpos=="2" and orient=="anti":
            if count==1:
                ChangeOrientation("clock")
         
        #3-5
        if oldpos=="3" and orient=="clock":
            if count==1 and execute=="no":
                Continue(0.5)
            if count==2:
                FixR()
            if count==3:
                Right(nin)
            if count==4:
                Continue(0.5)
            if count==5:
                GoTo5()
        if oldpos=="3" and orient=="anti":
            ChangeOrientation("clock")
         
        #0-5 
        if oldpos=="0" and orient=="anti":
            print("execute is equal to"+str(execute))
            if count==1 and execute=="no":
                Continue(0.5)
            if count==2:
                Left(nin)
            if count==3:
                Continue(0.5)
            if count==4:
                GoTo5()
        if oldpos=="0" and orient=="clock":
            ChangeOrientation("anti")
            
        #4-5 
        if oldpos=="4" and orient=="anti":
            if count==1:
                Continue(0.5)
            if count==2:
                Continue(0.5)
            if count==3:
                Left(nin)
            if count==4:
                Continue(0.5)
            if count==5:
                GoTo5()
        if oldpos=="4" and orient=="clock":
            ChangeOrientation("anti")
            
def GoTo5():
    Stop(1)
    Move()
    time.sleep(0.5)
    while distance>60:
        GetSensor()
        print(distance)
        Forward()
    Stop(2)
    exit()
            
def ChangeOrientation(s):
    global orient, execute
    Left(tabout)
    orient=s
    Continue(0.5)
    execute="yes"
    print("in change orient, count = "+str(count))
    
def ChangeDirection():
    Left(tabout)
    Continue(0.5)
                
#Movement functions

def Forward():
    digitalWrite(37, 1)
    analogWrite(38, forward)
    digitalWrite(39, 1)
    analogWrite(40, forward)
    
def Backward():
    digitalWrite(37, 0)
    analogWrite(38, backward)
    digitalWrite(39, 0)
    analogWrite(40, backward)
    
#def FixL():
#    while True:
#        GetSensor()
#        #print("combinR= "+str(combinR))
#        #print("combinL= "+str(combinL))
#        if (combinR-10<combinL<combinR+10):
#            print("returned")
#            return
#        else:
#            analogWrite(38, 300)
#            analogWrite(40, 50)

#def FixR():
    #while True:
        #GetSensor()
        #print("combinR= "+str(combinR))
        #print("combinL= "+str(combinL))
        #if (combinL-10<combinR<combinL+10):
        #    print("returned")
        #    return
        #else:
        #    analogWrite(38, 300)
        #    analogWrite(40, 50)        

    
def FixL():
    analogWrite(38, 430)
    analogWrite(40, 50)
    time.sleep(0.5)
    #print("In Left Fix")
    #print("values from far left to far right")
    #print(str(farleft) +":"+ str(left) +":"+ str(middle) +":"+ str(right) +":"+ str(farright))
    #print(combin)
    
def FixR():
    analogWrite(38, 50)
    analogWrite(40, 300)
    time.sleep(0.5)
    #print("In Right Fix")
    #print("values from far left to far right")
    #print(str(farleft) +":"+ str(left) +":"+ str(middle) +":"+ str(right) +":"+ str(farright))
    #print(combin)
    
def Stop(s):
        #print("In Stop")
        analogWrite(38, 0)
        analogWrite(40, 0)
        #print(str(farleft) +":"+ str(left) +":"+ str(middle) +":"+ str(right) +":"+ str(farright))
        #print(combin)
        time.sleep(s)
        return
        
def Continue(s):
    Forward()
    time.sleep(s)
    print("in continue, count = "+str(count))
   
def Continue1(s):
    while True:
        print("In Continue, right ="+str(right))
        print("In Continue, left ="+str(left))
        GetSensor()
        if right<10 or left<10:
            return
        else:
            Forward()
            
def smallL():
    digitalWrite(37, 1)
    analogWrite(38, outs)
    digitalWrite(39, 1)
    analogWrite(40, ins)

def smallR():
    digitalWrite(37, 1)
    analogWrite(38, ins)
    digitalWrite(39, 1)
    analogWrite(40, outs)   

def largeL():
    digitalWrite(37, 1)
    analogWrite(38, outl)
    digitalWrite(39, 1)
    analogWrite(40, inl)

def largeR():
    digitalWrite(37, 1)
    analogWrite(38, inl)
    digitalWrite(39, 1)
    analogWrite(40, outl)

def XLargeL():
    digitalWrite(37, 1)
    analogWrite(38, outxl)
    digitalWrite(39, 0)
    analogWrite(40, inxl)

def XLargeR():
    digitalWrite(37, 0)
    analogWrite(38, inxl)
    digitalWrite(39, 1)
    analogWrite(40, outxl)
    
def Left(s):
    print("In left")
    Forward()
    time.sleep(1)
    Stop(1)
    digitalWrite(37, 1)
    analogWrite(38, 400)
    digitalWrite(39, 0)
    analogWrite(40, 400)
    time.sleep(s)
    #print(str(farleft) +":"+ str(left) +":"+ str(middle) +":"+ str(right) +":"+ str(farright))
    return

def Right(s):
    print("In right")
    Forward()
    time.sleep(1)
    Stop(1)
    digitalWrite(37, 0)
    analogWrite(38, 400)
    digitalWrite(39, 1)
    analogWrite(40, 400)
    time.sleep(s)
    return


def Left1(s):
    Continue(1)
    i=0
    while True:
        GetSensor()
        time.sleep(50/1000)
        print(combinR)
        digitalWrite(37, 1)
        analogWrite(38, 400)
        digitalWrite(39, 0)
        analogWrite(40, 400)
        if combinR>253:
            print("in combinR")
            i=i+1
            if i==s:
                return
            
def Right1(s):
    i=0
    while True:
        GetSensor()
        print(right)
        digitalWrite(37, 0)
        analogWrite(38, 400)
        digitalWrite(39, 1)
        analogWrite(40, 400)
        if 235<left<255:
            #print(right)
            time.sleep(50/100)
            print("in count")
            i=i+1
            if i==s:
                return
            

def FollowLine():
        GetSensor()
        if low<right<=mid: 
            smallR()
        if mid<right<=high or low<farright<=mid:
            largeR()
        if right>high or mid<farright:
            XLargeR()
        if low<left<=mid:
            smallL()
        if mid<left<=high or low<farleft<=mid:
            largeL()
        if left>high or mid<farleft:
            XLargeL()
    
def Move():
    if middle>mline:
        Forward()
    else: 
        FollowLine()
        
while True:
    GetSensor()
    combin = farright+right+middle+left+farleft
    if combin > crossthres:
        CrossLine()
    else:
        Move()