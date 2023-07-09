import pygame
import ctypes
#  === TCP 客户端程序 client.py ===
import time
from socket import *
import threading
import re

global pi_reg,pi_sure_flag,pi_row,pi_col,pi_flash,message,SOR,sure_flag,flash_flag,over_pos,regret_flag,over_flag

pi_sure_flag=re.compile(r'sure_f(\d)')
pi_row=re.compile(r'row(\d)')
pi_col=re.compile(r'col(\d)')
pi_flash=re.compile(r'flash(\d)')##刷新参数
pi_reg = re.compile(r'reg(\d)')
message= "sure_f0 row0 col0 flash0 SenOrRec0 reg0"
SOR = 1
sure_flag = 0
flash_flag = 0
regret_flag = 0
over_pos= []
# IP = '127.0.0.1'
IP ='192.168.2.95'
SERVER_PORT = 50000
BUFLEN = 1024

# 实例化一个socket对象，指明协议
dataSocket = socket(AF_INET, SOCK_STREAM)
global Send_Flag,Receive_Flag,current_player,previewImg,gameMode
Send_Flag = 0
Receive_Flag = 1
current_player = 'X'#服务端先下
gameMode = 0
send_row = 0
send_col = 0
# 连接服务端socket
dataSocket.connect((IP, SERVER_PORT))
# 初始化 pygame
pygame.init()

# 定义颜色
blue = (78, 140, 243)
light_blue = (100, 100, 255)
red = (242, 89, 97)
light_red = (255, 100, 100)
dark_grey = (85, 85, 85)
light_grey = (100, 100, 100)
background_color = (225, 225, 225)

# 创建窗口
screen = pygame.display.set_mode((600, 800))
pygame.display.set_caption('井字棋-客户端')

# 游戏图片
crossImg = pygame.image.load('Images/crossImg.png')
crossImg_rect = crossImg.get_rect()
crossImg_rect.center = (200, 300)
circleImg = pygame.image.load('Images/circleImg.png')
circleImg_rect = crossImg.get_rect()
circleImg_rect.center = (400, 300)
previewCrossImg = pygame.image.load('Images/prev_crossImg.png')
previewCircleImg = pygame.image.load('Images/prev_circleImg.png')
previewImg = previewCrossImg
# 按钮图片
restartImg = pygame.image.load('Images/restart.png')
restartHoveredImg = pygame.image.load('Images/restart_hovered.png')
ReGretImg = pygame.image.load('Images/button4Img.png')

# 定义棋盘
board = [['', '', ''],
         ['', '', ''],
         ['', '', '']]

# 定义计分板
score = {'X': 0, 'O': 0}
font = pygame.font.Font('freesansbold.ttf', 32)
X_score = pygame.image.load('Images/X_scoreImg.png')
O_score = pygame.image.load('Images/O_scoreImg.png')

# 菜单图片
buttom1 = pygame.image.load('Images/button1Img.png')
buttom1_rect = buttom1.get_rect()
buttom1_rect.center = (300, 312)
buttom2 = pygame.image.load('Images/button2Img.png')
buttom2_rect = buttom2.get_rect()
buttom2_rect.center = (300, 472)
buttom3 = pygame.image.load('Images/button3Img.png')
buttom3_rect = buttom3.get_rect()
buttom3_rect.center = (300, 632)
buttom4_rect = ReGretImg.get_rect()
buttom4_rect.center = (478, 751)
logo = pygame.image.load('Images/logo.png')

# 选择菜单图片
chooseImg = pygame.image.load('Images/choose.png')


def menu():
    global gameMode
    running = True
    while running:
        screen.fill(background_color)
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buttom1_rect.collidepoint((mx, my)):
                    gameMode= 0
                    game(0, 'X')
                elif buttom2_rect.collidepoint((mx, my)):
                    player = choose()
                    if player is not None:
                        gameMode= 1
                        game(1, player)
                elif buttom3_rect.collidepoint((mx, my)):
                    gameMode = 2
                    game(2, 'O')
        screen.blit(logo, (8, 25))
        screen.blit(buttom1, (100, 250))
        screen.blit(buttom2, (100, 410))
        screen.blit(buttom3, (100, 570))
        pygame.display.update()


