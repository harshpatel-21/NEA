import pygame,os,WINDOW
import pygame.freetype, os ,sys
from button import Button
from boxes import Textbox

pygame.init()
pygame.freetype.init()
x,y = WINDOW.x,WINDOW.y
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"

#game window
#50,37 : y,x

FPS = 60
clock = pygame.time.Clock()

theme = 1

get_path = WINDOW.get_path

window = WINDOW.Display()
window.screen.set_colorkey((0,0,0))
window.background = window.GREEN
SCREEN_WIDTH, SCREEN_HEIGHT = window.SIZE

GROUND_BLOCK = 10
FLOOR_BLOCK = 1


#load images
background = pygame.transform.scale(pygame.image.load(WINDOW.get_path('backgrounds/background_1.png')),window.SIZE)

# load tiles
tile_num = 16
tiles = []

for i in range(1,tile_num + 1):
	img = pygame.transform.scale(pygame.image.load(get_path(f'images/tiles/{theme}/{i}.png')).convert_alpha(),(46,46))
	if i in [12,16] : img = pygame.transform.flip(img,False,True)
	tiles += [img]

player_tile = pygame.transform.scale(pygame.image.load(f'images/player/Idle/1.png'),(46,92))
tiles += [player_tile]
tiles_1d = tiles.copy()

# create buttons
group_num = 4 # how many tiles in one row
buttons = []
tiles = [tiles[i:i+group_num] for i in range(0,len(tiles),group_num)] # grouping the tiles in a max of group_num

padding = 5
for i in range(len(tiles)): # display the buttons in groups of group_num
	for j in range(len(tiles[i])):
		x = 1050 + (46 * (j)) + (padding*j)
		y = 46+ ((46) * (i)) + (padding*i)
		buttons += [Button(x,y,tiles[i][j],1,(j+1)+(i*group_num))]

def draw_bg(scroll):
	background_width = background.get_width()
	for i in range(4):
		window.screen.blit(background,((i * background_width) + scroll,0))

def draw_grid(scroll):
	tiles_x, tiles_y = window.TILE_DIMENSION_X,window.TILE_DIMENSION_Y
	lines_x = background.get_width()//tiles_x
	lines_y = background.get_height()//tiles_y

	#vertical lines
	for j in range(window.MAX_BLOCKS_X + 1):
		x=(j*tiles_x)
		pygame.draw.line(window.screen,(200,200,200),(x + scroll,0),(x + scroll,background.get_height()))

	#horizontal liens
	for i in range(lines_y + 1):
		y = (i*tiles_y)
		pygame.draw.line(window.screen,(200,200,200),(0 + scroll,y),(SCREEN_WIDTH*4+scroll,y))

#draw map
def draw_map(scroll,arr):
	for y,row in enumerate(arr):
		for x,tile in enumerate(row):
			if tile == -1:
				continue
			window.screen.blit(tiles_1d[tile],(x*46 + scroll,y*46))

# load level
def load_level(level):
	level_path = f'levels/level{level}.txt'
	array = []
	if not get_path(level_path): return generate_new_map()
	with open(level_path,'r') as file:
		data = file.read().replace('\n','')
		array = [*eval(data)] # turns the data into a 2d array and converts all info to integers without having to do extra steps
	return array

# save level
def save_level(level,arr): #iterative development: ask if the user is sure they wanna overwrite a pre-made level
	# print('save')
	with open(f'levels/level{level}.txt','w+') as file:
		file.write(','.join(str(i) for i in arr))
		# for j in map_array:
		# 	file.write(str(j))
def generate_new_map():
	default_arr = [[-1 for i in range(window.MAX_BLOCKS_X)] for j in range(window.BLOCKS_Y)]
	default_arr[-1] = [GROUND_BLOCK for j in range(window.MAX_BLOCKS_X)]
	default_arr[-2] = [FLOOR_BLOCK for j in range(window.MAX_BLOCKS_X)]
	return default_arr.copy()

