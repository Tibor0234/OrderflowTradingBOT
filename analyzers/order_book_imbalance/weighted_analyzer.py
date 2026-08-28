from analyzers.order_book_imbalance.base_analyzer import BaseOrderBookImbalanceAnalyzer

class OrderBookWeightedImbalanceAnalyzer(BaseOrderBookImbalanceAnalyzer):
    def get_weight(self, i):
        return i + 1