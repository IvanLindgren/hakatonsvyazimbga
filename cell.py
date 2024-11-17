import pyxel
from PIL import Image

BORDER_OFFSET = 25
STEP = 1
COLOR_ROAD = (255, 0, 0, 255)
COLOR_BLACK = (0, 0, 0, 255)
COLOR_PLAYER = (255, 255, 255, 255)
COLOR_WHITE = (255, 255, 255, 255)

def isColor(color, COLOR):
    offset = 15
    if (COLOR[0] - offset <= color[0] <= COLOR[0] + offset) and \
        (COLOR[1] - offset <= color[1] <= COLOR[1] + offset) and \
        (COLOR[2] - offset <= color[2] <= COLOR[2] + offset):
            return True
    return False

def isPlus(x, y, img):
    width, height = img.size
    
    kef = 5

    startX = x - kef
    startY = y
    flag = True
    for j in range(1):
        for i in range(kef * 2):
            color = img.getpixel((startX + i, startY + j))
            if (not isColor(color, COLOR_BLACK)):
                flag = False
                break
    
    color = img.getpixel((x, y - 10))
    if (isColor(color, COLOR_WHITE)):
        flag = False
    color = img.getpixel((x, y + 10))
    if (isColor(color, COLOR_WHITE)):
        flag = False

    return flag
    
            
            




def parse_image():
    road = []
    img = Image.open('bw2.png')
    img = img.convert("RGB")
    pix = img.load()
    width, height = img.size


    x = 0
    y = 0
    player = list()
    lst = list()
    for y in range(BORDER_OFFSET, height-BORDER_OFFSET, STEP):
        for x in range(BORDER_OFFSET, width-BORDER_OFFSET, STEP):
            # color = pix[x, y]
            color = img.getpixel((x, y))

            if isColor(color, COLOR_WHITE):
                road.append((x, y))
            elif isColor(color, COLOR_BLACK):
                player.append((x, y))
            
            if isPlus(x, y, img):
                lst.append((x, y))

    

    return x, y, player, road, lst



# Просмотр трафарета на изображении
class Game:
    def __init__(self):
        width, height, self.player, self.road, self.lst = parse_image()
        pyxel.init(width, height)
        pyxel.run(self.update, self.draw)

    def update(self):
        pass

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)
        for c in self.road:
            pyxel.circ(c[0], c[1], 1, pyxel.COLOR_WHITE)
        for c in self.lst:
            pyxel.circ(c[0], c[1], 3, pyxel.COLOR_RED)


Game()