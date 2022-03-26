try:
    import pygame,os
    from WINDOW import Display
    from boxes import Textbox, Inputbox
    import re,json
    import WINDOW
except ImportError as error:
    print(error)
x,y = WINDOW.x,WINDOW.y
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"


pygame.init()
clock = pygame.time.Clock()

def get_path(path):
    absolute_path = os.path.abspath(path)
    assert os.path.exists(absolute_path), f"{path} doesn't exist"
    return absolute_path

background = get_path('images/logo.png')
window = Display(caption='Main Menu',size=(1426, 690),arrow_pos=(525,515))
image = pygame.image.load(background)
background = pygame.transform.scale(image,(1426, 690))
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
def check_details(username,password,state):
    data = read('user_info/users.json')

    if state=='login':
        if data.get(username) == password:return 1
        return -1
    elif state=='sign up':
        if username in data.keys():return -1
        else: data[username] = password; write(data,'user_info/users.json');return 1
    return 0

    write(data,'user_info/users.json')


def validate_character(string,click,character):
    # Only allow characters, numbers and certain symbols
    valid_chars = (re.match('''[A-Za-z0-9]{1,15}[-!$%^&*()_+|~=`{}\[\]:";'<>?,.\/]*''',character))
    # return True if the username as long as the length is 
    # < 15 and typing in the username box
    return (len(string)<15 and (click) and bool(valid_chars))

def validate_info(string):
    return (4 <= len(string) <= 15)

def input_information(state):
    max_length=15
    
    username = ''
    password = ''
    fill_text = 'Username'
    fillpass_text = 'Password'

    counter = 0
    username_click = False
    password_click = False
    
    random_box = Inputbox(100,200,text='j',text_size='medlarge',padding=(0,0),limit=False)
    
    username_box = Inputbox(100,460,text=fill_text.center(15),text_size='medlarge',padding=(0,0),size=(300,60))
    password_box = Inputbox(100,530,text=fillpass_text.center(15),text_size='medlarge',size=(300,60))

    continue_button = Textbox(100,635,text='Continue',size=(150,50),text_size='medlarge')
    continue_button.create_rect()
    continue_click = False

    incorrect_details = False

    continue_state = False#

    display_string_length = False

    successful_signUp = successful_login = False

    delete = False

    delete_counter = 0

    while True:
        window.refresh(back=True)

        username_box.text=fill_text
        password_box.text=fillpass_text

        username_box.create_rect()
        password_box.create_rect()
        continue_button.create_rect()

        continue_state = username and password # checks if both fields have an input in them

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            if event.type == pygame.KEYDOWN: # handle key presses
                if username_click or password_click:
                    incorrect_details = False # removes the error message if user has clicked/ is typing in an inputbox

                character = event.unicode # collect the string format of the key pressed
                
                if event.key==pygame.K_BACKSPACE:
                    incorrect_details = False # remove the error message if it is present
                    delete = True
                    continue # a backspace isn't a valid 'character' that can be added to username and password, therefore

                # only add to username and/or password if the character is valid
                if validate_character(username,username_click,character): username += character
                if validate_character(password,password_click,character): password += character

            if event.type == pygame.KEYUP:
                if event.key==pygame.K_BACKSPACE:
                    delete=False
                    delete_counter = 0
                    if username_click:username=username[:-1]
                    if password_click:password=password[:-1]
                    random_box.text = random_box.text[:-1]

            if event.type == pygame.MOUSEBUTTONDOWN: # check which button has been clicked
                mouse_pos = pygame.mouse.get_pos()

                go_back = window.check_return(mouse_pos)
                if go_back:
                    return

                username_click = username_box.check_click(mouse_pos)
                password_click = password_box.check_click(mouse_pos)
                continue_click = continue_button.check_click(mouse_pos) and continue_state # checking if continue button is available and also clicked

                if username_click or password_click:
                    incorrect_details = display_string_length = successful_signUp = False

        if incorrect_details and state=='login':
            window.draw_text(text='Incorrect username or password',pos=(window.screen.get_width()//2 - 175,590),color=(255,0,0),size='MEDLARGE')
        
        elif incorrect_details and state=='sign up':
            window.draw_text(text='Username already taken',pos=(window.screen.get_width()//2 - 130,590),color=(255,0,0),size='MEDLARGE')

        elif display_string_length and state == 'sign up':
            window.draw_text(text='Username and Password must be between 4 and 15 characters long',pos=(window.screen.get_width()//2 - 380,590),color=(255,0,0),size='MEDLARGE')

        elif successful_signUp:
            window.draw_text(text='New user has been signed up',pos=(window.screen.get_width()//2 - 160,590),color=(0,255,0),size='MEDLARGE')
            # pygame.time.delay(60)
            # return 1
        if successful_login:
            return 1

        if continue_state: # if the username and password fields are filled make the continue button brighter
            continue_button.surface.set_alpha(300)
        else:
            continue_button.surface.set_alpha(100)

        if delete:
            delete_counter += 1
        else:
            delete_counter = 0

        if delete_counter > 8 and (delete_counter%2)==0: # allows for singular + held down deletion
            if username_click:username=username[:-1]
            if password_click:password=password[:-1]
            random_box.text = random_box.text[:-1]
        
        if not username: # if nothing has been typed in the username box, it should display 'Username'
            fill_text='Username'
        if not password:# if nothing has been typed in the username box, it should display 'Password'
            fillpass_text = 'Password'

        if username_click: # if the the user has chosen to type in the username field highlight the border 
            username_box.set_properties(border=username_box.GREEN)
            fill_text = username
        else:
            username_box.set_properties(border=username_box.BORDER)

        if password_click: # if the user has chosen to type in the password field hightlight the border
            password_box.set_properties(border=password_box.GREEN)
            fillpass_text = '*'*len(password) # cover the characters in the password
        else:
            password_box.set_properties(border=password_box.BORDER)
            
        if continue_click: # if the continue button has been pressed
            valid_username = validate_info(username)
            valid_password = validate_info(password)
            
            if (not(valid_username) or not(valid_password)) and state=='sign up':
                display_string_length = True
                incorrect_details = False

            else:
                display_string_length = False
                correct = check_details(username,password,state)
                incorrect_details = correct < 1
                if not(incorrect_details) and state == 'sign up':
                    successful_signUp = True
                elif not(incorrect_details) and state == 'login':
                    successful_login = True

            continue_click = False # once the button has been pressed, it should be counted as 'not pressed' after this section is ran


            # if not incorrect_details: return 1

        if username_box.rect.width > 290: 
            username=username[:-1]
        if password_box.rect.width > 290:
            password=password[:-1]

        mouse_pos = pygame.mouse.get_pos()
        username_box.check_hover(mouse_pos)
        password_box.check_hover(mouse_pos)
        if continue_state: continue_button.check_hover(mouse_pos)
        
        # Display username and password boxes    
        username_box.show(window.screen, center=True)
        password_box.show(window.screen, center=True)
        continue_button.show(window.screen, center=True)
        # random_box.show(window.screen)

        counter += 1
        window.blit(window.screen,(0,0))
        pygame.display.update()
        clock.tick(30)
