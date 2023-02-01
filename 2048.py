import csv
import random
import time
from math import sqrt

import pygame
import keyboard
import matplotlib.pyplot as plt
import numpy as np

def init_grid():
    grid = np.ndarray(shape=(4, 4), dtype=np.int_)
    grid = np.zeros((4, 4), dtype=int)
    empty_array = np.where(grid == 0)
    x_empty_list = empty_array[0]
    y_empty_list = empty_array[1]
    random_index = np.random.randint(0, 15, 2)

    if random_index[0] == random_index[1] and random_index[0] < 15:
        random_index[1] += 1
    elif random_index[0] == random_index[1] and random_index[0] == 15:
        random_index[1] -= 1

    grid[x_empty_list[random_index[0]], y_empty_list[random_index[0]]] = 2
    grid[x_empty_list[random_index[1]], y_empty_list[random_index[1]]] = 2

    return grid

def add_new(grid):
    empty_array = np.where(grid == 0)
    x_empty_list = empty_array[0]
    y_empty_list = empty_array[1]
    len_list = len(x_empty_list)

    if len_list == 0:
        return (False)

    random_index = np.random.randint(0, len_list, 1)

    if random.randint(0, 100) > 80:
        grid[x_empty_list[random_index], y_empty_list[random_index]] = 4
    else:
        grid[x_empty_list[random_index], y_empty_list[random_index]] = 2

    return grid

def rollin_row(row):
    row = np.array(row)
    score = 0
    for i in range(0, 4):
        for j in range(i, 4):
            if row[i] == row[j] and i != j:
                if abs(i - j) == 1:
                    row[i] = row[i] + row[j]
                    row[j] = 0
                    score += row[i]
                    i = j
                if abs(i - j) > 1 and row[i + 1: j].any() == 0:
                    row[i] = row[i] + row[j]
                    row[j] = 0
                    score += row[i]
                    i = j
    row = decaler(row)
    return(row, score)

def decaler(row):
    k = 0
    while k < 3:
        if row[k] == 0:
            i = 3
            while i > k:
                if row[i] != 0 and row[i - 1] == 0:
                    row[i - 1] = row[i]
                    row[i] = 0
                i -= 1
        k += 1
    return row

def rollin(grid, direction):
    global rotate, rotate_reverse
    if direction == "gauche":
        rotate = 0
        rotate_reverse = 0
    elif direction == "bas":
        rotate = -1
        rotate_reverse = 1
    elif direction == "droite":
        rotate = 2
        rotate_reverse = -2
    elif direction == "haut":
        rotate = 1
        rotate_reverse = -1

    score = 0
    rollin_tuple = ()
    new_grid = np.zeros((4, 4))
    new_grid = np.rot90(grid, rotate)
    for i in range(0, 4):
        rollin_tuple = rollin_row(new_grid[i, :])
        new_grid[i, :] = rollin_tuple[0]
        score += rollin_tuple[1]
    new_grid = np.rot90(new_grid, rotate_reverse)
    new_grid = add_new(new_grid)
    return (new_grid, score)


