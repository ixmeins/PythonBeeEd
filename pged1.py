from sys import argv
from tkinter import E
import pygame
import random
import time

# Written by Ingmar Meins whilst sick at home with Covid19 in October 2022.

# This is a PCG and screen editor for the Microbee series of computers.
# The character_4k.rom file is copyright Microbee Systems - it can be freely obtained from
# various sources on the web and by copying the ROM on your own Microbee.

# It is unlikely many Americans will use this software so lets not waste any time with
# the sort of disclaimers that most of the intelligent world find obvious. Eg If you burn your toast and the
# fire brigade turns up and charges you $2000 for a callout because you were too busy editing PCG 
# characters then stiff shit.

# The filename entry stuff "TextEntry" is grotty and simple. All filenames are presumed to begin with:
# PCG- eg if you enter a filename of 12345 you get PCG-12345.bin or .asm if I have written that code yet.
# VID-
# COL-

# Todo: Allow the user to change between selecting a PCG or a ROM character to place on the screen or copy
# to the pixel editor window.

# Changelog....
# 14/10/22 19:02 added save pcg to asm file as well as a bin file.
# 14/10/22 22:30 adding support to select PCG or ROM character for PLACEment or copying to pixel editor

# IF YOU HAVE A SMALL ONE 
ScreenWidth = 850
ScreenHeight = 600
BeeScrnHMul = 2 # y scaling factor ie 256 becomes 768
BeeScrnWMul = 1 # x scaling factor ie 512 becomes 1024 
ButtonHeight = 30
ButtonSpacing = 4

# IF YOU HAVE A BIG ONE
#ScreenWidth = 1400
#ScreenHeight = 900
#BeeScrnHMul = 3 # y scaling factor ie 256 becomes 768
#BeeScrnWMul = 2 # x scaling factor ie 512 becomes 1024 
#ButtonHeight = 32
#ButtonSpacing = 8

DoingTextEntry = False
TextEntry = "default"
RenderedCharX = 0 # used to display a sample of the BG/FG
RenderedCharY = 0

BeeScrnTopX = 10 # x of top left corner of screen rendition in pygame window
BeeScrnTopY = 10 # y of top left corner of screen rendition in pygame window
BeeScrnWidth = 512
BeeScrnHeight = 256


BeeScrnBorderCol = pygame.Color(64,64,64)
BeeScrnBorderWid = 2

NextToBeeScrnX = (BeeScrnTopX + BeeScrnWidth * BeeScrnWMul + BeeScrnBorderWid * 3) # next space available
print(NextToBeeScrnX)

# Setup the Microbee 16 colour palette. Pygame Color is B G R
# Colour 6 in the pallete needs to be a Brown ie modified RGBI not a dark yellow.
BeeStdInten = 128
BeeHiInten = 180
BeeLoInten = 64

BeePalette = [pygame.Color(0,0,0), 
            pygame.Color(0,0,BeeStdInten), 
            pygame.Color(0,BeeStdInten,0), 
            pygame.Color(0,BeeStdInten,BeeStdInten),
            pygame.Color(BeeStdInten,0,0), 
            pygame.Color(BeeStdInten,0,BeeStdInten),
            pygame.Color(BeeStdInten-30,BeeStdInten-70,0),
            pygame.Color(BeeStdInten,BeeStdInten,BeeStdInten),
            pygame.Color(BeeLoInten,BeeLoInten,BeeLoInten), 
            pygame.Color(0,0,BeeHiInten), 
            pygame.Color(0,BeeHiInten,0), 
            pygame.Color(0,BeeHiInten,BeeHiInten),
            pygame.Color(BeeHiInten,0,0), 
            pygame.Color(BeeHiInten,0,BeeHiInten),
            pygame.Color(BeeHiInten,BeeHiInten,0),
            pygame.Color(BeeHiInten,BeeHiInten,BeeHiInten)]

BeeScrnBGCol = BeePalette[0] # pygame.Color(0,32,0)
BeeScrnFGCol = BeePalette[2] # pygame.Color(128,128,128)
BeeScrBGP = 0
BeeScrFGP = 2

BeeVidRam = bytearray(2048) # screen memory is 2k F000-F7FF
BeeColRam = bytearray(2048) # colour ram sits behind PCG ram F800-FFFF with colour control bit set
BeeAttrRam = bytearray(2048)
BeePcgRam = bytearray(2048) # A bank of PCG memory F800-FFFF with colour control bit reset
BeeCharRom = bytearray(4096) # The character ROM contains the 64x16 and 80x24 character sets each is 2k. 

# This is the character ROM display below the Bee screen area.
PcgDumpFGCol = BeeScrnFGCol
PcgDumpBGCol = pygame.Color(16,16,16)
PcgDumpTopX = BeeScrnTopX 
PcgDumpTopY = BeeScrnTopY + BeeScrnBorderWid + (BeeScrnHeight * BeeScrnHMul) + 4
PcgDumpHeight = 32 * BeeScrnHMul
PcgDumpWidth = 8 * 64 * BeeScrnWMul

