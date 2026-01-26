from mcp.server.fastmcp import FastMCP
from parsing_logic import get_geo_sample_metadata
import pdb_logic
import json

mcp = FastMCP("Bio-Bridge")

@mcp.tool()
def analyze_sample(geo_id: str) -> str:
    """
    Analyzes an NCBI GEO sample to detect treatment conditions and dosage.
    """
    if not geo_id.startswith("GSM"):
        return f"Error: Invalid GEO ID format '{geo_id}'. Expected ID starting with 'GSM'."

    try:
        data = get_geo_sample_metadata(geo_id)
        
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
    """
    Retrieves a summary of a PDB structure, including classification and a detailed check for mutations.
    This tool is useful for identifying if a protein structure contains mutations even if the top-level 
    summary says 'Mutation: 0'.
    """
    try:
        data = pdb_logic.get_pdb_summary(pdb_id)
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
    """
    Lists the ligands (drugs, small molecules) bound to a specific PDB structure.
    Returns their names, formulas, and binding affinity info if available.
    """
    try:
        ligands = pdb_logic.get_pdb_ligands(pdb_id)
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
    """
    Calculates the coordinates of binding pockets for a given ligand (or the primary ligand if none specified).
    Returns the geometric center (X, Y, Z) for each instance of the ligand found in the structure.
    """
    try:
        data = pdb_logic.get_binding_pocket(pdb_id, ligand_id)
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

if __name__ == "__main__":
    mcp.run()
