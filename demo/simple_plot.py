import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
plt.figure(1)                # the first figure
ax = plt.subplot(211)             # the first subplot in the first figure
plt.plot([1, 2, 3])
plt.subplot(212)             # the second subplot in the first figure
plt.plot([4, 5, 6])


plt.figure(2)                # a second figure
plt.plot([4, 5, 6])          # creates a subplot(111) by default

fig, ax3 = plt.subplots()
ax3.scatter([1, 2, 3], [4, 5, 6])


plt.title('Easy as 1, 2, 3') # subplot 211 title
plt.show()
