# Bio-Bridge Usage Guide

## Quick Routing

- Papers, studies, literature: `search_pubmed_papers`, `advanced_pubmed_search`,
  `get_pubmed_abstract`
- GEO, GSE, RNA-seq, microarray: `search_geo_datasets`, `analyze_geo_series`,
  `classify_geo_samples`
- Gene details or search: `get_gene_info`, `search_genes`
- Sequence lookup or BLAST: `fetch_sequence`, `blast_sequence`
- Experimental structures, ligands, pockets: `pdb_search`, `pdb_get_summary`,
  `pdb_get_ligands`, `pdb_find_pockets`
- Predicted structure only: `get_alphafold_structure`
- Protein function and GO terms: `get_uniprot_entry`, `search_uniprot_proteins`,
  `get_protein_go_terms`, `get_protein_pathways`
- Pathways: `search_kegg_pathway`, `get_kegg_pathway_info`, `get_kegg_pathway_genes`
- Variants and pathogenic mutations: `search_clinvar_variants`, `search_clinvar_by_gene`

## Critical Distinction

- AlphaFold: predicted structures, no ligand analysis
- PDB: experimental structures, use for ligand and pocket analysis

## Common Workflows

Ligand binding:

```text
pdb_search -> pdb_get_ligands -> pdb_find_pockets
```

Protein to structure:

```text
search_uniprot_proteins -> pdb_search_by_uniprot -> pdb_get_summary
```

Gene expression:

```text
search_geo_datasets -> analyze_geo_series -> classify_geo_samples
```

Disease variants:

```text
search_clinvar_by_gene -> get_gene_info -> search_kegg_pathway
```
