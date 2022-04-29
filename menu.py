import pygame, os, re, sys, WINDOW, game_level
from boxes import Textbox
from boxes import BoxGroup, AutoBox
from transition import ScreenFade
import matplotlib.pyplot as plt
pygame.init()

x, y = WINDOW.x, WINDOW.y
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"

FPS = 60
clock = pygame.time.Clock()
window = WINDOW.Display(new_window=True)

topic_num = {
        'Systems Architecture':"1.1",
        'Software and Software development': "1.2",
        'Exchanging Data': "1.3",
        'Data types, Data structures, and Algorithms': "1.4",
        'Elements of Computational thinking, Problem solving, and programming': "2"
    }

def get_topic_number(topic):
    return topic_num.get(topic)

def show_leaderboards(surface, user_data) -> None:
    sum_points = lambda user: sum(user_data[user]['points'])
    user_points = [[username, sum(user_data[username]['points'])] for username in user_data] # create a 2D array with [[username,points] for each user]
    top_ten = WINDOW.bubble_sort2D(user_points)[:10] # highest -> lowest of the top 10
    font = pygame.font.SysFont('Sans', 30)
    longest_name = font.render('W'*15, 1, (255, 255, 255)).get_rect()  # longest name's data
    padding_y = 20
    padding_x = longest_name.width + 20
    start_x = (window.WIDTH - padding_x) // 2
    start_y = (window.HEIGHT - (padding_y * 6) - longest_name.height * 10) // 2  # position all names to the vertical center

    # draw text username and points titles
    username = font.render('Username', 1, (255, 255, 255))
    points = font.render('Points',1,(255,255,255))
    surface.blit(username, (start_x, 60))
    surface.blit(points, (start_x+padding_x - 20 ,60))
    pygame.draw.line(surface, (255,255,255),(start_x-13,65+username.get_height()),(start_x+padding_x+points.get_width()-10,65+username.get_height()))

    # draw the actual values for each user
    for i in range(len(top_ten)):
        rendered_name = font.render(top_ten[i][0], 1, (255, 255, 255))
        rendered_points = font.render(str(top_ten[i][1]), 1, (255, 255, 255))
        surface.blit(rendered_name, (start_x, (padding_y * i) + (longest_name.height * i) + start_y))
        surface.blit(rendered_points, (start_x + padding_x, (padding_y * i) + (longest_name.height * i) + start_y))

def get_graph(username) -> None:
    user_data = WINDOW.read_json('user_info/users.json')
    points = user_data[username]['points']
    start_x, end_x = 1, len(points)
    plt.rcParams["figure.figsize"] = (9.4,6)
    if len(points) > 20:

        start_x = len(points) - 19
        end_x = len(points)
        points = points[-20:]
    x_range = range(start_x, end_x + 1)
    # points = [sum(points[:i]) for i in range(1,len(points))] # cumulative points
    color = 'black'
    fig, axis = plt.subplots(nrows=1,ncols=1) # just one graph

    plt.xticks(x_range, color=color)
    plt.yticks(range(min(points),max(points) + 10,10),color=color)
    axis.plot(list(x_range), points, marker='.')
    plt.xlabel('Session', color=color)
    plt.ylabel('Points', color=color)

    plt.title('Points Gained At Each Attempt')
    plt.savefig('images/points.png') # save the image of the graph in a png file, which will then be loaded and blitted
    # plt.show()

def get_accuracy(question_data, username) -> str:
    total_attempted = 0
    accuracy = 0
    for question in question_data:
        stats = question_data[question][username]
        attempts = stats[0] + stats[1]
        if attempts > 0: # if attempts were made
            total_attempted += 1
            accuracy += stats[2] # the index that points to the accuracy

    if total_attempted: # making sure denominator is not 0, and that they have attempted questions
        accuracy = (accuracy/total_attempted)*100

    if total_attempted: # if they've answered at least one question and got it right/wrong
        accuracy = str(round(accuracy, 2))+'%'
    else:
        accuracy = 'N/A'

    return accuracy

