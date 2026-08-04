from visualizer.price_chart_visualizer import PriceChartVisualizer
from model.book_map import BookMap
import plotly.graph_objects as go
from datetime import datetime

class BookMapVisualizer(PriceChartVisualizer):
    def __init__(self, book_map: BookMap):
        self.book_map = book_map

    def get_shapes(self):
        if not self.book_map.content:
            return []

        shapes = []
        prev_time = None

        for snapshot in self.book_map.content:
            # max qty a szín skálázáshoz
            max_qty = max(
                float(b['qty'])
                for side in ['bids', 'asks']
                for b in snapshot[side]
            ) or 1

            # idő konvertálás másodpercre (Plotly datetime kompatibilis)
            curr_time = datetime.fromtimestamp(snapshot['time'] / 1000)

            # ha nincs előző snapshot, x0 legyen egy kis offset
            x0 = datetime.fromtimestamp(prev_time / 1000) if prev_time is not None else curr_time
            x1 = curr_time

            # Először a bids a háttérben, asks előtér
            for side in ['bids', 'asks']:
                for b in snapshot[side]:
                    qty = float(b['qty'])
                    bottom = float(b['bottom'])
                    top = float(b['top'])
                    alpha = 0.3 + 0.7 * qty / max_qty
                    color = f'rgba(0, 0, 255, {alpha})'

                    shapes.append(dict(
                        type="rect",
                        x0=x0,
                        x1=x1,
                        y0=bottom,
                        y1=top,
                        fillcolor=color,
                        line=dict(width=0),
                        layer="below"
                    ))

            prev_time = snapshot['time']

        return shapes