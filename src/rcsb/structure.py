import requests
from .utils import get_json, post_graphql
from .constants import RCSB_DATA_API, TIMEOUT

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

def get_validation_report(pdb_id: str) -> dict:
    pdb_id = pdb_id.upper()
    try:
        data = get_json(f"{RCSB_DATA_API}{pdb_id}")
        
        info = data.get("rcsb_entry_info") or {}
        
        report = {
            "pdb_id": pdb_id,
            "resolution": info.get("resolution_combined") or [info.get("diffrn_resolution_high", {}).get("value")],
            "quality_assessment": "Unknown"
        }
        
        res = report.get('resolution')
        if res and isinstance(res, list) and res[0]:
            try:
                val = float(res[0])
                if val < 1.5:
                    report["quality_assessment"] = "Excellent (<1.5 A)"
                elif val < 2.0:
                    report["quality_assessment"] = "Good (<2.0 A)"
                elif val < 3.0:
                    report["quality_assessment"] = "Acceptable"
                else:
                    report["quality_assessment"] = "Poor (>3.0 A)"
            except:
                pass
                
        return report

    except Exception as e:
        return {"error": f"Validation fetch failed: {str(e)}"}

def download_structure(pdb_id: str, file_format: str = "pdb") -> str:
    pdb_id = pdb_id.lower()
    valid_formats = ["pdb", "cif", "xml"]
    if file_format not in valid_formats:
        return f"Error: Invalid format '{file_format}'. Valid formats are: {', '.join(valid_formats)}"
    
    ext = "cif" if file_format == "mmcif" else file_format
    
    url = f"https://files.rcsb.org/download/{pdb_id}.{ext}"
    
    try:
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        return r.text
    except Exception as e:
        return f"Error downloading structure: {str(e)}"
