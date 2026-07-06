from rcsb.structure import download_structure


def fetch_pdb_text(pdb_id: str) -> str:
    content = download_structure(pdb_id, "pdb")
    if content.startswith("Error"):
        raise ValueError(content)
    return content
