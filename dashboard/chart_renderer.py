import plotly.graph_objects as go
from visualizers.market_entity.base import MarketEntityVisualizer
from visualizers.price_chart.base import PriceChartVisualizer
from visualizers.context_chart.base import ContextChartVisualizer
from visualizers.data_analysis.equity_curve import EquityCurveVisualizer

class ChartRenderer:
    def __init__(self):
        self.axis_count = 1
        self.axes_assigned = False

    def build_price_chart(self, execution_visualizers: list[MarketEntityVisualizer], price_visualizers: list[PriceChartVisualizer]):

        fig = go.Figure()
        shapes = []

        for visualizer in execution_visualizers:
            shapes.extend(visualizer.get_shapes())

        for visualizer in price_visualizers:
            traces = visualizer.get_traces()
            fig.add_traces(traces)
            shapes.extend(visualizer.get_shapes())

        fig.update_layout(self._price_layout(shapes))

        return fig

    def build_context_chart(self, visualizers: list[ContextChartVisualizer]):

        fig = go.Figure()
        shapes = []
        has_volume_profile = any(
            getattr(visualizer, "uses_volume_axis", False)
            for visualizer in visualizers
        )

        for visualizer in visualizers:
            fig.add_traces(visualizer.get_traces())
            shapes.extend(visualizer.get_shapes())

        fig.update_layout(self._context_layout(shapes, has_volume_profile))

        return fig

    def build_equity_curve(self, visualizer: EquityCurveVisualizer):

        fig = go.Figure()
        shapes = []

        if visualizer:
            fig.add_traces(visualizer.get_traces())
            shapes.extend(visualizer.get_shapes())

        fig.update_layout(self._equity_layout(shapes))

        return fig

    def _base_layout(self):

        return dict(
            autosize=True,
            plot_bgcolor="black",
            paper_bgcolor="#1e1e1e",
            font=dict(color="white"),
            showlegend=True,
            margin=dict(l=0, r=0, t=10, b=0)
        )

    def _price_layout(self, shapes):
        shapes.append(
            dict(
                type="line",
                xref="paper",
                x0=0,
                x1=1,
                yref="paper",
                y0=0.2,
                y1=0.2,
                line=dict(
                    color="rgba(255,255,255,0.2)",
                    width=1
                )
            )
        )

        layout = self._base_layout()

        layout.update(
            xaxis=dict(
                showgrid=False,
                gridcolor="gray",
                linecolor="white",
                rangeslider=dict(visible=False),
                anchor="y2"
            ),
            yaxis=dict(
                showgrid=False,
                gridcolor="gray",
                linecolor="white",
                domain=[0.2, 1]
            ),
            yaxis2=dict(
                showgrid=False,
                linecolor="white",
                zeroline=False,
                domain=[0, 0.2]
            ),
            xaxis2=dict(
                showticklabels=False,
                showgrid=False,
                domain=[0, 0.15],
                anchor="y"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(color="white")
            ),
            shapes=shapes
        )

        return layout

    def _context_layout(self, shapes, has_volume_profile=False):

        layout = self._base_layout()

        layout.update(
            xaxis=dict(
                showgrid=False,
                gridcolor="gray",
                linecolor="white",
                rangeslider=dict(visible=False),
                showticklabels=False,
                domain=[0.2, 1] if has_volume_profile else [0, 1],
                anchor="y",
            ),
            yaxis=dict(
                showgrid=False,
                gridcolor="gray",
                linecolor="white"
            ),
            legend=dict(
                orientation="h",
                x=0.5,
                xanchor="center",
                y=0,
                yanchor="bottom",
                font=dict(size=12),
                bgcolor="rgba(0,0,0,0)"
            ),
            shapes=shapes
        )

        if has_volume_profile:
            layout["xaxis2"] = dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                domain=[0, 0.18],
                anchor="y",
            )

        return layout

    def _equity_layout(self, shapes):

        layout = self._base_layout()

        layout.update(
            xaxis=dict(
                showgrid=False,
                gridcolor="gray",
                linecolor="white",
                showticklabels=False
            ),
            yaxis=dict(
                showgrid=False,
                gridcolor="gray",
                linecolor="white",
            ),
            shapes=shapes
        )

        return layout