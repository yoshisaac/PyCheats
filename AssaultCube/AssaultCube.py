import dearpygui.dearpygui as dpg
import pymem, utility, pyautogui
import math
import threading, time
import sys, keyboard

process = pymem.Pymem("ac_client.exe")
screenWidth, screenHighet = pyautogui.size()

terminateAllThreads = False

entityListAddress = process.base_address + 0x18AC04
entityList = process.read_uint(entityListAddress)
offset = 0

class Engine:
    fieldOfViewPtr = process.base_address + 0x18AC00
    FOV = utility.FindDMAAddy(process.process_handle, fieldOfViewPtr, [0x334], 32)

    playerCountPtr = process.base_address + 0x18AC0C
    playerCount = process.read_int(utility.FindDMAAddy(process.process_handle, playerCountPtr, [], 32))

pLocal = process.base_address + 0x17E0A8 #Local Player Pointer
LocalP = utility.FindDMAAddy(process.process_handle, pLocal, [0x0], 32)
#5558436 is basically the integer value the local player pointer points to.
#While dead, the pointer's data changes for some reason.
#When trying to read memory while the data is offset incorrectly you don't get any of the correct information
OneTime = False
while process.read_int(LocalP) != 5558436:
    if OneTime == False:
        print("Waiting until you are alive")
        OneTime = True
    LocalP = utility.FindDMAAddy(process.process_handle, pLocal, [0x0], 32)

class localPlayer:
    pLocal = process.base_address + 0x17E0A8 #Local Player Pointer
    LocalP = utility.FindDMAAddy(process.process_handle, pLocal, [0x0], 32)

    def iHealth():
        return process.read_int(utility.FindDMAAddy(process.process_handle, pLocal, [0xEC], 32))
    def iArmor():
        return process.read_int(utility.FindDMAAddy(process.process_handle, pLocal, [0xF0], 32))
    
    def mPitch():
        return process.read_float(utility.FindDMAAddy(process.process_handle, pLocal, [0x38], 32))
    def mYaw():
        return process.read_float(utility.FindDMAAddy(process.process_handle, pLocal, [0x34], 32))

    def isDead():
        return process.read_int(utility.FindDMAAddy(process.process_handle, pLocal, [0x318], 32))

    def getName():
        return process.read_string(utility.FindDMAAddy(process.process_handle, pLocal, [0x205], 32))
    
    #(1=RVSF, 0=CLA, 4=Spectator, Deathmatch=NoTeam)
    def teamNumber():
        return process.read_int(utility.FindDMAAddy(process.process_handle, pLocal, [0x30C], 32))

    #The difference between the feet and the head is 4.5 units
    def feetHighet():
        return process.read_float(utility.FindDMAAddy(process.process_handle, pLocal, [0x30], 32))
    def headPosition():
        return [process.read_float(utility.FindDMAAddy(process.process_handle, pLocal, [0x4], 32)), 
    process.read_float(utility.FindDMAAddy(process.process_handle, pLocal, [0x8], 32)), 
    process.read_float(utility.FindDMAAddy(process.process_handle, pLocal, [0xC], 32))]

class Player:
    iHealth = 0

    isDead = 0

    getName = ""

    teamNumber = 0

    mPitch = 0
    mYaw = 0

    headPosition = []

dpg.create_context()
with dpg.window(label=" ", width=500, height=500, no_move=True, no_collapse=True, no_resize=True, no_title_bar=True):
    with dpg.tab_bar(label="yes"):
        
        with dpg.tab(label="Info"):
            dpg.add_text(tag="currentHealth")
            dpg.add_text(tag="currentArmor")

            dpg.add_spacer(height=5)

            dpg.add_text(tag="currentTeam")
            dpg.add_text(tag="currentName")

            dpg.add_spacer(height=15)

            dpg.add_text(tag="currentPitch")
            dpg.add_text(tag="currentYaw")

            dpg.add_spacer(height=15)

            dpg.add_text(tag="headhighet")
            dpg.add_text(tag="feethighet")
            
            dpg.add_button(tag="destButton", label="destroy gui")
"""
        with dpg.tab(label="Playerlist"):

            #this is stupid but mostly works
            dpg.add_button(tag=1, label="Player")
            dpg.add_button(tag=2, label="Player")
            dpg.add_button(tag=3, label="Player")
            dpg.add_button(tag=4, label="Player")
            dpg.add_button(tag=5, label="Player")
            dpg.add_button(tag=6, label="Player")
            dpg.add_button(tag=7, label="Player")
            dpg.add_button(tag=8, label="Player")
            dpg.add_button(tag=9, label="Player")
            dpg.add_button(tag=10, label="Player")
            dpg.add_button(tag=11, label="Player")
            dpg.add_button(tag=12, label="Player")
            dpg.add_button(tag=13, label="Player")
            dpg.add_button(tag=14, label="Player")
            dpg.add_button(tag=15, label="Player")
            dpg.add_button(tag=16, label="Player")
            dpg.add_button(tag=17, label="Player")
            dpg.add_button(tag=18, label="Player")
            dpg.add_button(tag=19, label="Player")
            dpg.add_button(tag=20, label="Player")
            dpg.add_button(tag=21, label="Player")
            dpg.add_button(tag=22, label="Player")
            dpg.add_button(tag=23, label="Player")
            dpg.add_button(tag=24, label="Player")
            dpg.add_button(tag=25, label="Player")
            dpg.add_button(tag=26, label="Player")
            dpg.add_button(tag=27, label="Player")
            dpg.add_button(tag=28, label="Player")
            dpg.add_button(tag=29, label="Player")
            dpg.add_button(tag=30, label="Player")
            dpg.add_button(tag=31, label="Player")
            dpg.add_button(tag=32, label="Player")
            dpg.add_text()
"""

