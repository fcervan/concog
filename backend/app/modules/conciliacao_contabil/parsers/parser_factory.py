from .parser_resgistry import PARSERS

class ParserFactory:

    @staticmethod
    def get_parser(nome_parser: str):
        parser_class = PARSERS.get(nome_parser)

        if not parser_class:
            raise ValueError(f"Parser '{nome_parser}' não encontrado")

        return parser_class()