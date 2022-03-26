#---------------------------------- Imports ----------------------------------#

try:
    import pygame,os
    from WINDOW import Display
    from boxes import Textbox, Inputbox
    import re,json
    from access import input_information
    import WINDOW
    from Game_files import Game_V4
except ImportError as error:
    print(error)

# lapto
x,y = WINDOW.x,WINDOW.y
# school computer
# x,y = 50,80
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"
#--------------------------------- Setting Up --------------------------------#

pygame.init()
clock = pygame.time.Clock()

def get_path(path):
    absolute_path = os.path.abspath(path)
    assert os.path.exists(absolute_path), f"{path} doesn't exist"
    return absolute_path

background = get_path('images/logo.png')
window = Display(caption='Main Menu',size=(1426, 690))
image = pygame.image.load(background)
background = pygame.transform.scale(image,window.SIZE)
window.background = background
#------------------------------ get/set details ------------------------------#
def read(path):
    details = get_path(path)
    with open(details,'r') as file:
        return json.load(file)

def write(data,path):
    details = get_path(path)
    with open(details,'w') as file:
        file.seek(0)
        json.dump(data,file)
#----------------------------------- Login -----------------------------------#

def validator(string,click,letter):
    # Only allow letters, numbers and certain symbols
    valid_chars = (re.match('''[A-Za-z0-9]{1,15}[-!$%^&*()_+|~=`{}\[\]:";'<>?,.\/]*''',letter))
    # return True if the username as long as the length is < 15 and typing in the username box
    return (len(string)<15 and (click) and bool(valid_chars))

#------------------------------- Main Game Loop ------------------------------#

def main():
    username_box = Textbox(100,460,'Login',text_size='medlarge',padding=(200,35),size=(300,60))
    signUp_box = Textbox(100,530,'Sign Up',text_size='medlarge',padding=(175,35),size=(300,60))

    login=sign_up=False

    signUp_result=login_result=0
    while True:
        window.refresh()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                login = username_box.check_click(mouse_pos)
                sign_up = signUp_box.check_click(mouse_pos)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

        mouse_pos = pygame.mouse.get_pos()
        username_box.check_hover(mouse_pos)
        signUp_box.check_hover(mouse_pos)

        username_box.show(window.screen,center=True)
        signUp_box.show(window.screen,center=True)

        if login:
            login_result = input_information(state='login')
            login = False

        elif sign_up:
            signUp_result = input_information(state='sign up')
            sign_up = False

        if signUp_result: # return them back to main menu
            pass

        if login_result:
            Game_V4.main(1)
            login_result = False


        pygame.display.update()
        clock.tick()

if __name__ == '__main__':
    main()
