'''
Interface for raspberry pi to run the gcode for the mill
'''

import serial
import time
import tkinter as tk
import tkinter.messagebox as mb
import tkinter.filedialog as fd
import os
import sys
import keyboard
import numpy as np
import re

def extractCoordinates(fileName):
    '''
    This function creates a list of all sets of coordinates given in the gcode.
    It must be passed the name of the file that it will be searching so it can
    find it.
    '''
    coordRegex = re.compile(r'G1 (X(\d*\.)?\d+ )?(Y(\d*\.)?\d+ )?(Z(\d*\.)?\d+ )?(F\d+)')
    #we create our regular expression for finding the information

    f = open(fileName,'r')
    info = f.read()
    f.close()
    #open, read, and close the file, storing the file information in 'info'

    groups = coordRegex.findall(info)
    #we locate all the groups within 'info', searching using our coordRegex

    outmid = []
    outunedited = []
    '''
    this for/while construct's purpose is to convert the groups outputted by
    the regex search into a list of the general format X### Y### Z### 
    and filling in any implied values
    (in gcode if a coordinate is omitted, it is assumed that it is the same 
    as the last given one, so X21 Y23 Z24, followed by X22.5 Y26, would be 
    implied to also be at Z24)
    '''
    for i in range(len(groups)):
        outmid.append(list(groups[i][::2]))
        outunedited.append(groups[i][::2])
        while '' in outmid[i]:
            tempindex = outmid[i].index('')
            if tempindex == 0:
                outmid[i][0] = outmid[i-1][0]
            elif tempindex == 1:
                outmid[i][1] = outmid[i-1][1]
            elif tempindex == 2:
                outmid[i][2] = outmid[i-1][1]
            else:
                print('error, speed missing')
    
    outarray = np.array(outmid)
    #outcutarray = outarray[:,:3]
    
    outfinal = []
    
    #compiles final list, converting given coordinates to floats and removing
    #the X, Y, or Z
    for j in range(len(outarray)):
        tempout = []
        tempxstr = str(outarray[j,0])
        tempout.append(float(tempxstr[1:]))
        tempystr = str(outarray[j,1])
        tempout.append(float(tempystr[1:]))
        tempzstr = str(outarray[j,2])
        tempout.append(float(tempzstr[1:]))
        outfinal.append(tempout)
    
    outfinalarray = np.array(outfinal)

    return outfinalarray

def bootUpMill():
    '''
    Open up a serial port connection with the mill, and wake up grbl
    '''
    try:
        #open up the serial port at this given port
        mainMenu.s = serial.Serial('/dev/ttyUSB0',115200)
        
        # Wake up grbl
        mainMenu.s.write(b"\r\n\r\n")
        
        time.sleep(2)   # Wait for grbl to initialize 
        mainMenu.s.flushInput()  # Flush startup text in serial input
        
        mainMenu.millOn = True
    except:
        mb.showerror(title='An exception has occured',message=str(sys.exc_info()[0]))
    return

def exitInterface():
    '''
    tries to close everything, because if we hit X to close and later try to
    open an already open serial port afterwards, we'll get an error that may
    be confusing to the operator
    '''
    try:
        mainMenu.s.close()
        mainMenu.file.close()
    except:
        print("couldnt close all ports, this is not necessarily an error")
    mainMenu.destroy()
    return

def loadGCodeFile():
    try:
        #make a file dialog
        mainMenu.fileName = fd.askopenfilename(initialdir = os.getcwd(),title = "Select file",filetypes = (("text files","*.txt"),("all files","*.*")))
        
        #display a preview of the gcode file in the matplot canvas
        displayPlot()
        
        #say that we successfully loaded the file
        mb.showinfo(title='Success',message=('File '+mainMenu.fileName+' successfully loaded'))
        mainMenu.fileLoaded = True
        
    except:
        mb.showerror(title='An exception has occured',message=str(sys.exc_info()[0]))
        mainMenu.fileLoaded = False
    return

