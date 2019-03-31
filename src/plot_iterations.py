import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('iterations.csv')
plt.scatter(df['cnots'], df['exvalue'])
plt.show()