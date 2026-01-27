from mcp.server.fastmcp import FastMCP
from ncbi.client import NcbiClient
from rcsb.client import RcsbClient
from uniprot.client import UniProtClient
from kegg.client import KeggClient
from alphafold.client import AlphaFoldClient
import json
import re

mcp = FastMCP("Bio-Bridge")
ncbi_client = None
rcsb_client = None
uniprot_client = None
kegg_client = None
alphafold_client = None

try:
    ncbi_client = NcbiClient()
except Exception as e:
    print(f"Warning: NCBI Client could not be initialized: {e}")

try:
    rcsb_client = RcsbClient()
except Exception as e:
    print(f"Warning: RCSB Client could not be initialized: {e}")

try:
    uniprot_client = UniProtClient()
except Exception as e:
    print(f"Warning: UniProt Client could not be initialized: {e}")

try:
    kegg_client = KeggClient()
except Exception as e:
    print(f"Warning: KEGG Client could not be initialized: {e}")

try:
    alphafold_client = AlphaFoldClient()
except Exception as e:
    print(f"Warning: AlphaFold Client could not be initialized: {e}")

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
def blast_sequence(sequence: str, database: str = "nt", program: str = "blastn") -> str:
    if not ncbi_client:
        return "Error: NCBI Client is not initialized."
    
    try:
        result = ncbi_client.blast_sequence(sequence, database, program)
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        output = [f"### BLAST Results ({result['program']} vs {result['database']})"]
        output.append(f"**Query Length:** {result['query_length']} bp")
        output.append(f"**Hits Found:** {result['hits_found']}")
        output.append("---")
        
        for i, hit in enumerate(result['hits'][:5], 1):
            output.append(f"**{i}. {hit['accession']}**")
            output.append(f"   {hit['title']}")
            output.append(f"   - E-value: {hit['e_value']:.2e}")
            output.append(f"   - Identity: {hit['identity']}")
            output.append(f"   - Coverage: {hit['query_coverage']}")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error running BLAST: {str(e)}"

@mcp.tool()
def fetch_sequence(accession: str, seq_type: str = "nucleotide") -> str:
    if not ncbi_client:
        return "Error: NCBI Client is not initialized."
    
    try:
        result = ncbi_client.fetch_sequence(accession, seq_type)
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        output = [f"### Sequence: {result['accession']}"]
        output.append(f"**Description:** {result['description']}")
        
        if "organism" in result:
            output.append(f"**Organism:** {result['organism']}")
        
        output.append(f"**Length:** {result['full_sequence_length']} bp")
        output.append("---")
        
        if "features" in result and result['features']:
            output.append("**Features:**")
            for feat in result['features']:
                feat_str = f"- {feat['type']}"
                if "gene" in feat:
                    feat_str += f" ({feat['gene']})"
                if "product" in feat:
                    feat_str += f": {feat['product']}"
                output.append(feat_str)
            output.append("---")
        
        output.append(f"**Sequence (first 500 bp):**")
        output.append(f"```\n{result['sequence']}\n```")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error fetching sequence: {str(e)}"

@mcp.tool()
def get_gene_info(gene_symbol: str, organism: str = "human") -> str:
    if not ncbi_client:
        return "Error: NCBI Client is not initialized."
    
    try:
        result = ncbi_client.get_gene_info(gene_symbol, organism)
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        output = [f"### Gene: {result.get('official_symbol', gene_symbol)}"]
        output.append(f"**Full Name:** {result.get('full_name', 'N/A')}")
        output.append(f"**Gene ID:** {result.get('gene_id', 'N/A')}")
        output.append(f"**Organism:** {result.get('organism', organism)}")
        
        if "chromosome" in result:
            output.append(f"**Chromosome:** {result['chromosome']}")
        
        if "aliases" in result:
            output.append(f"**Aliases:** {', '.join(result['aliases'])}")
        
        output.append("---")
        
        if "summary" in result:
            output.append(f"**Summary:**")
            output.append(result['summary'])
        
        return "\n".join(output)
    except Exception as e:
        return f"Error getting gene info: {str(e)}"

@mcp.tool()
def search_genes(query: str, organism: str = "human") -> str:
    if not ncbi_client:
        return "Error: NCBI Client is not initialized."
    
    try:
        results = ncbi_client.search_genes(query, organism, limit=10)
        
        if not results:
            return f"No genes found for '{query}' in {organism}"
        
        if "error" in results[0]:
            return f"Error: {results[0]['error']}"
        
        output = [f"### Gene Search Results for '{query}' ({organism})"]
        for gene in results:
            output.append(f"- **{gene['symbol']}** (ID: {gene['gene_id']})")
            output.append(f"  {gene['description']}")
            if gene.get('chromosome') != 'N/A':
                output.append(f"  *Chromosome: {gene['chromosome']}*")
        
        output.append("\n*Use `get_gene_info` for detailed information about a specific gene.*")
        return "\n".join(output)
    except Exception as e:
        return f"Error searching genes: {str(e)}"