# Parameters that define the character editor/display area to the right of the screen
# This will be an 8x16 pixel area but we will add a pixel on each side to show the 
# adjoining character on the screen. Therefore we have 10x18 pixels to show.

PixEdTopX = BeeScrnTopX+ (BeeScrnBorderWid * 4) + (64 * 8 * BeeScrnWMul)
PixEdTopY = BeeScrnTopY
PixEdPw = 16
PixEdPh = 16
PixEdBorderWid = BeeScrnBorderWid
PixEdBuffer = bytearray(16)
PixEdFGCol = BeeScrnFGCol
PixEdBGCol = BeeScrnBGCol

PixelsChanged = False # Flag indicates a change was made in the pixel editor area.
PixelsEditable = False # Indicates if the character in the Pixel editor area is an editable one (might be ROM char)
PcgBeingEdited = 0 # The character code 0-255 of the character being edited. If 0-127 then need to specify char to save in.

# UI Elements
ScrnCsr = 0     # The cursor on the bee screen 0-1023
PcgCsr = 0     # The PCG selection cursor 0-127
IsGridEnabled = False # Show grid on Bee screen
ShowingPcg = True # Showing PCG in the character dump

TextTopX = 1048 # This gets updated at startup
TextTopY = 720
TextWidth = 300
TextHeight = 60
TextMaxChar = 16
TextCharCount = 0

ButtonWidth = 70

ButtonFontSize = 16

ButtonTextColour = pygame.Color("black")
ButtonDiabledColour = pygame.Color("gray")
ButtonColour = pygame.Color("dark gray")

MyButton = dict()
Buttons = []

DialogTopX = (BeeScrnTopX + (BeeScrnWidth/2 * BeeScrnWMul) + BeeScrnBorderWid) /2 #534 # The middle of the "Bee" screen area
DialogTopY = (BeeScrnTopY + (BeeScrnHeight/2 * BeeScrnHMul) + BeeScrnBorderWid) /2 # 377
DialogTextColour = pygame.Color("yellow")
DialogBorderColour = pygame.Color("red")
DialogBgColour = pygame.Color(32,32,32)

def drawScreenCursor(screen):
    global ScrnCsr
    global BeeScrnTopX
    global BeeScrnTopY
    global BeeScrnWMul
    global BeeScrnHMul

    print("CURSOR")
    col = ScrnCsr & 63
    row = ScrnCsr >> 6

    x = BeeScrnTopX + BeeScrnWMul * 8 * col + 1
    y = BeeScrnTopY + BeeScrnHMul * 16 * row +1

    pygame.draw.rect(screen, pygame.Color("red"), (x,y,6*BeeScrnWMul,15*BeeScrnHMul),1)

def drawPcgCursor(screen):
    global PcgCsr

    col = PcgCsr & 63
    row = PcgCsr >> 6

    x = PcgDumpTopX + BeeScrnWMul * 8 * col + 1

    if row == 0:
        y = PcgDumpTopY + BeeScrnHMul * 17 * row + 1
    else:
        y = PcgDumpTopY + BeeScrnHMul * 17 * row + 1

    pygame.draw.rect(screen, pygame.Color("red"), (x,y,6*BeeScrnWMul,14*BeeScrnHMul),1)

def baseFileName():
    return time.strftime("%H%M%S")

def noFunction(screen,x,y):
    print("Function undefined",x,y)

def btnSavePcg(screen,x,y):
    global BeePcgRam
    global TextEntry

    filename = "PCG-"+TextEntry+".bin"
    file = open(filename,"w+b")
    file.write(BeePcgRam[0:2048])
    file.close()

    savePCGasm(TextEntry)
    print("Save PCG:", filename)

def btnLoadPcg(screen,x,y):
    global BeePcgRam
    global TextEntry

    try:
        filename = "PCG-"+TextEntry+".bin"
        file = open(filename,"rb")
        BeePcgRam[0:2048] = file.read(2048)
        file.close()
        drawPcgDumpScreen(screen)
        renderBeeScreen(screen)
    except:
        drawDialog(screen, "Could not load PCG file")
        time.sleep(3)
        renderBeeScreen(screen)

def btnSaveVram(screen,x,y):
    global BeeVidRam
    global TextEntry

    filename = "VID-"+TextEntry+".bin"
    file = open(filename,"w+b")
    file.write(BeeVidRam[0:2048])
    file.close()
    print("Save VRAM", filename)

def btnLoadVram(screen,x,y):
    global BeeVidRam
    global TextEntry

    try:
        filename = "VID-"+TextEntry+".bin"
        file = open(filename,"rb")
        BeeVidRam[0:2048] = file.read(2048)
        file.close()
        renderBeeScreen(screen)
    except:
        drawDialog(screen, "Could not load VRAM file")
        time.sleep(3)
        renderBeeScreen(screen)

def btnSaveCol(screen,x,y):
    global BeeColRam
    global TextEntry

    filename = "COL-"+TextEntry+".bin"
    file = open(filename,"w+b")
    file.write(BeeColRam[0:2048])
    file.close()

