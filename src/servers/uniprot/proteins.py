from shared.clients import get_uniprot_client
from shared.tool_metadata import READ_ONLY_OPEN_WORLD


def register_uniprot_tools(mcp):
    @mcp.tool(title="Get UniProt entry", annotations=READ_ONLY_OPEN_WORLD)
    def get_uniprot_entry(uniprot_id: str) -> str:
        """Get detailed protein information from UniProt."""
        uniprot_client = get_uniprot_client()
        if not uniprot_client:
            return "Error: UniProt Client is not initialized."

        try:
            result = uniprot_client.get_entry(uniprot_id)
            if "error" in result:
                return f"Error: {result['error']}"

            output = [f"### Protein: {result['protein_name']}"]
            output.append(f"**Accession:** {result['accession']}")
            genes = ", ".join(result["gene_names"]) if result["gene_names"] else "N/A"
            output.append(f"**Gene(s):** {genes}")
            output.append(f"**Organism:** {result['organism']}")
            output.append("---")

            if result.get("function"):
                output.append("**Function:**")
                output.append(result["function"])
                output.append("---")

            if result.get("sequence_info"):
                seq = result["sequence_info"]
                output.append(
                    f"**Sequence:** {seq.get('length', 0)} aa, "
                    f"{seq.get('mass', 0) / 1000:.1f} kDa"
                )
            return "\n".join(output)
        except Exception as exc:
            return f"Error getting UniProt entry: {exc}"

    @mcp.tool(title="Search UniProt proteins", annotations=READ_ONLY_OPEN_WORLD)
    def search_uniprot_proteins(query: str, organism: str = "human") -> str:
        """Search for proteins in UniProt."""
        uniprot_client = get_uniprot_client()
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
                genes = ", ".join(protein["gene_names"][:2]) if protein["gene_names"] else "N/A"
                output.append(f"- **{protein['accession']}**: {protein['protein_name']}")
                output.append(f"  *Gene(s): {genes}*")

            output.append("")
            output.append("*Use `get_uniprot_entry` for detailed information.*")
            return "\n".join(output)
        except Exception as exc:
            return f"Error searching proteins: {exc}"

    @mcp.tool(title="Get protein GO terms", annotations=READ_ONLY_OPEN_WORLD)
    def get_protein_go_terms(uniprot_id: str) -> str:
        """Get Gene Ontology terms for a protein."""
        uniprot_client = get_uniprot_client()
        if not uniprot_client:
            return "Error: UniProt Client is not initialized."

        try:
            result = uniprot_client.get_go_terms(uniprot_id)
            if "error" in result:
                return f"Error: {result['error']}"

            output = [f"### GO Terms for {result['accession']} ({result['protein_name']})"]
            go_terms = result.get("go_terms", {})

            if go_terms.get("molecular_function"):
                output.append("**Molecular Function:**")
                for term in go_terms["molecular_function"]:
                    output.append(f"- {term['id']}: {term['name']}")

            if go_terms.get("biological_process"):
                output.append("**Biological Process:**")
                for term in go_terms["biological_process"]:
                    output.append(f"- {term['id']}: {term['name']}")

            if go_terms.get("cellular_component"):
                output.append("**Cellular Component:**")
                for term in go_terms["cellular_component"]:
                    output.append(f"- {term['id']}: {term['name']}")

            if not any(go_terms.values()):
                output.append("No GO terms found.")
            return "\n".join(output)
        except Exception as exc:
            return f"Error getting GO terms: {exc}"

    @mcp.tool(title="Get protein pathways", annotations=READ_ONLY_OPEN_WORLD)
    def get_protein_pathways(uniprot_id: str) -> str:
        """Get metabolic and signaling pathways for a protein."""
        uniprot_client = get_uniprot_client()
        if not uniprot_client:
            return "Error: UniProt Client is not initialized."

        try:
            result = uniprot_client.get_pathways(uniprot_id)
            if "error" in result:
                return f"Error: {result['error']}"

            output = [f"### Pathways for {result['accession']} ({result['protein_name']})"]
            pathways = result.get("pathways", [])
            if pathways:
                for pathway in pathways:
                    output.append(f"- **{pathway['database']}**: {pathway['id']}")
                    if pathway.get("name"):
                        output.append(f"  {pathway['name']}")
            else:
                output.append("No pathway information found.")
            return "\n".join(output)
        except Exception as exc:
            return f"Error getting pathways: {exc}"
