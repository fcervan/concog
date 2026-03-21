from .base_parser import BaseParser

class XptoParser(BaseParser):

    def parse(self, arquivo):
        # aqui entra seu código do openpyxl
        # retorna lista de JSONs (um por empresa)
        return [
            {"a": 1},
            {"b": 2}
        ]