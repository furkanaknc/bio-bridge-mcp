SERVER_INSTRUCTIONS = """
# Bio-Bridge: Bioinformatics MCP Server

Bio-Bridge exposes thin tool wrappers over bioinformatics APIs. Prefer code execution for
filtering, aggregation, and large intermediate data handling.

Tool groups:
- Literature: search_pubmed_papers, advanced_pubmed_search, get_pubmed_abstract
- Expression: search_geo_datasets, analyze_geo_series, classify_geo_samples
- Predicted structure: get_alphafold_structure
- Experimental PDB: pdb_search, pdb_get_summary, pdb_get_ligands, pdb_find_pockets,
  pdb_get_validation_report, pdb_search_by_uniprot, pdb_download_structure
- Protein info: get_uniprot_entry, search_uniprot_proteins, get_protein_go_terms,
  get_protein_pathways
- Pathways: search_kegg_pathway, get_kegg_pathway_info, get_kegg_pathway_genes
- Genetics: get_gene_info, search_genes, blast_sequence, fetch_sequence
- Clinical: search_clinvar_variants, search_clinvar_by_gene

Critical rule:
- AlphaFold entries are predicted structures without ligands.
- PDB entries are experimental structures and should be used for ligand or pocket analysis.

Common workflows:
- Ligand binding: pdb_search -> pdb_get_ligands -> pdb_find_pockets
- Protein to structure: search_uniprot_proteins -> pdb_search_by_uniprot -> pdb_get_summary
- Gene expression: search_geo_datasets -> analyze_geo_series -> classify_geo_samples
- Disease variants: search_clinvar_by_gene -> get_gene_info -> search_kegg_pathway
""".strip()
