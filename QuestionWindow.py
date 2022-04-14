import os, sys, pygame, WINDOW, random
from boxes import Textbox, DynamicBox
from boxes import BoxGroup
from transition import ScreenFade

def StartQuestion(question, question_data,timer=0,x1=None):
    # ---------- key variables -------------#
    pygame.init()
    x, y = WINDOW.x, WINDOW.y
    Display = WINDOW.Display
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"
    FPS = 60
    clock = pygame.time.Clock()
    window = WINDOW.Display(new_window=True, caption='Question Display')
    w, h = window.width, 200

    text = question
    options = question_data[question]['options']
    correct_answer = question_data[question]['options'][0] # correct answer will always be at first index of options
    question_box = DynamicBox(0, 0, (w, h*0.8), obj_type='question', text=text)

    left_shift = 0.1
    x1 = int(window.width*left_shift//4)
    width = 1-left_shift
    options = random.sample(options, 4) # select a random order from the options, shuffling the order of options
    option_w, option_h = (w*width//2,(window.height-h)//2)

    # creating all the option instances, and positioning them respectively
    option_1=DynamicBox(question_box.rect.x + x1, question_box.rect.bottom + 13.3, (option_w, option_h), obj_type='option', text=options[0])
    option_2=DynamicBox(question_box.rect.center[0] + x1, question_box.rect.bottom + 13.3, (option_w, option_h), obj_type='option', text=options[1])
    option_3=DynamicBox(option_1.rect.left, option_1.rect.bottom + 13.3, (option_w, option_h), obj_type='option', text=options[2])
    option_4=DynamicBox(option_2.rect.left, option_2.rect.bottom + 13.3, (option_w, option_h), obj_type='option', text=options[3])
    main_group = BoxGroup(option_1, option_2, option_3, option_4, question_box)
    # feedback instance
    feedback_text = question_data[question]['feedback']
    feedback = DynamicBox(0,4,(window.SIZE[0],window.SIZE[1]-4),text=feedback_text,obj_type='feedback',font_size=30,center_text=False,color=Display.BACKGROUND)

    main_continue = Textbox(100, 0.9*window.height,text='Continue',text_size='medlarge')
    feedback_continue = Textbox(100, 0.9*window.height,text='Continue',text_size='medlarge')
    options_screen = True
    result = False
    check_click = True
    move_to_feedback = 6000 # the time to wait until moving onto feedback screen
    time1 = 0
    main_continue.create_rect()
    feedback_continue.create_rect()
    start_fade = True
    fade = ScreenFade(1, (0, 0, 0))
    going_back = False
    x1 = x1
    timer = timer
    paused = False
    while True:
        window.refresh()
        for event in pygame.event.get():
            if event.type == pygame.QUIT and 1==2:
                pygame.quit()
                return timer
                # sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return timer

            if event.type == pygame.MOUSEBUTTONDOWN:
                # check for the continue button click on the main/ options screen
                if pygame.time.get_ticks() - time1 > move_to_feedback and time1 and options_screen: # wait a bit of time
                    if main_continue.check_click():
                        options_screen = False # don't display options anymore, signalling the feedback screen to show
                        if result: # if they were right, then go back immediately, don't go to feedback screen
                            going_back = True
                            start_fade = True
                            options_screen = True

                # check for continue button click on the feedback screen
                if feedback_continue.check_click() and not options_screen:
                    start_fade = True
                    going_back = True

                clicked = main_group.check_clicks() # if an option has been clicked
                if clicked and check_click:
                    result = clicked.text == correct_answer # check if the clicked option's text matches to the correct answer
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
                        option.check_collision = False
                        paused=True

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
            for box in main_group.get_list():
                if box.obj_type =='question':
                    continue
                box.surface.set_alpha(150)

        if start_fade: # do the fade animation
            if going_back:
                fade.direction = -1 # fading out
            if fade.fade(window.screen):
                start_fade = False
                if going_back: # if they're exiting the question screen
                    return result, timer

        if (pygame.time.get_ticks() - x1) >= 1000 and not paused: # 1 ticks == 1 millisecond, 1000 millisecond = 1 second, update timer every second
            timer += 1  # account for the time in the question screen
            x1 = pygame.time.get_ticks()
        window.draw_text(text=f'Time: {WINDOW.convert_time_format(timer)}', pos=(670,3), size='MEDIUM',center=True)
        pygame.display.update()
        clock.tick(FPS)

