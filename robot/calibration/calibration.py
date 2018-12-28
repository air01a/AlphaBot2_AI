import compass
import time

compass.wake()
#compass.setHighSpeedDataRate()

data = []
x_north = None
x_south = None
y_north = None
y_south = None

input("Turn the x-axis towards north and press enter")
# Read 400 values and compute the mean and repeat for all axis and all cardinal directions
for i in range(400):
    data.append(compass.readAxisData()[0])
    time.sleep(0.005)
x_north = sum(data)/len(data)
del data[:]

input("Turn the x-axis towards south and press enter")
for i in range(400):
    data.append(compass.readAxisData()[0])
    time.sleep(0.005)
x_south = sum(data)/(len(data))
del data[:]

input("Turn the y-axis towards north and press enter")
for i in range(400):
    data.append(compass.readAxisData()[1])
    time.sleep(0.005)
y_north = sum(data)/(len(data))
del data[:]

input("Turn the y-axis towards south and press enter")
for i in range(400):
    data.append(compass.readAxisData()[1])
    time.sleep(0.005)
y_south = sum(data)/(len(data))
del data[:]

#compass.setNormalSpeedDataRate()
compass.sleep()

x_offset = -(x_north + x_south)/2 # The readings for north and south should give the same values but with different signs. This calculates the offset (zero if north and south give the same result). The minus sign is there because I thought it would be nicer to use addition instead of subtraction when using this to read data later.
x_amp = abs(x_north - x_south) # Get the amplitude of the x-readings. Used to calculate how much to scale the y-axis.
y_offset = -(y_north + y_south)/2 # Offset of the y-axis
y_amp = abs(y_north - y_south) # Amplitude of the y-axis
y_scale = x_amp/y_amp # This value should then be multiplied with the values coming from the y-axis to make both axis have uniform length.

print()
print("Add {} to the x-axis".format(x_offset))
print("Add {} to the y-axis and multiply it by {}".format(y_offset, y_scale))
