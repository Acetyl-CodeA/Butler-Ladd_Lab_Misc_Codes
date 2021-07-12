# -*- coding: utf-8 -*-
"""
lets make a gui for making gcode!
"""

import tkinter as tk
import tkinter.messagebox as mb
import tkinter.filedialog as fd
import numpy as np
import re
import os
import sys

MM = tk.Tk() #Main Menu

''' Settings that shouldn't be changed lightly '''
MM.originSet = 'G92\n'

MM.units_setting = 'G21\n' #millimeters

MM.positioning_type = 'G90\n' #absolute

MM.clearance_level =  'G1 Z2.0 F800\n' 
#g1 is move, xyz is coords, f800 is the speed

#MM.drill_speed = 'M3 S10000\n' #10,000 rpm
''' '''

def generategcode():
    MM.ms = MM.originSet #MM.ms means master string
    MM.ms += MM.units_setting
    MM.ms += MM.positioning_type
    MM.ms += MM.clearance_level
    MM.ms += drillSpeedEntry.get()
    MM.ms += 'G1 Z0\n'
    
    Pattern = pattern.get()
    
    numpass = int(numPassEntry.get())
    depth = float(depthEntry.get())
    speed = float(speedEntry.get())
    channelBodyLength = float(channelBodyLengthEntry.get())
    channelWidth = float(channelWidthEntry.get())
    channelHeadLength = float(channelHeadLengthEntry.get())
    dpp = depth/numpass
    
    if Pattern == 'Straight Channel':
        for i in range(numpass):
            MM.ms += 'G1 Z' + str(dpp*i*-1) + ' F' + str(speed) + '\n'
            MM.ms += 'G1 X' + str(channelBodyLength) + ' F' + str(speed) + '\n'
            MM.ms += 'G1 X0 F' + str(speed) + '\n'
            MM.ms += 'G1 Z2.0 F800\n'
    elif Pattern == 'Expansion Contraction Channel':
        for j in range(numpass):
            MM.ms += 'G1 Z' + str(dpp*j*-1) + ' F' + str(speed) + '\n'
            MM.ms += 'G1 Y' + str(channelWidth) + ' F' + str(speed) + '\n'
            MM.ms += 'G1 X' + str(channelBodyLength) + ' F' + str(speed) + '\n'
            MM.ms += 'G1 Y' + str(channelWidth/2) + ' F' + str(speed) + '\n'
            MM.ms += 'G1 X' + str(channelBodyLength+channelHeadLength) + ' F' + str(speed) + '\n'
            MM.ms += 'G1 X' + str(channelBodyLength) + ' F' + str(speed) + '\n'
            MM.ms += 'G1 Y' + str(0) + ' F' + str(speed) + '\n'
            MM.ms += 'G1 X' + str(0) + ' F' + str(speed) + '\n'
        print('expandcontract')
    else:
        print('You must select a channel type to continue.')
        return
    #displayPlot()
    f = fd.asksaveasfile(mode='w',defaultextension='.txt')
    f.write(MM.ms)
    f.close()
    return

def displayPlot(): #this creates a preview of the gcode file in a graph
    try:
        #get the coordinate information from the file
        xyz = extractCoordinates()
       
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
        canvas = FigureCanvasTkAgg(f,MM)
        
        #place the canvas
        canvas.get_tk_widget().grid(row=1,column=1)
        
        #draw the data onto the canvas
        canvas.draw()
    except:
        mb.showerror(title='An exception has occured',message=str(sys.exc_info()[0]))
    return

def extractCoordinates():
    '''
    This function creates a list of all sets of coordinates given in the gcode.
    It must be passed the name of the file that it will be searching so it can
    find it.
    '''
    coordRegex = re.compile(r'G1 (X(\d*\.)?\d+ )?(Y(\d*\.)?\d+ )?(Z(\d*\.)?\d+ )?(F\d+)')
    #we create our regular expression for finding the information

    info = MM.ms
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

MM.title('GCode Generation')


pattern = tk.StringVar()

patternList = ['Select Pattern','Straight Channel','Expansion Contraction Channel']
pattern.set(patternList[0])

dropdown = tk.OptionMenu(MM,pattern,*patternList)
dropdown.grid(row=0,column=0)

''' Inputs Frame '''
inpf = tk.Frame(MM,relief='solid',borderwidth=1) #input frame
inpf.grid(row=1,column=0)

numPassLabel = tk.Label(inpf,text='Number of passes: ')
numPassLabel.grid(row=0,column=0)
numPassEntry = tk.Entry(inpf)
numPassEntry.grid(row=0,column=1)

depthLabel = tk.Label(inpf,text='Depth (in mm): ')
depthLabel.grid(row=1,column=0)
depthEntry = tk.Entry(inpf)
depthEntry.grid(row=1,column=1)

speedLabel = tk.Label(inpf,text='Drill feed: ')
speedLabel.grid(row=2,column=0)
speedEntry = tk.Entry(inpf)
speedEntry.grid(row=2,column=1)

channelBodyLengthLabel = tk.Label(inpf,text='Length of body of channel: ')
channelBodyLengthLabel.grid(row=3,column=0)
channelBodyLengthEntry = tk.Entry(inpf)
channelBodyLengthEntry.grid(row=3,column=1)
#use body length for length of straight channel, do not use head length

channelWidthLabel = tk.Label(inpf,text='Width of channel:[not used for straight channel] ')
channelWidthLabel.grid(row=4,column=0)
channelWidthEntry = tk.Entry(inpf)
channelWidthEntry.grid(row=4,column=1)

channelHeadLengthLabel = tk.Label(inpf,text='Length of head of channel [not used for straight channel]: ')
channelHeadLengthLabel.grid(row=5,column=0)
channelHeadLengthEntry = tk.Entry(inpf)
channelHeadLengthEntry.grid(row=5,column=1)

drillSpeedLabel = tk.Label(inpf, text='Turn speed of drill (in rpm): ')
drillSpeedLabel.grid(row=6,column=0)
drillSpeedEntry = tk.Entry(inpf)
drillSpeedEntry.grid(row=6,column=1)
''' '''

generateButton = tk.Button(text='Generate GCode',command=generategcode)
generateButton.grid(row=0,column=1)

MM.mainloop()