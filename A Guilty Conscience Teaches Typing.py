#!/usr/bin/env python2.7
import os, sys
import string
import pygame
from pygame.locals import *

#CLASSES

class Rachel:
    def __init__(self, player, talkingpoints, tearpoints, wordcolor, backgroundcolor):
        #First let's open and load Rachel's speech. We do this in the class because, first, that's probably where it should be, and second, we need to get the player's name before we do it.
        speechfile = open(os.path.dirname(os.path.abspath(__file__))+"/data/speech.txt", "r")
        self.speech = speechfile.read()
        speechfile.close()
        self.speech = self.speech.replace("^p", player)
        self.speech = self.speech.split("|")
        
        self.talkingpoints = talkingpoints
        self.tearpoints = tearpoints
        self.color = wordcolor
        self.backgroundcolor = backgroundcolor
        self.timer = 4 #This controls how many words her speech stays up for. I'll want to play with it later.
        #Load and tweak our various images of Rachel:
        self.rachelstill = pygame.image.load(os.path.dirname(os.path.abspath(__file__))+'/data/rachelstill.bmp')
        self.rachelstill.set_colorkey((255,255,255))
        self.rachelstill.set_alpha(245)
        self.rachelbreeze = pygame.image.load(os.path.dirname(os.path.abspath(__file__))+'/data/rachelbreeze.bmp')
        self.rachelbreeze.set_colorkey((255,255,255))
        self.rachelbreeze.set_alpha(245)
        self.rachelgust1 = pygame.image.load(os.path.dirname(os.path.abspath(__file__))+'/data/rachelgust1.bmp')
        self.rachelgust1.set_colorkey((255,255,255))
        self.rachelgust1.set_alpha(245)
        self.rachelgust2 = pygame.image.load(os.path.dirname(os.path.abspath(__file__))+'/data/rachelgust2.bmp')
        self.rachelgust2.set_colorkey((255,255,255))
        self.rachelgust2.set_alpha(245)
        #...and her speech bubble:
        self.bubble  = pygame.image.load(os.path.dirname(os.path.abspath(__file__))+'/data/speechbubble.bmp')
        self.bubble = pygame.transform.rotozoom(self.bubble, 0, .8)
        self.bubble.set_colorkey((255,255,255))
        self.bubble.set_alpha(245)
        #Pixel-tears-related variables:
        self.stream = pygame.Surface((8, 35))
        self.stream.fill(self.backgroundcolor)
        self.teardrops = [(3,0), (3,2), (2,2), (2,4), (1,7), (1,8), (0,16), (0,18), (1,24), (2,26), (5,33), (6,35)]
        self.drip = 0

        self.wind = 0
        self.nexttalkpoint = 0
        self.nexttearpoint = 0
        self.speaking = False
        self.clear = False
        self.crying = False

        self.reporterror = False
        
#Drawing Rachel:
    def draw(self, speed, minimumspeed, topspeed, activeword, cursorposx):
        if speed >= topspeed - 1 and self.wind < 100 and cursorposx < (windowsizeXY[0]/9)*7:
            self.wind += 2
        elif self.wind > 0:
            self.wind -= 4
            
        if self.wind > 15 and self.wind <= 70:
            window.blit(self.rachelbreeze, (180, 170))
        elif self.wind > 70 and activeword %2 != 0:
            window.blit(self.rachelgust1, (180, 170))
        elif self.wind > 70 and activeword %2 == 0:
            window.blit(self.rachelgust2, (180, 170))
        else:
            window.blit(self.rachelstill, (180, 170))
        
