import spacy
import random
from spacy.training.example import Example
from backend.app.core.ai.nlp.spacy.converter import converter


def treinar():
    TRAIN_DATA = converter("backend/app/core/ai/nlp/spacy/labelstudio.json")

    # verificar_anotacoes(TRAIN_DATA)

    nlp = spacy.blank("pt")

    ner = nlp.add_pipe("ner")

    # adicionar labels
    for texto, anotacoes in TRAIN_DATA:
        for ent in anotacoes["entities"]:
            ner.add_label(ent[2])

    optimizer = nlp.begin_training()

    for epoch in range(100):
        random.shuffle(TRAIN_DATA)
        losses = {}

        for texto, anotacoes in TRAIN_DATA:
            doc = nlp.make_doc(texto)
            example = Example.from_dict(doc, anotacoes)
            nlp.update([example], losses=losses)

        print(f"Epoch {epoch} - Losses: {losses}")

    dir_modelo_spacy = "backend/app/core/ai/nlp/spacy/modelo_spacy"
    nlp.to_disk(dir_modelo_spacy)
    print(f"\n✅ Modelo salvo em {dir_modelo_spacy}")


def verificar_anotacoes(TRAIN_DATA):
    nlp_debug = spacy.blank("pt")

    for i, (texto, anotacoes) in enumerate(TRAIN_DATA):
        print(f"\n=== Exemplo {i} ===")
        print(f"Texto: {texto}")

        doc = nlp_debug.make_doc(texto)
        print(f"Tokens: {[t.text for t in doc]}")
        print(f"Token boundaries: {[(t.idx, t.idx + len(t.text)) for t in doc]}")

        for ent in anotacoes["entities"]:
            start, end, label = ent
            texto_ent = texto[start:end]
            print(f"Entidade: '{texto_ent}' ({start}, {end}, {label})")

            # Verifica se os índices batem com tokens
            tokens_afetados = [t for t in doc if t.idx >= start and t.idx < end]
            print(f"Tokens afetados: {[t.text for t in tokens_afetados]}")

            # Verifica alinhamento
            if not tokens_afetados:
                print("⚠️ ALERTA: Nenhum token encontrado para esta entidade!")
                # print(texto)
    exit()


if __name__ == "__main__":
    treinar()