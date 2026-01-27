from mcp.server.fastmcp import FastMCP
from ncbi.client import NcbiClient
from rcsb.client import RcsbClient
import json
import re

mcp = FastMCP("Bio-Bridge")
ncbi_client = None
rcsb_client = None

try:
    ncbi_client = NcbiClient()
except Exception as e:
    print(f"Warning: NCBI Client could not be initialized: {e}")

try:
    rcsb_client = RcsbClient()
except Exception as e:
    print(f"Warning: RCSB Client could not be initialized: {e}")

@mcp.tool()
def search_geo_datasets(query: str) -> str:
    if not ncbi_client:
        return "Error: NCBI Client is not initialized."
    
    results = ncbi_client.search_geo(query)
    if not results:
        return f"No GEO results found for query: '{query}'"
        
    output = [f"### GEO Search Results for '{query}'"]
    for item in results:
        output.append(f"- **{item['id']}**: {item['title']}")
    return "\n".join(output)

@mcp.tool()
def search_pubmed_papers(query: str) -> str:
  
    if not ncbi_client:
        return "Error: NCBI Client is not initialized."
    
    results = ncbi_client.search_pubmed(query)
    
    if not results:
         return f"No PubMed results found for query: '{query}'. Try simplifying keywords (e.g., 'Tamoxifen breast cancer' instead of complex sentences)."
    
    if "error" in results[0]:
        return f"Error searching PubMed: {results[0]['error']}"
        
    output = [f"### PubMed Search Results for '{query}'"]
    for item in results:
        authors = ", ".join(item['authors'][:3]) + ("..." if len(item['authors']) > 3 else "")
        output.append(f"- **PMID:{item['id']}**: {item['title']}")
        output.append(f"  *Authors: {authors}*")
        output.append(f"  *Journal: {item['journal']} ({item['pub_date']})*")
    return "\n".join(output)

@mcp.tool()
def analyze_sample(input_text: str) -> str:
    if not ncbi_client:
        return "Error: NCBI Client is not initialized."

    match = re.search(r'(GSM\d+)', input_text, re.IGNORECASE)
    if not match:
        return f"Error: No valid GSM ID found in input '{input_text}'. Please provide a valid GEO Sample ID (e.g., GSM12345)."
    
    geo_id = match.group(1).upper()

    try:
        data = ncbi_client.fetch_geo_details(geo_id)
        
        if "error" in data:
            return f"Error fetching data for {geo_id}: {data['error']}"
            
        output = []
        output.append(f"### Analysis for {data['accession']}")
        output.append(f"**Title:** {data['title']}")
        output.append(f"**Organism:** {data['organism']}")
        output.append("---")
        output.append(f"**Condition:** {data['condition']}")
        
        if data['dosage']:
            output.append(f"**Dosage Detected:** {data['dosage']}")
        else:
            output.append("**Dosage:** Not found / Not Applicable")
            
        output.append("---")
        output.append(f"**Summary:**\n{data['summary']}")
        
        return "\n".join(output)

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

@mcp.tool()
def pdb_get_summary(pdb_id: str) -> str:
    if not rcsb_client:
        return "Error: RCSB Client is not initialized."
        
    try:
        data = rcsb_client.get_pdb_summary(pdb_id)
        if "error" in data:
            return f"Error: {data['error']}"
            
        output = []
        output.append(f"### PDB Structure: {data.get('pdb_id')} ({data.get('title')})")
        output.append(f"**Classification:** {data.get('classification')}")
        output.append("---")
        
        if data.get("has_mutations"):
            output.append("**Mutations Detected:** YES")
            for m in data.get("mutation_details", []):
                output.append(f"- Entity {m['entity_id']}: Official Count={m['official_count']}")
                if m['details']:
                    for d in m['details']:
                        output.append(f"  * {d}")
        else:
            output.append("**Mutations:** None detected (Wild Type)")
            
        return "\n".join(output)
    except Exception as e:
        return f"Error analyzing PDB summary: {str(e)}"

@mcp.tool()
def pdb_get_ligands(pdb_id: str) -> str:
    if not rcsb_client:
        return "Error: RCSB Client is not initialized."

    try:
        ligands = rcsb_client.get_pdb_ligands(pdb_id)
        if not ligands:
            return f"No significant ligands found for {pdb_id}."
            
        output = [f"### Ligands in {pdb_id}"]
        for l in ligands:
            output.append(f"**{l['ligand_id']}** ({l['name']})")
            if l.get('binding_info'):
                 output.append(f"- Binding Data: {'; '.join(l['binding_info'])}")
            output.append("---")
            
        return "\n".join(output)
    except Exception as e:
         return f"Error fetching ligands: {str(e)}"