#Speech functions, including drawing text.
    def checkspeech(self, activeword):
        try:
            if self.talkingpoints[self.nexttalkpoint] == activeword:
                self.speaking = True
                self.clear = False
                self.startword = activeword
                self.charactercount = 0
                self.firstline = ""
                self.secondline = ""
                self.twolines = False
                if self.speech[self.nexttalkpoint] == "^x": #new!
                    self.clear = True
                    self.say = typeface2.render("", False, self.color)
                else:
                    for character in self.speech[self.nexttalkpoint]:
                        if self.charactercount < 25:
                            self.firstline += character
                            self.charactercount += 1
                        elif not self.twolines and character != " ": #This handy little causal stops words from being split between lines.
                            self.firstline += character
                            self.charactercount += 1
                        else:
                            self.secondline += character
                            self.charactercount += 1
                            self.twolines = True
                    self.say = typeface2.render(self.firstline, False, self.color)
                    if self.twolines:
                        self.secondline = self.secondline.lstrip(" ")
                        self.say2 = typeface2.render(self.secondline, False, self.color)
                if (self.nexttalkpoint + 1) < len(self.speech)-1:
                    self.nexttalkpoint += 1
        except IndexError:
            if not self.reporterror:
                print("Rachel wants to say more than the story allows! She's a talkative one--but in a good way!")
                self.reporterror = True
        if self.speaking and (activeword - self.startword) <= self.timer:
            if self.twolines == False:
                window.blit(self.say, (408, 175))
            elif self.twolines:
                window.blit(self.say, (408, (175-typeface2.size(self.secondline[0])[1])))
                window.blit(self.say2, (408, 175))
            if not self.clear:
                window.blit(self.bubble, (360, 217))
        elif self.speaking and (activeword - self.startword) > self.timer:
            self.speaking = False
            self.clear = False

    def checktears(self, activeword):
        if self.tearpoints[self.nexttearpoint] == activeword:
            self.crying = True
            pygame.draw.line(self.stream, (0,0,125), self.teardrops[self.drip], self.teardrops[self.drip+1], 2)
            if (self.drip+2) < len(self.teardrops)-1: self.drip += 2
            if (self.nexttearpoint + 1) < len(self.tearpoints)-1:
                self.nexttearpoint += 1           
    def drawtears(self):
        if self.crying:
            window.blit(self.stream, (269,240))
            

