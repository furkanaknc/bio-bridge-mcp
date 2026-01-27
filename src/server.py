from mcp.server.fastmcp import FastMCP
from ncbi.client import NcbiClient
from rcsb.client import RcsbClient
from uniprot.client import UniProtClient
from kegg.client import KeggClient
from alphafold.client import AlphaFoldClient
from clinvar.client import ClinVarClient
import json
import re

mcp = FastMCP(
    "Bio-Bridge",
    instructions="""
# Bio-Bridge: Bioinformatics MCP Server

## 🎯 Tool Selection Guide

| Category | Tools | Use When |
|----------|-------|----------|
| 📚 Literature | `advanced_pubmed_search`, `get_pubmed_abstract` | Papers, publications, research, clinical studies |
| 🧬 Expression | `search_geo_datasets`, `analyze_geo_series`, `classify_geo_samples` | Gene expression, RNA-seq, microarray, GEO datasets |
| 🔬 Structure | `get_alphafold_structure` | Protein 3D structures, PDB, predicted structures |
| 🧪 Protein Info | `get_uniprot_entry`, `search_uniprot_proteins`, `get_protein_go_terms`, `get_protein_pathways` | Protein function, sequence, annotations, GO terms |
| 🛤️ Pathways | `search_kegg_pathway`, `get_kegg_pathway_info`, `get_kegg_pathway_genes` | Metabolic pathways, signaling pathways, gene networks |
| 🧬 Genetics | `get_gene_info`, `search_genes`, `blast_sequence`, `fetch_sequence` | Gene details, sequences, BLAST search |
| 🏥 Clinical | `search_clinvar_variants`, `search_clinvar_by_gene` | Genetic variants, mutations, disease associations |

## 🔄 Common Workflows

### Drug Discovery
`search_uniprot_proteins` → `get_uniprot_entry` → `get_alphafold_structure`

### Gene Function Analysis  
`advanced_pubmed_search` → `search_geo_datasets` → `analyze_geo_series`

### Disease Research
`search_clinvar_by_gene` → `get_gene_info` → `search_kegg_pathway`
"""
)

ncbi_client = None
rcsb_client = None
uniprot_client = None
kegg_client = None
alphafold_client = None
clinvar_client = None

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

try:
    clinvar_client = ClinVarClient()
except Exception as e:
    print(f"Warning: ClinVar Client could not be initialized: {e}")

@mcp.tool()
def search_geo_datasets(query: str) -> str:
    """
    Search for gene expression datasets in NCBI GEO.

    USE THIS WHEN: User asks for "expression data", "microarray studies", "RNA-seq datasets", 
    or "GSE" series related to a topic (e.g., "breast cancer expression data").
    
    DO NOT USE FOR: Searching for specific genes (use `search_genes`) or proteins (use `search_uniprot_proteins`).

    Args:
        query: Keywords for the search (e.g., "diabetes illumina", "GSE12345").
    """
    if not ncbi_client:
        return "Error: NCBI Client is not initialized."
    
    results = ncbi_client.search_geo(query)
    if not results:
        return f"No GEO results found for query: '{query}'"
        
    output = [f"### GEO Search Results for '{query}'"]
    for item in results:
        output.append(f"- **{item['id']}**: {item['title']}")
        output.append(f"  *{item.get('organism', 'Unknown')} | {item.get('type', 'Unknown')} | {item.get('samples', 0)} samples*")
    return "\n".join(output)