def game(gameMode, player):
    global send_row, send_col, Send_Flag, Receive_Flag,row, col,current_player,previewImg,message,sure_flag,flash_flag,over,regret_flag
    my = player
    # player = current_player
    running = True
    if gameMode == 2:
        previewImg = previewCrossImg  # 服务端先下
    else:
        previewImg = previewCircleImg

    while running:
        mouse = pygame.mouse.get_pos()
        row, col = int(mouse[0] / 200), int(mouse[1] / 200)
        for event in pygame.event.get():
            if verifyWinner('O'):
                # player = 'O'
                # previewImg = previewCrossImg
                 pass
            if verifyWinner('X'):
                # player = 'X'
                # previewImg = previewCrossImg
                pass
            if event.type == pygame.QUIT:
                resetGame()
                running = False
            elif isBoardFull():
                ctypes.windll.user32.MessageBoxW(0, '平局', '提示', 0)
                resetBoard()
            elif gameMode == 1 and player != my:
                computerMove(player)
                drawBoard()
                pygame.display.update()
                if verifyWinner(player):
                    player = 'O'
                    previewImg = previewCrossImg
                else:
                    player, previewImg = updatePlayer(player)
            # elif gameMode == 2 and player != my:
            #     CounterMove(player)
            #     drawBoard()
            #     pygame.display.update()
            #     if verifyWinner(player):
            #         player = 'O'
            #         previewImg = previewCrossImg
            #     else:
            #         player, previewImg = updatePlayer(player)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if gameMode != 2:
                    if row < 3 and col < 3 and board[row][col] == '':
                        send_row = row
                        send_col = col
                        playerMove(player, row, col)
                        drawBoard()
                        # Send_Flag = 1
                        # time.sleep(0.5)
                        if verifyWinner('O'):
                            player = 'X'
                            previewImg = previewCrossImg
                        else :
                            player, previewImg = updatePlayer(player)
                    #
                    #     else:
                    #         Receive_Flag = 1
                    # elif 550 < mouse[0] < 582 and 610 < mouse[1] < 642:
                    #     resetGame()
                if gameMode == 2:
                    if row < 3 and col < 3 and board[row][col] == '':
                        print("Current_Player", current_player)
                    if row < 3 and col < 3 and board[row][col] == '' and current_player == 'O':#自己的回合鼠标才能点击
                        send_row = row
                        send_col = col
                        sure_flag =1
                        message = "sure_f" + str(sure_flag) + "row" + str(send_row) + " col" + str(
                            send_col) + "flash" + str(
                            flash_flag) + "reg" + str(regret_flag)
                        playerMove('O', row, col)
                        drawBoard()
                        current_player = 'X'#下完换对方
                        previewImg = previewCrossImg
                        regret_flag = 0
                        Send_Flag = 1
                        Receive_Flag = 1
                        print("I am going to send O message")
                        # time.sleep(0.5)
                        print("I am wating for message")
                        # if verifyWinner(player):
                        #     player = 'O'
                        #     previewImg = previewCrossImg
                        # elif gameMode != 2:
                        #
                    # else:
                    #         Receive_Flag = 1
                if 550 < mouse[0] < 582 and 610 < mouse[1] < 642:
                    flash_flag = 1
                    message = "sure_f" + str(sure_flag) + "row" + str(send_row) + " col" + str(
                        send_col) + "flash" + str(flash_flag) + "reg" + str(regret_flag)
                    resetGame()
                if buttom4_rect.collidepoint((mouse[0], mouse[1])):
                    if gameMode != 1:
                        print("悔棋一次")
                        lenth =len(over_pos)
                        if lenth > 0:
                            x = over_pos[lenth - 1][0]
                            y = over_pos[lenth - 1][1]
                            del over_pos[lenth-1]
                            if lenth == 1:
                                resetGame()
                            elif board[x][y] == "X":
                                print("regret x")
                                Current_Player = "O"
                                previewImg = previewCircleImg
                                board[x][y] = " "
                                drawBoard()
                            elif board[x][y] == "O":
                                print("regret o")
                                Current_Player = "X"
                                previewImg = previewCrossImg
                                board[x][y] = " "
                                drawBoard()
                            pygame.display.update()
                    if gameMode == 1:
                        print("按钮有效")
                        lenth =len(over_pos)
                        print("regret,computer1111")
                        if lenth > 1 and current_player == my:
                            print("regret,computer")
                            x1 = over_pos[lenth - 1][0]
                            y1 = over_pos[lenth - 1][1]
                            x2 = over_pos[lenth - 2][0]
                            y2 = over_pos[lenth - 2][1]
                            del over_pos[lenth-1]
                            del over_pos[lenth-2]
                            board[x1][y1]= ' '
                            board[x2][y2]= ' '
                            drawBoard()
                            pygame.display.update()
                    if gameMode == 2 :
                        print("regret.....in  ..here")
                        regret_flag = 1
                        message = "sure_f"+str(sure_flag) + "row" + str(send_row)+" col"+str(send_col) + "flash"+ str(flash_flag)+"reg"+str(regret_flag)
        screen.fill(background_color)
        drawBoard()
        drawBottomMenu(mouse)
        if row < 3 and col < 3:
            visualizeMove(row, col, previewImg)
        pygame.display.update()


