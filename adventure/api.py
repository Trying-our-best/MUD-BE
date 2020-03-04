from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# from pusher import Pusher
from django.http import JsonResponse
from decouple import config
from django.contrib.auth.models import User
from .models import *
from rest_framework.decorators import api_view
import json

# instantiate pusher
# pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

@csrf_exempt
@api_view(["GET"])
def initialize(request):
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.room()
    players = room.playerNames(player_id)
    return JsonResponse({'uuid': uuid, 'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players}, safe=True)

@csrf_exempt
@api_view(["GET"])
def getGameMap(request):
    allRooms = Room.objects.all().order_by("id")

    maxCoordX = 0
    maxCoordY = 0
    roomArr = []
    tempArr = []
    gameMap = []

    for room in allRooms:
        if room.coordinateX > maxCoordX:
            maxCoordX = room.coordinateX
        if room.coordinateY > maxCoordY:
            maxCoordY = room.coordinateY
    
    
    for room in allRooms:
        if room.coordinateX == maxCoordX:
            tempArr.append(room)
            roomArr.append(tempArr)
            tempArr = []
        else:
            tempArr.append(room)

    for i in range(len(roomArr) * 2 + 1):
            gameMap.append([None] * (2 * len(roomArr[0]) + 1))
            
    
    for i in range(len(gameMap)):
            for j in range(len(gameMap[i])):
                if i % 2 == 0:
                    gameMap[i][j] = 0

    
    for i, row in enumerate(roomArr):
            for j, tile in enumerate(row):
                #Print Entrance and in Between Rooms
                if tile.n_to == 1:
                    gameMap[i * 2][j * 2 + 1] = 1   
                
                #Print Exit to South
                if i == len(roomArr) - 1 and tile.s_to == 1:
                    gameMap[len(roomArr)*2][j*2 + 1] = 1

                #East Wall
                if j == 0:
                    gameMap[i*2+1][j] = 0

                #east-west connection
                if j > 0:
                    if row[j-1].e_to == 1 and row[j].w_to == 1:
                        gameMap[i*2+1][j*2] = 1
                    else: 
                        gameMap[i*2+1][j*2] = 0

                #current room
                gameMap[i*2 + 1][j*2+1] = 1

                #West Wall
                if j == len(row) - 1:
                    gameMap[i*2 + 1][j*2+2] = 0
                

    return JsonResponse({'gameMap': gameMap}, safe=True)

# @csrf_exempt
@api_view(["POST"])
def move(request):
    dirs={"n": "north", "s": "south", "e": "east", "w": "west"}
    reverse_dirs = {"n": "south", "s": "north", "e": "west", "w": "east"}
    player = request.user.player
    player_id = player.id
    player_uuid = player.uuid
    data = json.loads(request.body)
    direction = data['direction']
    room = player.room()
    nextRoomID = None
    if direction == "n":
        nextRoomID = room.n_to
    elif direction == "s":
        nextRoomID = room.s_to
    elif direction == "e":
        nextRoomID = room.e_to
    elif direction == "w":
        nextRoomID = room.w_to
    if nextRoomID is not None and nextRoomID > 0:
        nextRoom = Room.objects.get(id=nextRoomID)
        player.currentRoom=nextRoomID
        player.save()
        players = nextRoom.playerNames(player_id)
        currentPlayerUUIDs = room.playerUUIDs(player_id)
        nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
        # for p_uuid in currentPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
        # for p_uuid in nextPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
        return JsonResponse({'name':player.user.username, 'title':nextRoom.title, 'description':nextRoom.description, 'players':players, 'error_msg':""}, safe=True)
    else:
        players = room.playerNames(player_id)
        return JsonResponse({'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players, 'error_msg':"You cannot move that way."}, safe=True)


@csrf_exempt
@api_view(["POST"])
def say(request):
    # IMPLEMENT
    return JsonResponse({'error':"Not yet implemented"}, safe=True, status=500)
