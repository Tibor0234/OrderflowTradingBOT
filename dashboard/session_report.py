from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Callable

import plotly.graph_objects as go
import plotly.io as pio

from global_services.events.bus import EventBus
from global_services.events.utils import EventBusMsgType


@dataclass(frozen=True)
class SessionReportSnapshot:
    session_number: int | None
    figures: dict[str, go.Figure]
    panels: dict[str, object]


class SessionReport:
    """Captures and exports the dashboard state at session end."""

    def __init__(
        self,
        snapshot_provider: Callable[[], SessionReportSnapshot],
        output_dir: str | Path = "session_reports"
    ):
        self.snapshot_provider = snapshot_provider
        self.output_dir = Path(output_dir)
        EventBus().subscribe(
            EventBusMsgType.SESSION_END,
            self.export_on_session_end
        )

    def export_on_session_end(self):
        snapshot = self.snapshot_provider()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.output_dir / self._filename(snapshot)
        report_path.write_text(self.render(snapshot), encoding="utf-8")
        return report_path

    def render(self, snapshot: SessionReportSnapshot) -> str:
        sections = []
        include_plotlyjs = "cdn"

        for title, figure in snapshot.figures.items():
            sections.append(f"<section><h2>{escape(title)}</h2>")
            sections.append(
                pio.to_html(
                    figure,
                    full_html=False,
                    include_plotlyjs=include_plotlyjs
                )
            )
            sections.append("</section>")
            include_plotlyjs = False

        for title, panel in snapshot.panels.items():
            sections.append(f"<section><h2>{escape(title)}</h2>")
            sections.append(self._component_to_html(panel))
            sections.append("</section>")

        return (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>Session report</title>"
            "<style>body{background:#121212;color:#fff;font-family:Arial,sans-serif}"
            "section{margin:24px 0;padding:12px;background:#1e1e1e}"
            "h2{margin:0 0 8px}table{color:#fff}</style>"
            "</head><body>"
            + "".join(sections)
            + "</body></html>"
        )

    def _filename(self, snapshot: SessionReportSnapshot) -> str:
        if snapshot.session_number is None:
            return "session_unknown.html"
        return f"session_{snapshot.session_number:04d}.html"

    def _component_to_html(self, component) -> str:
        if component is None:
            return ""
        if isinstance(component, (str, int, float)):
            return escape(str(component))
        if isinstance(component, (list, tuple)):
            return "".join(self._component_to_html(item) for item in component)
        if not hasattr(component, "to_plotly_json"):
            return escape(str(component))

        component_data = component.to_plotly_json()
        tag = component_data["type"].lower()
        props = component_data.get("props", {})
        children = props.get("children", [])
        attributes = []

        for name, value in props.items():
            if value is None or name in {"children", "style"}:
                continue
            if name == "className":
                name = "class"
            attributes.append(f' {name}="{escape(str(value))}"')

        style = props.get("style")
        if style:
            css_style = ";".join(
                f"{self._to_css_name(name)}:{value}"
                for name, value in style.items()
            )
            attributes.append(f' style="{escape(css_style)}"')

        return (
            f"<{tag}{''.join(attributes)}>"
            f"{self._component_to_html(children)}</{tag}>"
        )

    def _to_css_name(self, name: str) -> str:
        return "".join(
            f"-{character.lower()}" if character.isupper() else character
            for character in name
        )