def user_interface_2048():
    beige1 = (30, 70, 90)
    beige2 = (45, 75, 95)
    grey = (128, 128, 128)
    black = (255, 255, 255)
    white = (0, 0, 0)

    directions = {}
    directions = {"droite": 0, "haut": 0, "gauche": 0, "bas": 0}
    stop = False
    grid = np.ndarray(shape=(4, 4), dtype=int)

    rollin_tuple = ()
    game_data = []
    score_list = []
    nb_empty_cell_evolution = []

    nb_plays = 0
    score = 0

    # initiate pygame and give permission
    # to use pygame's functionality.
    pygame.init()

    # assigning values to X and Y variable
    X = 500
    Y = 500

    # create the display surface object of specific dimension..(X, Y).
    display_surface = pygame.display.set_mode((X, Y))
    # set the pygame window name
    pygame.display.set_caption('2048')

    grid = init_grid()
    start = time.time()

    game_data = ReadData_2048()
    for i in game_data:
        score_list.append(int(i['Score']))

    best_score = max(score_list)

    display_game(display_surface, grid, score, best_score)

    key_game = 'gauche'

    # infinite loop
    while True:
        if key_game == 'esc':
            end = time.time()
            game_time = int(end - start)
            game_data = ReadData_2048()
            game_data.append({'TempsdeJeu': game_time, 'Score': score, 'NombredeCoups': nb_plays})

            display_surface.fill(beige1)

            # Display a message when the game is finished
            font = pygame.font.SysFont('univers', 30)

            text = font.render("Votre score est de: " + str(score), True, black, beige1)
            textRect = text.get_rect()
            textRect.center = (250, 220)
            display_surface.blit(text, textRect)

            text = font.render("Cliquez sur Echap pour fermer", True, black, beige1)
            textRect = text.get_rect()
            textRect.center = (250, 270)
            display_surface.blit(text, textRect)

            # Draws the surface object to the screen.
            pygame.display.update()
            key_game = keyboard.read_key()

            StoreData_2048(game_data)
            Game_Data_Graph(game_data, directions, nb_empty_cell_evolution)

            if key_game == 'esc':
                # deactivates the pygame library
                pygame.quit()
                # quit the program.
                quit()

        else:
            key_game = keyboard.read_key()
            rollin_tuple = rollin(grid, keyboard.read_key())
            grid = rollin_tuple[0]
            score += rollin_tuple[1]

            if isinstance(grid, bool):
                key_game = 'esc'
            else:
                nb_empty_cell = 0
                for i in range(0, 4):
                    for j in range(0, 4):
                        if grid[i, j] == 0:
                            nb_empty_cell += 1

                nb_empty_cell_evolution.append([nb_plays, nb_empty_cell])

                nb_plays += 1

                if key_game in directions:
                    directions[key_game] += 1

                display_game(display_surface, grid, score, best_score)


def display_game(display_surface, grid, score, best_score):
    # define the RGB value for color
    beige2 = (128,128,128)
    beige1 = (169,169,169)
    grey = (192,192,192)
    black = (255, 255, 255)
    white_false = (0, 0, 0)

    # define the RGB value for each number of the grid
    dico_color_number = {'8': (255, 178, 102), '16': (229, 164, 86), '32': (187, 127, 68), '64': (164, 110, 56), '128': (141, 93, 45), '256': (119, 76, 34), '512': (96, 59, 22), '1024': (73, 42, 11), '2048': (51, 25, 0)}

    # create a font object.
    # 1st parameter is the font style which is present in pygame.
    # 2nd parameter is size of the font
    font = pygame.font.SysFont('univers', 35)

    # completely fill the surface object with a color
    display_surface.fill(grey)

    # display the score in the game's window
    # create a text object with a string, the color of the text and the color of his surface
    text = font.render("Score: " + str(score), True, black, grey)

    # create a rectangular object for the text surface object
    textRect = text.get_rect()

    # set the center of the rectangular object.
    textRect.topleft = (20, 20)

    # display the text on the surface
    display_surface.blit(text, textRect)

    # display the best score in the game's window
    text = font.render("Best score: " + str(best_score), True, black, grey)
    textRect = text.get_rect()
    textRect.topleft = (200, 20)
    display_surface.blit(text, textRect)

    # display the grid in the window's game
    for i in range(0, 4):
        for j in range(0, 4):
            if grid[i, j] == 0 or grid[i, j] == 2 or grid[i, j] == 4:
                text_color = (255, 165 ,0)
            else:
                text_color = dico_color_number[str(grid[i, j])]

            if len(str(grid[i, j])) <= 2:
                font = pygame.font.SysFont('univers', 80)
            elif len(str(grid[i, j])) == 3:
                font = pygame.font.SysFont('univers', 60)
            elif len(str(grid[i, j])) == 4:
                font = pygame.font.SysFont('univers', 45)

            if grid[i, j] != 0:
                if grid[i, j] <= 4:
                    text = font.render(str(grid[i, j]), True, text_color, beige2)
                    textRect = text.get_rect()
                    textRect.center = (100 + j * 100, 100 + i * 100)
                    pygame.draw.rect(display_surface, beige2, (60 + j * 100, 60 + i * 100, 80, 80), 0, 5)
                    display_surface.blit(text, textRect)
                else:
                    nb_rect = 0
                    grid_temp = grid[i, j]
                    while grid_temp / 2 != 1:
                        grid_temp = grid_temp / 2
                        nb_rect += 1

                    for k in range(0, nb_rect):
                        pygame.draw.rect(display_surface, white_false, ((60 - k) + j * 100, (60 - k) + i * 100, 80, 80), 0, 5)

                    text = font.render(str(grid[i, j]), True, text_color, beige2)
                    textRect = text.get_rect()
                    textRect.center = ((100 - nb_rect -1) + j * 100, (100 - nb_rect -1) + i * 100)
                    pygame.draw.rect(display_surface, beige2, ((60 - nb_rect - 1) + j * 100, (60 - nb_rect - 1) + i * 100, 80, 80), 0, 5)
                    display_surface.blit(text, textRect)

    pygame.display.update()


