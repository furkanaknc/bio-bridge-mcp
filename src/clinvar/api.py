import os
from Bio import Entrez
import httpx
from shared.env import load_project_env

load_project_env()

CLINVAR_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
CLINVAR_ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
TIMEOUT = 30.0


def search_variants(query: str, limit: int = 10) -> list:
    try:
        if not Entrez.email:
            Entrez.email = os.getenv("NCBI_EMAIL")
            if not Entrez.email:
                return [{"error": "NCBI_EMAIL is not set."}]
        
        api_key = os.getenv("NCBI_API_KEY")
        
        params = {
            "db": "clinvar",
            "term": query,
            "retmax": limit,
            "retmode": "json"
        }
        if api_key:
            params["api_key"] = api_key
        
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(CLINVAR_ESEARCH, params=params)
            response.raise_for_status()
            data = response.json()
        
        id_list = data.get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return []
        
        return get_variant_summaries(id_list, api_key)
        
    except Exception as e:
        return [{"error": f"ClinVar search failed: {str(e)}"}]


def get_variant_summaries(id_list: list, api_key: str = None) -> list:
    try:
        params = {
            "db": "clinvar",
            "id": ",".join(id_list),
            "retmode": "json"
        }
        if api_key:
            params["api_key"] = api_key
        
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(CLINVAR_ESUMMARY, params=params)
            response.raise_for_status()
            data = response.json()
        
        results = []
        result_data = data.get("result", {})
        
        for uid in id_list:
            if uid in result_data:
                item = result_data[uid]
                
                clinical_sig = "Unknown"
                if "clinical_significance" in item:
                    sig = item["clinical_significance"]
                    if isinstance(sig, dict):
                        clinical_sig = sig.get("description", "Unknown")
                    else:
                        clinical_sig = str(sig)
                
                gene_info = item.get("genes", [])
                gene_symbol = gene_info[0].get("symbol", "N/A") if gene_info and isinstance(gene_info[0], dict) else "N/A"
                
                results.append({
                    "uid": uid,
                    "title": item.get("title", "N/A"),
                    "gene": gene_symbol,
                    "clinical_significance": clinical_sig,
                    "variation_type": item.get("obj_type", "N/A"),
                    "accession": item.get("accession", "N/A")
                })
        
        return results
        
    except Exception as e:
        return [{"error": f"Failed to get variant summaries: {str(e)}"}]


def get_variant_details(variant_id: str) -> dict:
    try:
        if not Entrez.email:
            Entrez.email = os.getenv("NCBI_EMAIL")
            if not Entrez.email:
                return {"error": "NCBI_EMAIL is not set."}
        
        api_key = os.getenv("NCBI_API_KEY")
        
        handle = Entrez.efetch(
            db="clinvar",
            id=variant_id,
            rettype="vcv",
            retmode="xml"
        )
        
        from xml.etree import ElementTree
        tree = ElementTree.parse(handle)
        handle.close()
        root = tree.getroot()
        
        result = {
            "variant_id": variant_id,
            "title": "",
            "gene": "",
            "clinical_significance": "",
            "review_status": "",
            "conditions": [],
            "molecular_consequence": "",
            "chromosomal_location": ""
        }
        
        for elem in root.iter():
            if elem.tag == "Name" and not result["title"]:
                result["title"] = elem.text or ""
            elif elem.tag == "GeneSymbol":
                result["gene"] = elem.text or ""
            elif elem.tag == "Description" and "pathogenic" in (elem.text or "").lower():
                result["clinical_significance"] = elem.text or ""
        
        return result
        
    except Exception as e:
        return {"error": f"Failed to get variant details: {str(e)}"}


def search_by_gene(gene_symbol: str, significance: str = None) -> list:
    query = f"{gene_symbol}[gene]"
    if significance:
        query += f" AND {significance}[clinical_significance]"
    return search_variants(query)


def search_by_condition(condition: str, limit: int = 10) -> list:
    query = f"{condition}[disease]"
    return search_variants(query, limit)
