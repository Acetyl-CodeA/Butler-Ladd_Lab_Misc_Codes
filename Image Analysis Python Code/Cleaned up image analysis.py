import numpy as np
import tkinter as tk
import tkinter.messagebox as mb
import tkinter.filedialog as fd
from PIL import Image
import sys

def tifFolderSelection():
    mainMenu.fovFolderName =  fd.askdirectory()
    tfri.configure(bg='green',text=mainMenu.fovFolderName)
    return

def tifAnalyzeV3():
    try:
        '''
        Collect data from all the important entries. This will fail if any of
        the entries are empty or contain non digit characters.
        '''
        fStart = int(fovStartEntry.get())
        fStop = int(fovStopEntry.get())
        baseline = int(baselineEntry.get())
        yint = int(interceptEntry.get())
        slope = int(slopeEntry.get())
    except:
        mb.showerror(title='An exception has occured',message=\
                     str(sys.exc_info()[0]))
        return
    if mainMenu.fovFolderName == None:
        mb.showerror(title='Error',message='The location of the tiff data has not been chosen, select the tiff data location and try again')
        return
    mainMenu.fovnList = []
    for fovNumber in range(fStart,fStop):
        '''
        fStart and fStop, the fovns listed as the start and stop, does not
        include (won't check the fovn listed as stop)
        '''
        fovnTiff = Image.open(mainMenu.fovFolderName+'\\fov'+str(fovNumber)\
                              +'\\tiff_images\\fov'+str(fovNumber)\
                              +'img_stack.tif')
        averageOfEachFrame = []
        percentOver255InEachFrame = []
        for frameNumber in range(1000):
            '''
            Checks each frame until its out of index. If a tiff has >1000
            frames, this will stop at 1000.
            '''
            try:
                fovnTiff.seek(frameNumber) #go to that frame in the TIFF
                thisFrame = np.array(fovnTiff)
                averageOfEachFrame.append(np.average(thisFrame))
                over255 = thisFrame>255
                anyin = thisFrame>-999
                percentOver255InEachFrame.append((over255.sum()/anyin.sum())*100)
                '''
                The PercentOver255 calculation works as follows:
                It turns fovnTiff into two arrays, over 255, and anyin,
                both of which are boolean arrays.
                The first array is >255, so if the values are above 255, they
                will be a 1, if not, they are a 0. The array is then summed, so
                the sum will be the number of values above 255. The second
                array is all numbers above -999. If they are greater (which
                they should be, as the numbers should be from 0-256).
                Then we divide their sums and multiply by 100 and that should
                be % over 255.
                '''
            except EOFError:
                break
        intensitiesInstance = []
        for i in range(0,len(averageOfEachFrame),5):
            intensitiesInstance.append(max(averageOfEachFrame[i:i+5]))
            #find the max of that slice of 5 averages and that is the intensity
        intensitiesInstanceArray = np.array(intensitiesInstance)
        
        #calculations-
        correctedIntensity = intensitiesInstanceArray - baseline
        dnaConc = (correctedIntensity-yint)/slope
        mainMenu.fovnList.append([fovNumber,averageOfEachFrame,\
                                  intensitiesInstanceArray,correctedIntensity,\
                                  dnaConc,percentOver255InEachFrame])    
    
    mb.showinfo(title='Done',message='Analysis complete')
    for i in range(len(mainMenu.fovnList)):
        print('FOVN:',mainMenu.fovnList[i][0],'\n')
        print('Average of each frame (unadjusted):\n',mainMenu.fovnList[i][1])
        print('Intensities (max of every 5 frames, unadjusted):')
        print(mainMenu.fovnList[i][2])
        print('Adjusted Intensities (subtracted baseline):')
        print(mainMenu.fovnList[i][3])
        print('DNA conc (from every 5 frames):\n',mainMenu.fovnList[i][4])
        print('Percent over 255 in each frame:\n',mainMenu.fovnList[i][5])
    mainMenu.areResults = True
    return

