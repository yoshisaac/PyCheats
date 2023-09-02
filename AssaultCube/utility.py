import ctypes
import math
from consts import *

kernel32 = ctypes.windll.kernel32

def GetProcId(processName):
    procId = None
    hSnap = kernel32.CreateToolhelp32Snapshot(THIS_SNAPPROCESS, 0)

    if (hSnap != INVALID_HANDLE_VALUE):
        procEntry = PROCESSENTRY32()
        procEntry.dwSize = ctypes.sizeof(PROCESSENTRY32)

        if (kernel32.Process32First(hSnap, ctypes.byref(procEntry))):
            def processCmp(procEntry):
                if (procEntry.szExeFile.decode("utf-8") == processName):
                    nonlocal procId
                    procId = int(procEntry.th32ProcessID)

            processCmp(procEntry)
            while (kernel32.Process32Next(hSnap, ctypes.byref(procEntry))):
                processCmp(procEntry)

    kernel32.CloseHandle(hSnap)
    return (procId)

def FindDMAAddy(hProc, base, offsets, arch=64):
    size = 8
    if (arch == 32): size = 4
    address = ctypes.c_uint64(base)

    for offsets in offsets:
        kernel32.ReadProcessMemory(hProc, address, ctypes.byref(address), size, 0)
        address = ctypes.c_uint64(address.value + offsets)

    return (address.value)

def patchBytes(handle, src, destination, size):
    src = bytes.fromhex(src)
    size = ctypes.c_size_t(size)
    destination = ctypes.c_ulonglong(destination)
    oldProtect = ctypes.wintypes.DWORD()

    kernel32.VirtualProtectEx(handle, destination, size, PAGE_EXECUTE_READWRITE, ctypes.byref(oldProtect))
    kernel32.WriteProcessMemory(handle, destination, src, size, None)
    kernel32.VirtualProtectEx(handle, destination, size, oldProtect, ctypes.byref(oldProtect))

def nopBytes(handle, destination, size):
    hexString = ""
    for i in range(size):
        hexString += "90"
    patchBytes(handle, hexString, destination, size)

def Magnitude3D(X, Y, Z):
    return abs(math.sqrt((X * X) + (Y * Y) + (Z * Z)))

def Normalize3D(X, Y, Z):
    return [X / Magnitude3D(X, Y, Z), Y / Magnitude3D(X, Y, Z), Z / Magnitude3D(X, Y, Z)]

def Distance2D(sourceX, sourceY, destinationX, destinationY):
    return math.sqrt((math.pow(destinationX - sourceX, 2)) + (math.pow(destinationY - sourceY, 2)))

def CalcAngle(sourceX, sourceY, sourceZ, destinationX, destinationY, destinationZ):
    angleX = 0
    angleY = 0

    angleX = math.atan2(destinationX - sourceX, destinationY - sourceY) / math.pi * 180 #+ 180
    angleY = math.asin((destinationZ - sourceZ) / Distance2D(sourceX, sourceY, destinationX, destinationY)) * 180 / math.pi

    return angleX, angleY