def choose():
    player = None
    running = True
    while running:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if crossImg_rect.collidepoint((mouse[0], mouse[1])):
                    player = 'X'
                    running = False
                elif circleImg_rect.collidepoint((mouse[0], mouse[1])):
                    player = 'O'
                    running = False
        screen.blit(crossImg, (80, 300))
        screen.blit(circleImg, (340, 300))
        screen.blit(chooseImg, (8, 25))
        pygame.display.update()
    return player


def drawBoard():
    # 画棋子
    for row in range(3):
        for col in range(3):
            pos = (row * 200 + 12, col * 200 + 12)
            if board[row][col] == 'X':
                screen.blit(crossImg, pos)
            elif board[row][col] == 'O':
                screen.blit(circleImg, pos)
    # 画网格
    width = 10
    color = dark_grey
    pygame.draw.line(screen, color, (200, 0), (200, 600), width)
    pygame.draw.line(screen, color, (400, 0), (400, 600), width)
    pygame.draw.line(screen, color, (0, 200), (600, 200), width)
    pygame.draw.line(screen, color, (0, 400), (600, 400), width)
    # 画边框
    pygame.draw.rect(screen, color, (0, 0, 10, 600))
    pygame.draw.rect(screen, color, (0, 0, 600, 10))
    pygame.draw.rect(screen, color, (590, 0, 10, 600))


def drawBottomMenu(mouse):
    pygame.draw.rect(screen, dark_grey, (0, 600, 600, 100))
    pygame.draw.rect(screen, light_grey, (10, 610, 580, 80))
    screen.blit(restartImg, (550, 610))
    screen.blit(ReGretImg,(400,720))
    # Hover animation
    if 550 < mouse[0] < 582 and 610 < mouse[1] < 642:
        screen.blit(restartHoveredImg, (548, 608))
    screen.blit(X_score, (200, 610))
    screen.blit(O_score, (370, 610))
    scoreboard = font.render(': %d x %d :' % (score['X'], score['O']), True, background_color, light_grey)
    screen.blit(scoreboard, (244, 610))


def visualizeMove(row, col, previewImg):
    if board[row][col] == '':
        screen.blit(previewImg, (row * 200 + 12, col * 200 + 12))


def playerMove(player, row, col):
    board[row][col] = player
    over_pos.append((row,col))

def computerMove(player):
    global  over_pos
    bestScore = float('inf')
    for row in range(3):
        for col in range(3):
            if board[row][col] == '':
                board[row][col] = 'O'
                score = minimax(board, 'X')
                board[row][col] = ''
                if score < bestScore:
                    bestScore = score
                    bestMove = (row, col)
    board[bestMove[0]][bestMove[1]] = player
    over_pos.append((bestMove[0],bestMove[1]))

scores = {'X': 1, 'O': -1, 'tie': 0}


def minimax(board, cur_player):
    if isWinner('X'):
        return scores['X']
    elif isWinner('O'):
        return scores['O']
    elif isBoardFull():
        return scores['tie']
    if cur_player == 'X':
        bestScore = float('-inf')
        nextPlayer = 'O'
        minORmax = max
    else:
        bestScore = float('inf')
        nextPlayer = 'X'
        minORmax = min
    for row in range(3):
        for col in range(3):
            if board[row][col] == '':
                board[row][col] = cur_player
                score = minimax(board, nextPlayer)
                board[row][col] = ''
                bestScore = minORmax(score, bestScore)
            if bestScore == scores[cur_player]:
                return bestScore
    return bestScore


def updatePlayer(player):
    if player == 'X':
        newPlayer = 'O'
        previewImg = previewCircleImg
    else:
        newPlayer = 'X'
        previewImg = previewCrossImg
    return newPlayer, previewImg



def isWinner(player):
    return ((board[0][0] == player and board[0][1] == player and board[0][2] == player) or
            (board[1][0] == player and board[1][1] == player and board[1][2] == player) or
            (board[2][0] == player and board[2][1] == player and board[2][2] == player) or
            (board[0][0] == player and board[1][0] == player and board[2][0] == player) or
            (board[0][1] == player and board[1][1] == player and board[2][1] == player) or
            (board[0][2] == player and board[1][2] == player and board[2][2] == player) or
            (board[0][0] == player and board[1][1] == player and board[2][2] == player) or
            (board[0][2] == player and board[1][1] == player and board[2][0] == player))


