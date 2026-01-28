from . import api


class ClinVarClient:
    
    def __init__(self):
        print("[OK] ClinVar Client initialized (uses NCBI API key if available)")
    
    def search_variants(self, query: str, limit: int = 10) -> list:
        return api.search_variants(query, limit)
    
    def get_variant_details(self, variant_id: str) -> dict:
        return api.get_variant_details(variant_id)
    
    def search_by_gene(self, gene_symbol: str, significance: str = None) -> list:
        return api.search_by_gene(gene_symbol, significance)
    
    def search_by_condition(self, condition: str, limit: int = 10) -> list:
        return api.search_by_condition(condition, limit)
