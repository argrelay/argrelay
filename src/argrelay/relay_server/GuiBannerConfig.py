from dataclasses import dataclass, field


@dataclass
class GuiBannerConfig:
    meter_html: str = field()
    tagline_html: str = field()
    header_html: str = field()
    footer_html: str = field()
