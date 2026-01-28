from . import api


class KeggClient:
    
    def __init__(self):
        print("[OK] KEGG Client initialized (free for academic use)")
    
    def search_pathway(self, query: str, organism: str = "hsa") -> list:
        return api.search_pathway(query, organism)
    
    def get_pathway_info(self, pathway_id: str) -> dict:
        return api.get_pathway_info(pathway_id)
    
    def get_pathway_genes(self, pathway_id: str) -> list:
        return api.get_pathway_genes(pathway_id)
    
    def get_gene_pathways(self, gene_id: str, organism: str = "hsa") -> list:
        return api.get_gene_pathways(gene_id, organism)
