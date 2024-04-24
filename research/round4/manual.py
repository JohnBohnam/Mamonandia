import numpy as np

N = 101
probs = np.linspace(0, 1, N)
probs = probs/np.sum(probs)
cdf = np.cumsum(probs)
keys = np.array(list(range(900,900+N)))
result = (0,0,0)

for p1 in range(N):
	p2 = 84
	profit = cdf[p1]*(1000-keys[p1]) + (cdf[p2] - cdf[p1])*(1000- keys[p2])
	if profit > result[2]:
		result = (p1,p2,profit)
print(keys[result[0]], keys[result[1]], result[2])
			
def fminus1(a):
	return ((a-0.01)**2-0.25)*(1-a)
	
def fplus1(a):
	return ((a+0.01)**2-0.25)*(1-(a+0.01))

for a in np.linspace(0,1,100):
	print(a, fminus1(a), fplus1(a))
	
best_profit = (0,0,0)
for l in range(101):
	profit = ((l/100)**2) *(1-l/100) + ((y/100)**2 - (l/100)**2) *(1-y/100)
	if profit > best_profit[2]:
		best_profit = (l,y,profit)