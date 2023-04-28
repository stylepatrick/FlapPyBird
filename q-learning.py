# file with improved speed no GUI
#import flappy_without_gui
# need to play the game with learned data
import flappy
from collections import defaultdict
import numpy as np
import pickle

# init variables
rewardAlive = 1
rewardKill = -10000
alpha = 0.1
gamma = 1

#Q = defaultdict(lambda: [0, 0])
# need to play the game with learned data
Q = None

# need to play the game with loaded learned data
with open("Q/qlearning_100000.pickle", "rb") as file:
    Q = defaultdict(lambda: [0, 0], pickle.load(file))

def paramsToState(params):
    playerVelY = params['playerVelY']
    playery = params["playery"]

    if int(params["upperPipes"][0]['x']) < 40:
        index = 1
    else:
        index = 0

    upperPipeX = round(int(params["upperPipes"][index]['x']) / 3) * 3
    upperPipeY = int(params["upperPipes"][index]['y'])

    yDiff = round((playery - upperPipeY) / 3) * 3

    return str(playerVelY) + "_" + str(yDiff) + "_" + str(upperPipeX)

# global variables to store states, needed in the next actions to update
prevState = None
prevAction = None
gameCounter = 0
gameScores = []

def onGameover(gameInfo):
    global prevState
    global prevAction
    global gameCounter
    global gameScores

    gameScores.append(gameInfo['score'])

    # print the gameCounter every 10000 game overs
    if gameCounter % 10000 == 0:
        print(str(gameCounter) + ": " + str(np.mean(gameScores[-10000:])))

    prevReward = Q[prevState]
    index = None
    if prevAction == False:
        index = 0
    else:
        index = 1

    # update prevReward with the negative value due to gameOver
    prevReward[index] = (1 - alpha) * prevReward[index] + alpha * rewardKill
    Q[prevState] = prevReward

    prevState = None
    prevAction = None

    # dump learned data every 10000 game overs
    if gameCounter % 10000 == 0:
       with open("Q/qlearning_" + str(gameCounter) + ".pickle", "wb") as file:
           pickle.dump(dict(Q), file)

    gameCounter += 1

def shouldEmulateKeyPress(params):
    global prevState
    global prevAction

    state = paramsToState(params)
    # load estimated reward from dictionary
    # if value not yet present use the default value [0, 0]
    estReward = Q[state]

    # get previous reward to update
    prevReward = Q[prevState]
    index = None
    if prevAction == False:
        index = 0
    else:
        index = 1

    # calculation of previous reward for previous state
    # will update with positive values because player is still alive
    prevReward[index] = (1 - alpha) * prevReward[index] + alpha * (rewardAlive + gamma * max(estReward))

    Q[prevState] = prevReward

    prevState = state
    action = None
    if estReward[0] >= estReward[1]:
        action = False
    else:
        action = True

    prevAction = action
    return action

flappy.main(shouldEmulateKeyPress, onGameover)