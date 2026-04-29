import json

def converter(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    train_data = []

    for item in data:
        texto = item["text"]
        entidades = []

        for ent in item.get("label", []):
            start = ent["start"]
            end = ent["end"]
            label = ent["labels"][0]

            # padronizar label
            if label == "IDENT":
                label = "IDENTIFICADOR"

            # validação (IMPORTANTE)
            if texto[start:end] != ent["text"]:
                print("⚠️ ERRO DE SPAN:", texto)
                print("Esperado:", ent["text"])
                print("Encontrado:", texto[start:end])
                continue

            entidades.append((start, end, label))

        train_data.append((texto, {"entities": entidades}))

    return train_data


if __name__ == "__main__":
    TRAIN_DATA = converter("backend/app/core/ai/nlp/spacy/labelstudio.json")

    print("Exemplo convertido:\n")
    for item in TRAIN_DATA[:10]:
        print(item)