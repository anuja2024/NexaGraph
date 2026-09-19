import re

from transformers import pipeline


MODEL_NAME = "Davlan/xlm-roberta-base-ner-hrl"

MIN_CONFIDENCE = 0.70


ner = pipeline(
    "token-classification",
    model=MODEL_NAME,
    aggregation_strategy="simple",
    device=0,
)


def normalize_entity(text: str):
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.strip("-–—,.;:")
    return text


def canonicalize_entity(text: str):
    text = normalize_entity(text)

    replacements = {
        "Dotmatic": "Dotmatics",
        "Innomotics Gmb H": "Innomotics GmbH",
        "Digital Industrie": "Digital Industries",
    }

    return replacements.get(text, text)


def extract_entities(text: str):
    results = ner(text)

    entities = []

    for result in results:
        entity_type = result.get("entity_group")
        confidence = float(result.get("score", 0.0))

        if confidence < MIN_CONFIDENCE:
            continue

        if entity_type not in {"ORG", "LOC"}:
            continue

        entity_text = canonicalize_entity(
            result.get("word", "")
        )

        if not entity_text:
            continue

        entities.append(
            {
                "text": entity_text,
                "label": entity_type,
                "confidence": confidence,
            }
        )

    return entities