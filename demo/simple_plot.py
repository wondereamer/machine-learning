'''
Author: your name
Date: 2020-06-07 10:58:19
LastEditTime: 2022-02-19 15:24:45
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/demo/simple_plot.py
'''
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
# plt.figure(1)                # the first figure
# ax = plt.subplot(211)             # the first subplot in the first figure
# plt.plot([1, 2, 3])
# plt.subplot(212)             # the second subplot in the first figure
# plt.plot([4, 5, 6])


# plt.figure(2)                # a second figure
# plt.plot([4, 5, 6])          # creates a subplot(111) by default

# fig, ax3 = plt.subplots()
# ax3.scatter([1, 2, 3], [4, 5, 6])


# plt.title('Easy as 1, 2, 3') # subplot 211 title
# plt.show()

# plt.close('all')

def example_plot(ax):
    ax.plot([1,3,3])

fig = plt.figure()

ax1 = plt.subplot2grid((3, 3), (0, 0))
ax2 = plt.subplot2grid((3, 3), (0, 1), colspan=2)
ax3 = plt.subplot2grid((3, 3), (1, 0), colspan=2, rowspan=2)
ax4 = plt.subplot2grid((3, 3), (1, 2), rowspan=2)

# example_plot(ax1)
# example_plot(ax2)
# example_plot(ax3)
# example_plot(ax4)

plt.tight_layout()


plt.show()