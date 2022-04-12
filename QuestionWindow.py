import os, sys, pygame, WINDOW, random
from boxes import Textbox
from entity_class import BoxGroup


class QuestionBox(Textbox):
    LARGE_FONT = pygame.font.SysFont('Sans', 35)
    MEDLARGE_FONT = pygame.font.SysFont('Sans', 30)
    MEDIUM_FONT = pygame.font.SysFont('Sans', 25)
    SMALL_FONT = pygame.font.SysFont('Sans', 15)

    incorrect_color = (204, 51, 0)
    correct_color = (51, 153, 51)

    def __init__(self, x, y, size, obj_type, text='', font_size='MEDIUM'):
        self.obj_type = obj_type
        self.x, self.y = x, y
        self.rect = pygame.Rect(x, y, *size)
        self.surface = pygame.Surface(self.rect.size)
        self.background = Textbox.BACKGROUND
        text_rect_size = [*map(lambda i: i*0.9,self.rect.size)] # create a padding for where the text will be placed
        # calculate the offset of where the text rectangle will be placed
        dx = (self.rect.w - text_rect_size[0])//2
        dy = (self.rect.h - text_rect_size[1])//2
        self.text_rect = pygame.Rect((self.rect.x + dx, self.rect.y + dy, *text_rect_size))
        self.font = eval(f"self.{font_size}_FONT")
        self.surf = None
        self.text=text
        self.border_color = None
        self.add_text(text)

    def show(self, surface):
        # self.surface.fill(self.background)
        pygame.draw.rect(self.surface, self.background, (0, 0, self.rect.w, self.rect.h))
        if self.border_color: # if there is a border color
            pygame.draw.rect(self.surface, self.border_color, (0, 0, self.rect.w, self.rect.h), 1)
        # pygame.draw.rect(self.surface, self.border_color, (self.text_rect.x-self.rect.x, self.text_rect.y-self.rect.y, self.text_rect.w,self.text_rect.h),1)
        surface.blit(self.surface,(self.rect.topleft))
        if self.surf:
            surface.blit(self.surf, self.text_rect.topleft)

    # this allows text to fit in a specified box.
    def add_text(self, text, delay=False):
        text = text.split() # split all the words
        # modification variables
        add_y = 0
        widths = 0
        # text variables
        pointer = 0
        letter_count = 0
        height = self.font.render('h',1,(255,255,255)).get_rect().height
        self.surf = pygame.Surface(self.text_rect.size, pygame.SRCALPHA, 32)
        self.surf.convert_alpha()

        if self.obj_type == 'button' and len(text)==1:
            rendered = self.font.render(text[0],1,(255,255,255))
            self.surf.blit(rendered,(0,0))
            return

        # to evaluate: this can go on forever if the box is too small for all of the text to fit in
        while pointer <= len(text) - 1:
            temp = self.surf.copy() # create a temporary surface where letters will be blitted
            font_letters = []
            for letter in text[pointer]:
                font_letters += [self.font.render(letter, 1, (255, 255, 255))]

            for letter in font_letters:
                rect = letter.get_rect()
                if not letter_count: # if the row has no letters (if its the first letter)
                    proposed_x, proposed_y = 5, add_y * height
                    letter_count+=1
                    widths = 5 # initial padding from the side of rectangle
                else:
                    proposed_x = widths # sum all the widths + padding of previous letters
                    proposed_y = add_y * height

                    # if adding a character of a word will overflow, add the whole word to the next line
                    if proposed_x + rect.w > self.text_rect.w:
                        add_y += 1 # increasing the y
                        widths = 1 # resetting the widths to 1
                        letter_count = 0 # reset the letter count on the row
                        break # repeat the process again for this word but on a new line

                temp.blit(letter, (proposed_x, proposed_y)) # blit it on the temp surface
                widths += rect.w + 1 # +1 is for the padding between letters

            else: # if the loop finished iterating meaning that all letters were successfully blitted
                if letter_count: # if there is a first character on the row
                    # self.surf.blit(self.font.render('   ',1,(255,255,255)), (proposed_x, proposed_y))
                    widths += 10 # this is the "space" between each word
                pointer += 1 # once a word has finished blitting, move onto the next one
                self.surf = temp.copy() # if a word was fully blitted, then add it onto the main canvas/surface

    def check_hover(self, mouse_pos=0):
        # if the mouse position is over the rectangle, change color, otherwise change it back to normal
        if self.obj_type != 'question':
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.background = self.hover_color
                self.border_color = (0, 0, 255)
            else:
                self.background = self.background_color
                self.border_color = None

    def check_click(self, mouse_pos=0):
        if self.obj_type != 'question':
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos) and (pygame.mouse.get_pressed()[0]):
                return self

