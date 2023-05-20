from dataclasses import dataclass


@dataclass
class GuiBannerConfig:
    header_html: str
    footer_html: str
