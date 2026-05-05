import json
import spacy


class AgruparLancamentoService:

    def __init__(self):
        self.nlp = spacy.load("backend/app/core/ai/nlp/spacy/modelo_spacy")

    def agrupar(self, lancamentos):
        lancamentos = json.loads(lancamentos)
        resultado = {}

        for lancamento in lancamentos['lancamentos']:
            historico = lancamento["historico"]
            ids = self.extrair(historico)

            if ids:  # Se encontrou algum identificador
                id_encontrado = ids[0]  # Pega o primeiro identificador encontrado

                # Inicializa a lista para o identificador se não existir
                if id_encontrado not in resultado:
                    resultado[id_encontrado] = []

                # Adiciona o histórico ao grupo do identificador
                resultado[id_encontrado].append(lancamento)
            else:
                print(f"⚠️ - Identificador não encontrado para o lançamento: {historico}")

        return resultado

    def extrair(self, texto):
        doc = self.nlp(texto)

        ids = [ent.text for ent in doc.ents if ent.label_ == "IDENTIFICADOR"]

        return ids