class Word:

    #Is a lengthy init a sign that I was right to make this a class?
    def __init__(self, text, xpos, length, ypos, wordcolor, windowsizeXY):
        self.text = text
        self.xpos = xpos
        self.length = length
        self.ypos = ypos
        self.originalypos = ypos #Animations will need to remember the original Y position of the word.
        self.yspeed = 0
        self.typed = False
        self.mistyped = False
        self.wordcolor = wordcolor
        self.windowsizeXY = windowsizeXY
        self.letters = [] #The list we're going to fill with letter surfaces.
        self.alpha = []
        self.alphaspeed = [] #Stores how fast each letter should vanish. 
        for x in range(len(self.text)):
            self.alpha.append(0) #Default starting alpha for all words is just a little transparent.
        self.letterxpos = []
        xpositioninword = 0 #Incrementing this establishes how many pixels the letter is from the word's x position.
        x = 0
        for x in range(len(self.text)):
            #Set each letters' x position.
            self.letterxpos.append(xpositioninword)
            xpositioninword += typeface.size(self.text[x])[0]
            self.letters.append(typeface.render(self.text[x], False, self.wordcolor)) #Creating the letter surfaces in a list.
            self.letters[x].set_alpha(self.alpha[x])
        #So here we've gotta take care of the fact that we aren't actually watching the SHIFT key:
        self.text = string.replace(self.text, '"', "'")
        self.text = string.replace(self.text, "?", "/")
        self.text = string.replace(self.text, ":", ";")
        self.text = string.replace(self.text, ")", "0")
        self.text = string.replace(self.text, "!", "1")
        self.text = string.replace(self.text, "@", "2")
        self.text = string.replace(self.text, "#", "3")
        self.text = string.replace(self.text, "$", "4")
        self.text = string.replace(self.text, "%", "5")
        self.text = string.replace(self.text, "^", "6")
        self.text = string.replace(self.text, "&", "7")
        self.text = string.replace(self.text, "*", "8")
        self.text = string.replace(self.text, "(", "9")

    #Change a word's state:
    def win(self):
        self.typed = True
        self.yspeed = -10/(fps/30) #Affects all letters equally.
        #self.scale = [] #Because we're gonna scale these things! --One day :(
        #self.scalespeed = [] #How fast they should scale.
        for x in range(len(self.text)):
            #self.scale.append(1)
            #self.scalespeed.append(((len(self.text)-x)*0.03)/(fps/30)) #Probably fucked up this algorithm.
            self.alphaspeed.append(((len(self.text)*2-x*2)/1.1)/(fps/30))
 
    def explode(self):
        self.mistyped = True
        self.yspeed = -14/(fps/30) #The upward velocity of all the letters. Negative because top left corner is point of origin for X/Y.
        self.letterxspeed = [] #The list we'll populate with how fast each letter should fly horizontally.
        self.angle = [] #This list will keep track of the angle each letter's pointing.
        self.letterrotatespeed = [] #This list will keep track of how quickly each letter should rotate & which direction.
        x = 0 
        for x in range(len(self.text)):
            self.letterxspeed.append((-(len(self.text)/2 - x)*1)/(fps/30)) #Set what direction each letter should fly horizontally..
            self.angle.append(0) #Set each letter's angle at zero.
            self.letterrotatespeed.append((len(self.text)/2 - x)/(fps/30)) #Set how fast each letter should rotate.
            self.alphaspeed.append(15/(fps/30))
            
    #Draw a word in various states:	
    def draw(self, origin):
        if -self.length < origin+self.xpos < (self.windowsizeXY[0]/9)*8 and self.ypos < self.windowsizeXY[1]: #Is the word in frame?
            #How to loop the values for the glory animation:
            if self.typed:
                if self.ypos > self.originalypos-55 and self.yspeed < -1: #Lowers the acceleration of the word as it gets higher.
                    self.yspeed /= (1.1)
                for letter in range(len(self.text)):
                    if self.ypos < self.originalypos-50: #and self.scale[letter] < 1.0001:
                        #self.scale[letter] += self.scalespeed[letter]
                        #self.letters[letter] = pygame.transform.rotozoom(self.letters[letter], 0, self.scale[letter])
                    #if self.scale[letter] > 1.00000009:
                        self.alpha[letter] -= self.alphaspeed[letter]
                        self.letters[letter].set_alpha(self.alpha[letter])
                self.ypos += self.yspeed #This value can stay out of the FOR loop below, because it affects all letters.
            #How to loop the values for the exploding animation:
            elif self.mistyped:
                self.ypos += self.yspeed #BOOM! Explode upward!
                for letter in range(len(self.text)): #Adjust the values for all letters:
                    self.letterxpos[letter] += self.letterxspeed[letter] #
                    #window.blit(self.letters[letter], (origin+self.xpos+self.letterxpos[letter], self.ypos))
                    self.letters[letter] = pygame.transform.rotate(self.letters[letter], self.angle[letter]) #This is first so the letter doesn't rotate immediately.
                    if abs(self.angle[letter]) < 8: #This rotates the angle of the letter, but only if it hasn't rotated too far already.
                        self.angle[letter] += self.letterrotatespeed[letter]
                    if self.ypos < self.originalypos+100:
                        self.alpha[letter] -= self.alphaspeed[letter] #self.ypos/17
                        self.letters[letter].set_alpha(self.alpha[letter])
                self.yspeed += gravity #Also known as "gravity."
            #How to loop the values if they haven't been touched.    
            elif not self.typed and not self.mistyped:
                for letter in range(len(self.text)):
                    if origin+self.xpos+self.letterxpos[letter] < (windowsizeXY[0]/9)*8 and self.alpha[letter] < 100:
                        self.alpha[letter] += abs((origin+self.xpos+self.letterxpos[letter])-(windowsizeXY[0]))/20 #Needs to be self.alpha += something.
                        self.letters[letter].set_alpha(self.alpha[letter])
        #Now the values are set, let's draw it!
            for letter in range(len(self.text)):
                window.blit(self.letters[letter], (origin+self.xpos+self.letterxpos[letter], self.ypos))



#FUNCTIONS

