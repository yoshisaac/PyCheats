import dearpygui.dearpygui as dpg
import pymem, threading, keyboard, time, sys, pyautogui

#Constants
doJump = 5
dontJump = 4
#End of Constants

killAllThreads = False

#Declaration
onGround = hex
dwForceJump = hex
process = 0
clientDLL = 0

#Get the correct offset for the correct game
for window in pyautogui.getAllWindows():
    if window.title == "HALF-LIFE: Deathmatch":
        process = pymem.Pymem("hl2.exe")
        clientDLL = pymem.pymem.process.module_from_name(process.process_handle, "client.dll").lpBaseOfDll
        onGround = clientDLL + 0x46AF1C
        dwForceJump = clientDLL + 0x468994
    
    if window.title == "Counter-Strike Source":
        process = pymem.Pymem("hl2.exe")
        clientDLL = pymem.pymem.process.module_from_name(process.process_handle, "client.dll").lpBaseOfDll
        onGround = clientDLL + 0x4F82AC
        dwForceJump = clientDLL + 0x4F5D24

    if window.title == "Team Fortress 2":
        process = pymem.Pymem("hl2.exe")
        clientDLL = pymem.pymem.process.module_from_name(process.process_handle, "client.dll").lpBaseOfDll
        onGround = clientDLL + 0xC93A3C
        dwForceJump = clientDLL + 0xC90840

    if window.title == "Counter-Strike: Global Offensive - Direct3D 9":
        process = pymem.Pymem("csgo.exe")
        clientDLL = pymem.pymem.process.module_from_name(process.process_handle, "client.dll").lpBaseOfDll        
        onGround = clientDLL + 0xDF1B54
        dwForceJump = clientDLL + 0x52BBCD8
    
    if window.title == "Left 4 Dead 2 - Direct3D 9":
        process = pymem.Pymem("left4dead2.exe")
        clientDLL = pymem.pymem.process.module_from_name(process.process_handle, "client.dll").lpBaseOfDll        
        onGround = clientDLL + 0x77FBB4
        dwForceJump = clientDLL + 0x757DF0

#if no game is open
if onGround == hex or dwForceJump == hex or process == 0 or clientDLL == 0:
    sys.exit()

# functions for the key binding
def get_bind(elem): # function to get the bind from a button
    button_label = dpg.get_item_label(elem) # getting button label
    return button_label.split(':')[1].strip()

def set_bind(sender):
    dpg.set_item_indent("bhopKey", 10)
    while True:
        key = keyboard.read_key()
        if key:break # if a key is pressed, break
    dpg.set_item_indent("bhopKey", 0)
    dpg.set_item_label(sender, f'bind: {key}') # setting bind to button

#Window & GUI creation
dpg.create_context()
with dpg.window(label=" ", width=300, height=300, no_move=True, no_collapse=True, no_resize=True):

    dpg.add_checkbox(tag="bhopCheck", label="Toggle Bhop", default_value=True)
    dpg.add_button(tag="bhopKey", label="Key: space", callback=set_bind) #Button that acts a key bind
    dpg.add_spacer(height=150)

    dpg.add_button(tag="destButton", label="destroy gui")

dpg.create_viewport(title="Bhop", width=300, max_width=300, min_width=300, height=300, max_height=300, min_height=300)
dpg.setup_dearpygui()
dpg.show_viewport()

#Bhop function/thread
def bhop():
    while True:
        if killAllThreads == True:
            sys.exit()

        if process.read_int(onGround) == True:
            if keyboard.is_pressed(get_bind("bhopKey")):
                if dpg.get_value("bhopCheck") == False: # ? I WOULD place the if check outside of these other if statements
                    continue                            # ? BUT the keyboard library is picky about when checking the key
                                                        # ? that it causes input lag.
                process.write_int(dwForceJump, doJump)
        else:
            process.write_int(dwForceJump, dontJump)
bhopThread = threading.Thread(target=bhop, args=())
bhopThread.start()

#Main rendering loop
while dpg.is_dearpygui_running():

    #Close button
    if dpg.get_item_state("destButton")['clicked'] == True:
        killAllThreads = True
        dpg.stop_dearpygui()

    dpg.render_dearpygui_frame()

#If they press the X button, then it will hit this and exit.
killAllThreads = True
dpg.destroy_context()