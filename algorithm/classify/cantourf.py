from matplotlib import pyplot as plt
import numpy as np
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression

X, y = load_iris(return_X_y=True)
X = X[:, :2]
clf = LogisticRegression(random_state=0).fit(X, y)

x2, y2 = np.meshgrid(np.linspace(X[:, 0].min()-.5, X[:, 0].max()+.5, 20),
                     np.linspace(X[:, 1].min()-.5, X[:, 1].max()+.5, 20) )
pred = clf.predict(np.c_[x2.ravel(), y2.ravel()])
c = pred.reshape(x2.shape)
cmap = plt.get_cmap('Set1', 3)
plt.scatter(x2.ravel(), y2.ravel(), c=pred, s=10, cmap=cmap, label='Prediction on grid')
plt.scatter(X[:, 0], X[:, 1], c=y, s=50, cmap=cmap, ec='black', label='Given values')
plt.contourf(x2, y2, pred.reshape(x2.shape), cmap=cmap, alpha=0.4, levels=2, zorder=0)
plt.legend(ncol=2, loc="lower center", bbox_to_anchor=(0.5,1.01))
plt.show()
# https://stackoverflow.com/questions/63234019/explain-matplotlib-contourf-function