def loadstory(story):
    xstart = 0
    paragraph = []
    talkingpoints = []
    tearpoints = []
    story = story.split("|")
    for currentword in story:
        if currentword == "^n":
            xstart += typeface.size("                           ")[0]
        elif currentword == "^r":
            talkingpoints.append(len(paragraph))
        elif currentword == "^t":
            tearpoints.append(len(paragraph))
        else:
            length = typeface.size(currentword)[0]
            paragraph.append(Word(currentword, xstart, length, ypos, wordcolor, windowsizeXY)) #Filling the list with instances of Word.
            xstart += length
    return paragraph, xstart, talkingpoints, tearpoints

def keyboard():
    keypress = []
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if pygame.key.name(event.key) == 'space': keypress.append(' ')
            else: keypress.append(pygame.key.name(event.key))
        elif event.type == QUIT:
            pygame.display.quit()
            pygame.quit()
            sys.exit()
    return keypress
           


#GLOBALS

windowsizeXY = (1280, 768) #1440, 900 is native.
fps = 30
ypos = (windowsizeXY[1]/5)*3
fontsize = 60
wordcolor = [0,30,30] #(255,255,255)
backgroundcolor = [250,255,245] #(0,30,30)
gravity = 4/(fps/30) #You're gonna want this to be 2 or 4. Elsewise it bogs things down. Not sure why.

storyfile = open(os.path.dirname(os.path.abspath(__file__))+"/data/story.txt", "r")
story = storyfile.read()
storyfile.close()
#story = "And |then |she |was |there. |Across |the |salad |bar, |she's gorgeous. |\n|I |stam|mered |a bit |when |she |asked |how |I |was |doing. |The answer |would've |surprised |her. |Or |anyone, |really.| "

#Turning on pygame:
pygame.init()
fpsclock = pygame.time.Clock()
window = pygame.display.set_mode(windowsizeXY, DOUBLEBUF|NOFRAME|FULLSCREEN|HWSURFACE) # | FULLSCREEN | HWSURFACE
pygame.display.set_caption("A Guilty Conscience Teaches Typing")
pygame.mouse.set_visible(False)
pygame.event.set_allowed([QUIT, KEYDOWN])

#Setting up the font:
typeface = pygame.font.Font(os.path.dirname(os.path.abspath(__file__))+'/data/edunline.ttf', fontsize)
typeface2 = pygame.font.Font(os.path.dirname(os.path.abspath(__file__))+'/data/blokus.ttf', 43)
#Turn our story into Word instances and a list of where Rachel should talk (called talkingpoints).
paragraph, paragraphlength, talkingpoints, tearpoints = loadstory(story)

#Draw-related variables:
origin = windowsizeXY[0] #The x coordinate we're going to move, and have everything else chase.
activeword = 0
currentletter = 0

#Setting up speed control:
midpoint = (windowsizeXY[0]/5)*3
stoppoint = 400 #(windowsizeXY[0]/5) #The right edge of Rachel-ish.
topspeed = 15.0/(fps/30)
minimumspeed = 8/(fps/30)
speed = topspeed
drag = .09/(fps/30)#.09/(fps/30)
    


#MAIN

#Get the player's name:
nameless = True
prompt = typeface2.render("What's your name?", False, wordcolor)
player = ""
while nameless:
    showname = typeface.render(player, False, wordcolor)

    window.fill(backgroundcolor)
    window.blit(prompt, ((windowsizeXY[0]/2-typeface2.size("What's y")[0]), windowsizeXY[1]/4))
    playermid = len(player)/2+1
    window.blit(showname, ((windowsizeXY[0]/2-typeface2.size(player[0:playermid])[0]), windowsizeXY[1]/2))
    
    letterstyped = keyboard()
    #letterstyped = letterstyped.
    for letter in letterstyped:
        if letter == "backspace" and len(player) > 0: player = player[:-1]
        elif letter == "return" and len(player) > 0:
            player = string.upper(player[0]) + player[1:]
            nameless = False
        elif letter == "escape":
            pygame.display.quit()
            pygame.quit()
            sys.exit()
        elif letter in string.printable and len(player) < 10: player += letter
    
    pygame.display.flip()
    fpsclock.tick(fps)


