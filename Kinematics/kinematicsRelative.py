import math

def getDistance(p1, p2):
    #gets the wire lengths using 3D point distance formula
    return math.sqrt(((p2[0]-p1[0])**2)+((p2[1]-p1[1])**2)+((p2[2]-p1[2])**2))

step = 0.000005 #one step = 0.0005 cm

lastLengths = [-1,-1,-1,-1]

#the positions of the microphones
m1 = [6.5,13,0]
m2 = [1,3,0]
m3 = [12,3,0]
m4 = [6.5, 6.5, 13]

while(1):
    #mic position
    mic = [
        float(input("x position: ")),
        float(input("y position: ")),
        float(input("z position: "))
    ]

    #get the distance between the mic and all the motors
    d1 = getDistance(m1, mic)
    d2 = getDistance(m2, mic)
    d3 = getDistance(m3, mic)
    d4 = getDistance(m4, mic)

    print()
    print("wire lengths: ")
    print(d1)
    print(d2)
    print(d3)
    print(d4)

    #check if there are previous lengths, skip if there are not
    if lastLengths[0] != -1:
        #get the difference between the last position and the new one
        diff1 = lastLengths[0] - d1
        diff2 = lastLengths[1] - d2
        diff3 = lastLengths[2] - d3
        diff4 = lastLengths[3] - d4

        print()
        print("differences: ")
        print(diff1)
        print(diff2)
        print(diff3)
        print(diff4)
        
        #convert into steps with a 0.000005 m error
        steps1 = int(diff1/step)
        steps2 = int(diff2/step)
        steps3 = int(diff3/step)
        steps4 = int(diff4/step)
        print()
        print("steps: ")
        print("motor 1: ", steps1)
        print("motor 2: ", steps2)
        print("motor 3: ", steps3)
        print("motor 4: ", steps4)

    #save the current wire lengths
    lastLengths = [d1, d2, d3, d4]
    print()
