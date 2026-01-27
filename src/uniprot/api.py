import httpx
from typing import Optional

UNIPROT_BASE = "https://rest.uniprot.org/uniprotkb"
TIMEOUT = 30.0


def get_entry(uniprot_id: str) -> dict:
    try:
        clean_id = uniprot_id.strip().upper()
        
        url = f"{UNIPROT_BASE}/{clean_id}.json"
        
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(url)
            
            if response.status_code == 404:
                return {"error": f"UniProt entry not found: {clean_id}"}
            
            response.raise_for_status()
            data = response.json()
        
        protein_name = "Unknown"
        if "proteinDescription" in data:
            rec_name = data["proteinDescription"].get("recommendedName", {})
            if "fullName" in rec_name:
                protein_name = rec_name["fullName"].get("value", "Unknown")
        
        gene_names = []
        for gene in data.get("genes", []):
            if "geneName" in gene:
                gene_names.append(gene["geneName"].get("value", ""))
        
        organism = "Unknown"
        if "organism" in data:
            organism = data["organism"].get("scientificName", "Unknown")
        
        function_text = ""
        for comment in data.get("comments", []):
            if comment.get("commentType") == "FUNCTION":
                for text in comment.get("texts", []):
                    function_text = text.get("value", "")
                    break
        
        go_terms = extract_go_terms(data)
        
        pathways = extract_pathways(data)
        
        seq_info = {}
        if "sequence" in data:
            seq_info = {
                "length": data["sequence"].get("length", 0),
                "mass": data["sequence"].get("molWeight", 0),
                "sequence": data["sequence"].get("value", "")[:200] + "..." if len(data["sequence"].get("value", "")) > 200 else data["sequence"].get("value", "")
            }
        
        return {
            "accession": data.get("primaryAccession", clean_id),
            "protein_name": protein_name,
            "gene_names": gene_names,
            "organism": organism,
            "function": function_text[:500] + "..." if len(function_text) > 500 else function_text,
            "go_terms": go_terms,
            "pathways": pathways,
            "sequence_info": seq_info
        }
        
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error: {e.response.status_code}"}
    except Exception as e:
        return {"error": f"Failed to fetch UniProt entry: {str(e)}"}


def extract_go_terms(data: dict) -> dict:
    """Extract GO terms organized by category."""
    go_terms = {
        "molecular_function": [],
        "biological_process": [],
        "cellular_component": []
    }
    
    for xref in data.get("uniProtKBCrossReferences", []):
        if xref.get("database") == "GO":
            go_id = xref.get("id", "")
            
            go_name = ""
            go_category = ""
            for prop in xref.get("properties", []):
                if prop.get("key") == "GoTerm":
                    value = prop.get("value", "")
                    if ":" in value:
                        prefix, go_name = value.split(":", 1)
                        if prefix == "F":
                            go_category = "molecular_function"
                        elif prefix == "P":
                            go_category = "biological_process"
                        elif prefix == "C":
                            go_category = "cellular_component"
            
            if go_category and go_name:
                go_terms[go_category].append({
                    "id": go_id,
                    "name": go_name.strip()
                })
    
    for cat in go_terms:
        go_terms[cat] = go_terms[cat][:5]
    
    return go_terms


def extract_pathways(data: dict) -> list:
    pathways = []
    
    for xref in data.get("uniProtKBCrossReferences", []):
        db = xref.get("database", "")
        
        if db in ["Reactome", "KEGG", "WikiPathways"]:
            pathway_id = xref.get("id", "")
            pathway_name = ""
            
            for prop in xref.get("properties", []):
                if prop.get("key") == "PathwayName":
                    pathway_name = prop.get("value", "")
            
            if pathway_id:
                pathways.append({
                    "database": db,
                    "id": pathway_id,
                    "name": pathway_name
                })
    
    return pathways[:10]


def search_proteins(query: str, organism: str = "human", limit: int = 10) -> list:
    try:
        search_query = f"({query})"
        if organism:
            search_query += f" AND (organism_name:{organism})"
        
        url = f"{UNIPROT_BASE}/search"
        params = {
            "query": search_query,
            "format": "json",
            "size": limit,
            "fields": "accession,protein_name,gene_names,organism_name"
        }
        
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        
        results = []
        for entry in data.get("results", []):
            protein_name = "Unknown"
            if "proteinDescription" in entry:
                rec_name = entry["proteinDescription"].get("recommendedName", {})
                if "fullName" in rec_name:
                    protein_name = rec_name["fullName"].get("value", "Unknown")
            
            gene_names = []
            for gene in entry.get("genes", []):
                if "geneName" in gene:
                    gene_names.append(gene["geneName"].get("value", ""))
            
            results.append({
                "accession": entry.get("primaryAccession", ""),
                "protein_name": protein_name,
                "gene_names": gene_names,
                "organism": entry.get("organism", {}).get("scientificName", "Unknown")
            })
        
        return results
        
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]


def get_protein_features(uniprot_id: str) -> dict:
    try:
        clean_id = uniprot_id.strip().upper()
        url = f"{UNIPROT_BASE}/{clean_id}.json"
        
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(url)
            
            if response.status_code == 404:
                return {"error": f"UniProt entry not found: {clean_id}"}
            
            response.raise_for_status()
            data = response.json()
        
        features = {
            "domains": [],
            "active_sites": [],
            "binding_sites": [],
            "modifications": [],
            "other": []
        }
        
        for feat in data.get("features", []):
            feat_type = feat.get("type", "")
            feat_info = {
                "type": feat_type,
                "description": feat.get("description", ""),
                "start": feat.get("location", {}).get("start", {}).get("value"),
                "end": feat.get("location", {}).get("end", {}).get("value")
            }
            
            if feat_type == "Domain":
                features["domains"].append(feat_info)
            elif feat_type == "Active site":
                features["active_sites"].append(feat_info)
            elif feat_type == "Binding site":
                features["binding_sites"].append(feat_info)
            elif feat_type in ["Modified residue", "Glycosylation", "Phosphorylation"]:
                features["modifications"].append(feat_info)
            else:
                features["other"].append(feat_info)
        
        for cat in features:
            features[cat] = features[cat][:10]
        
        return {
            "accession": clean_id,
            "features": features
        }
        
    except Exception as e:
        return {"error": f"Failed to get features: {str(e)}"}
