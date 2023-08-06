from dataclasses import dataclass, field


@dataclass
class GuiBannerConfig:
    header_html: str = field()
    footer_html: str = field()
