import pygame, os, re, sys, WINDOW, game_level
from boxes import Textbox
from boxes import BoxGroup, DynamicBox
from matplotlib.pyplot import plot as plt
pygame.init()

x, y = WINDOW.x, WINDOW.y
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"

FPS = 60
clock = pygame.time.Clock()
window = WINDOW.Display(new_window=True)

def show_leaderboards(surface, user_data):
    highest_points = lambda user: sum(user_data[user]['points'])
    top_ten = sorted(user_data, key=highest_points)[:10]
    font = pygame.font.SysFont('Sans',30)
    longest_name = font.render(max(top_ten, key=len), 1, (255, 255, 255)).get_rect()  # longest name
    most_points = font.render(max(top_ten, key=highest_points), 1, (255, 255, 255)).get_rect()
    padding_y = 20
    padding_x = longest_name.width + 20
    start_x = (window.WIDTH - padding_x - most_points.width) // 2
    start_y = (window.HEIGHT - (padding_y * 9) - longest_name.height * 10) // 2  # position all names to the vertical center

    for i in range(len(top_ten)):
        rendered_name = font.render(top_ten[i], 1, (255, 255, 255))
        rendered_points = font.render(str(sum(user_data[top_ten[i]]['points'])), 1, (255, 255, 255))
        surface.blit(rendered_name, (start_x, (padding_y * i) + (longest_name.height * i) + start_y))
        surface.blit(rendered_points, (start_x + padding_x, (padding_y * i) + (longest_name.height * i) + start_y))

def show_graph(username, user_data):
    pass

def show_menu(username):
    user_data = WINDOW.read_json('user_info/users.json')
    topics = []
    row_1 = ['Systems Architecture', 'Software and Software development', 'Exchanging Data']
    row_2 = ['Data types, Data structures, and Algorithms',
             'Elements of Computational thinking, Problem solving, and programming']

    # arrange topic selection
    width1 = 430
    padding1 = (window.WIDTH - 3 * width1) // 4
    for i in range(3):
        topics.append(
            DynamicBox(padding1 * i + (width1 * i) + padding1, 200, (width1, 0.4 * width1), 'topic', text=row_1[i]))

    width2 = 520
    padding2 = (window.WIDTH - 2 * width2) // 3
    padding_y = 200
    for j in range(2):
        topics.append(DynamicBox(padding2 * j + (width2 * j) + padding2, topics[1].rect.h + padding_y + padding1,(width2, 0.35 * width2), 'topic', text=row_2[j]))
    rec = topics[2].rect
    username_width = DynamicBox.MEDIUM_FONT.render(f'username: {username}', 1, (255, 255,255)).get_width() + 42  # finding out the maximum width for a username since 'W' is largest width character

    username_box = DynamicBox(rec.x + (rec.w - username_width)//2, 40, (username_width, topics[1].rect.h // 2), 'username',text=f'username: {username} \\n points: {sum(user_data[username]["points"])}', font_size=23, center_text=True)

    width = DynamicBox.MEDIUM_FONT.render(f'Leaderboards', 1, (255, 255, 255)).get_width() * 1.3
    rec = topics[1].rect # the 2nd topic's rect
    # position the leaderboards box at the centered x position relative to the 2nd topic box
    leaderboard_box = DynamicBox(rec.x + (rec.w - width)//2, 40, (width, topics[1].rect.h // 2), 'leaderboard',text='Leaderboards',center_text=True)

    all_boxes = BoxGroup(*topics, username_box, leaderboard_box)
    leaderboards = False
    print(user_data)
    while True:
        window.refresh(back=True, show_mouse_pos=True)
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
                if bool(clicked):
                    if clicked.obj_type == 'topic':
                        corresponding_num = WINDOW.topics[clicked.text]
                        game_level.play_level(username, 0, corresponding_num)

                    elif clicked.obj_type == 'leaderboard':
                        leaderboards = True

                # check for back click
                elif window.check_return():
                    if leaderboards:
                        leaderboards = False
                    else:
                        return
        if leaderboards:
            show_leaderboards(window.screen, user_data)
        else:
            all_boxes.update_boxes(window.screen)

        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    show_menu('Testing1')
