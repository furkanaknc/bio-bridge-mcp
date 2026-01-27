import os
from dotenv import load_dotenv
from Bio import Entrez
from . import geo, pubmed, blast, sequence

load_dotenv()

class NcbiClient:
    def __init__(self):
        self.email = os.getenv("NCBI_EMAIL")
        if not self.email:
            raise ValueError("NCBI_EMAIL environment variable is not set.")
        Entrez.email = self.email
        
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