def displayPlot(): #this creates a preview of the gcode file in a graph
    try:
        #get the coordinate information from the file
        xyz = extractCoordinates(mainMenu.fileName)
       
        #establish a new figure plot
        import matplotlib
        #matplotlib.use("TkAgg")
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure
        f = Figure(figsize=(5,5), dpi=50)
        a = f.add_subplot(111)
        
        #print(xyz[:,:2])
        #print(xyz[:,0])
        
        #plot the xy data in subplot a of figure f
        a.plot(xyz[:,0],xyz[:,1])
        
        #make a canvas
        canvas = FigureCanvasTkAgg(f,mainMenu)
        
        #place the canvas
        canvas.get_tk_widget().grid(row=2,column=1)
        
        #draw the data onto the canvas
        canvas.draw()
    except:
        mb.showerror(title='An exception has occured',message=str(sys.exc_info()[0]))
    return

def runGCodeFile():
    if mainMenu.millOn:
        if mainMenu.fileLoaded:
            try:
                mb.showinfo(title='Info',message='In order to emergency stop the program, hold down the x key')
                mainMenu.file = open(mainMenu.fileName,'r')
                for line in mainMenu.file:
                    if keyboard.is_pressed('x'):
                        break
                    l = line.strip() # Strip all EOL characters for consistency
                    print('Sending: ')
                    mainMenu.s.write(l,'\n') # Send g-code block to grbl
                    grbl_out = mainMenu.s.readline() # Wait for grbl response with carriage return
                    print( ' : ' + grbl_out.strip())
                mainMenu.file.close()
            except:
                mb.showwarning(title='Failure',message='Failed to open file')
                return
        else:
            mb.showwarning(title='Warning',message='No file loaded')
    else:
        mb.showwarning(title='Warning',message='Mill not on')
    return

def ESO():
    mb.showwarning(title='Unimplemented',message='This feature is unimplemented')
    return

def genCode():
    mb.showwarning(title='Unimplemented',message='This feature is unimplemented')
    return

def moveUp():
    moveGeneral(0,1,0)
    return

def moveDown():
    moveGeneral(0,-1,0)
    return

def moveLeft():
    moveGeneral(-1,0,0)
    return

def moveRight():
    moveGeneral(1,0,0)
    return

def moveGeneral(xinfo,yinfo,zinfo):
    if mainMenu.millOn:
        try:
            speedInfo = feedVar.get()
            stepInfo = stepVar.get()
        except:
            mb.showerror(title='An exception has occured',message=str(sys.exc_info()[0]))
            return
        mainMenu.s.write('G90\n')
        mainMenu.s.readline()
        moveCommand = 'G1 X'+ str(xinfo*stepInfo) + ' Y' + str(yinfo*stepInfo) + ' Z' + str(zinfo*stepInfo) + ' F'+ str(speedInfo) + ' \n'
        mainMenu.s.write(moveCommand)
        mainMenu.s.readline()
    else:
        mb.showwarning(title='Warning',message='Mill not on')
    return

def toggleSpindle():
    if mainMenu.millOn:
        if mainMenu.spindleOn:
            try:
                spindleInfo = spindleVar.get()
            except:
                mb.showerror(title='An exception has occured',message=str(sys.exc_info()[0]))
                return
            mainMenu.s.write('M3 S' + str(spindleInfo) + ' \n')
            mainMenu.s.readline()
        else:
            mainMenu.s.write('M3 S0')
            mainMenu.s.readline()
    else:
        mb.showwarning(title='Warning',message='Mill not on')
    return

mainMenu = tk.Tk()
mainMenu.title('Mill control')

mainMenu.fileLoaded = False
mainMenu.millOn = False
mainMenu.spindleOn = False

''' Load/Execute Frame [lef]'''

lef = tk.Frame(mainMenu,relief='solid',borderwidth=1)
lef.grid(row=1,column=0)