def btnLoadCol(screen,x,y):
    global BeeColRam
    global TextEntry
    try:
        filename = "COL-"+TextEntry+".bin"
        file = open(filename,"rb")
        BeeColRam[0:2048] = file.read(2048)
        renderBeeScreen(screen)
        file.close()
    except:
        drawDialog(screen,"Could not load COLRAM file")
        time.sleep(3)
        renderBeeScreen(screen)

def btnPixLeft(screen,x,y):
    global PixEdBuffer

    mask = 1
    for row in range(0,16):
        t = PixEdBuffer[row] & 128
        if t > 0:
            t = 1
        PixEdBuffer[row] = (((PixEdBuffer[row] << 1) & 255) | t)

    drawPixEd(screen, 0)


def btnPixRight(screen,x,y):
    global PixEdBuffer

    mask = 1
    for row in range(0,16):
        t = PixEdBuffer[row] & 1
        if t > 0:
            t = 128
        PixEdBuffer[row] = (((PixEdBuffer[row] >> 1) & 255) | t)

    drawPixEd(screen, 0)

def btnPixUp(screen,x,y):
    global PixEdBuffer

    t = PixEdBuffer[0]
    PixEdBuffer[0:15] = PixEdBuffer[1:16]
    PixEdBuffer[15] = t
    drawPixEd(screen, 0)

def btnPixDown(screen,x,y):
    global PixEdBuffer

    t = PixEdBuffer[15]
    PixEdBuffer[1:16] = PixEdBuffer[0:15]
    PixEdBuffer[0] = t
    drawPixEd(screen, 0)

def btnPixInvert(screen,x,y):
    global PixEdBuffer

    for i in range(0,16):
        PixEdBuffer[i] = ~PixEdBuffer[i] & 255

    drawPixEd(screen, 0)

def btnPixClear(screen,x,y):
    global PixEdBuffer

    for i in range(0,16):
        PixEdBuffer[i] = 0

    drawPixEd(screen, 0)

def btnPixRevert(screen,x,y):
    drawPixEd(screen, 0)

def btnPixCommit(screen,x,y):
    global BeePcgRam
    global PixEdBuffer

    if not ShowingPcg:
        drawDialog(screen,"You need to select a PCG destination")
        time.sleep(2)
        renderBeeScreen(screen)
        return

    drawPixEd(screen, 0)
    BeePcgRam[PcgCsr * 16:PcgCsr * 16+16] = PixEdBuffer[0:16]
    drawPcgDumpScreen(screen)
    drawPcgCursor(screen)
    renderBeeScreen(screen)
    drawScreenCursor(screen)

def btnGridToggle(screen,x,y):
    global BeePcgRam
    global PixEdBuffer
    global IsGridEnabled

    if IsGridEnabled == True:
        IsGridEnabled = False
    else:
        IsGridEnabled = True

    renderBeeScreen(screen)
    drawScreenCursor(screen)

# 10100110 -> 01100101
def btnPixHflip(screen,x,y):
    global PixEdBuffer

    for row in range (0,16):
        masks = 1
        maskd = 128
        t = 0
        for bit in range (0,8):
            f = PixEdBuffer[row] & (masks << bit) # 1,2,4,8,16 etc
            if f > 0:
                t = t | (maskd >> bit)
        PixEdBuffer[row] = t        

    drawPixEd(screen, 0)

def btnPixVflip(screen,x,y):
    global PixEdBuffer
    
    tmp = PixEdBuffer[0:16]
    
    for i in range(0,16):
        PixEdBuffer[i] = tmp[15-i]

    drawPixEd(screen, 0)

def btnCls(screen,x,y):
    global BeeVidRam
    global BeeColRam
    global BeeScrBGP
    global BeeScrFGP

    for i in range(0,2048):
        BeeVidRam[i] = 32
        BeeColRam[i] = (BeeScrBGP << 4) | BeeScrFGP
    
    renderBeeScreen(screen)

def btnSelectPCG(screen,x,y):
    global ShowingPcg
    
    ShowingPcg = True
    drawPcgDumpScreen(screen)
    print("Show PCG in character set dump")

def btnSelectROM(screen,x,y):
    global ShowingPcg

    ShowingPcg = False
    drawPcgDumpScreen(screen)
    print("Show ROM characters in dump")

def btnEdSelPcg(screen, x,y):
    global PcgBeingEdited
    global PixEdBuffer
    global PcgCsr

    pcgadr = PcgCsr * 16 # each character takes 16 bytes
    PcgBeingEdited = PcgCsr
    if ShowingPcg:
        PixEdBuffer = BeePcgRam[pcgadr:pcgadr+16]
    else:
        PixEdBuffer = BeeCharRom[pcgadr:pcgadr+16]
    drawPixEd(screen)

# Place currently selected PCG or character ROM character on screen at cursor and advance cursor
def btnPlaceChar(screen,x,y):
    global BeeVidRam
    global ScrnCsr
    global PcgCsr

    if ShowingPcg: # working with PCG character at pcgcsr address
        BeeVidRam[ScrnCsr] = PcgCsr + 128
    else:
        BeeVidRam[ScrnCsr] = PcgCsr

    BeeColRam[ScrnCsr] = (BeeScrBGP << 4) | BeeScrFGP
    ScrnCsr = (ScrnCsr + 1) & 1023
    renderBeeScreen(screen)
    drawScreenCursor(screen)