@mcp.tool()
def pdb_find_pockets(pdb_id: str, ligand_id: str = None) -> str:
    if not rcsb_client:
        return "Error: RCSB Client is not initialized."

    try:
        data = rcsb_client.get_binding_pocket(pdb_id, ligand_id)
        if "error" in data:
            return f"Error: {data['error']}"
            
        lid = data.get("ligand_id")
        pockets = data.get("pockets", [])
        
        output = [f"### Binding Pockets for {lid} in {pdb_id}"]
        output.append(f"**Description:** {data.get('description')}")
        output.append("---")
        
        for p in pockets:
            if isinstance(p, str):
                output.append(f"- {p}")
            else:
                c = p.get("center")
                cid = p.get("chain_id")
                output.append(f"**Instance (Chain {cid}):** X={c.get('x')}, Y={c.get('y')}, Z={c.get('z')}")
        
        return "\n".join(output)
                
    except Exception as e:
        return f"Error calculating binding pocket: {str(e)}"

@mcp.tool()
def pdb_search(query: str, resolution: str = None, method: str = None) -> str:
    """
    Search for PDB structures utilizing advanced filters.
    
    Args:
        query: Free-text search query (e.g. 'hemoglobin').
        resolution: Resolution filter (e.g. '<2.0', '1.5-2.5').
        method: Experimental method (e.g. 'X-RAY DIFFRACTION', 'NMR').
    """
    if not rcsb_client:
        return "Error: RCSB Client is not initialized."

    try:
        results = rcsb_client.search_structures(query, resolution=resolution, method=method)
        if not results:
            msg = f"No PDB structures found for query: '{query}'"
            if resolution: msg += f" (Resolution: {resolution})"
            if method: msg += f" (Method: {method})"
            return msg
            
        if "error" in results[0]:
            return f"Error searching PDB: {results[0]['error']}"
            
        output = [f"### PDB Search Results for '{query}'"]
        if resolution or method:
            output.append(f"*(Filters: Resolution={resolution or 'Any'}, Method={method or 'Any'})*")
            
        for item in results:
            output.append(f"- **{item['pdb_id']}** (Score: {item.get('score', 'N/A')})")
        
        output.append("\nYou can now use 'pdb_get_summary', 'pdb_get_ligands' or 'pdb_find_pockets' with these IDs.")
        return "\n".join(output)
    except Exception as e:
        return f"Error executing search: {str(e)}"

@mcp.tool()
def pdb_get_validation_report(pdb_id: str) -> str:
    if not rcsb_client:
        return "Error: RCSB Client is not initialized."

    try:
        report = rcsb_client.get_validation_report(pdb_id)
        if "error" in report:
            return f"Error: {report['error']}"
            
        output = []
        output.append(f"### Validation Report for {report.get('pdb_id')}")
        output.append(f"**Overall Quality:** {report.get('quality_assessment')}")
        
        res = report.get('resolution')
        output.append(f"- **Resolution:** {res[0] if isinstance(res, list) and res else res} Å")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error fetching validation report: {str(e)}"

@mcp.tool()
def pdb_search_by_uniprot(uniprot_id: str) -> str:
    if not rcsb_client:
        return "Error: RCSB Client is not initialized."

    try:
        results = rcsb_client.search_by_uniprot(uniprot_id)
        if not results:
            return f"No PDB structures found for UniProt ID: '{uniprot_id}'"
            
        if "error" in results[0]:
            return f"Error searching by UniProt: {results[0]['error']}"
            
        output = [f"### PDB Structures for UniProt {uniprot_id}"]
        for item in results:
            output.append(f"- **{item['pdb_id']}** (Score: {item.get('score', 'N/A')})")
            
        return "\n".join(output)
    except Exception as e:
        return f"Error executing UniProt search: {str(e)}"
@mcp.tool()
def pdb_download_structure(pdb_id: str, file_format: str = "pdb") -> str:
    if not rcsb_client:
        return "Error: RCSB Client is not initialized."

    try:
        content = rcsb_client.download_structure(pdb_id, file_format)
        if content.startswith("Error"):
            return content
            
        lines = content.splitlines()
        if len(lines) > 2000:
             return "\n".join(lines[:2000]) + f"\n... (Truncated. Total lines: {len(lines)})"
        return content
    except Exception as e:
        return f"Error downloading structure: {str(e)}"

if __name__ == "__main__":
    mcp.run()
