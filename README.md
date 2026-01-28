# Bio-Bridge: Bioinformatics MCP Server

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-brightgreen)](https://modelcontextprotocol.io)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Bio-Bridge** is a powerful **Model Context Protocol (MCP) server** that connects Large Language Models (LLMs) like Claude, GPT, and others to major bioinformatics databases. It provides **27 specialized tools** for querying scientific literature, gene expression data, protein structures, genetic variants, and biological pathways.

> 🧬 **Perfect for researchers, bioinformaticians, and developers** building AI-powered tools for life sciences.

---

## 🎯 Key Features

### Supported Databases & APIs

| Database        | Description                                         | Tools                                                                                                                                                  |
| --------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **NCBI GEO**    | Gene Expression Omnibus - RNA-seq & microarray data | `search_geo_datasets`, `analyze_geo_series`, `classify_geo_samples`                                                                                    |
| **NCBI PubMed** | Scientific literature & abstracts                   | `search_pubmed_papers`, `advanced_pubmed_search`, `get_pubmed_abstract`                                                                                |
| **NCBI Gene**   | Gene information database                           | `get_gene_info`, `search_genes`                                                                                                                        |
| **NCBI BLAST**  | Sequence similarity search                          | `blast_sequence`, `fetch_sequence`                                                                                                                     |
| **RCSB PDB**    | Protein Data Bank - experimental 3D structures      | `pdb_search`, `pdb_get_summary`, `pdb_get_ligands`, `pdb_find_pockets`, `pdb_get_validation_report`, `pdb_search_by_uniprot`, `pdb_download_structure` |
| **UniProt**     | Protein sequence & function database                | `get_uniprot_entry`, `search_uniprot_proteins`, `get_protein_go_terms`, `get_protein_pathways`                                                         |
| **KEGG**        | Kyoto Encyclopedia of Genes and Genomes             | `search_kegg_pathway`, `get_kegg_pathway_info`, `get_kegg_pathway_genes`                                                                               |
| **AlphaFold**   | AI-predicted protein structures                     | `get_alphafold_structure`                                                                                                                              |
| **ClinVar**     | Clinical variants database                          | `search_clinvar_variants`, `search_clinvar_by_gene`                                                                                                    |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- An NCBI account email (for API access)

### Installation

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/bio-bridge.git
cd bio-bridge
```

2. **Create and activate a virtual environment:**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4.  **Configure your NCBI credentials:**

```bash
cp .env.example .env
```

Edit `.env` and set your NCBI credentials:

```
NCBI_EMAIL=your.email@example.com
NCBI_API_KEY=your_api_key_here
```

> 💡 **Tip:** Get your free API key from [NCBI](https://www.ncbi.nlm.nih.gov/account/settings/). API key increases rate limit from 3 to 10 requests/second.

### Running the Server

**Development mode:**

```bash
mcp dev src/server.py
```

**Production mode:**

```bash
python src/server.py
```

---

## 🐳 Docker Installation

For easy deployment without managing Python environments:

1.  **Build the Docker image:**

```bash
docker build -t bio-bridge .
```

2.  **Run the container:**

```bash
docker run -i --rm \
  -e NCBI_EMAIL=your.email@example.com \
  -e NCBI_API_KEY=your_api_key_here \
  bio-bridge
```

---

## ⚙️ MCP Client Configuration

### Claude Desktop

Add to your `claude_desktop_config.json`:

**Python (Local):**

```json
{
  "mcpServers": {
    "bio-bridge": {
      "command": "path/to/venv/python",
      "args": ["path/to/bio-bridge/src/server.py"],
      "env": {
        "NCBI_EMAIL": "your.email@example.com",
        "NCBI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Docker:**

```json
{
  "mcpServers": {
    "bio-bridge": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "NCBI_EMAIL=your.email@example.com",
        "-e",
        "NCBI_API_KEY=your_api_key_here",
        "bio-bridge"
      ]
    }
  }
}
```

### Other MCP Clients

Bio-Bridge works with any MCP-compatible client including:

- Cursor IDE
- Cody (Sourcegraph)
- Continue.dev
- Custom MCP implementations

---

## 📖 Usage Examples

Once connected to your LLM, you can ask natural language questions:

### Literature Search

> "Find recent papers about CRISPR-Cas9 gene editing in cancer therapy"

> "Get the abstract of PubMed article 39012345"

### Gene Expression Analysis

> "Search for breast cancer RNA-seq datasets in GEO"

> "Analyze GSE53986 and classify samples as control or treated"

### Protein Structure Analysis

> "Find the crystal structure of human insulin receptor"

> "What ligands are bound to PDB structure 7SV7?"

> "Get the AlphaFold predicted structure for P04637 (p53)"

### Pathway & Gene Analysis

> "What pathways is the BRCA1 gene involved in?"

> "Find genes related to apoptosis in humans"

### Variant Analysis

> "Find pathogenic variants in the BRCA1 gene"

> "Search ClinVar for cystic fibrosis mutations"

### Sequence Analysis

> "Identify this DNA sequence: ATGCGATCGATCG..."

> "Get the nucleotide sequence for NM_000546"

---

## 🔧 Available Tools (27 Total)

### 📚 Literature & Publications (3 tools)

| Tool                     | Description                                              |
| ------------------------ | -------------------------------------------------------- |
| `search_pubmed_papers`   | Search PubMed for scientific articles                    |
| `advanced_pubmed_search` | Structured search with gene, disease, drug, year filters |
| `get_pubmed_abstract`    | Get full abstract for a specific PMID                    |

### 🧬 Gene Expression - NCBI GEO (3 tools)

| Tool                   | Description                                          |
| ---------------------- | ---------------------------------------------------- |
| `search_geo_datasets`  | Find expression datasets (RNA-seq, microarray)       |
| `analyze_geo_series`   | Get experiment details for a GSE ID                  |
| `classify_geo_samples` | Automatically classify samples as Control vs Treated |

### 🔬 Experimental Structures - RCSB PDB (7 tools)

| Tool                        | Description                                      |
| --------------------------- | ------------------------------------------------ |
| `pdb_search`                | Search structures with resolution/method filters |
| `pdb_get_summary`           | Structure details, mutations, classification     |
| `pdb_get_ligands`           | List bound small molecules and drugs             |
| `pdb_find_pockets`          | Identify binding pockets/active sites            |
| `pdb_get_validation_report` | Quality and resolution metrics                   |
| `pdb_search_by_uniprot`     | Find structures for a UniProt ID                 |
| `pdb_download_structure`    | Download PDB/mmCIF file content                  |

### 🔮 Predicted Structures - AlphaFold (1 tool)

| Tool                      | Description                                       |
| ------------------------- | ------------------------------------------------- |
| `get_alphafold_structure` | Get AlphaFold predicted structure (⚠️ no ligands) |

### 🧪 Protein Information - UniProt (4 tools)

| Tool                      | Description                                          |
| ------------------------- | ---------------------------------------------------- |
| `get_uniprot_entry`       | Full protein details (function, sequence, mutations) |
| `search_uniprot_proteins` | Search proteins by name or function                  |
| `get_protein_go_terms`    | Gene Ontology annotations                            |
| `get_protein_pathways`    | Metabolic and signaling pathway cross-references     |

### 🛤️ Pathways - KEGG (3 tools)

| Tool                     | Description                     |
| ------------------------ | ------------------------------- |
| `search_kegg_pathway`    | Find pathways by keyword        |
| `get_kegg_pathway_info`  | Pathway details and description |
| `get_kegg_pathway_genes` | List genes in a pathway         |

### 🧬 Gene Information - NCBI Gene (4 tools)

| Tool             | Description                                 |
| ---------------- | ------------------------------------------- |
| `get_gene_info`  | Detailed gene information                   |
| `search_genes`   | Find genes by keyword                       |
| `blast_sequence` | Run BLAST sequence similarity search        |
| `fetch_sequence` | Retrieve DNA/protein sequences by accession |

### 🏥 Clinical Variants - ClinVar (2 tools)

| Tool                      | Description                                    |
| ------------------------- | ---------------------------------------------- |
| `search_clinvar_variants` | Search genetic variants                        |
| `search_clinvar_by_gene`  | Find variants by gene with significance filter |

---

## 🔄 Common Workflows

### Ligand Binding Analysis

```
1. pdb_search("CFTR ivacaftor")     → Find experimental structure
2. pdb_get_ligands("7SV7")          → Get ligand code (e.g., "VX7")
3. pdb_find_pockets("7SV7", "VX7")  → Analyze binding pocket
```

### Protein Structure Pipeline

```
1. search_uniprot_proteins("insulin receptor") → Find protein ID
2. pdb_search_by_uniprot("P06213")             → Find PDB structures
3. pdb_get_summary("1IR3")                     → Get structure details
```

### Gene Expression Analysis

```
1. search_geo_datasets("tamoxifen breast cancer") → Find datasets
2. analyze_geo_series("GSE312800")                → Analyze series
3. classify_geo_samples("GSE312800")              → Control vs Treated
```

### Disease Variant Research

```
1. search_clinvar_by_gene("BRCA1", "Pathogenic") → Find variants
2. get_gene_info("BRCA1")                         → Gene details
3. get_uniprot_entry("P38398")                    → Protein context
```

---

## ⚠️ Important: AlphaFold vs PDB

| Feature | AlphaFold (AF-\*)         | PDB (1ABC, 7DF4)                 |
| ------- | ------------------------- | -------------------------------- |
| Type    | AI Predicted              | Experimental (X-ray/NMR/Cryo-EM) |
| Ligands | ❌ **NONE**               | ✅ May contain drugs/ligands     |
| Use For | Structure visualization   | Drug binding analysis            |
| Tools   | `get_alphafold_structure` | `pdb_*` tools                    |

> **Rule:** For ligand/pocket analysis → **ALWAYS use PDB tools**, NEVER AlphaFold!

---

## 📁 Project Structure

```
bio-bridge/
├── src/
│   ├── server.py           # Main MCP server with all 27 tools
│   ├── ncbi/               # NCBI clients (GEO, PubMed, BLAST, Gene)
│   │   ├── client.py
│   │   ├── geo.py
│   │   ├── blast.py
│   │   ├── pubmed.py
│   │   └── sequence.py
│   ├── rcsb/               # RCSB PDB client
│   │   ├── client.py
│   │   ├── search.py
│   │   ├── structure.py
│   │   └── ligands.py
│   ├── uniprot/            # UniProt client
│   │   └── client.py
│   ├── kegg/               # KEGG client
│   │   └── client.py
│   ├── alphafold/          # AlphaFold client
│   │   └── client.py
│   └── clinvar/            # ClinVar client
│       └── client.py
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

---

## 🔑 API & Rate Limits

Bio-Bridge uses public APIs from NCBI, RCSB, UniProt, KEGG, and AlphaFold. Please respect their usage policies:

| Database                               | Authentication                   | Rate Limit                      |
| -------------------------------------- | -------------------------------- | ------------------------------- |
| **NCBI** (GEO, PubMed, BLAST, ClinVar) | Email required, API key optional | 3 req/s (10 req/s with API key) |
| **RCSB PDB**                           | None                             | Unlimited                       |
| **UniProt**                            | None                             | Unlimited                       |
| **KEGG**                               | None                             | Unlimited                       |
| **AlphaFold**                          | None                             | Unlimited                       |

> 📌 **Get your NCBI API Key:** Visit [NCBI Account Settings](https://www.ncbi.nlm.nih.gov/account/settings/) to generate a free API key.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🏷️ Keywords

_NCBI MCP Server, NCBI GEO MCP, PubMed MCP, BLAST MCP, PDB MCP Server, RCSB MCP, UniProt MCP, KEGG MCP, AlphaFold MCP, ClinVar MCP, Bioinformatics AI, LLM Bioinformatics, Gene Expression Analysis, Protein Structure Analysis, MCP Server Biology, Claude Bioinformatics, GPT Bioinformatics, Model Context Protocol Bioinformatics, Life Sciences AI Tools, Computational Biology MCP_

---

## 🔗 Related Resources

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io)
- [NCBI Entrez](https://www.ncbi.nlm.nih.gov/home/develop/api/)
- [RCSB Protein Data Bank](https://www.rcsb.org/)
- [UniProt](https://www.uniprot.org/)
- [KEGG](https://www.kegg.jp/)
- [AlphaFold Database](https://alphafold.ebi.ac.uk/)
- [ClinVar](https://www.ncbi.nlm.nih.gov/clinvar/)

---

<p align="center">
  <strong>Built with ❤️ for the bioinformatics community</strong>
</p>