def btnForeground(screen, x,y):
    global BeeScrnFGCol
    global BeeScrFGP
    global BeePalette
    global BeeCharRom
    global BeeScrnBGCol

    BeeScrFGP = (BeeScrFGP + 1) & 15
    BeeScrnFGCol = BeePalette[BeeScrFGP]
    render8x16(screen, BeeCharRom[72*16:72*16+16], RenderedCharX, RenderedCharY-3,BeeScrnFGCol, BeeScrnBGCol,2,2)

def btnBackground(screen,x,y):
    global BeeScrnBGCol
    global BeeScrBGP
    global BeePalette
    global BeeCharRom
    global BeeScrnFGCol

    BeeScrBGP = (BeeScrBGP + 1) & 15
    BeeScrnBGCol = BeePalette[BeeScrBGP]
    render8x16(screen, BeeCharRom[72*16:72*16+16], RenderedCharX, RenderedCharY-3,BeeScrnFGCol, BeeScrnBGCol,2,2)

def AddButton(screen,x,y,label,function,w=ButtonWidth,h=ButtonHeight,enabled=True, fg=ButtonColour, bt=ButtonTextColour):
    global Buttons

    m = dict({
        "label": label,
        "function": function,
        "x": x,
        "y": y,
        "w": w,
        "h": h,
        "enabled": enabled,
        "fg": fg,
        "bt": bt
        })

    Buttons.append(m)
    drawButton(screen, x, y, label,fg=m["fg"], bt=m["bt"])

def redrawButtons(screen):
    global Buttons

    for btn in Buttons:
        if btn["enabled"] == True:
            drawButton(screen, btn["x"], btn["y"], btn["label"],fg=btn["fg"], bt=btn["bt"])

# iterate the button collection, and if we are clicking on one run it's code.
def scanButtons(screen, x, y):
    global Buttons

    for btn in Buttons:
        if btn["enabled"] == True:
            if btn["label"] == "FG":
                btn["fg"] = BeeScrnFGCol
            
            if btn["label"] == "BG":
                btn["fg"] = BeeScrnBGCol
                
            if x >= btn["x"] and x <= btn["x"] + btn["w"]:
                 if y >= btn["y"] and y <= btn["y"] + btn["h"]:
                    print("Pressed :",btn["label"])
                    btn["function"](screen,x,y) # call the function associated with the button


# Draw a basic UI push button
def drawButton(screen, x, y, label, width=ButtonWidth, height=ButtonHeight, fontSize=ButtonFontSize, fg=ButtonColour, bt=ButtonTextColour):
    global ButtonWidth
    global ButtonHeight
    global ButtonFontSize
    global ButtonTextColour
    global ButtonColour

    pygame.draw.rect(screen, fg, 
        (x, y, width, height),border_radius=4)
    font = pygame.font.SysFont("arial",size=fontSize)
    btnText = font.render(label, True, bt)
    btnTextRect = btnText.get_rect()
    btnTextRect.center = (x+ButtonWidth/2,y+ButtonHeight/2-1)
    screen.blit(btnText, btnTextRect)
    pygame.draw.rect(screen, BeeScrnBorderCol, 
        (x-1, y-1, width+2, height+2),border_radius=4,width=1)


def doPixEdBorder(screen):
    if PixelsChanged:
        border = pygame.Color("red")
    else:
        border = BeeScrnBorderCol

    pygame.draw.rect(screen, border, 
        (PixEdTopX, PixEdTopY, PixEdPw * 10 + 11, PixEdPh * 18 + 19), 1) 

# Draw the pixel editor screen, and render the pixels in PixEdBuffer.
# There is a 1 pixel buffer around each rendered "pixel" to allow room for a cursor.
# This adds 1 pixel per pixel width and height +1
# |*|*|*|*|*|*|*|*| 
# Normal pixel rendered as 24x24 at a 25 pixel spacing.
# |************************|*****
# Borders are 25x25 rectangle of width 1 at 25 pixel spacing.
def drawPixEd(screen, pixelSource = 0, fg = PixEdFGCol, bg = PixEdBGCol):
    #pygame.draw.rect(screen, BeeScrnBorderCol, 
    #(PixEdTopX-BeeScrnBorderWid, PixEdTopY-BeeScrnBorderWid, 
    #10 * PixEdPw +(2*BeeScrnBorderWid)+11, 18 * PixEdPh +(2*BeeScrnBorderWid)+19), BeeScrnBorderWid)

    for y in range(0, 18):
        for x in range(0, 10):
            # print(PixEdTopX + x * (PixEdPw+1), PixEdTopY + y * (PixEdPh+1))
            pygame.draw.rect(screen, BeeScrnBorderCol, 
                (PixEdTopX + (x * (PixEdPw+1)), PixEdTopY + (y * (PixEdPh+1)), PixEdPw+2, PixEdPh+2), 1)

    # This editor can be displaying a couple of possible data sources.
    # pixelSource = 0 if it is from the PCG RAM by being selected in the PCG dump
    # pixelSource = 1 if is is from a screen selection. In which case show a pixel from bounding stuff too

    if pixelSource == 0:
        mask = 1
        yi = 0
        tx = PixEdTopX + PixEdPw + 1
        ty = PixEdTopY + PixEdPh + 1 # top corner of actual 8x16

        for b in PixEdBuffer:
            for x in range(0,8):
                if b & (mask<<(7-x)):
                    pygame.draw.rect(screen, fg,(tx+(x * (PixEdPw+1))+1, ty+(yi * (PixEdPh+1))+1, PixEdPw, PixEdPh))
                else:
                    pygame.draw.rect(screen, bg,(tx+(x * (PixEdPw+1))+1, ty+(yi * (PixEdPh+1))+1, PixEdPw, PixEdPh))
            yi=yi+1

    doPixEdBorder(screen)