@mcp.tool()
def search_pubmed_papers(query: str) -> str:
    """
    Search PubMed for scientific papers and articles.
    
    USE THIS WHEN: User asks about "research papers", "clinical studies", "publications", 
    or wants to find scientific literature on a topic (e.g., "latest studies on CRISPR").
    
    DO NOT USE FOR: General knowledge questions not requiring specific papers.
    
    Args:
        query: Search keywords (e.g., "breast cancer immunotherapy", "TP53 mutations review").
    """
  
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
    """
    Run a BLAST search to find matching sequences in the NCBI database.
    
    USE THIS WHEN: User provides a DNA or protein sequence (e.g., "ATGC...") and asks "what is this?" 
    or "identify this sequence".
    
    Args:
        sequence: The nucleotide or protein sequence string.
        database: 'nt' (nucleotide) or 'nr' (protein).
        program: 'blastn', 'blastp', 'blastx', etc.
    """
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
    """
    Fetch a specific DNA/RNA or protein sequence from NCBI.
    
    USE THIS WHEN: User asks for the sequence of a specific accession ID (e.g., "Get sequence of NM_000546").
    
    Args:
        accession: NCBI Accession ID (e.g., 'NM_000546.5', 'NP_000537.3').
        seq_type: 'nucleotide' or 'protein'.
    """
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
    """
    Get detailed information about a specific gene.
    
    USE THIS WHEN: User asks about a gene (e.g., "What does BRCA1 do?", "Show me details for TP53").
    Returns location, aliases, summary, and ID.
    
    Args:
        gene_symbol: Gene symbol (e.g., 'BRCA1', 'EGFR').
        organism: Target organism (default: 'human').
    """
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
    """
    Search for genes by keyword.
    
    USE THIS WHEN: User wants to find genes related to a function, disease, or topic 
    (e.g., "genes related to apoptosis", "insulin receptors").
    
    DO NOT USE FOR: Retrieving details of a specific gene (use `get_gene_info`).
    
    Args:
        query: Search keywords.
        organism: Target organism.
    """
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
    """
    Get detailed protein information from UniProt.
    
    USE THIS WHEN: User asks for protein details (function, sequences, mutations) of a specific ID.
    
    Args:
        uniprot_id: UniProt ID (e.g., 'P04637').
    """
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
    """
    Search for proteins in UniProt.
    
    USE THIS WHEN: User asks for proteins by name (e.g., "Insulin", "P53") or function.
    
    Args:
        query: Search keywords.
        organism: Target organism.
    """
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
    """
    Get Gene Ontology (GO) terms for a protein.
    
    USE THIS WHEN: User asks about molecular function, biological process, or cellular component.
    
    Args:
        uniprot_id: UniProt ID.
    """
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
    """
    Get metabolic and signaling pathways for a protein.
    
    USE THIS WHEN: User asks "what pathways is this protein involved in?" or "does P53 affect apoptosis?".
    
    Args:
        uniprot_id: UniProt ID.
    """
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
    """
    Search for KEGG pathways by keyword.
    
    USE THIS WHEN: User wants to find pathways related to a process (e.g., "cell cycle", "glycolysis").
    
    Args:
        query: Search keywords.
        organism: KEGG organism code (default: 'hsa' for human).
    """
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
    """
    Get details of a specific KEGG pathway.
    
    USE THIS WHEN: User asks about a specific pathway ID (e.g., "hsa04110").
    
    Args:
        pathway_id: KEGG Pathway ID.
    """
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
    """
    Get the list of genes involved in a KEGG pathway.
    
    USE THIS WHEN: User asks "what genes are in the apoptosis pathway?".
    
    Args:
        pathway_id: KEGG Pathway ID.
    """
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
    """
    Analyze a GEO Series (GSE) to get experiment details.
    
    USE THIS WHEN: User provides a GSE ID (e.g., "GSE53986") and asks for analysis or summary.
    
    Args:
        gse_id: GEO Series ID.
    """
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
    """
    Classify samples in a GEO Series into Control vs Treated groups.
    
    USE THIS WHEN: User wants to know experimental groups or sample conditions.
    
    Args:
        gse_id: GEO Series ID.
    """
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
    """
    Get the predicted 3D structure of a protein from AlphaFold.
    
    USE THIS WHEN: User asks for "structure", "3D model", or "AlphaFold prediction".
    
    Args:
        uniprot_id: UniProt ID.
    """
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

@mcp.tool()
def search_clinvar_variants(query: str) -> str:
    """
    Search ClinVar for genetic variants.
    
    USE THIS WHEN: User asks for variants by disease, gene name (for all variants), or specific conditions.
    
    Args:
        query: Search term (e.g., "BRCA1", "Cystic Fibrosis").
    """
    if not clinvar_client:
        return "Error: ClinVar Client is not initialized."
    
    try:
        results = clinvar_client.search_variants(query, limit=10)
        
        if not results:
            return f"No variants found for '{query}'"
        
        if "error" in results[0]:
            return f"Error: {results[0]['error']}"
        
        output = [f"### ClinVar Variants for '{query}'"]
        for v in results:
            output.append(f"- **{v['title']}**")
            output.append(f"  Gene: {v['gene']} | Significance: {v['clinical_significance']}")
            output.append(f"  Accession: {v['accession']}")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error searching variants: {str(e)}"

@mcp.tool()
def search_clinvar_by_gene(gene_symbol: str, significance: str = None) -> str:
    """
    Search variants by gene symbol with optional clinical significance filter.
    
    USE THIS WHEN: User wants variants of a specific gene (e.g., "Pathogenic variants in TP53").
    
    Args:
        gene_symbol: Gene symbol (e.g., 'TP53').
        significance: Optional filter (e.g., 'Pathogenic', 'Benign').
    """
    if not clinvar_client:
        return "Error: ClinVar Client is not initialized."
    
    try:
        results = clinvar_client.search_by_gene(gene_symbol, significance)
        
        if not results:
            return f"No variants found for gene '{gene_symbol}'"
        
        if "error" in results[0]:
            return f"Error: {results[0]['error']}"
        
        sig_text = f" ({significance})" if significance else ""
        output = [f"### ClinVar Variants for {gene_symbol}{sig_text}"]
        
        for v in results:
            output.append(f"- **{v['title'][:60]}**")
            output.append(f"  Significance: {v['clinical_significance']} | {v['accession']}")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error searching by gene: {str(e)}"

