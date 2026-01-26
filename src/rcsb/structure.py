from .utils import get_json, post_graphql
from .constants import RCSB_DATA_API

def get_pdb_summary(pdb_id: str) -> dict:
    pdb_id = pdb_id.upper()
    try:
        data = get_json(f"{RCSB_DATA_API}{pdb_id}")
    except Exception as e:
        return {"error": f"Could not fetch data for {pdb_id}: {str(e)}"}

    title = data.get("struct", {}).get("title", "Unknown Title")
    classification = data.get("struct_keywords", {}).get("pdbx_keywords", "Unknown")

    gql_query = """
    query($pdbId: String!) {
      entry(entry_id: $pdbId) {
        polymer_entities {
          rcsb_polymer_entity_container_identifiers { entity_id }
          rcsb_polymer_entity_annotation { type description annotation_id }
        }
      }
    }
    """
    mutations = []
    has_mutation_flag = False

    try:
        gql_data = post_graphql(gql_query, {"pdbId": pdb_id})
        polymer_entities = (gql_data.get("entry") or {}).get("polymer_entities", []) or []
        for entity in polymer_entities:
            annotations = entity.get("rcsb_polymer_entity_annotation") or []
            mutation_anns = [a for a in annotations if (a.get("type") or "").lower() == "mutation"]
            entity_id = (entity.get("rcsb_polymer_entity_container_identifiers") or {}).get("entity_id")
            if mutation_anns:
                has_mutation_flag = True
                mutations.append({
                    "entity_id": entity_id,
                    "count": len(mutation_anns),
                    "details": [a.get("description") for a in mutation_anns if a.get("description")]
                })
    except Exception as e:
        return {
            "pdb_id": pdb_id,
            "title": title,
            "classification": classification,
            "has_mutations": None,
            "mutation_details": [],
            "warning": f"GraphQL mutation query failed: {str(e)}",
        }

    return {
        "pdb_id": pdb_id,
        "title": title,
        "classification": classification,
        "has_mutations": has_mutation_flag,
        "mutation_details": mutations,
        "note": "Mutation annotations are not always complete; if needed, switch to rcsb_mutation_count-based check.",
    }