# draw the microbee screen representation
def drawBee6416screen(screen):
    # Border
    pygame.draw.rect(screen, BeeScrnBorderCol, 
    (BeeScrnTopX-BeeScrnBorderWid, BeeScrnTopY-BeeScrnBorderWid, 
    BeeScrnWidth*BeeScrnWMul+(2*BeeScrnBorderWid), BeeScrnHeight*BeeScrnHMul+(2*BeeScrnBorderWid)), BeeScrnBorderWid)
    
    # Screen area
    pygame.draw.rect(screen, BeeScrnBGCol, (BeeScrnTopX, BeeScrnTopY, 
    BeeScrnWidth*BeeScrnWMul, BeeScrnHeight*BeeScrnHMul))

# draw the pixels for a single 8x16 character from bytearray
def render8x16(screen, bytes, x, y, fg=PcgDumpFGCol, bg=PcgDumpBGCol,hm=BeeScrnHMul, wm=BeeScrnWMul):
    global BeeScrnHMul
    global BeeScrnWMul

    mask = 1
    #print(bytes)
    yi = 0 # y index for each row we do
    for b in bytes:
        for sx in range(0,8):
            # print("%02x"%(mask << (7-sx)))
            if b & (mask<<(7-sx)):
                pygame.draw.rect(screen, fg,(x+(sx * wm), y+(yi * hm), wm, hm))
            else:
                pygame.draw.rect(screen, bg,(x+(sx * wm), y+(yi * hm), wm, hm))
        yi=yi+1

# The pcg dump screen is the area under the main bee screen showing all 128 PCG characters (1 PCG bank)
def drawPcgDumpScreen(screen):
    pygame.draw.rect(screen, BeeScrnBorderCol, 
    (PcgDumpTopX-BeeScrnBorderWid, PcgDumpTopY-BeeScrnBorderWid, 
    PcgDumpWidth+(2*BeeScrnBorderWid), PcgDumpHeight+(2*BeeScrnBorderWid)+1), BeeScrnBorderWid)

    x = PcgDumpTopX
    y = PcgDumpTopY
    for char in range(0,64):
        if ShowingPcg:
            render8x16(screen, BeePcgRam[(char * 16):(char * 16)+16], x, y)
        else:
            render8x16(screen, BeeCharRom[(char * 16):(char * 16)+16], x, y,fg=pygame.Color(48,48,48))
        x = x + 8 * BeeScrnWMul

    x = PcgDumpTopX
    y = y + (16*BeeScrnHMul) + 1 # the plus 1 gives us a 1 pixel divider between the two rows
    for char in range(64,128):
        if ShowingPcg:
            render8x16(screen, BeePcgRam[(char * 16):(char * 16)+16], x, y)
        else:
            render8x16(screen, BeeCharRom[(char * 16):(char * 16)+16], x, y,fg=pygame.Color(48,48,48))
        x = x + 8 * BeeScrnWMul

# Set a pixel on the bee screen 
def setBeePixel(screen, x, y, colour = BeeScrnFGCol):
    pygame.draw.rect(screen, colour, (x*BeeScrnWMul+BeeScrnTopX, y*BeeScrnHMul+BeeScrnTopY, BeeScrnWMul, BeeScrnHMul))

# Reset a pixel on the bee screen (call setpixel with erase or BG colour)
def resetBeePixel(screen, x, y, colour = BeeScrnBGCol):
    setBeePixel(screen, x, y, colour)

# Load the standard Microbee 4k character rom from file.
def loadCharRom():
    global BeeCharRom
    global BeePcgRam

    try:
        file = open("character_4k.rom","rb")
        BeeCharRom = bytearray(file.read())
        BeePcgRam = BeeCharRom[0:2048]
        file.close()
        print("Loaded 4k character rom")
    except(RuntimeError):
        print("Could not open the character_4k.rom file")
        quit()

