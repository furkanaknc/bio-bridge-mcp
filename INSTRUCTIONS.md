# Bio-Bridge Usage Guide for LLMs

## 🎯 Quick Reference

### When user mentions...

- **"paper", "publication", "study", "research"**
  - ➡️ Use `advanced_pubmed_search` or `search_pubmed_papers`
- **"expression", "GEO", "GSE", "GSM", "microarray", "RNA-seq"**
  - ➡️ Use `search_geo_datasets` then `analyze_geo_series`
- **"structure", "3D", "AlphaFold", "model"**
  - ➡️ Use `get_alphafold_structure`
- **"protein function", "sequence", "GO terms", "uniprot"**
  - ➡️ Use `get_uniprot_entry`, `search_uniprot_proteins`

- **"pathway", "KEGG", "metabolism", "signaling"**
  - ➡️ Use `search_kegg_pathway`, `get_kegg_pathway_genes`

- **"variant", "mutation", "SNP", "clinical significance"**
  - ➡️ Use `search_clinvar_variants`, `search_clinvar_by_gene`

- **"gene", "promoter", "sequence"**
  - ➡️ Use `get_gene_info`, `fetch_sequence`

---

## 🔄 Workflow Examples

**"Find drug targets for diabetes"**

1. `advanced_pubmed_search(disease="diabetes", limit=5)` - Find literature context
2. `search_kegg_pathway("diabetes")` - Find relevant pathways
3. `get_kegg_pathway_genes("hsa04930")` - Get genes in Type II diabetes pathway

**"Analyze gene expression in breast cancer"**

1. `search_geo_datasets("breast cancer treatment")` - Find datasets
2. `analyze_geo_series("GSE12345")` - Analyze specific series
3. `classify_geo_samples("GSE12345")` - Check sample groups

**"Check if TP53 mutations are pathogenic"**

1. `search_clinvar_by_gene("TP53", significance="Pathogenic")` - Find known pathogenic variants
2. `get_uniprot_entry("P04637")` - Check where these mutations occur in the protein structure
3. `get_alphafold_structure("P04637")` - Visualize the structure context

**"What is this sequence?"**

1. `blast_sequence("ATGC...")` - Identify the sequence provided by user
