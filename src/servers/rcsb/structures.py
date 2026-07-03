from shared.clients import get_rcsb_client


def register_rcsb_tools(mcp):
    @mcp.tool()
    def pdb_get_summary(pdb_id: str) -> str:
        """Get details about a PDB structure, including classification and mutations."""
        rcsb_client = get_rcsb_client()
        if not rcsb_client:
            return "Error: RCSB Client is not initialized."

        try:
            data = rcsb_client.get_pdb_summary(pdb_id)
            if "error" in data:
                return f"Error: {data['error']}"

            output = [f"### PDB Structure: {data.get('pdb_id')} ({data.get('title')})"]
            output.append(f"**Classification:** {data.get('classification')}")
            output.append("---")

            if data.get("has_mutations"):
                output.append("**Mutations Detected:** YES")
                for mutation in data.get("mutation_details", []):
                    output.append(
                        f"- Entity {mutation['entity_id']}: "
                        f"Official Count={mutation['official_count']}"
                    )
                    for detail in mutation.get("details", []):
                        output.append(f"  * {detail}")
            else:
                output.append("**Mutations:** None detected (Wild Type)")

            return "\n".join(output)
        except Exception as exc:
            return f"Error analyzing PDB summary: {exc}"

    @mcp.tool()
    def pdb_get_ligands(pdb_id: str) -> str:
        """List small molecule ligands bound to a PDB structure."""
        rcsb_client = get_rcsb_client()
        if not rcsb_client:
            return "Error: RCSB Client is not initialized."

        try:
            ligands = rcsb_client.get_pdb_ligands(pdb_id)
            if not ligands:
                return f"No significant ligands found for {pdb_id}."

            output = [f"### Ligands in {pdb_id}"]
            for ligand in ligands:
                output.append(f"**{ligand['ligand_id']}** ({ligand['name']})")
                if ligand.get("binding_info"):
                    output.append(
                        f"- Binding Data: {'; '.join(ligand['binding_info'])}"
                    )
                output.append("---")
            return "\n".join(output)
        except Exception as exc:
            return f"Error fetching ligands: {exc}"

    @mcp.tool()
    def pdb_find_pockets(pdb_id: str, ligand_id: str = None) -> str:
        """Identify binding pockets in a PDB structure."""
        rcsb_client = get_rcsb_client()
        if not rcsb_client:
            return "Error: RCSB Client is not initialized."

        try:
            data = rcsb_client.get_binding_pocket(pdb_id, ligand_id)
            if "error" in data:
                return f"Error: {data['error']}"

            output = [f"### Binding Pockets for {data.get('ligand_id')} in {pdb_id}"]
            output.append(f"**Description:** {data.get('description')}")
            output.append("---")

            for pocket in data.get("pockets", []):
                if isinstance(pocket, str):
                    output.append(f"- {pocket}")
                    continue
                center = pocket.get("center", {})
                output.append(
                    f"**Instance (Chain {pocket.get('chain_id')}):** "
                    f"X={center.get('x')}, Y={center.get('y')}, Z={center.get('z')}"
                )

            return "\n".join(output)
        except Exception as exc:
            return f"Error calculating binding pocket: {exc}"

    @mcp.tool()
    def pdb_search(query: str, resolution: str = None, method: str = None) -> str:
        """Search for PDB structures using advanced filters."""
        rcsb_client = get_rcsb_client()
        if not rcsb_client:
            return "Error: RCSB Client is not initialized."

        try:
            results = rcsb_client.search_structures(
                query,
                resolution=resolution,
                method=method,
            )
            if not results:
                message = f"No PDB structures found for query: '{query}'"
                if resolution:
                    message += f" (Resolution: {resolution})"
                if method:
                    message += f" (Method: {method})"
                return message
            if "error" in results[0]:
                return f"Error searching PDB: {results[0]['error']}"

            output = [f"### PDB Search Results for '{query}'"]
            if resolution or method:
                output.append(
                    f"*(Filters: Resolution={resolution or 'Any'}, "
                    f"Method={method or 'Any'})*"
                )

            for item in results:
                output.append(f"- **{item['pdb_id']}** (Score: {item.get('score', 'N/A')})")

            output.append("")
            output.append(
                "You can now use 'pdb_get_summary', 'pdb_get_ligands' or "
                "'pdb_find_pockets' with these IDs."
            )
            return "\n".join(output)
        except Exception as exc:
            return f"Error executing search: {exc}"

    @mcp.tool()
    def pdb_get_validation_report(pdb_id: str) -> str:
        """Get the quality validation report for a PDB structure."""
        rcsb_client = get_rcsb_client()
        if not rcsb_client:
            return "Error: RCSB Client is not initialized."

        try:
            report = rcsb_client.get_validation_report(pdb_id)
            if "error" in report:
                return f"Error: {report['error']}"

            resolution = report.get("resolution")
            if isinstance(resolution, list) and resolution:
                resolution = resolution[0]

            output = [f"### Validation Report for {report.get('pdb_id')}"]
            output.append(f"**Overall Quality:** {report.get('quality_assessment')}")
            output.append(f"- **Resolution:** {resolution} A")
            return "\n".join(output)
        except Exception as exc:
            return f"Error fetching validation report: {exc}"

    @mcp.tool()
    def pdb_search_by_uniprot(uniprot_id: str) -> str:
        """Find PDB structures corresponding to a UniProt entry."""
        rcsb_client = get_rcsb_client()
        if not rcsb_client:
            return "Error: RCSB Client is not initialized."

        try:
            results = rcsb_client.search_by_uniprot(uniprot_id)
            if not results:
                return f"No PDB structures found for UniProt ID: '{uniprot_id}'"
            if "error" in results[0]:
                return f"Error searching by UniProt: {results[0]['error']}"

            output = [f"### PDB Structures for UniProt {uniprot_id}"]
            for item in results:
                output.append(f"- **{item['pdb_id']}** (Score: {item.get('score', 'N/A')})")
            return "\n".join(output)
        except Exception as exc:
            return f"Error executing UniProt search: {exc}"

    @mcp.tool()
    def pdb_download_structure(pdb_id: str, file_format: str = "pdb") -> str:
        """Download the raw content for a PDB structure file."""
        rcsb_client = get_rcsb_client()
        if not rcsb_client:
            return "Error: RCSB Client is not initialized."

        try:
            content = rcsb_client.download_structure(pdb_id, file_format)
            if content.startswith("Error"):
                return content

            lines = content.splitlines()
            if len(lines) > 2000:
                return "\n".join(lines[:2000]) + f"\n... (Truncated. Total lines: {len(lines)})"
            return content
        except Exception as exc:
            return f"Error downloading structure: {exc}"