# This will render the Microbee screen area by looking up the BeeVidRam area, grabbing the character code and rendering that
# symbol from the BeeCharRom or BeePcgRam using the colour in the BeeColRam array. Just like the real thing.
def renderBeeScreen(screen):
    global BeeVidRam 
    global BeeColRam 
    global BeeCharRom
    global BeePcgRam
    global IsGridEnabled

    # BeeVidRam = random.randbytes(1024)
    if IsGridEnabled == True:
        for column in range(1,64): #
            pygame.draw.line(screen, pygame.Color(20,20,20), 
                (BeeScrnTopX+column*BeeScrnWMul*8-1,BeeScrnTopY),
                (BeeScrnTopX+column*BeeScrnWMul*8-1, BeeScrnTopY+BeeScrnHMul*256-1))

        for row in range(1,16): #
            pygame.draw.line(screen, pygame.Color(20,20,20), 
                (BeeScrnTopX, BeeScrnTopY+row*BeeScrnHMul*16-1),
                (BeeScrnTopX+BeeScrnWMul*8*64-1, BeeScrnTopY+row*BeeScrnHMul*16-1))
    else:
        for column in range(0,64):
            for row in range(0,16):
                chrCode = BeeVidRam[column + (row * 64)]

                if chrCode < 127: # Render from the BeeCharRom
                    render8x16(screen, BeeCharRom[(chrCode * 16):(chrCode * 16)+16], 
                        BeeScrnTopX+(column *(8 * BeeScrnWMul)), BeeScrnTopY+(row * (16 * BeeScrnHMul)), 
                        fg=getFgColAtxy(column,row), bg=getBgColAtxy(column,row))
                else: # Render from the BeePcgRam
                    chrCode = chrCode - 128
                    render8x16(screen, BeePcgRam[(chrCode * 16):(chrCode * 16)+16], 
                        BeeScrnTopX+(column *(8 * BeeScrnWMul)), BeeScrnTopY+(row * (16 * BeeScrnHMul)),
                        fg=getFgColAtxy(column,row), bg=getBgColAtxy(column,row))

    

# Return the foreground colour for the cell at x,y (typically 0-63, 0-15)
# For the foreground colour we take the lower 4 bits of the colour ram in IBGR format
def getFgColAtxy(x,y):
    global BeeColRam
    global BeePalette

    fg = BeeColRam[x + (y*64)]
    fg = fg & 15
    return BeePalette[fg]

# Return the foreground colour for the cell at x,y (typically 0-63, 0-15)
# For the foreground colour we take the lower 4 bits of the colour ram in IBGR format
def getBgColAtxy(x,y):
    global BeeColRam
    global BeePalette

    bg = BeeColRam[x + (y*64)]
    bg = bg >> 4
    return BeePalette[bg]

# This will determine where the mouse is.
# 0 Not in a special area
# 1 Within the Bee screen area
# 2 within the PCG dump area
# 3 within the pixel editor live area (inner 8x16)
# 4 in the colour palette

def whereIsTheMouse(x,y):
    rx = 0
    ry = 0

    # Is it on the bee screen?
    if x >= BeeScrnTopX and x <= BeeScrnTopX + (512 * BeeScrnWMul) and \
        y >= BeeScrnTopY and y<= BeeScrnTopY + (256 * BeeScrnHMul):
        rx=int((x - BeeScrnTopX) / (BeeScrnWMul * 8)-0.1)
        ry=int((y - BeeScrnTopY) / (BeeScrnHMul * 16)-0.1)
        adr = rx+(ry * 64)
        return 1,rx,ry,adr

    # Is it on the pcg dump?
    if x >= PcgDumpTopX and x <= PcgDumpTopX + (512 * BeeScrnWMul) and \
        y >= PcgDumpTopY and y<= PcgDumpTopY + (32 * BeeScrnHMul) + 1:
        rx=int((x - PcgDumpTopX) / (BeeScrnWMul * 8)-0.1)
        ry=int((y - PcgDumpTopY) / (BeeScrnHMul * 16)-0.1)
        adr = rx+(ry * 64)
        return 2,rx,ry,adr

    # Is it in the pixel editor?
    if x >= PixEdTopX+PixEdPw+1 and x <= PixEdTopX + (9 * (PixEdPw+1)) and \
        y >= PixEdTopY+PixEdPh+1 and y<= PixEdTopY + (17 * (PixEdPh+1)):
        rx=int((x - PixEdTopX - PixEdPw+1) / (PixEdPw + 1)-0.1)
        ry=int((y - PixEdTopY - PixEdPh+1) / (PixEdPh + 1)-0.1)
        adr = rx+(ry * 8)
        return 3,rx,ry,adr

    # Is it in the filename text field?
    if x >= TextTopX and x <= TextTopX + TextWidth and \
        y >= TextTopY and y<= TextTopY + TextHeight:
        return 4,0,0,0

    return 0,0,0,0

