import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

plt.subplot(311)
plt.plot([1, 2, 3])

# the axes attributes need to be set before the call to subplot
plt.rc('font', weight='bold')
plt.rc('xtick.major', size=5, pad=7)
plt.rc('xtick', labelsize=15)

# using aliases for color, linestyle and linewidth; gray, solid, thick
plt.rc('grid', c='0.5', ls='-', lw=5)
plt.rc('lines', lw=2, color='g')
plt.subplot(312)

plt.plot([1, 2, 3])
plt.grid(True)

plt.rcdefaults()
plt.subplot(313)
plt.plot([1, 2, 3])
plt.grid(True)
plt.show()