dpg.create_viewport(title=" ", width=500, max_width=500, min_width=500, height=500, max_height=500, min_height=500, always_on_top=True)
dpg.setup_dearpygui()
dpg.show_viewport()

def concat(table):
    final = ""

    for element in table:
        final = final + str(element) + " "
    
    return final

def enumeratePlayers():
    while True:
        if terminateAllThreads == True:
            sys.exit()

        for player in range(1, 32, 1):
            currentPlayer = entityList + (player*4)

            try:
                Player.teamNumber = process.read_int(utility.FindDMAAddy(process.process_handle, currentPlayer, [0x30C], 32))

                Player.getName = process.read_string(utility.FindDMAAddy(process.process_handle, currentPlayer, [0x205], 32))
                Player.iHealth = process.read_int(utility.FindDMAAddy(process.process_handle, currentPlayer, [0xEC], 32))
                #print(int(player/4))
                #print("Name: ", Player.getName)

                currentTeam = str
                if Player.teamNumber == 1:
                    currentTeam = "RVSF"
                elif Player.teamNumber == 0:
                    currentTeam = "CLA"
                elif Player.teamNumber == 4:
                    currentTeam = "SPEC"
                
                dpg.set_item_label(int(player), concat([Player.getName, Player.iHealth, currentTeam]))
                """print("Health: ", process.read_int(utility.FindDMAAddy(process.process_handle, currentPlayer, [0xEC], 32)))
                print("Pitch: ", process.read_float(utility.FindDMAAddy(process.process_handle, currentPlayer, [0x38], 32)))
                print("Yaw: ", process.read_float(utility.FindDMAAddy(process.process_handle, currentPlayer, [0x34], 32)))
                print("Is Dead: ", process.read_int(utility.FindDMAAddy(process.process_handle, currentPlayer, [0x318], 32)))
                print("Position: ", 
                    process.read_float(utility.FindDMAAddy(process.process_handle, currentPlayer, [0x4], 32)), #X
                    process.read_float(utility.FindDMAAddy(process.process_handle, currentPlayer, [0x8], 32)), #Y
                    process.read_float(utility.FindDMAAddy(process.process_handle, currentPlayer, [0xC], 32))  #Z
                    )"""
                #print()
                #print()
                """
                
                Player.isDead = process.read_int(utility.FindDMAAddy(process.process_handle, currentPlayer, [0x318], 32))

                Player.mPitch = process.read_float(utility.FindDMAAddy(process.process_handle, currentPlayer, [0x38], 32))
                Player.mYaw = process.read_float(utility.FindDMAAddy(process.process_handle, currentPlayer, [0x34], 32))

                Player.headPosition = process.read_float(utility.FindDMAAddy(process.process_handle, currentPlayer, [0x4], 32))[1]
                Player.headPosition = process.read_float(utility.FindDMAAddy(process.process_handle, currentPlayer, [0x8], 32))[2]
                Player.headPosition = process.read_float(utility.FindDMAAddy(process.process_handle, currentPlayer, [0xC], 32))[3]
                """
            except:
                #print("excepted")
                break
enumeratePlayersThread = threading.Thread(target=enumeratePlayers, args=())
enumeratePlayersThread.start()

while dpg.is_dearpygui_running():

    if localPlayer.isDead() == True:
        dpg.set_value("currentHealth", "Health: 0")
        dpg.set_value("currentArmor", "Armor: 0")
    elif localPlayer.iHealth() >= 0:
        dpg.set_value("currentHealth", "Health: " + str(localPlayer.iHealth()))
        dpg.set_value("currentArmor", "Armor: " + str(localPlayer.iArmor()))
    else:
        dpg.set_value("currentHealth", "Health: 0")
        dpg.set_value("currentArmor", "Armor: 0")

    if localPlayer.teamNumber() == 1:
        dpg.set_value("currentTeam", "Team: RVSF")
    elif localPlayer.teamNumber() == 0:
        dpg.set_value("currentTeam", "Team: CLA")
    elif localPlayer.teamNumber() == 4:
        dpg.set_value("currentTeam", "Team: Spectator")
    
    dpg.set_value("currentName", "Name: " + localPlayer.getName())

    dpg.set_value("currentPitch", "Pitch: " + str(localPlayer.mPitch()))
    dpg.set_value("currentYaw", "Yaw: " + str(localPlayer.mYaw()))

    dpg.set_value("headhighet", "Head pos:" + str(localPlayer.headPosition()))
    dpg.set_value("feethighet", "Feet pos: " + str(localPlayer.feetHighet()))

    if dpg.get_item_state("destButton")['clicked'] == True:
        dpg.stop_dearpygui()
        terminateAllThreads = True

    dpg.render_dearpygui_frame()

dpg.destroy_context()
terminateAllThreads = True