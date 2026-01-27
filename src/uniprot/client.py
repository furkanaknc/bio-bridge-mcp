from . import api


class UniProtClient:
    
    def __init__(self):
        print("[OK] UniProt Client initialized (no API key required)")
    
    def get_entry(self, uniprot_id: str) -> dict:
        return api.get_entry(uniprot_id)
    
    def search_proteins(self, query: str, organism: str = "human", limit: int = 10) -> list:
        return api.search_proteins(query, organism, limit)
    
    def get_protein_features(self, uniprot_id: str) -> dict:
        return api.get_protein_features(uniprot_id)
    
    def get_go_terms(self, uniprot_id: str) -> dict:
        result = api.get_entry(uniprot_id)
        if "error" in result:
            return result
        return {
            "accession": result.get("accession"),
            "protein_name": result.get("protein_name"),
            "go_terms": result.get("go_terms", {})
        }
    
    def get_pathways(self, uniprot_id: str) -> dict:
        result = api.get_entry(uniprot_id)
        if "error" in result:
            return result
        return {
            "accession": result.get("accession"),
            "protein_name": result.get("protein_name"),
            "pathways": result.get("pathways", [])
        }
