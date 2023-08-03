import dearpygui.dearpygui as dpg
import pymem, threading, keyboard, time, sys

#Constants
doJump = 5
dontJump = 4

process = pymem.Pymem("hl2.exe")
clientDLL = pymem.pymem.process.module_from_name(process.process_handle, "client.dll").lpBaseOfDll

killAllThreads = False
key = "space"
 
onGround = clientDLL + 0x4F82AC
dwForceJump = clientDLL + 0x4F5D24

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

dpg.create_context()
with dpg.window(label=" ", width=300, height=300, no_move=True, no_collapse=True, no_resize=True):

    dpg.add_button(tag="bhopKey", label="Key: space", callback=set_bind, indent=0)
    dpg.add_spacer(height=180)

    dpg.add_button(tag="destButton", label="destroy gui")

dpg.create_viewport(title="CS:S Bhop Cheat", width=300, max_width=300, min_width=300, height=300, max_height=300, min_height=300)
dpg.setup_dearpygui()
dpg.show_viewport()

def bhop():
    while True:
        if killAllThreads == True:
            sys.exit()

        if process.read_int(onGround) == True:
            if keyboard.is_pressed(get_bind("bhopKey")):
                process.write_int(dwForceJump, doJump)
        else:
            process.write_int(dwForceJump, dontJump)
bhopThread = threading.Thread(target=bhop, args=())
bhopThread.start()


while dpg.is_dearpygui_running():

    #Close button
    if dpg.get_item_state("destButton")['clicked'] == True:
        killAllThreads = True
        dpg.stop_dearpygui()

    dpg.render_dearpygui_frame()

killAllThreads = True
dpg.destroy_context()