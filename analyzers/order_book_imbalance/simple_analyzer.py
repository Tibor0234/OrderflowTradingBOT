from analyzers.order_book_imbalance.base_analyzer import BaseOrderBookImbalanceAnalyzer

class OrderBookImbalanceAnalyzer(BaseOrderBookImbalanceAnalyzer):
    def get_weigth(self, i):
        return 1