def StartQuestion(question, question_data):
    # ---------- key variables -------------#
    pygame.init()
    x, y = WINDOW.x, WINDOW.y
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"
    FPS = 60
    clock = pygame.time.Clock()
    window = WINDOW.Display(new_window=True, caption='Question Display', size=(1000, 500))
    w, h = window.width, 200

    text = question
    options = question_data[question]['options']
    correct_answer = question_data[question]['options'][0] # correct answer will always be at first index
    question_box = QuestionBox(0, 0, (w, h*0.8), obj_type='question', text=text)

    left_shift = 0.1
    x1 = int(window.width*left_shift//4)
    width = 1-left_shift
    options = random.sample(options, 4) # select a random order from the options, shuffling the order of options
    option_w, option_h = (w*width//2,(window.height-h)//2)

    # creating all the option instances, and positioning them respectively
    option_1=QuestionBox(question_box.rect.x + x1, question_box.rect.bottom + 10, (option_w, option_h), obj_type='option', text=options[0])
    option_2=QuestionBox(question_box.rect.center[0] + x1, question_box.rect.bottom + 10, (option_w, option_h), obj_type='option', text=options[1])
    option_3=QuestionBox(option_1.rect.left, option_1.rect.bottom + 15, (option_w, option_h), obj_type='option', text=options[2])
    option_4=QuestionBox(option_2.rect.left, option_2.rect.bottom + 15, (option_w, option_h), obj_type='option', text=options[3])
    main_group = BoxGroup(option_1, option_2, option_3, option_4, question_box)
    # feedback instance
    feedback_text = question_data[question]['feedback']
    feedback = QuestionBox(0,0,window.SIZE,text=feedback_text,obj_type='feedback',font_size='MEDIUM')

    main_continue = Textbox(100, 0.9*window.height,text='Continue',text_size='medlarge')
    feedback_continue = Textbox(100, 0.9*window.height,text='Continue',text_size='medlarge')
    options_screen = True
    result = False
    check_click = True
    move_to_feedback = 6000
    time1 = 0
    main_continue.create_rect()
    feedback_continue.create_rect()
    while True:
        window.refresh()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
                # sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                    pass

            if event.type == pygame.MOUSEBUTTONDOWN:
                # check for the continue button click on the main/ options screen
                if pygame.time.get_ticks() - time1 > move_to_feedback and time1 and options_screen: # wait a bit of time
                    if main_continue.check_click():
                        options_screen = False # don't display options anymore, signalling the feedback screen to show
                        if result: return result # if the answer was correct, then don't go to feedback screen

                # check for continue button click on the feedback screen
                if feedback_continue.check_click() and not options_screen:
                    return result

                clicked = main_group.check_clicks() # if an option has been clicked
                if clicked and check_click:
                    result = clicked.text==correct_answer # if the clicked option's text matches to the correct answer
                    time1 = pygame.time.get_ticks()
                    check_click = False # don't check for more clicks on any other options
                    for option in main_group.objects:
                        if option.text != correct_answer and option.obj_type!='question':
                            option.background_color = option.incorrect_color
                            option.hover_color = option.incorrect_color
                        else:
                            option.background_color = option.correct_color
                            option.hover_color = option.correct_color
                            move_to_feedback //= 2 # if they're right, move on to the next stage faster

        if options_screen:
            main_group.update_boxes(window.screen) # update the boxes (draw them) onto the screen

        elif not options_screen: # if an option has been picked, and it was incorrect show the feedback text
            feedback.show(window.screen) # show the feedback
            feedback_continue.show(window.screen)
            feedback_continue.check_hover(pygame.mouse.get_pos())
            feedback_continue.show(window.screen, center=True)

        # after a option is picked, and after a certain time, move to feedback screen, and display its continue button
        if pygame.time.get_ticks() - time1 > move_to_feedback and time1 and options_screen:
            main_continue.check_hover(pygame.mouse.get_pos())
            main_continue.show(window.screen, center=True)

        pygame.display.update()
        clock.tick(FPS)
