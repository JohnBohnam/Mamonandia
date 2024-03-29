import numpy as np
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the Excel file into a pandas DataFrame
df = pd.read_csv('simple_data.csv')

amethyst_df = df[df['product'] == 'AMETHYSTS']
starfruit_df = df[df['product'] == 'STARFRUIT']


amethyst_mid_prices = np.array(amethyst_df['mid_price'].tolist())
starfruit_mid_prices = np.array(starfruit_df['mid_price'].tolist())
amethyst_mid_prices_adjusted=amethyst_mid_prices-10000.0
time_stamp = df['timestamp'].tolist()

#print(len(time_stamp[4::2])," ",len(starfruit_mid_prices))
x=np.arange(0,len(starfruit_mid_prices))
#print(amethyst_mid_prices)
plt.scatter(x[0:100],amethyst_mid_prices_adjusted[0:100])
plt.xlabel("time stamp up to 100")
plt.ylabel("price of amethyst-1000")
plt.show()


plt.scatter(x[0:100],amethyst_mid_prices_adjusted[0:100])
plt.xlabel("time stamp up to 100")
plt.ylabel("price of amethyst-1000")
plt.show()

