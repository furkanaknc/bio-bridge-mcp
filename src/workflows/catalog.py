WORKFLOWS = {
    "ligand_binding_analysis": {
        "steps": ["pdb_search", "pdb_get_ligands", "pdb_find_pockets"],
        "description": "Find an experimental structure, inspect ligands, then inspect pockets.",
    },
    "protein_to_structure": {
        "steps": ["search_uniprot_proteins", "pdb_search_by_uniprot", "pdb_get_summary"],
        "description": "Resolve a protein to an experimental structure and summarize it.",
    },
    "gene_expression_analysis": {
        "steps": ["search_geo_datasets", "analyze_geo_series", "classify_geo_samples"],
        "description": "Locate a GEO series and classify its samples.",
    },
    "disease_variant_research": {
        "steps": ["search_clinvar_by_gene", "get_gene_info", "search_kegg_pathway"],
        "description": "Move from variants to gene context and pathway context.",
    },
}
