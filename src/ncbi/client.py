import os
from dotenv import load_dotenv
from Bio import Entrez
from . import geo, pubmed

load_dotenv()

class NcbiClient:
    def __init__(self):
        self.email = os.getenv("NCBI_EMAIL")
        if not self.email:
            raise ValueError("NCBI_EMAIL environment variable is not set.")
        Entrez.email = self.email

    def search_geo(self, query: str, limit: int = 5) -> list:
        return geo.search(query, limit)

    def fetch_geo_details(self, accession: str) -> dict:
        return geo.fetch_metadata(accession)
    
    def search_pubmed(self, query: str, limit: int = 5) -> list:
        return pubmed.search(query, limit)
