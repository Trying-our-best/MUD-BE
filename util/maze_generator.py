"""
    Written by turidus (github.com/turidus) in python 3.6.0
    Dependend on Pillow 4.2, a fork of PIL (https://pillow.readthedocs.io/en/4.2.x/index.html)
"""
import random as rnd
import re
from adventure.models import Room, Player
from util.title_generator import generate_desc_title

class Maze:

    class __MazeError(Exception):
        """ Custom Maze Error, containing a string describing the error that occurred
                and an errorcode:
                
                errorcode       meaning
                1               A wrong value was passed
                2               Out of bounds of list
                3               A maze algorithm tried to change a already changed maze
                4               A function that assumed a formed maze found an unformed maze
        """
        def __init__(self, string, errorcode):
            self.string = string
            self.errorcode = errorcode
        def __str__(self):
            return (str(self.string) + " |Errorcode: {}".format(self.errorcode))
            
    
    
    
    
    def __init__(self, dimensionX, dimensionY):
        """Generator for the Maze class.
           It takes two integer to decide the size of the maze (X and Y).
        
        """
        
        if not isinstance(dimensionX, int) or not isinstance(dimensionY, int):      #Checking input errors
            raise self.__MazeError("Maze dimensions have to be an integer > 0",1)
            
        
        if dimensionX < 1 or dimensionY < 1:
            raise self.__MazeError("Maze dimensions have to be an integer > 0",1)
   
        self.sizeX = dimensionX     #The size of the Maze in the X direction (from left to right)
        self.sizeY = dimensionY     #The size of the Maze in the Y direction (from up to down)
        
        self.__mazeIsDone = False     #When this flag is False, no picture can be made. When this flag is True, the maze can not be changed
        
        self.mazeList = []          #A nested List of maze Tiles. The internal representation of the maze
        
        self.wallList = []          #A list of all lists that are walls (needed for certain algorithm)
        self.tileList = []          #A single list of all tiles (needed of certain algorithm)
        
        self.mazeString = ""        #A string describing the Maze in a pseudo graphical manner, gets generated everytime __str__() gets called
        
        
    def __repr__(self): 
        """ Generates a representing string
        """
            
            
        return "This is a Maze with width of {} and height of {}".format(self.sizeX , self.sizeY)
    
    def __getNextTiles(self,X,Y): 
        """ 
            This function collects all nearest neighbour of a tile. Important for tiles that lay on a border.
            
        """
        
        if X < 0 or Y < 0:  #Checks input error (this should never happen)
            
            raise self.__MazeError("Inputs have to be an integer > 0",1)
        
        templist = []
        
        try:
            if Y == 0:
                pass
            else:
                templist.append(self.mazeList[Y-1][X])
        
        except(IndexError):
            pass

        try:
            templist.append(self.mazeList[Y+1][X])
        except(IndexError):
            pass
            
        try:
            if X == 0:
                pass
            else:
                templist.append(self.mazeList[Y][X-1])
        except(IndexError):
            pass
            
        try:
            templist.append(self.mazeList[Y][X+1])
        except(IndexError):
            pass
        
        return templist
        
    def __connectTiles(self, tileA, tileB):
        """   Takes two tiles and returns True if successful. 
              Connect the two given tiles to make a way. This is used to decide where walls shouldn't be in the final picture.
              The Tile connectTo field is appended by the compass direction of the tile it connects to (N,S,E,W).
        """
        X1 = tileA.coordinateX 
        Y1 = tileA.coordinateY
        
        X2 = tileB.coordinateX 
        Y2 = tileB.coordinateY
        
        if X1 == X2:
            
            if Y1 < Y2:
                tileA.s_to = tileB.id
                tileB.n_to = tileA.id
            
            elif Y1 > Y2:
                tileA.n_to = tileB.id
                tileB.s_to = tileA.id

        else:
            if X1 < X2:
                tileA.e_to = tileB.id
                tileB.w_to = tileA.id
            
            else:
                tileA.w_to = tileB.id
                tileB.e_to = tileA.id
        
        tileA.save()
        tileB.save()

        return True
        

    def __makeEntryandExit(self,random = False):
        """ Takes an optional boolean
            If random is set to True, it chooses the entry and exit field randomly.
            It set to False, it chooses the left upper most and right lower most corner as entry. 
        """
        if random:
            
            tile = rnd.choice(self.mazeList[0])
            tile.n_to = -1
            tile.save()
                    
            tile = rnd.choice(self.mazeList[-1])
            tile.s_to = -2
            tile.save()
        else:
            self.mazeList[0][0].n_to = -1
            self.mazeList[-1][-1].s_to = -2
            self.mazeList[0][0].save()
            self.mazeList[-1][-1].save()
        return True
                
    def makeMazeSimple(self): 
        if self.__mazeIsDone:     #Can only run if the maze is not already formed
            raise self.__MazeError("Maze is already done",3)

        Room.objects.all().delete() #Delete all stored rooms before creating            
        for indexY in range (0,self.sizeY):     #This loops generates the mazeList and populates it with new untouched floor tiles
            templist = []
            
            for indexX in range(0,self.sizeX):
                title_desc = generate_desc_title()
                print(title_desc)
                newTile = Room(title = title_desc['title'], description = title_desc['desc'], coordinateX = indexX, coordinateY = indexY)
                newTile.save()
                templist.append(newTile)
                
            self.mazeList.append(templist)
        
        frontList = []          #A list of all untouched tiles that border a touched tile
        startingtile = rnd.choice(rnd.choice(self.mazeList))    #A randomly chosen tile that acts as starting tile
        
        startingtile.workedOn = True    #This flag always gets set when a tile has between worked on.
        frontList += self.__getNextTiles(startingtile.coordinateX, startingtile.coordinateY)  #populates the frontier
 
        while len(frontList) > 0 : #When the frontier list is empty the maze is finished because all tiles have been connected

            newFrontTiles = []
            workedOnList = []
            
            rnd.shuffle(frontList)
            nextTile = frontList.pop()
            nextTile.workedOn = True
            
            tempList = self.__getNextTiles(nextTile.coordinateX,nextTile.coordinateY)
            

            for tile in tempList: #Finds all neighbours who are touched and all that are a untouched
                if tile.workedOn:
                    
                    workedOnList.append(tile)
                else:
                    if not tile in frontList:
                        newFrontTiles.append(tile)
                    
            frontList += newFrontTiles
            

            
            if len(workedOnList) > 1:   #Chooses the neighbor the tile should connect to
                connectTile = rnd.choice(workedOnList)
            else:
                connectTile = workedOnList[0]
            
            self.__connectTiles(nextTile,connectTile)
            
        self.__makeEntryandExit(random = True)     #Finally produces a Entry and an Exit
        self.__mazeIsDone = True
        return True
            
#Examples:
#newMaze = Maze(10,10)
#newMaze.makeMazeSimple()