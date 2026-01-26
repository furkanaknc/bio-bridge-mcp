import requests
from .constants import RCSB_SEARCH_API, TIMEOUT

def search_structures(query_text: str, limit: int = 10, resolution: str = None, method: str = None) -> list:
    if not query_text:
        return []

    text_query_node = {
        "type": "terminal",
        "service": "full_text",
        "parameters": {
            "value": query_text
        }
    }

    query_nodes = [text_query_node]

    if method:
        query_nodes.append({
            "type": "terminal",
            "service": "text",
            "parameters": {
                "attribute": "exptl.method",
                "operator": "exact_match",
                "value": method.upper()
            }
        })

    if resolution:
        operator = "range"
        value = {}
        
        if "-" in resolution:
            parts = resolution.split("-")
            if len(parts) == 2:
                try:
                    value = {"from": float(parts[0]), "to": float(parts[1])}
                except ValueError:
                    pass
        elif resolution.startswith("<"):
            try:
                val = float(resolution[1:])
                value = {"to": val, "include_upper": False}
            except ValueError:
                pass
        elif resolution.startswith(">"):
             try:
                val = float(resolution[1:])
                value = {"from": val, "include_lower": False}
             except ValueError:
                pass
        else:
             try:
                 val = float(resolution)
                 value = {"to": val, "include_upper": True}
             except ValueError:
                 pass

        if value:
             query_nodes.append({
                "type": "terminal",
                "service": "text",
                "parameters": {
                    "attribute": "rcsb_entry_info.resolution_combined",
                    "operator": "range",
                    "value": value
                }
            })

    if len(query_nodes) > 1:
        final_query = {
            "type": "group",
            "logical_operator": "and",
            "nodes": query_nodes
        }
    else:
        final_query = text_query_node

    search_request = {
        "query": final_query,
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
        r = requests.post(RCSB_SEARCH_API, json=search_request, timeout=TIMEOUT)
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
