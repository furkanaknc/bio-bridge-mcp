from shared.clients import get_clinvar_client
from shared.tool_metadata import READ_ONLY_OPEN_WORLD


def register_clinvar_tools(mcp):
    @mcp.tool(title="Search ClinVar variants", annotations=READ_ONLY_OPEN_WORLD)
    def search_clinvar_variants(query: str) -> str:
        """Search ClinVar for genetic variants."""
        clinvar_client = get_clinvar_client()
        if not clinvar_client:
            return "Error: ClinVar Client is not initialized."

        try:
            results = clinvar_client.search_variants(query, limit=10)
            if not results:
                return f"No variants found for '{query}'"
            if "error" in results[0]:
                return f"Error: {results[0]['error']}"

            output = [f"### ClinVar Variants for '{query}'"]
            for variant in results:
                output.append(f"- **{variant['title']}**")
                output.append(
                    "  "
                    f"Gene: {variant['gene']} | "
                    f"Significance: {variant['clinical_significance']}"
                )
                output.append(f"  Accession: {variant['accession']}")
            return "\n".join(output)
        except Exception as exc:
            return f"Error searching variants: {exc}"

    @mcp.tool(title="Search ClinVar by gene", annotations=READ_ONLY_OPEN_WORLD)
    def search_clinvar_by_gene(
        gene_symbol: str,
        significance: str | None = None,
    ) -> str:
        """Search ClinVar variants by gene symbol."""
        clinvar_client = get_clinvar_client()
        if not clinvar_client:
            return "Error: ClinVar Client is not initialized."

        try:
            results = clinvar_client.search_by_gene(gene_symbol, significance)
            if not results:
                return f"No variants found for gene '{gene_symbol}'"
            if "error" in results[0]:
                return f"Error: {results[0]['error']}"

            label = f" ({significance})" if significance else ""
            output = [f"### ClinVar Variants for {gene_symbol}{label}"]
            for variant in results:
                output.append(f"- **{variant['title'][:60]}**")
                output.append(
                    f"  Significance: {variant['clinical_significance']} | "
                    f"{variant['accession']}"
                )
            return "\n".join(output)
        except Exception as exc:
            return f"Error searching by gene: {exc}"
