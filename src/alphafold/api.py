import httpx
from typing import Optional

ALPHAFOLD_BASE = "https://alphafold.ebi.ac.uk/api"
TIMEOUT = 30.0


def get_prediction(uniprot_id: str) -> dict:
    try:
        clean_id = uniprot_id.strip().upper()
        url = f"{ALPHAFOLD_BASE}/prediction/{clean_id}"
        
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(url)
            
            if response.status_code == 404:
                return {"error": f"No AlphaFold prediction found for {clean_id}"}
            
            response.raise_for_status()
            data = response.json()
        
        if not data:
            return {"error": f"No prediction data for {clean_id}"}
        
        prediction = data[0] if isinstance(data, list) else data
        
        return {
            "uniprot_id": clean_id,
            "entry_id": prediction.get("entryId", ""),
            "gene": prediction.get("gene", ""),
            "organism": prediction.get("organismScientificName", ""),
            "pdb_url": prediction.get("pdbUrl", ""),
            "cif_url": prediction.get("cifUrl", ""),
            "pae_image_url": prediction.get("paeImageUrl", ""),
            "model_created": prediction.get("modelCreatedDate", ""),
            "latest_version": prediction.get("latestVersion", 1),
            "sequence_length": prediction.get("uniprotEnd", 0) - prediction.get("uniprotStart", 0) + 1
        }
        
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error: {e.response.status_code}"}
    except Exception as e:
        return {"error": f"Failed to get AlphaFold prediction: {str(e)}"}


def download_structure(uniprot_id: str, format: str = "pdb") -> dict:
    try:
        result = get_prediction(uniprot_id)
        if "error" in result:
            return result
        
        if format.lower() == "pdb":
            url = result.get("pdb_url")
        else:
            url = result.get("cif_url")
        
        if not url:
            return {"error": f"No {format} URL available for {uniprot_id}"}
        
        with httpx.Client(timeout=60.0) as client:
            response = client.get(url)
            response.raise_for_status()
            content = response.text
        
        return {
            "uniprot_id": uniprot_id,
            "format": format,
            "content": content[:5000] + "..." if len(content) > 5000 else content,
            "full_length": len(content)
        }
        
    except Exception as e:
        return {"error": f"Failed to download structure: {str(e)}"}


def search_by_sequence(sequence: str) -> dict:
    try:
        clean_seq = ''.join(c for c in sequence.upper() if c.isalpha())
        
        if len(clean_seq) < 20:
            return {"error": "Sequence too short (min 20 residues)"}
        
        return {"error": "Sequence search not supported by AlphaFold API. Use UniProt ID instead."}
        
    except Exception as e:
        return {"error": f"Sequence search failed: {str(e)}"}
