import httpx
from typing import Optional

KEGG_BASE = "https://rest.kegg.jp"
TIMEOUT = 30.0


def search_pathway(query: str, organism: str = "hsa") -> list:
    try:
        url = f"{KEGG_BASE}/find/pathway/{query}"
        
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(url)
            response.raise_for_status()
            text = response.text
        
        if not text.strip():
            return []
        
        pathways = []
        for line in text.strip().split('\n'):
            if '\t' in line:
                parts = line.split('\t', 1)
                pathway_id = parts[0].strip()
                pathway_name = parts[1].strip() if len(parts) > 1 else ""
                
                if organism and not pathway_id.startswith(f"path:{organism}"):
                    org_pathway_id = pathway_id.replace("path:map", f"path:{organism}")
                else:
                    org_pathway_id = pathway_id
                
                pathways.append({
                    "id": org_pathway_id.replace("path:", ""),
                    "name": pathway_name
                })
        
        return pathways[:20]
        
    except Exception as e:
        return [{"error": f"Pathway search failed: {str(e)}"}]


def get_pathway_info(pathway_id: str) -> dict:
    try:
        clean_id = pathway_id.strip()
        url = f"{KEGG_BASE}/get/{clean_id}"
        
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(url)
            
            if response.status_code == 404:
                return {"error": f"Pathway not found: {clean_id}"}
            
            response.raise_for_status()
            text = response.text
        
        info = {
            "id": clean_id,
            "name": "",
            "description": "",
            "genes": [],
            "compounds": [],
            "diseases": []
        }
        
        current_section = None
        current_content = []
        
        for line in text.split('\n'):
            if line.startswith('NAME'):
                info["name"] = line.replace('NAME', '').strip()
            elif line.startswith('DESCRIPTION'):
                info["description"] = line.replace('DESCRIPTION', '').strip()
            elif line.startswith('GENE'):
                current_section = 'genes'
                gene_line = line.replace('GENE', '').strip()
                if gene_line:
                    current_content.append(parse_gene_line(gene_line))
            elif line.startswith('COMPOUND'):
                current_section = 'compounds'
            elif line.startswith('DISEASE'):
                current_section = 'diseases'
            elif line.startswith('            ') and current_section == 'genes':
                gene_line = line.strip()
                if gene_line:
                    current_content.append(parse_gene_line(gene_line))
            elif line.startswith(' ') and not line.startswith('            '):
                if current_section == 'genes' and current_content:
                    info["genes"] = current_content[:50]
                    current_content = []
                current_section = None
        
        if current_section == 'genes' and current_content:
            info["genes"] = current_content[:50]
        
        return info
        
    except Exception as e:
        return {"error": f"Failed to get pathway info: {str(e)}"}


def parse_gene_line(line: str) -> dict:
    parts = line.split(';', 1)
    gene_id = ""
    gene_name = ""
    description = ""
    
    if parts:
        id_part = parts[0].strip()
        id_tokens = id_part.split(None, 1)
        if id_tokens:
            gene_id = id_tokens[0]
            if len(id_tokens) > 1:
                gene_name = id_tokens[1]
        
        if len(parts) > 1:
            description = parts[1].strip()
    
    return {
        "id": gene_id,
        "symbol": gene_name,
        "description": description
    }


def get_pathway_genes(pathway_id: str) -> list:
    result = get_pathway_info(pathway_id)
    if "error" in result:
        return [result]
    return result.get("genes", [])


def get_gene_pathways(gene_id: str, organism: str = "hsa") -> list:
    try:
        url = f"{KEGG_BASE}/find/genes/{gene_id}"
        
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(url)
            response.raise_for_status()
            text = response.text
        
        if not text.strip():
            return []
        
        kegg_gene_id = None
        for line in text.strip().split('\n'):
            if line.startswith(organism):
                kegg_gene_id = line.split('\t')[0].strip()
                break
        
        if not kegg_gene_id:
            return [{"error": f"Gene not found: {gene_id}"}]
        
        url = f"{KEGG_BASE}/link/pathway/{kegg_gene_id}"
        
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(url)
            response.raise_for_status()
            text = response.text
        
        pathways = []
        for line in text.strip().split('\n'):
            if '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    pathway_id = parts[1].replace("path:", "").strip()
                    pathways.append({"id": pathway_id})
        
        for pathway in pathways[:10]:
            info = get_pathway_info(pathway["id"])
            if "error" not in info:
                pathway["name"] = info.get("name", "")
        
        return pathways[:10]
        
    except Exception as e:
        return [{"error": f"Failed to get gene pathways: {str(e)}"}]