lefTitle = tk.Label(lef,text='Load and execute gcode')
lefTitle.grid(row=0,column=0)

loadButton = tk.Button(lef, text='Load GCode File', command=loadGCodeFile)
loadButton.grid(row=1,column=0)

runButton = tk.Button(lef, text='Run GCode File', command=runGCodeFile)
runButton.grid(row=2,column=0)

'''Mill Power Frame [mpf]'''

mpf = tk.Frame(mainMenu,relief='solid',borderwidth=1)
mpf.grid(row=1,column=2,padx=10)

mpfTitle = tk.Label(mpf,text='Mill Power')
mpfTitle.grid(row=0,column=0)

bootUpButton = tk.Button(mpf,text='Boot up mill',command=bootUpMill)
bootUpButton.grid(row=1,column=0)

'''
ESO = tk.Button(mpf, text='Emergency Shutoff of Mill',command=ESO)
#ESO = emergency shut off
ESO.grid(row=2,column=0)
#temporarily de implemented for the purposes of the picture for the build
'''

ESOText = tk.Label(mpf, text='Press x during G-code streaming to shut off the mill')
ESOText.grid(row=2,column=0)

''' '''

''' Free objects (not in a frame) '''
gcodeGenButton = tk.Button(mainMenu,text='Generate Gcode',command=genCode)
gcodeGenButton.grid(row=0,column=0,pady=10)

exitButton = tk.Button(mainMenu,text='Close', command=exitInterface)
exitButton.grid(row=0,column=2,padx=10,pady=10)
''' '''

''' Manual Adjustment Frame [maf]'''

maf = tk.Frame(mainMenu, relief='solid',borderwidth=1)
maf.grid(row=2,column=0,padx=20,pady=10)

mafTitle = tk.Label(maf, text='Manual Bit Control')
mafTitle.grid(row=0,column=0)

''' arrowsFrame subframe of maf '''
arrowsFrame = tk.Frame(maf,relief='solid',borderwidth=1)
arrowsFrame.grid(row=1,column=0,pady=10)

upButton = tk.Button(arrowsFrame,text='↑',command=moveUp)
upButton.grid(row=0,column=1)

downButton = tk.Button(arrowsFrame,text='↓',command=moveDown)
downButton.grid(row=2,column=1)

leftButton = tk.Button(arrowsFrame,text='←',command=moveLeft)
leftButton.grid(row=1,column=0)

rightButton = tk.Button(arrowsFrame,text='→',command=moveRight)
rightButton.grid(row=1,column=2)
''' '''

'''Spindle'''
spinf = tk.Frame(maf)
spinf.grid(row=2,column=0)

spindleLabel = tk.Label(spinf,text='Spindle:')
spindleLabel.grid(row=0,column=0)

spindleVar = tk.StringVar()
spindleVar.set('0')
spindleEntry = tk.Entry(spinf,textvariable=spindleVar)
spindleEntry.grid(row=0,column=1)

'''Step'''
stepF = tk.Frame(maf)
stepF.grid(row=3,column=0)

stepLabel = tk.Label(stepF,text='     Step:')
stepLabel.grid(row=0,column=0)

stepVar = tk.StringVar()
stepVar.set('1')
stepEntry = tk.Entry(stepF,textvariable=stepVar)
stepEntry.grid(row=0,column=1)

'''Feed'''
feedF = tk.Frame(maf)
feedF.grid(row=4,column=0)

feedLabel = tk.Label(feedF,text='    Feed:')
feedLabel.grid(row=0,column=0)

feedVar = tk.StringVar()
feedVar.set('200')
feedEntry = tk.Entry(feedF,textvariable=feedVar)
feedEntry.grid(row=0,column=1)
''' '''

toggleSpindleButton = tk.Button(maf, text='Toggle spindle on/off',command=toggleSpindle)
toggleSpindleButton.grid(row=6,column=0)
''' '''

mainMenu.mainloop()