def get_topic_boxes(username, user_data) -> list:
    default_message = 'Achieve 100% accuracy and enter the portal in the level to unlock'
    topics = []
    row_1 = ['Systems Architecture', 'Software and Software development', 'Exchanging Data']
    row_2 = ['Data types, Data structures, and Algorithms',
             'Elements of Computational thinking, Problem solving, and programming']

    accuracy_1 = []
    for topic in row_1:
        topic_number = get_topic_number(topic)
        question_data = WINDOW.read_json(f'Questions/{topic_number}.json')
        accuracy_1.append(get_accuracy(question_data,username))

    accuracy_2 = []
    for topic in row_2:
        topic_number = get_topic_number(topic)
        question_data = WINDOW.read_json(f'Questions/{topic_number}.json')
        accuracy_2.append(get_accuracy(question_data, username))

    # arrange topic selection
    width1 = 430
    padding1 = (window.WIDTH - 3 * width1) // 4
    for i in range(3):
        current_time = user_data[username][get_topic_number(row_1[i])]
        if current_time == -1:
            current_time = default_message
        else:
            current_time = WINDOW.convert_time_format(current_time)
        topics.append(
            AutoBox(padding1 * i + (width1 * i) + padding1, 200, (width1, 0.4 * width1), row_1[i], text=row_1[i]+f' \\n \\n Accuracy: {accuracy_1[i]}  \\n Best Time: {current_time}',center_text=(False,True),font_size=22))

    width2 = 520
    padding2 = (window.WIDTH - 2 * width2) // 3
    padding_y = 200

    for j in range(2):
        current_time = user_data[username][get_topic_number(row_2[j])]
        if current_time == -1:
            current_time = default_message
        else:
            current_time = WINDOW.convert_time_format(current_time)
        topics.append(AutoBox(padding2 * j + (width2 * j) + padding2, topics[1].rect.h + padding_y + padding1,(width2, 0.35 * width2), row_2[j], text=row_2[j]+f' \\n \\n Accuracy: {accuracy_2[j]}  \\n Best Time: {current_time}',center_text=(False,True),font_size=22))
    return topics

def show_graph(surface, graph_img):
    img_rect = graph_img.get_rect()
    surface.screen.blit(graph_img, ((surface.WIDTH - img_rect.w)//2, (surface.HEIGHT - img_rect.h)//2))

def show_instructions(surface):
    instructions = pygame.image.load('images/instructions.png')
    surface.screen.blit(instructions, (0, 0))

def show_menu(username) -> None:
    user_data = WINDOW.read_json('user_info/users.json')
    topics = get_topic_boxes(username, user_data)
    rec = topics[2].rect
    username_width = AutoBox.MEDIUM_FONT.render(f'username: {"W"*15}', 1, (255, 255,255)).get_width() + 42  # finding out the maximum width for a username since 'W' is largest width character

    username_box = AutoBox(rec.x + (rec.w - username_width)//2, 40, (username_width, topics[1].rect.h // 2), 'username',text=f'Username: {username} \\n Points: {sum(user_data[username]["points"])}', font_size=23, center_text=(False,True))

    width = AutoBox.MEDIUM_FONT.render(f'Leaderboards', 1, (255, 255, 255)).get_width() * 1.3
    rec = topics[1].rect # the 2nd topic's rect
    # position the leaderboards box at the centered x position relative to the 2nd topic box
    leaderboard_box = AutoBox(rec.x + (rec.w - width)//2, 40, (width, topics[1].rect.h // 2), 'leaderboard',text='Leaderboards', center_text=(True,True))
    instructions_box = AutoBox(leaderboard_box.rect.x - width - 200, 40, (width, topics[1].rect.h // 2), 'instructions',text='How-To-Play', center_text=(True,True))
    all_boxes = BoxGroup(*topics, username_box, leaderboard_box, instructions_box)
    leaderboards = False
    fade = ScreenFade(1,(0,0,0))
    screen_fade = True
    graph = False
    instructions = False
    back_pos = None
    while True:
        window.refresh(back=True, show_mouse_pos=True, pos=back_pos)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # check for button clicks
                clicked = all_boxes.check_clicks()

                # check for back click
                if window.check_return():
                    if leaderboards:
                        leaderboards = False
                    elif graph:
                        graph = False
                    elif instructions:
                        instructions = False
                        back_pos = None
                    else:
                        return

                elif bool(clicked): # if something was returned
                    corresponding_num = get_topic_number(clicked.obj_type)
                    if corresponding_num: # if the clicked box is a topic
                        game_level.play_level(username, 0, corresponding_num)
                        # update user information after a change has been made by finishing a level don't do it constantly
                        user_data = WINDOW.read_json('user_info/users.json')
                        username_box.update_text(f'Username: {username} \\n Points: {sum(user_data[username]["points"])}')
                        topics = get_topic_boxes(username,user_data) # updates the text_box size and text after user completes a level
                        all_boxes = BoxGroup(*topics, username_box, leaderboard_box, instructions_box)

                    elif clicked.obj_type == 'leaderboard':
                        leaderboards = True

                    elif clicked.obj_type == 'username':
                        graph = True
                        get_graph(username)

                    elif clicked.obj_type == 'instructions':
                        instructions = True

        if leaderboards:
            show_leaderboards(window.screen, user_data)

        elif graph:
            graph_img = pygame.image.load('images/points.png')
            show_graph(window, graph_img)
        elif instructions:
            show_instructions(window)
        else:
            all_boxes.update_boxes(window.screen)

        window.draw_back(back_pos)
        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    import random
    # show_menu(random.choice(list(WINDOW.read_json('user_info/users.json'))))
    show_menu('Harsh21')