@mcp.tool()
def advanced_pubmed_search(gene: str = None, disease: str = None, drug: str = None, year_from: int = None) -> str:
    """
    Perform a structured search in PubMed using specific filters.
    
    USE THIS WHEN: User wants to combine criteria (e.g., "Papers on TP53 and Cancer from 2020").
    
    Args:
        gene: Gene symbol.
        disease: Disease or condition.
        drug: Drug or chemical.
        year_from: Start year.
    """
    if not ncbi_client:
        return "Error: NCBI Client is not initialized."
    
    try:
        results = ncbi_client.advanced_pubmed_search(
            gene=gene, disease=disease, drug=drug, year_from=year_from, limit=10
        )
        
        if not results:
            return "No articles found with the specified criteria"
        
        if "error" in results[0]:
            return f"Error: {results[0]['error']}"
        
        criteria = []
        if gene: criteria.append(f"Gene: {gene}")
        if disease: criteria.append(f"Disease: {disease}")
        if drug: criteria.append(f"Drug: {drug}")
        if year_from: criteria.append(f"From: {year_from}")
        
        output = [f"### PubMed Search Results"]
        output.append(f"*Criteria: {', '.join(criteria)}*")
        output.append("---")
        
        for article in results:
            authors = article.get('authors', [])[:2]
            author_str = ', '.join(authors) + ' et al.' if len(article.get('authors', [])) > 2 else ', '.join(authors)
            output.append(f"**{article['title'][:80]}...**")
            output.append(f"*{author_str}* - {article['journal']} ({article['pub_date']})")
            output.append(f"PMID: {article['id']}")
            output.append("")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error in advanced search: {str(e)}"

@mcp.tool()
def get_pubmed_abstract(pmid: str) -> str:
    """
    Get the abstract and details of a specific PubMed article.
    
    USE THIS WHEN: User provides a PMID and asks for the summary or abstract.
    
    Args:
        pmid: PubMed ID (e.g., '34567890').
    """
    if not ncbi_client:
        return "Error: NCBI Client is not initialized."
    
    try:
        result = ncbi_client.get_pubmed_abstract(pmid)
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        output = [f"### {result['title']}"]
        output.append(f"**Authors:** {', '.join(result['authors'])}")
        output.append(f"**Journal:** {result['journal']} ({result['year']})")
        output.append(f"**PMID:** {result['pmid']}")
        output.append("---")
        output.append("**Abstract:**")
        output.append(result['abstract'])
        
        return "\n".join(output)
    except Exception as e:
        return f"Error getting abstract: {str(e)}"


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
    """
    Get details about a PDB structure, including classification and mutations.
    
    USE THIS WHEN: User asks for details of a specific PDB ID or wants to know if it has mutations.
    
    Args:
        pdb_id: PDB ID (e.g., '1TUP').
    """
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
    """
    List small molecule ligands bound to a PDB structure.
    
    USE THIS WHEN: User asks "what is bound to this structure?" or "does it contain any drugs/ligands?".
    
    Args:
        pdb_id: PDB ID.
    """
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
    """
    Identify binding pockets in a PDB structure.
    
    USE THIS WHEN: User asks about drug binding sites or active pockets.
    
    Args:
        pdb_id: PDB ID.
        ligand_id: Optional ligand to focus on.
    """
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
    
    USE THIS WHEN: User asks for experimental protein structures (e.g., "crystal structure of hemoglobin", 
    "NMR structures of kinases", "high-resolution X-ray structures").
    
    DO NOT USE FOR: Predicted structures (use `get_alphafold_structure`) or protein info without structure (use `get_uniprot_entry`).
    
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
    """
    Get the quality validation report for a PDB structure.
    
    USE THIS WHEN: User asks about the quality, resolution, or reliability of a crystal structure.
    
    Args:
        pdb_id: PDB ID.
    """
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
    """
    Find PDB structures corresponding to a UniProt entry.
    
    USE THIS WHEN: User wants experimental structures for a specific protein ID.
    
    Args:
        uniprot_id: UniProt ID.
    """
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
    """
    Download a PDB structure file content.
    
    USE THIS WHEN: User explicitly asks to download or fetch detail thing about a structure or see the raw file content of a structure.
    
    Args:
        pdb_id: PDB ID.
        file_format: 'pdb' or 'cif'.
    """
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