#Rachel needed to know her lover's name. Now she does, and we can set her up:
rachel = Rachel(player, talkingpoints, tearpoints, wordcolor, backgroundcolor)


#Now LET'S PLAY! (The main loop):
play = True
time = 0
while play:

    window.fill(backgroundcolor)

    if activeword < len(paragraph)-1:
        #Here's our attempt at handling the words' speed:
        cursorposx = origin + paragraph[activeword].xpos + paragraph[activeword].letterxpos[currentletter]
        if cursorposx > (windowsizeXY[0]/9)*8:
            speed = topspeed
        elif cursorposx > midpoint and speed > minimumspeed:
            speed -= drag
        elif cursorposx < midpoint and speed > 0:
            speed -= drag*1.5
        if cursorposx <= stoppoint: speed = 0
        if speed < 0: speed = 0

        #Check if Rachel is supposed to speak or weep. If so, she will. She's pretty self-sufficient:
        rachel.checkspeech(activeword)
        rachel.checktears(activeword)

        #Check for and handle keypresses:
        keypress = keyboard()
        for key in keypress:
            if currentletter < len(paragraph[activeword].text):
                if key in string.printable and cursorposx < (windowsizeXY[0]/9)*8:
                    if key == string.lower(paragraph[activeword].text[currentletter]):
                        if cursorposx > midpoint and speed < topspeed:
                            speed += 2/(fps/30)
                            #speed += ((topspeed)/(windowsizeXY[0]-cursorposx))
                        paragraph[activeword].letters[currentletter].set_alpha(255)
                        if currentletter < len(paragraph[activeword].text)-1:
                            currentletter+= 1
                        else:
                            paragraph[activeword].win()
                            currentletter = 0
                            if activeword < len(paragraph): activeword += 1
                    elif key != paragraph[activeword].text[currentletter]:
                        paragraph[activeword].explode()
                        currentletter = 0
                        if activeword < len(paragraph): activeword += 1
                elif key == 'return':
                    paragraph[activeword].explode()
                    currentletter = 0
                    if activeword < len(paragraph): activeword += 1
                elif key == 'escape':
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()

    #Draw the words:
    for word in paragraph:
        word.draw(origin)

    #Draw Rachel:
    rachel.draw(speed, minimumspeed, topspeed, activeword, cursorposx)
    rachel.drawtears()
    #Move the words for next time around.
    origin -= abs(speed)

    #Check if we're out of words and need to start wrapping up.
    if activeword == len(paragraph)-1:
        time += 1
        if speed > minimumspeed:
            speed -= drag/3
    if time == fps*5:
        play = False

    #And finally, reset the display.
    pygame.display.flip()
    fpsclock.tick(fps)


#Black screen before credits:
time = 0
while time < fps*4:
    window.fill(wordcolor)
    pygame.display.flip()
    pygame.event.clear
    fpsclock.tick(fps)
    time += 1

#Roll the credits :)
time = 0
rolling = True
gameby = typeface2.render("a game by Andrew Schmidt (@Scatterfelt)", False, backgroundcolor)
artby = typeface2.render("with art by the lovely @JazminEck", False, backgroundcolor)
moralby = typeface2.render("and extra help from @JonathanTurpen", False, backgroundcolor)
while rolling:
    window.fill(wordcolor)
    window.blit(gameby, (50, (windowsizeXY[1]/5)+20+50))
    window.blit(artby, (50, (windowsizeXY[1]/5)*2+50))
    window.blit(moralby, (50, (windowsizeXY[1]/5)*3-20+50))

    if time < fps*2:
        pygame.event.clear()
    if time > fps*2:
        getout = keyboard()
        for hit in getout:
            if hit != "": rolling = False

    time += 1
    pygame.display.flip()
    fpsclock.tick(fps)
    

pygame.display.quit()
pygame.quit()
sys.exit()