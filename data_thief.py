from datamodel import TradingState


# - `STARFRUIT`: 20
# AMETHYSTS

class Trader:

    def __init__(self):
        self.products = ["STARFRUIT", "AMETHYSTS"]
        for product in self.products:
            print(f"{product} lowest ask price; {product} highest bid price;", end="")
            print(f"{product} transport fees; {product} export tariff; {product}", end="")
            print(f"import tariff; {product} sunlight; {product} humidity;", end="")
            print("\n")

    def run(self, state: TradingState):
        for product in self.products:
            if (product in state.order_depths):
                lowestAskPrice = list(state.order_depths[product].sell_orders.keys())
                lowestAskPrice.sort()
                if (len(lowestAskPrice) > 0):
                    lowestAskPrice = lowestAskPrice[0]
                else:
                    lowestAskPrice = -1

                highestBidPrice = list(state.order_depths[product].buy_orders.keys())
                highestBidPrice.sort(reverse=True)
                if len(highestBidPrice) > 0:
                    highestBidPrice = highestBidPrice[0]
                else:
                    highestBidPrice = -1

                print(f"{lowestAskPrice}; {highestBidPrice};", end="")
            else:
                print("-1; -1;", end="")

            if (product in state.observations.conversionObservations):
                conversionObservation = state.observations.conversionObservations[product]
                print(
                    f"{conversionObservation.transportFees}; {conversionObservation.exportTariff}; {conversionObservation.importTariff}; {conversionObservation.sunlight}; {conversionObservation.humidity};",
                    end="")
            else:
                print("-1; -1; -1; -1; -1;", end="")
            print("\n")

            # String value holding Trader state data required.
            # It will be delivered as TradingState.traderData on next execution.
        traderData = "SAMPLE"

        return {}, 0, traderData
