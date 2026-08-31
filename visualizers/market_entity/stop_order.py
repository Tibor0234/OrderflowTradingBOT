from dash import html
from trading.market_entities.stop_order import StopOrder, LiquidationOrder
from trading.market_entities.utils import Side
from visualizers.market_entity.base import MarketEntityVisualizer
from visualizers.utils import format_number

class StopOrderVisualizer(MarketEntityVisualizer):
    def __init__(self, stop_orders: list[StopOrder]):
        self.stop_orders = stop_orders

    def _visible_orders(self):
        return [order for order in self.stop_orders if not isinstance(order, LiquidationOrder)]

    def get_shapes(self):
        shapes = []

        for order in self._visible_orders():
            if order.price is None:
                continue

            price = float(order.price)
            is_long = order.side == Side.BUY

            # ---- STOP VONAL PAPER KOORDINÁTÁKKAL ----
            shapes.append(dict(
                type="line",
                xref="paper",
                yref="y",
                x0=0,
                x1=1,
                y0=price,
                y1=price,
                line=dict(
                    color="#4CAF50" if is_long else "#FF5722",
                    width=2,
                    dash="dash"
                )
            ))

        return shapes

    def get_panel_content(self):
        categories = [
            "Side",
            "Close Rate (%)",
            "Stop Price"
        ]

        values = []

        for order in self._visible_orders():
            side = html.Span(
                'BUY' if order.side == Side.BUY else 'SELL',
                style={
                    "color": "green" if order.side == Side.BUY else "#FF5722"
                }
            )

            close_rate_pct = f"{format_number(float(order.close_rate) * 100)}%"
            stop_price = format_number(float(order.price)) if order.price is not None else "-"

            values.append([side, close_rate_pct, stop_price])

        if not values:
            values.append([])

        return categories, values
