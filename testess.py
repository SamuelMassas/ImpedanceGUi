import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chi2


#x-axis ranges from 0 to 20 with .001 steps
x = np.arange(0, 150, 0.01)

#plot Chi-square distribution with 4 degrees of freedom
plt.plot(x, chi2.pdf(x, df=39))
plt.plot(54.57, chi2.pdf(54.57, df=39), 'rs')
plt.xlabel(u'\u03A7\u00B2')
plt.ylabel('frequency')
plt.title('k=39, Q=54.57')
plt.show()