def verifyWinner(player):
    global  Send_Flag,Receive_Flag,current_player,dataSocket,previewImg,gameMode,SOR
    if isWinner(player):
        print(player, "win")
        if gameMode ==2:
            previewImg = previewCrossImg
            current_player = 'X'  # 服务端先下
            SOR = 0
            # if player == 'X':
                # toSend = 'Over'
                # dataSocket.send(toSend.encode())
                # print("send_meseage:", toSend)
                # Send_Flag = 0
                # Receive_Flag = 1
        score[player] += 1
        ctypes.windll.user32.MessageBoxW(0, player + ' 获胜！', '提示', 0)
        resetBoard()
        return True
    return False


def isBoardFull():
    for i in range(3):
        for j in range(3):
            if board[i][j] == '':
                return False
    return True


def resetBoard():
    for i in range(3):
        for j in range(3):
            board[i][j] = ''

def Common_Reset():##对方刷新引起的刷新，被动刷新
    global Send_Flag,Receive_Flag,gameMode,current_player,previewImg,dataSocket
    resetBoard()
    score['X'] = 0
    score['O'] = 0
    if gameMode == 2:
        current_player = 'X'
        print("I have turn the picture to Cross")
        previewImg = previewCrossImg
def resetGame():##主动刷新
    global Send_Flag, Receive_Flag, gameMode, current_player, previewImg, dataSocket,over_pos
    resetBoard()
    over_pos= []
    score['X'] = 0
    score['O'] = 0
    if gameMode == 2:
        current_player = 'X'
        print("I have turn the picture to Cross")
        previewImg = previewCrossImg

    resetBoard()
    score['X'] = 0
    score['O'] = 0
global i
i = 0
def handle(rec):
    global send_row, send_col ,Send_Flag,row, col,Receive_Flag, i, current_player, previewImg,message,over_pos
    global pi_sure_flag, pi_row, pi_col, pr_flash
    if rec:
        re_sure_flag = int(pi_sure_flag.search(rec).group(1))
        re_row = int(pi_row.search(rec).group(1))
        re_col = int(pi_col.search(rec).group(1))
        re_flash = int(pi_flash.search(rec).group(1))
        re_reg = int(pi_reg.search(rec).group(1))
        if re_sure_flag == 1:
            counter_row = re_row
            counter_col = re_col
            board[counter_row][counter_col] = "X"
            over_pos.append((counter_row,counter_col))
            drawBoard()
            current_player = 'O'  ##收到对面信息后回到主场
            previewImg = previewCircleImg
            pygame.display.update()
        if re_flash ==1 :
            Common_Reset()
        if re_reg == 1:
            print("悔棋一次")
            lenth = len(over_pos)
            if lenth > 0:
                x = over_pos[lenth - 1][0]
                y = over_pos[lenth - 1][1]
                del over_pos[lenth - 1]
                if lenth == 1:
                    resetGame()
                elif board[x][y] == "X":
                    print("regret x")
                    Current_Player = "O"
                    previewImg = previewCircleImg
                    board[x][y] = " "
                    drawBoard()
                elif board[x][y] == "O":
                    print("regret o")
                    Current_Player = "X"
                    previewImg = previewCrossImg
                    board[x][y] = " "
                    drawBoard()
                pygame.display.update()



def TCP_Client():
    global send_row, send_col ,Send_Flag,row, col,Receive_Flag, i, current_player, previewImg,message,SOR,sure_flag,flash_flag,regret_flag
    global pi_send_flag, pi_received_flag, pi_row, pi_col, pr_flash
    pi_sr = re.compile(r'SenOrRec(\d)')
    while True:
        if SOR == 1:
            print("waiting for receiving...........")
            recved = dataSocket.recv(BUFLEN)
            rec = recved.decode()
            if not recved:
                break
            if rec:
                handle(rec)
                print("received", rec)
                dataSocket.send(message.encode())
                SOR = 0
        # time.sleep(0.3)
        if SOR == 0:
            print("sending",message)
            dataSocket.send(message.encode())
            sure_flag = 0
            flash_flag = 0
            regret_flag = 0
            message = "sure_f" + str(sure_flag) + "row" + str(send_row) + " col" + str(send_col) + "flash" + str(
                flash_flag) + "reg" + str(regret_flag)
            # time.sleep(0.1)
            SOR = 1


client_thread = threading.Thread(target=TCP_Client)
client_thread.start()

menu()
dataSocket.close()