def draw_outline(scroll):
	x,y = pygame.mouse.get_pos()
	x,y = 46*(x//46),46*(y//46)
	# pygame.draw.rect(window.screen,(255,0,0),(x-(scroll,y,46,46),2)


def main():
	#game variables
	window.alpha_counter=0
	scroll_left = scroll_right = False
	scroll = 0
	scroll_speed = 1
	scroll_x = 5

	current_tile = 0

	save_button = Textbox(1020,500,'Save','medlarge',size=(80,40),padding=(5,10))
	load_button = Textbox(1110,500,'Load','medlarge',size=(80,40),padding=(5,10))
	save_button.create_rect()
	load_button.create_rect()

	map_array = generate_new_map()
	level = 1

	x=0

	while True:
		window.refresh()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				return

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					scroll_left = True
				if event.key == pygame.K_RIGHT:
					scroll_right = True
				if event.key == pygame.K_LSHIFT:
					scroll_speed = 20
				if event.key == pygame.K_UP:
					level += 1
				if event.key == pygame.K_DOWN:
					level = max(level-1,1)
				if event.key == pygame.K_r: # r key maps to resetting the map
					map_array = generate_new_map()

			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT:
					scroll_left = False
				if event.key == pygame.K_RIGHT:
					scroll_right = False
				if event.key == pygame.K_LSHIFT:
					scroll_speed = 2

			if event.type == pygame.MOUSEBUTTONDOWN:
				if save_button.check_click(pygame.mouse.get_pos()):
					save_level(level,map_array)

				if load_button.check_click(pygame.mouse.get_pos()):
					loaded_level = load_level(level)
					if loaded_level:
						map_array = loaded_level

		#scroll the map
		if scroll_left:
			scroll = min(0, scroll + scroll_x * scroll_speed)
			# if ( scroll + 5 * scroll_speed <= 0):
			# 	scroll += 5 * scroll_speed
			# else: scroll = 0
		if scroll_right: # and ((scroll - 5 * scroll_speed) >= -(28*3*46)-5)
			scroll = max(scroll - scroll_x * scroll_speed, -(28*3*46) - 6*46 - 2)
			# if (scroll > -(28*3*46) - 6*46):
			# 	scroll -= 5 * scroll_speed
			# else:
			# 	scroll = -28*3*46 - 6*46

		#draw background
		draw_bg(scroll)
		draw_grid(scroll)
		draw_map(scroll,map_array)
		draw_outline(scroll)

		#draw rectangle area for tiles selection
		pygame.draw.rect(window.screen,window.GREEN,(1012,0,6*46,window.HEIGHT))

		# draw buttons
		button_count = 0 # default selected button
		for button_count,button in enumerate(buttons):
			if button.draw(window.screen):
				current_tile = button_count

		# highlight selected tile by drawing a rectangle at the same position and dimensions as the selected button
		pygame.draw.rect(window.screen,(255,0,0),buttons[current_tile].rect,2)

		# add tiles to map
		mouse_press = pygame.mouse.get_pressed()

		if mouse_press[0] or mouse_press[2]: # if left or right mousebutton have been clicked
			x,y = pygame.mouse.get_pos()
			if x < 1012: # making sure that the user has clicked on grid and not area for buttons
				arr_x = (x-scroll)//46
				arr_y = y//46

				if mouse_press[0]:
					map_array[arr_y][arr_x] = current_tile

				if mouse_press[2] or pygame.key.get_pressed()[pygame.K_d]:
					map_array[arr_y][arr_x] = -1

		# blit save and/or load level text
		save_button.check_hover()
		load_button.check_hover()

		save_button.show(window.screen)
		load_button.show(window.screen)

		# window.screen.blit(player[int(x)%len(player)],(500,500))
		x+=0.099
		# draw level
		window.draw_text(f'level:{level}',(1200,500),'medlarge')
		window.draw_text('Press UP or DOWN keys to change levels',(1020,550),'small')
		window.draw_text('Press [ r ] key to reset the level',(1055,570),'small')

		# alpha_counter += 1
		pygame.display.update()
		clock.tick(FPS)

if __name__ == '__main__':
	main()
