"""Reusable prompt templates for common Bio-Bridge investigations."""


def register_prompts(mcp) -> None:
    @mcp.prompt(
        title="Protein structure investigation",
        description="Trace a protein from UniProt to experimental and predicted structures.",
    )
    def investigate_protein_structure(uniprot_id: str) -> str:
        """Build an evidence-based protein structure investigation."""
        return f"""Investigate UniProt entry {uniprot_id}.

1. Use get_uniprot_entry for function and sequence context.
2. Use pdb_search_by_uniprot, then compare promising experimental structures with
   pdb_get_summary and pdb_get_validation_report.
3. For experimental structures, inspect ligands with pdb_get_ligands and relevant
   binding sites with pdb_find_pockets.
4. Use get_alphafold_structure only as a predicted-structure comparison; do not infer
   ligand binding from AlphaFold.
5. Summarize the strongest evidence, limitations, and the identifiers used."""

    @mcp.prompt(
        title="Gene and disease evidence review",
        description="Review literature, clinical variants, pathways, and gene context.",
    )
    def review_gene_disease_evidence(gene_symbol: str, disease: str) -> str:
        """Build a compact gene-disease evidence review."""
        return f"""Review evidence connecting {gene_symbol} to {disease}.

1. Retrieve the gene record with get_gene_info.
2. Search ClinVar with search_clinvar_by_gene and retain clinical significance.
3. Search recent literature with advanced_pubmed_search using both the gene and disease.
4. Inspect relevant pathways using search_kegg_pathway, then retrieve pathway details.
5. Separate established findings from hypotheses and cite PMID, ClinVar accession, gene,
   and pathway identifiers in the final synthesis."""

    @mcp.prompt(
        title="GEO experiment triage",
        description="Find and assess GEO studies before downstream expression analysis.",
    )
    def triage_geo_experiments(query: str) -> str:
        """Find GEO studies and assess whether their sample design is usable."""
        return f"""Triage GEO experiments for: {query}

1. Use search_geo_datasets and shortlist studies by organism, assay, and sample count.
2. Run analyze_geo_series on the best candidates.
3. Run classify_geo_samples to inspect control, treated, and ambiguous samples.
4. Report inclusion/exclusion reasoning, confounders visible in the metadata, and the
   GSE/GSM identifiers needed for a reproducible follow-up."""