# Do what needs to be done to register a mouse click in the pixel editor
def processPixelEditorClick(screen, x, y, address):
    global PixEdBuffer
    global PixelsChanged
    global PcgBeingEdited

    if PcgBeingEdited < 0: # a rom character can't be directly edited but needs to be moved to a PCG first
        print("I can't let you do that John")
    else:
        PixelsChanged = True # unclean ie needs saving later
        # Now 7-x is the bit and y is the byte in the buffer
        workByte = PixEdBuffer[y] # get the byte
 
        if workByte & (128 >> x): # if bit is set then clear it
            PixEdBuffer[y] = workByte & (255-(128 >> x))
        else:
            PixEdBuffer[y] = workByte | (128 >> x)

        drawPixEd(screen, 0)

        # Now can we update the screen and pcg dump in real time?
        #BeePcgRam[PcgBeingEdited * 16:] = PixEdBuffer[0:16]
        #renderBeeScreen(screen)
        #drawPcgDumpScreen(screen)
    

def processScreenAreaClick(screen, x, y, address):
    global ScrnCsr

    ScrnCsr = address
    renderBeeScreen(screen)
    drawScreenCursor(screen)

# A click in the PCG area selects that character for editing.
# So determine the character and place their contents into the edit PixEdBuffer and render it.
def processPcgAreaClick(screen, x, y, address):
    global PixEdBuffer
    global PcgBeingEdited
    global PcgCsr

    PcgCsr = address
    drawPcgDumpScreen(screen)
    drawPcgCursor(screen)

def drawTextBox(screen):
    global ScreenWidth
    global BeeScrnBorderWid
    global TextTopX
    global TextTopY

    font = pygame.font.SysFont("arial",size=24)
    text = font.render("Filename:"+TextEntry, True, pygame.Color(255,255,255), pygame.Color(64,64,64))
    textRect = text.get_rect()
    pygame.draw.rect(screen, pygame.Color(64,64,64),(TextTopX, TextTopY, 300, textRect.height)) # Solid
    textRect.center = (TextTopX + textRect.width/2,TextTopY +textRect.height/2)
    screen.blit(text, textRect)


def performTextEntry(screen, k):
    global TextEntry
    global DoingTextEntry
    
    print(k)
    if DoingTextEntry == False:
        return

    if k == 13:
        DoingTextEntry = False

        if len(TextEntry) == 0:
            TextEntry = "default"

        drawTextBox(screen)
        renderBeeScreen(screen)
        return


    if k == 8:
        if len(TextEntry) > 0:
            TextEntry = TextEntry[0:len(TextEntry)-1]
            print(TextEntry)

        print("backspace")

    if k >= ord(' ')+1 and k <=ord('z'):
        if len(TextEntry) < 16:
            if pygame.key.get_mods() & pygame.KMOD_SHIFT and k>= ord('a') and k<=ord('z'):
                k = k - 32

            if pygame.key.get_mods() & pygame.KMOD_SHIFT and k == ord('-'):
                k = ord('_')

            TextEntry = TextEntry + chr(k)

        print(TextEntry)
    drawTextBox(screen)
    
def drawDialog(screen, message):
    global DialogTopX
    global DialogTopY
    global DialogBgColour
    global DialogTextColour
    global DialogBorderColour

    font = pygame.font.SysFont("arial",size=24)
    text = font.render("Hey! - "+message, True, DialogTextColour, DialogBgColour)
    textRect = text.get_rect()
    textRect.center = (DialogTopX + textRect.width/2,DialogTopY +textRect.height/2)
    pygame.draw.rect(screen, DialogBorderColour,(textRect.x-5, textRect.y-5, textRect.width+10, textRect.height+10),1,4)
    screen.blit(text, textRect)
    pygame.display.update()

# Save the contents of the PCG memory as bytes in Z80 asm format.
def savePCGasm(filename):
    try:
        file = open("PCG-"+filename+".asm", "w")

        for theChar in range(0,128): # The character loop.
            file.write("PCG"+str(theChar))

            for line in range(0,2):
                if line == 0:
                    file.write("\t.byte ")
                else:
                    file.write("\t\t.byte ")

                for b in range(0,8):
                    file.write(str(BeePcgRam[(theChar*16)+(line*8)+b]))
                    if b<7:
                        file.write(",")
                file.write("\n")
        file.close()
    except:
        print("Epic fail...")

