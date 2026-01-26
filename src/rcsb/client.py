from . import search, structure, ligands

class RcsbClient:
    def __init__(self):
        pass

    def search_structures(self, query: str, limit: int = 10, resolution: str = None, method: str = None) -> list:
        return search.search_structures(query, limit, resolution, method)

    def search_by_uniprot(self, uniprot_id: str, limit: int = 10) -> list:
        return search.search_by_uniprot(uniprot_id, limit)

    def get_pdb_summary(self, pdb_id: str) -> dict:
        return structure.get_pdb_summary(pdb_id)
        
    def get_validation_report(self, pdb_id: str) -> dict:
        return structure.get_validation_report(pdb_id)
        
    def download_structure(self, pdb_id: str, file_format: str = "pdb") -> str:
        return structure.download_structure(pdb_id, file_format)

    def get_pdb_ligands(self, pdb_id: str) -> list:
        return ligands.get_pdb_ligands(pdb_id)

    def get_binding_pocket(self, pdb_id: str, ligand_id: str = None) -> dict:
        return ligands.get_binding_pocket(pdb_id, ligand_id)
