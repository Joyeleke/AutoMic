import math

def getAngle(a, b, c):
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return ang + 360 if ang < 0 else ang

#these will represent the motors
motorV = [0, 10]
motorU = [5, 0]
motorW = [10, 10]

#the mic position
mic = [int(input("x position: ")), int(input("y position: "))]
print(mic)

#the constant angles
WVU = 360 - getAngle(motorW, motorV, motorU)
UWV = 360 - getAngle(motorU, motorW, motorV)
VUW = 180 - (UWV + WVU)

print("UWV: ", UWV)
print("WVU: ", WVU)
print("VUW: ", VUW)

print()

#find first angles between motors and mic
MUV = getAngle(mic, motorU, motorV)
MVW = getAngle(mic, motorV, motorW)
MWU = getAngle(mic, motorW, motorU)

print("MUV: ", MUV)
print("MVW: ", MVW)
print("MWU: ", MWU)

print()

MUW = VUW - MUV
MVU = WVU - MVW
MWV = UWV - MWU

print("MUW: ", MUW)
print("MVU: ", MVU)
print("MWV: ", MWV)

print()

UMV = 180 - (MVU + MUV)
VMW = 180 - (MVW + MWV)
UMW = 180 - (MUW + MWU)

print("UMV: ", UMV)
print("VMW: ", VMW)
print("UMW: ", UMW)

print()

#distance between motors
VU = (math.sqrt(((motorV[0]-motorU[0])**2)+((motorV[1]-motorU[1])**2)))
UW = (math.sqrt(((motorU[0]-motorW[0])**2)+((motorU[1]-motorW[1])**2)))
WV = (math.sqrt(((motorW[0]-motorV[0])**2)+((motorW[1]-motorV[1])**2)))

print("VU: ", VU)
print("UW: ", UW)
print("WV: ", WV)

print()

UM = (math.sin(math.radians(MVU))) * (VU/(math.sin(math.radians(UMV))))
VM = math.sin(math.radians(MWV)) * (WV/(math.sin(math.radians(VMW))))
WM = math.sin(math.radians(MUW)) * (UW/(math.sin(math.radians(UMW))))

print("UM: ", UM)
print("VM: ", VM)
print("WM: ", WM)