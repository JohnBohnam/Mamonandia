from datamodel import TradingState


# - `STARFRUIT`: 20
# AMETHYSTS

class Trader:
	
	def __init__(self):
		self.products = ["STARFRUIT", "AMETHYSTS"]
		for product in self.products:
			print(f"{product} lowest ask price; {product} highest bid price;", end = "")
		print(
			"obs bidPrice; obs askPrice; obs transportFees; obs exportTariff; obs importTariff; "
            "obs sunlight; obs humidity\n")
	
	# self.huj = 0
	
	def run(self, state: TradingState):
		for product in self.products:
			if (product in state.orderDepths):
				lowestAskPrice = state.orderDepths[product].keys().sort()[0]
				highestBidPrice = state.orderDepths[product].keys().sort()[-1]
				print(f"{lowestAskPrice}; {highestBidPrice};", end = "")
			else:
				print("-1; -1;", end = "")
		
		# String value holding Trader state data required.
		# It will be delivered as TradingState.traderData on next execution.
		traderData = "SAMPLE"
		
		return {}, 0, traderData
