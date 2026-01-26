import requests
from .constants import RCSB_SEARCH_API, TIMEOUT

def search_structures(query_text: str, limit: int = 10) -> list:
    if not query_text:
        return []

    search_query = {
        "query": {
            "type": "terminal",
            "service": "full_text",
            "parameters": {
                "value": query_text
            }
        },
        "return_type": "entry",
        "request_options": {
            "paginate": {
                "start": 0,
                "rows": limit
            },
            "results_content_type": ["experimental"],
            "sort": [
                {
                    "sort_by": "score",
                    "direction": "desc"
                }
            ]
        }
    }

    try:
        r = requests.post(RCSB_SEARCH_API, json=search_query, timeout=TIMEOUT)
        r.raise_for_status()

        if r.status_code == 204:
            return []
            
        data = r.json()
        result_set = data.get("result_set", [])

        results = []
        for entry in result_set:
            results.append({
                "pdb_id": entry.get("identifier"),
                "score": entry.get("score")
            })
            
        return results

    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]

def search_by_uniprot(uniprot_id: str, limit: int = 10) -> list:
    if not uniprot_id:
        return []
        
    search_query = {
        "query": {
            "type": "terminal",
            "service": "text",
            "parameters": {
                "attribute": "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession",
                "operator": "exact_match",
                "value": uniprot_id
            }
        },
        "return_type": "entry",
        "request_options": {
            "paginate": {
                "start": 0,
                "rows": limit
            },
            "results_content_type": ["experimental"],
            "sort": [
                {
                    "sort_by": "score",
                    "direction": "desc"
                }
            ]
        }
    }

    try:
        r = requests.post(RCSB_SEARCH_API, json=search_query, timeout=TIMEOUT)
        if r.status_code == 204:
            return []
        r.raise_for_status()
        
        data = r.json()
        result_set = data.get("result_set", [])
        
        results = []
        for entry in result_set:
            results.append({
                "pdb_id": entry.get("identifier"),
                "score": entry.get("score")
            })
            
        return results

    except Exception as e:
        return [{"error": f"UniProt search failed: {str(e)}"}]
