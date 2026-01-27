# Bio-Bridge Usage Guide for LLMs

## 🎯 Quick Reference - 27 Tools

### When user mentions...

| User Says                                                | Use These Tools                                                         |
| -------------------------------------------------------- | ----------------------------------------------------------------------- |
| "paper", "publication", "study", "research"              | `search_pubmed_papers`, `advanced_pubmed_search`, `get_pubmed_abstract` |
| "expression", "GEO", "GSE", "RNA-seq", "microarray"      | `search_geo_datasets` → `analyze_geo_series` → `classify_geo_samples`   |
| "structure", "3D model", "AlphaFold"                     | `get_alphafold_structure` ⚠️ No ligands!                                |
| "crystal structure", "X-ray", "NMR", "ligand", "binding" | `pdb_search`, `pdb_get_ligands`, `pdb_find_pockets`                     |
| "protein function", "UniProt", "GO terms"                | `get_uniprot_entry`, `search_uniprot_proteins`, `get_protein_go_terms`  |
| "pathway", "KEGG", "metabolism", "signaling"             | `search_kegg_pathway`, `get_kegg_pathway_genes`                         |
| "variant", "mutation", "SNP", "pathogenic"               | `search_clinvar_variants`, `search_clinvar_by_gene`                     |
| "gene info", "gene function"                             | `get_gene_info`, `search_genes`                                         |
| "sequence", "accession", "BLAST"                         | `fetch_sequence`, `blast_sequence`                                      |

---

## ⚠️ CRITICAL: AlphaFold vs PDB

| Feature | AlphaFold (AF-\*)         | PDB (1ABC, 7DF4)             |
| ------- | ------------------------- | ---------------------------- |
| Type    | AI Predicted              | Experimental (X-ray/NMR)     |
| Ligands | ❌ NONE                   | ✅ May contain drugs/ligands |
| Use For | Structure visualization   | Drug binding analysis        |
| Tools   | `get_alphafold_structure` | `pdb_*` tools                |

**Rule:** For ligand/pocket analysis → ALWAYS use PDB tools, NEVER AlphaFold!

---

## 🔄 Workflow Examples

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

### Literature Search

```
1. advanced_pubmed_search(gene="TP53", disease="cancer", year_from=2023)
2. get_pubmed_abstract("39012345")               → Read specific paper
```