def ReadData_2048():
    with open('C:/Users/ouehb/OneDrive/Documents/Data_2048.txt', 'r', newline='') as csvfile:
        data_reader = csv.DictReader(csvfile, delimiter=',', quotechar="'")
        list_dict = []
        for row in data_reader:
            list_dict.append(row)
        return list_dict

def StoreData_2048(Data):

    with open('C:/Users/ouehb/OneDrive/Documents/Data_2048.txt', 'w', newline='') as csvfile:
        fieldnames = ['TempsdeJeu', 'Score', 'NombredeCoups']
        data_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        data_writer.writeheader()
        for i in Data:
            data_writer.writerow(i)

def Game_Data_Graph(game_data, directions, nb_empty_cell_evolution):

    #On créé 4 figures qu'on affiche dans une grille 2x2
    fig, ax = plt.subplots(2, 2)
    fig.suptitle('Statistiques 2048')

    # plot a first chart as the bar chart
    key_direction = ["droite", "haut", "gauche", "bas"]
    key_direction_value = [directions[key_direction[0]], directions[key_direction[1]], directions[key_direction[2]], directions[key_direction[3]]]
    bar_labels = ["droite", "haut", "gauche", "bas"]
    bar_colors = ['blue', 'green', 'red', 'orange']
    ax[0, 0].set_title('Coups par direction')
    ax[0, 0].set_ylabel('Nombre de coups')
    ax[0, 0].bar(key_direction, key_direction_value, label=bar_labels, color=bar_colors)

    # plot the second chart as a pie chart
    nb_push = 0
    for i in key_direction_value:
        nb_push += i

    ax[0, 1].set_title('Pourcentage par direction')
    explode = (key_direction_value[0] / (nb_push * 2.5), key_direction_value[1] / (nb_push * 2.5), key_direction_value[2] / (nb_push * 2.5), key_direction_value[3] / (nb_push * 2.5))
    ax[0, 1].pie(key_direction_value, explode=explode, shadow=True, labels=key_direction, autopct='%1.2f%%')

    # plot the third chart as a pie chart
    list_nb_coups = []
    list_nb_case_vide = []

    for i in nb_empty_cell_evolution:
        list_nb_coups.append(i[0])
        list_nb_case_vide.append(i[1])

    ax[1, 0].set_title('Nuage du nombre de cases vides')
    ax[1, 0].set_xlabel('Nombre de coups')
    ax[1, 0].set_ylabel('Nombre de cases vides')
    ax[1, 0].scatter(list_nb_coups, list_nb_case_vide)

    # plot the linear regression chart
    list_nb_coups2 = []
    list_score = []

    for stat_game in game_data:
        list_nb_coups2.append(int(stat_game['NombredeCoups']))
        list_score.append(int(stat_game['Score']))

    coeffs = np.polyfit(list_nb_coups2, list_score, 1)
    predictions = np.polyval(coeffs, list_nb_coups2)

    ax[1, 1].set_title('Tendance du score')
    ax[1, 1].scatter(list_nb_coups2, list_score)
    ax[1, 1].set_xlabel('Nombre de coups')
    ax[1, 1].set_ylabel('Score')
    ax[1, 1].plot(list_nb_coups2, predictions, color='red')

    # Display all the charts in the same figure
    plt.show()



user_interface_2048()