def main():

    global PixEdBuffer
    global BeeAttrRam
    global BeeCharRom
    global BeePcgRam
    global PixelsChanged
    global BeeVidRam
    global BeeColRam
    global ButtonHeight
    global ButtonWidth
    global ButtonSpacing
    global DoingTextEntry
    global RenderedCharX
    global RenderedCharY
    global TextTopX
    global TextTopY

    pygame.init()
    pygame.display.set_caption("Microbee Graphics Dev Ed")

    screen = pygame.display.set_mode((ScreenWidth,ScreenHeight))
   
    loadCharRom()
    # BeeVidRam = random.randbytes(1024)

    for i in range(0,2048):
        BeeColRam[i] = 2
        BeeVidRam[i] = 32

    #BeeColRam = random.randbytes(1024)

    BeeVidRam[0] = ord('H')
    BeeVidRam[1] = ord('e')
    BeeVidRam[2] = ord('l')
    BeeVidRam[3] = ord('l')
    BeeVidRam[4] = ord('o')

    PixEdBuffer = BeePcgRam[528:544]
    drawBee6416screen(screen)
    pygame.display.update()

    drawPcgDumpScreen(screen)
    drawPixEd(screen)
    renderBeeScreen(screen)
    pygame.display.update()

    bx = NextToBeeScrnX # 1048
    #by = 784
    bw = ButtonWidth
    bh = ButtonHeight
    bg = ButtonSpacing
    bnx = bw+bg
    bny = bh+bg

    by = 326
    AddButton(screen, bx,by, "Up", btnPixUp)
    AddButton(screen, bx+bnx, by, "Down", btnPixDown)    
    AddButton(screen, bx+bnx+bnx,by, "Left", btnPixLeft)
    AddButton(screen, bx+bnx+bnx+bnx, by, "Right", btnPixRight)

    by = by + bny
    AddButton(screen, bx,by, "Invert", btnPixInvert)
    AddButton(screen, bx+bnx, by, "Clear", btnPixClear)    
    AddButton(screen, bx+bnx+bnx,by, "H Flip", btnPixHflip)
    AddButton(screen, bx+bnx+bnx+bnx, by, "V Flip", btnPixVflip)

    by = by + bny
    AddButton(screen, bx,by, "Commit", btnPixCommit)
    AddButton(screen, bx+bnx, by, "Revert", btnPixRevert)    
    AddButton(screen, bx+bnx+bnx,by, "Edit PCG", btnEdSelPcg)

    # by = 460
    by = by + bny
    AddButton(screen, bx,by, "FG", btnForeground, fg=BeeScrnFGCol)
    AddButton(screen, bx+bnx, by, "BG", btnBackground, fg=BeeScrnBGCol, bt=pygame.Color(128,128,128))
    RenderedCharX = bx+bnx+bnx
    RenderedCharY = by
    render8x16(screen, BeeCharRom[72*16:72*16+16], RenderedCharX,RenderedCharY-3,BeeScrnFGCol, BeeScrnBGCol, 2,2) # 1224,450

    by = by + bny
    AddButton(screen, bx,by, "Load Vram", btnLoadVram)
    AddButton(screen, bx+bnx, by, "Save Vram", btnSaveVram)    
    AddButton(screen, bx+bnx+bnx, by, "Load Pcg", btnLoadPcg)
    AddButton(screen, bx+bnx+bnx+bnx, by, "Save Pcg", btnSavePcg)

    by = by + bny
    AddButton(screen, bx,by, "Load Col", btnLoadCol)
    AddButton(screen, bx+bnx, by, "Save Col", btnSaveCol)    
    AddButton(screen, bx+bnx+bnx,by, "Sel PCG", btnSelectPCG)
    AddButton(screen, bx+bnx+bnx+bnx, by, "Sel ROM", btnSelectROM)    

    by = by + bny
    AddButton(screen, bx,by, "CLS", btnCls)
    AddButton(screen, bx+bnx, by, "Place", btnPlaceChar)    
    AddButton(screen, bx+bnx+bnx,by, "Grid Tg", btnGridToggle)
    #AddButton(screen, bx+bnx+bnx+bnx, by, "Sel ROM", btnSelectROM)    
    
    TextTopX = bx # Where the filename entry text appears under the buttons
    TextTopY = by + bny
    drawTextBox(screen)

    # render8x16(screen,BeeCharRom[0:16],PcgDumpTopX,PcgDumpTopY)

    #setBeePixel(screen, 0,0)
    #setBeePixel(screen, 511,255)

    pygame.display.update()
    
    font = pygame.font.SysFont("arial",size=24)
    # pygame.font.Font('sans.ttf', 24)

    drawScreenCursor(screen)

    running = True

    while running:
        events = pygame.event.get()
        # textinput.update(events)
        #screen.blit(textinput.surface, (1200, 500))

        for event in events:
            
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and not DoingTextEntry:
                # renderBeeScreen(screen)
                x,y = pygame.mouse.get_pos()

                scanButtons(screen,x,y)

                mouseText = font.render(" "+str(x)+" , "+str(y)+" ", True, pygame.Color(255,255,255), pygame.Color(64,64,64))
                mouseTextRect = mouseText.get_rect()
                mouseTextRect.center = (ScreenWidth - mouseTextRect.width/2,ScreenHeight - mouseTextRect.height/2)
                screen.blit(mouseText, mouseTextRect)
                
                ClickedArea, x, y, address = whereIsTheMouse(x,y)
                print("Clicked: ", ClickedArea)

                if ClickedArea == 1:
                    processScreenAreaClick(screen, x, y, address)

                if ClickedArea == 2:
                    processPcgAreaClick(screen, x, y, address)

                if ClickedArea == 3:
                    processPixelEditorClick(screen, x, y, address)

                if ClickedArea == 4: # filename field
                    drawDialog(screen, "Enter a file name and press enter")
                    DoingTextEntry = True

            if event.type == pygame.KEYDOWN:
                k = event.key
                if DoingTextEntry == True:
                    performTextEntry(screen, k)

                

        pygame.display.update()

if __name__ == "__main__":
    print(argv)
    main()

    