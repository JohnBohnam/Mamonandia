from datamodel import *


class Trader:
	def eval_coconut(self, state: TradingState) -> float:
		mids = {}
		for product in ["COCONUT", "COCONUT_COUPON"]:
			best_bid = max(state.order_depths[product].buy_orders.keys())
			best_ask = min(state.order_depths[product].sell_orders.keys())
			mids[product] = (best_bid + best_ask) / 2
		x = mids["COCONUT_COUPON"] - 600
		if x <= 0:
			regression_coeffs = [(-26.80799835, 1.54459215), (-78.17969157, 1.59804532)]
			prices = [x * a[1] + a[0] for a in regression_coeffs]
			return (min(prices), max(prices))
		if x > 0:
			regression_coeffs = [(-61.22517152, 1.75887911), (-15.22083538, 1.20576268),
			                     (-59.73260114, 2.50990171)]
			prices = [x * a[1] + a[0] for a in regression_coeffs]
			return (min(prices), max(prices))
		return 10000
	
	def eval_coupon(self, state: TradingState) -> float:
		mids = {}
		for product in ["COCONUT", "COCONUT_COUPON"]:
			best_bid = max(state.order_depths[product].buy_orders.keys())
			best_ask = min(state.order_depths[product].sell_orders.keys())
			mids[product] = (best_bid + best_ask) / 2
		x = mids["COCONUT"] - 10000
		if x <= 0:
			regression_coeffs = [(34.08646745, 0.5302865), (56.67058553, 1.28420207),
			                     (16.60638543, 0.3410951)]
			prices = [x * a[1] + a[0] for a in regression_coeffs]
			return (min(prices), max(prices))
		if x > 0:
			regression_coeffs = [(51.9612041, 0.29568128), (24.64350008, 0.63945882)]
			prices = [x * a[1] + a[0] for a in regression_coeffs]
			return (min(prices), max(prices))
		return 600
