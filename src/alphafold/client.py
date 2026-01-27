from . import api


class AlphaFoldClient:
    
    def __init__(self):
        print("[OK] AlphaFold Client initialized (no API key required)")
    
    def get_prediction(self, uniprot_id: str) -> dict:
        return api.get_prediction(uniprot_id)
    
    def download_structure(self, uniprot_id: str, format: str = "pdb") -> dict:
        return api.download_structure(uniprot_id, format)
