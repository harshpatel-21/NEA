import pygame, os, sys, csv
pygame.init()

def load_level(level):
    layers = {}
    path = f'levels/level{level}'
    files = os.listdir(path)
    for index, file in enumerate(files):
        with open(os.path.join(path, file)) as file:
            level = csv.reader(file,delimiter=',')
            x=[]
            for row in level:
                x+=[[*map(int,row)]]
        layers[index] = x
        # sys.exit()
    return layers

game_level = load_level(2)
print(game_level)