@mcp.tool()
def get_uniprot_entry(uniprot_id: str) -> str:
    if not uniprot_client:
        return "Error: UniProt Client is not initialized."
    
    try:
        result = uniprot_client.get_entry(uniprot_id)
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        output = [f"### Protein: {result['protein_name']}"]
        output.append(f"**Accession:** {result['accession']}")
        output.append(f"**Gene(s):** {', '.join(result['gene_names']) if result['gene_names'] else 'N/A'}")
        output.append(f"**Organism:** {result['organism']}")
        output.append("---")
        
        if result.get('function'):
            output.append(f"**Function:**")
            output.append(result['function'])
            output.append("---")
        
        if result.get('sequence_info'):
            seq = result['sequence_info']
            output.append(f"**Sequence:** {seq.get('length', 0)} aa, {seq.get('mass', 0)/1000:.1f} kDa")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error getting UniProt entry: {str(e)}"

@mcp.tool()
def search_uniprot_proteins(query: str, organism: str = "human") -> str:
    if not uniprot_client:
        return "Error: UniProt Client is not initialized."
    
    try:
        results = uniprot_client.search_proteins(query, organism, limit=10)
        
        if not results:
            return f"No proteins found for '{query}' in {organism}"
        
        if "error" in results[0]:
            return f"Error: {results[0]['error']}"
        
        output = [f"### UniProt Search Results for '{query}' ({organism})"]
        for protein in results:
            genes = ', '.join(protein['gene_names'][:2]) if protein['gene_names'] else 'N/A'
            output.append(f"- **{protein['accession']}**: {protein['protein_name']}")
            output.append(f"  *Gene(s): {genes}*")
        
        output.append("\n*Use `get_uniprot_entry` for detailed information.*")
        return "\n".join(output)
    except Exception as e:
        return f"Error searching proteins: {str(e)}"

@mcp.tool()
def get_protein_go_terms(uniprot_id: str) -> str:
    if not uniprot_client:
        return "Error: UniProt Client is not initialized."
    
    try:
        result = uniprot_client.get_go_terms(uniprot_id)
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        output = [f"### GO Terms for {result['accession']} ({result['protein_name']})"]
        
        go_terms = result.get('go_terms', {})
        
        if go_terms.get('molecular_function'):
            output.append("**Molecular Function:**")
            for term in go_terms['molecular_function']:
                output.append(f"- {term['id']}: {term['name']}")
        
        if go_terms.get('biological_process'):
            output.append("**Biological Process:**")
            for term in go_terms['biological_process']:
                output.append(f"- {term['id']}: {term['name']}")
        
        if go_terms.get('cellular_component'):
            output.append("**Cellular Component:**")
            for term in go_terms['cellular_component']:
                output.append(f"- {term['id']}: {term['name']}")
        
        if not any(go_terms.values()):
            output.append("No GO terms found.")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error getting GO terms: {str(e)}"

@mcp.tool()
def get_protein_pathways(uniprot_id: str) -> str:
    if not uniprot_client:
        return "Error: UniProt Client is not initialized."
    
    try:
        result = uniprot_client.get_pathways(uniprot_id)
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        output = [f"### Pathways for {result['accession']} ({result['protein_name']})"]
        
        pathways = result.get('pathways', [])
        
        if pathways:
            for pathway in pathways:
                output.append(f"- **{pathway['database']}**: {pathway['id']}")
                if pathway.get('name'):
                    output.append(f"  {pathway['name']}")
        else:
            output.append("No pathway information found.")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error getting pathways: {str(e)}"

@mcp.tool()
def search_kegg_pathway(query: str, organism: str = "hsa") -> str:
    if not kegg_client:
        return "Error: KEGG Client is not initialized."
    
    try:
        results = kegg_client.search_pathway(query, organism)
        
        if not results:
            return f"No pathways found for '{query}'"
        
        if "error" in results[0]:
            return f"Error: {results[0]['error']}"
        
        output = [f"### KEGG Pathway Search Results for '{query}'"]
        for pathway in results:
            output.append(f"- **{pathway['id']}**: {pathway['name']}")
        
        output.append("\n*Use `get_kegg_pathway_info` for pathway details or `get_kegg_pathway_genes` for gene list.*")
        return "\n".join(output)
    except Exception as e:
        return f"Error searching pathways: {str(e)}"

