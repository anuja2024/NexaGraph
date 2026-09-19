from neo4j import GraphDatabase
from app.ingestion.pipeline import ingest_documents


NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "knowledgegraph123"


driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD),
)


def verify_connection():
    driver.verify_connectivity()


def create_document(tx, document_id):
    tx.run(
        """
        MERGE (document:Document {document_id: $document_id})
        """,
        document_id=document_id,
    )


def create_chunk(tx, chunk):
    tx.run(
        """
        MATCH (document:Document {document_id: $document_id})
        MERGE (chunk:Chunk {chunk_id: $chunk_id})
        SET chunk.page = $page,
            chunk.section = $section,
            chunk.text = $text
        MERGE (document)-[:CONTAINS]->(chunk)
        """,
        document_id=chunk["document_id"],
        chunk_id=chunk["chunk_id"],
        page=chunk["page"],
        section=chunk["section"],
        text=chunk["text"],
    )

def create_entity(tx, chunk_id, entity):
    tx.run(
        """
        MATCH (chunk:Chunk {chunk_id: $chunk_id})

        MERGE (entity:Entity {
            name: $name,
            type: $type
        })

        MERGE (chunk)-[:MENTIONS]->(entity)
        """,
        chunk_id=chunk_id,
        name=entity["text"],
        type=entity["label"],
    )

def index_entities(chunks):
    from app.graph.entity_extractor import extract_entities

    with driver.session() as session:
        for chunk in chunks:
            entities = extract_entities(chunk["text"])

            for entity in entities:
                session.execute_write(
                    create_entity,
                    chunk["chunk_id"],
                    entity,
                )


def create_entity_relationship(tx, entity_a, entity_b, chunk_id):
    tx.run(
        """
        MATCH (a:Entity {
            name: $name_a,
            type: $type_a
        })

        MATCH (b:Entity {
            name: $name_b,
            type: $type_b
        })

        MERGE (a)-[r:CO_OCCURS_WITH]-(b)

        SET r.source_chunk_ids =
            CASE
                WHEN $chunk_id IN coalesce(r.source_chunk_ids, [])
                THEN coalesce(r.source_chunk_ids, [])
                ELSE coalesce(r.source_chunk_ids, []) + $chunk_id
            END

        REMOVE r.source_chunk_id
        """,
        name_a=entity_a["text"],
        type_a=entity_a["label"],
        name_b=entity_b["text"],
        type_b=entity_b["label"],
        chunk_id=chunk_id,
    )

def index_entity_relationships(chunks):
    from itertools import combinations

    from app.graph.entity_extractor import extract_entities

    with driver.session() as session:
        for chunk in chunks:
            entities = extract_entities(chunk["text"])

            unique_entities = {
                (
                    entity["text"],
                    entity["label"],
                ): entity
                for entity in entities
            }

            for entity_a, entity_b in combinations(
                unique_entities.values(),
                2,
            ):
                session.execute_write(
                    create_entity_relationship,
                    entity_a,
                    entity_b,
                    chunk["chunk_id"],
                ) 

def get_entity_neighbors(entity_name, top_k=10):
    query = """
    MATCH (entity:Entity {name: $entity_name})
          -[r:CO_OCCURS_WITH]-
          (neighbor:Entity)

    RETURN
        neighbor.name AS entity,
        neighbor.type AS type,
        r.source_chunk_ids AS source_chunk_ids

    LIMIT $top_k
    """

    with driver.session() as session:
        result = session.run(
            query,
            entity_name=entity_name,
            top_k=top_k,
        )

        return [record.data() for record in result]                   

def index_chunks(chunks):
    with driver.session() as session:
        document_ids = {
            chunk["document_id"]
            for chunk in chunks
        }

        for document_id in document_ids:
            session.execute_write(
                create_document,
                document_id,
            )

        for chunk in chunks:
            session.execute_write(
                create_chunk,
                chunk,
            )    

if __name__ == "__main__":
    chunks = ingest_documents()

    index_chunks(chunks)
    index_entities(chunks)
    index_entity_relationships(chunks)

    print(
        f"Indexed {len(chunks)} chunks, "
        "entities, and entity relationships."
    )
    print(get_entity_neighbors("Siemens", top_k=10))

    driver.close()