import math

def getDistance(p1, p2):
    return math.sqrt(((p2[0]-p1[0])**2)+((p2[1]-p1[1])**2)+((p2[2]-p1[2])**2))

m1 = [1,0,0]
m2 = [0,2,0]
m3 = [2,2,0]
m4 = [1, 1, 4]

mic = [
    float(input("x position: ")),
    float(input("y position: ")),
    float(input("z position: "))
]

d1 = getDistance(m1, mic)
d2 = getDistance(m2, mic)
d3 = getDistance(m3, mic)
d4 = getDistance(m4, mic)

print()
print(d1)
print(d2)
print(d3)
print(d4)