@mcp.tool()
def get_kegg_pathway_info(pathway_id: str) -> str:
    if not kegg_client:
        return "Error: KEGG Client is not initialized."
    
    try:
        result = kegg_client.get_pathway_info(pathway_id)
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        output = [f"### KEGG Pathway: {result['id']}"]
        output.append(f"**Name:** {result.get('name', 'N/A')}")
        
        if result.get('description'):
            output.append(f"**Description:** {result['description']}")
        
        output.append("---")
        
        genes = result.get('genes', [])
        if genes:
            output.append(f"**Genes ({len(genes)} shown):**")
            for gene in genes[:15]:
                output.append(f"- {gene.get('id', 'N/A')} ({gene.get('symbol', '')}): {gene.get('description', '')[:50]}")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error getting pathway info: {str(e)}"

@mcp.tool()
def get_kegg_pathway_genes(pathway_id: str) -> str:
    if not kegg_client:
        return "Error: KEGG Client is not initialized."
    
    try:
        genes = kegg_client.get_pathway_genes(pathway_id)
        
        if not genes:
            return f"No genes found in pathway {pathway_id}"
        
        if "error" in genes[0]:
            return f"Error: {genes[0]['error']}"
        
        output = [f"### Genes in Pathway {pathway_id}"]
        output.append(f"**Total genes:** {len(genes)}")
        output.append("---")
        
        for gene in genes[:30]:
            symbol = gene.get('symbol', '')
            desc = gene.get('description', '')[:40]
            output.append(f"- **{gene.get('id', 'N/A')}** {symbol}: {desc}")
        
        if len(genes) > 30:
            output.append(f"\n*... and {len(genes) - 30} more genes*")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error getting pathway genes: {str(e)}"

@mcp.tool()
def analyze_geo_series(gse_id: str) -> str:
    if not ncbi_client:
        return "Error: NCBI Client is not initialized."
    
    try:
        result = ncbi_client.analyze_geo_series(gse_id)
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        output = [f"### GEO Series: {result['accession']}"]
        output.append(f"**Title:** {result.get('title', 'N/A')}")
        output.append(f"**Platform:** {result.get('platform', 'N/A')}")
        output.append(f"**Samples:** {result.get('sample_count', 0)}")
        output.append("---")
        
        if result.get('summary'):
            output.append(f"**Summary:** {result['summary'][:300]}...")
        
        if result.get('overall_design'):
            output.append(f"**Design:** {result['overall_design'][:200]}...")
        
        samples = result.get('samples', [])[:10]
        if samples:
            output.append("**Sample IDs (first 10):**")
            output.append(", ".join(samples))
        
        output.append("\n*Use `classify_geo_samples` to analyze sample conditions.*")
        return "\n".join(output)
    except Exception as e:
        return f"Error analyzing series: {str(e)}"

@mcp.tool()
def classify_geo_samples(gse_id: str) -> str:
    if not ncbi_client:
        return "Error: NCBI Client is not initialized."
    
    try:
        result = ncbi_client.classify_geo_samples(gse_id, max_samples=10)
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        output = [f"### Sample Classification for {result['accession']}"]
        output.append(f"**Title:** {result.get('title', 'N/A')}")
        output.append(f"**Total Samples:** {result.get('total_samples', 0)}")
        output.append(f"**Analyzed:** {result.get('analyzed_samples', 0)}")
        output.append("---")
        
        controls = result.get('control', [])
        treated = result.get('treated', [])
        unknown = result.get('unknown', [])
        
        if controls:
            output.append(f"**Control Samples ({len(controls)}):**")
            for s in controls[:5]:
                output.append(f"- {s['id']}: {s['title'][:40]}...")
        
        if treated:
            output.append(f"**Treated Samples ({len(treated)}):**")
            for s in treated[:5]:
                dosage = f" [{s['dosage']}]" if s.get('dosage') else ""
                output.append(f"- {s['id']}: {s['title'][:40]}...{dosage}")
        
        if unknown:
            output.append(f"**Unknown ({len(unknown)}):** {', '.join([s['id'] for s in unknown[:5]])}")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error classifying samples: {str(e)}"

@mcp.tool()
def get_alphafold_structure(uniprot_id: str) -> str:
    if not alphafold_client:
        return "Error: AlphaFold Client is not initialized."
    
    try:
        result = alphafold_client.get_prediction(uniprot_id)
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        output = [f"### AlphaFold Structure: {result['uniprot_id']}"]
        output.append(f"**Entry ID:** {result.get('entry_id', 'N/A')}")
        output.append(f"**Gene:** {result.get('gene', 'N/A')}")
        output.append(f"**Organism:** {result.get('organism', 'N/A')}")
        output.append(f"**Sequence Length:** {result.get('sequence_length', 0)} aa")
        output.append(f"**Model Version:** {result.get('latest_version', 1)}")
        output.append("---")
        output.append("**Download Links:**")
        output.append(f"- PDB: {result.get('pdb_url', 'N/A')}")
        output.append(f"- PAE Image: {result.get('pae_image_url', 'N/A')}")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error getting AlphaFold structure: {str(e)}"


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