def viewResults():
    if mainMenu.areResults == False:
        mb.showwarning(title='Error',message='No results to show, run analysis \
                       first')
        return
    else:
        mainMenu.resultsWindow = tk.Toplevel()
        mainMenu.resultsWindow.title('Results')
        masterString = ''
        for i in range(len(mainMenu.fovnList)):
            masterString += 'FOVN: '+str(mainMenu.fovnList[i][0])
            masterString += '\nAverage of each frame (unadjusted):\n'+str(mainMenu.fovnList[i][1])
            masterString += '\nIntensities (max of every 5 frames, unadjusted):\n'
            masterString += str(mainMenu.fovnList[i][2])
            masterString += '\nAdjusted Intensities (subtracted baseline):\n'
            masterString += str(mainMenu.fovnList[i][3])
            masterString += '\nDNA conc (from every 5 frames):\n'+str(mainMenu.fovnList[i][4])
            masterString += '\nPercent over 255 in each frame:\n'+str(mainMenu.fovnList[i][5])
        mainMenu.resultsText = tk.Text(mainMenu.resultsWindow)
        mainMenu.resultsText.insert(tk.END,masterString)
        mainMenu.resultsText.grid(column=0,row=1,columnspan=3,rowspan=100)
    return

''' Set up main window'''

mainMenu = tk.Tk()
mainMenu.title('Pixel Intensity Analysis')

#declare important variables
mainMenu.fovFolderName = None
mainMenu.areResults = False

''' '''

''' FOV setup options '''

'''
By FOV frame, I mean frame containing fovn selection, not anything about
individual frames of a TIFF
'''

fovFrame = tk.Frame(mainMenu,relief='solid',borderwidth=1)
fovFrame.grid(row=1,column=0,padx=10)

fovStartLabel = tk.Label(fovFrame,text='FOV start:')
fovStartLabel.grid(row=0,column=0)

defaultFovStart = tk.StringVar()
defaultFovStart.set('5065')
fovStartEntry = tk.Entry(fovFrame,textvariable=defaultFovStart)
fovStartEntry.grid(row=0,column=1)

fovStopLabel = tk.Label(fovFrame,text='FOV stop:')
fovStopLabel.grid(row=1,column=0)

defaultFovStop = tk.StringVar()
defaultFovStop.set('5066')
fovStopEntry = tk.Entry(fovFrame,textvariable=defaultFovStop)
fovStopEntry.grid(row=1,column=1)

''' '''

'''Where to save analysis and from which folder are we grabbing the tiff files'''

fileFrame = tk.Frame(mainMenu,relief='solid',borderwidth=1)
fileFrame.grid(row=1,column=2,padx=10)

#TFRI = tiff folder readiness indicator
tfri = tk.Label(fileFrame,text='No folder for TIFFs selected',bg='red')
tfri.grid(row=0,column=0)

tiffSelectionButton = tk.Button(fileFrame,\
                                text='Select folder containing fov folders',\
                                command=tifFolderSelection)
tiffSelectionButton.grid(row=1,column=0)

''' '''

''' Data Correction Zone ''' 
dcf = tk.Frame(mainMenu,relief='solid',borderwidth=1)
dcf.grid(row=2,column=0,pady=5)

baselineLabel = tk.Label(dcf,text='Baseline:')
baselineLabel.grid(row=0,column=0)

defaultBaseline = tk.StringVar()
defaultBaseline.set('0')
baselineEntry = tk.Entry(dcf,textvariable=defaultBaseline)
baselineEntry.grid(row=0,column=1)

slopeLabel = tk.Label(dcf,text='Slope:')
slopeLabel.grid(row=1,column=0)

defaultSlope = tk.StringVar()
defaultSlope.set('1')
slopeEntry = tk.Entry(dcf,textvariable=defaultSlope)
slopeEntry.grid(row=1,column=1)

interceptLabel = tk.Label(dcf,text='Intercept:')
interceptLabel.grid(row=2,column=0)

defaultIntercept = tk.StringVar()
defaultIntercept.set('0')
interceptEntry = tk.Entry(dcf,textvariable=defaultIntercept)
interceptEntry.grid(row=2,column=1)

''' '''

''' Execute analysis '''

runAnalysisButton = tk.Button(mainMenu,text='Run Analysis',command=tifAnalyzeV3)
runAnalysisButton.grid(row=0,column=1,pady=5)

''' '''
#view results in an at a glance window

viewResultsButton = tk.Button(mainMenu,text='View Results',command=viewResults)
viewResultsButton.grid(row=3, column=1,pady=5)

mainMenu.mainloop()