from .cwm import CwmParser
from .xpto import XptoParser

PARSERS = {
    "cwm": CwmParser,
    "xpto": XptoParser,
}