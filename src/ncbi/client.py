import os
from Bio import Entrez
from . import geo, pubmed, blast, sequence
from shared.env import load_project_env

load_project_env()

class NcbiClient:
    def __init__(self):
        self.email = os.getenv("NCBI_EMAIL", "anonymous@email.local")
        Entrez.email = self.email
        
        if self.email == "anonymous@email.local":
            print("[INFO] No NCBI_EMAIL set - using default. Set NCBI_EMAIL env var for better rate limits.")
        
        self.api_key = os.getenv("NCBI_API_KEY")
        if self.api_key:
            Entrez.api_key = self.api_key
            print("[OK] NCBI API Key active (10 req/s)")
        else:
            print("[INFO] No NCBI API Key found (3 req/s limit) - Set NCBI_API_KEY env var for higher limits")

    def search_geo(self, query: str, limit: int = 5) -> list:
        return geo.search(query, limit)

    def fetch_geo_details(self, accession: str) -> dict:
        return geo.fetch_metadata(accession)
    
    def search_pubmed(self, query: str, limit: int = 5) -> list:
        return pubmed.search(query, limit)
    
    def blast_sequence(self, seq: str, database: str = "nt", program: str = "blastn", max_hits: int = 10) -> dict:
        return blast.run_blast(seq, database, program, max_hits)
    
    def quick_blast(self, seq: str) -> dict:
        return blast.quick_blast(seq)
    
    def fetch_sequence(self, accession: str, seq_type: str = "nucleotide") -> dict:
        return sequence.fetch_sequence(accession, seq_type)
    
    def get_gene_info(self, gene_symbol: str, organism: str = "human") -> dict:
        return sequence.get_gene_info(gene_symbol, organism)
    
    def search_genes(self, query: str, organism: str = "human", limit: int = 10) -> list:
        return sequence.search_genes(query, organism, limit)
    
    def analyze_geo_series(self, gse_id: str) -> dict:
        return geo.analyze_series(gse_id)
    
    def classify_geo_samples(self, gse_id: str, max_samples: int = 20) -> dict:
        return geo.classify_samples(gse_id, max_samples)
    
    def advanced_pubmed_search(self, gene: str = None, disease: str = None, 
                               drug: str = None, author: str = None,
                               year_from: int = None, year_to: int = None,
                               limit: int = 10) -> list:
        return pubmed.advanced_search(gene, disease, drug, author, year_from, year_to, limit)
    
    def get_pubmed_abstract(self, pmid: str) -> dict:
        return pubmed.get_abstract(pmid)
