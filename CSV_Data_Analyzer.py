import numpy as np
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the Excel file into a pandas DataFrame
df = pd.read_csv('./data/simple_data.csv')

amethyst_df = df[df['product'] == 'AMETHYSTS']
starfruit_df = df[df['product'] == 'STARFRUIT']


amethyst_mid_prices = np.array(amethyst_df['mid_price'].tolist())
starfruit_mid_prices = np.array(starfruit_df['mid_price'].tolist())
amethyst_mid_prices_adjusted=amethyst_mid_prices-10000.0
starfruit_mid_prices_adjusted=starfruit_mid_prices-5000.0


amethyst_bid_price_1=np.array(amethyst_df['bid_price_1'].tolist())
amethyst_bid_price_2=np.array(amethyst_df['bid_price_2'].tolist())
amethyst_bid_price_3=np.array(amethyst_df['bid_price_3'].tolist())


amethyst_ask_price_1=np.array(amethyst_df['ask_price_1'].tolist())
amethyst_ask_price_2=np.array(amethyst_df['ask_price_2'].tolist())
amethyst_ask_price_3=np.array(amethyst_df['ask_price_3'].tolist())

time_stamp = df['timestamp'].tolist()

#print(len(time_stamp[4::2])," ",len(starfruit_mid_prices))
x=np.arange(0,len(starfruit_mid_prices))
#print(amethyst_mid_prices)
#plt.scatter(x[0:len(amethyst_mid_prices_adjusted)],amethyst_mid_prices_adjusted)
#plt.xlabel("time stamp")
#plt.ylabel("price of amethyst-1000")
#plt.show()


#plt.scatter(x[0:len(starfruit_mid_prices)],starfruit_mid_prices)
#plt.xlabel("time stamp")
#plt.ylabel("price of starfruit-1000")
#plt.show()


print(amethyst_ask_price_1)
print(amethyst_ask_price_2)
print(amethyst_ask_price_3)
print('')
amethyst_ask_price_1_no_nan = np.nan_to_num(amethyst_ask_price_1, nan=100000)
amethyst_ask_price_2_no_nan = np.nan_to_num(amethyst_ask_price_2, nan=100000)
amethyst_ask_price_3_no_nan = np.nan_to_num(amethyst_ask_price_3, nan=100000)

min12_no_nan=np.minimum(amethyst_ask_price_1_no_nan,amethyst_ask_price_2_no_nan)#works ok
min123_amethyst=np.minimum(min12_no_nan,amethyst_ask_price_3_no_nan)
print(min123_amethyst)
print('')
print('')
print(amethyst_bid_price_1)
print(amethyst_bid_price_2)
print(amethyst_bid_price_3)

amethyst_bid_price_1_no_nan = np.nan_to_num(amethyst_bid_price_1, nan=0)
amethyst_bid_price_2_no_nan = np.nan_to_num(amethyst_bid_price_2, nan=0)
amethyst_bid_price_3_no_nan = np.nan_to_num(amethyst_bid_price_3, nan=0)
max12_no_nan=np.maximum(amethyst_bid_price_1_no_nan,amethyst_bid_price_2_no_nan)#works ok
max123_amethyst=np.maximum(max12_no_nan,amethyst_bid_price_3_no_nan)
print(max123_amethyst)

#print min and max
#print(amethyst_mid_prices)
plt.scatter(x[0:len(max123_amethyst)],max123_amethyst)
plt.scatter(x[0:len(min123_amethyst)],min123_amethyst)
plt.xlabel("time stamp")
plt.ylabel("price of amethyst-min and max")
plt.show()