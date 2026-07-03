# Bio-Bridge

Bio-Bridge is a bioinformatics MCP server that exposes 27 tools over NCBI, RCSB PDB,
UniProt, KEGG, AlphaFold, and ClinVar.

## Architecture

The project now follows a code-first MCP layout:

- `src/server.py` is only the MCP bootstrap.
- `src/servers/<domain>/` contains thin tool wrappers.
- `src/shared/` contains shared instructions and lazy client initialization.
- `src/workflows/` contains reusable multi-step helpers.
- Existing API clients remain under the domain packages such as `src/ncbi/` and `src/rcsb/`.

This keeps wrappers small and filesystem-discoverable, and moves control flow and data
handling into code instead of the model context.

## Tool Groups

- Literature: `search_pubmed_papers`, `advanced_pubmed_search`, `get_pubmed_abstract`
- Gene expression: `search_geo_datasets`, `analyze_geo_series`, `classify_geo_samples`
- Genetics: `get_gene_info`, `search_genes`, `blast_sequence`, `fetch_sequence`
- Experimental structures: `pdb_search`, `pdb_get_summary`, `pdb_get_ligands`,
  `pdb_find_pockets`, `pdb_get_validation_report`, `pdb_search_by_uniprot`,
  `pdb_download_structure`
- Protein info: `get_uniprot_entry`, `search_uniprot_proteins`, `get_protein_go_terms`,
  `get_protein_pathways`
- Pathways: `search_kegg_pathway`, `get_kegg_pathway_info`, `get_kegg_pathway_genes`
- Predicted structures: `get_alphafold_structure`
- Clinical variants: `search_clinvar_variants`, `search_clinvar_by_gene`

## Important Rule

Use `pdb_*` tools for ligand and pocket analysis. AlphaFold entries are predicted
structures and do not provide ligand context.

## Run

```bash
pip install -r requirements.txt
mcp dev src/server.py
```

Production:

```bash
python src/server.py
```

## Test

```bash
python -m unittest discover -s tests -v
```

## Project Structure

```text
bio-bridge/
|-- src/
|   |-- server.py
|   |-- servers/
|   |-- shared/
|   |-- workflows/
|   |-- ncbi/
|   |-- rcsb/
|   |-- uniprot/
|   |-- kegg/
|   |-- alphafold/
|   `-- clinvar/
|-- tests/
|-- requirements.txt
`-- Dockerfile
```
