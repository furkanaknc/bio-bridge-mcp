from shared.clients import get_alphafold_client
from shared.tool_metadata import READ_ONLY_OPEN_WORLD


def register_alphafold_tools(mcp):
    @mcp.tool(title="Get AlphaFold structure", annotations=READ_ONLY_OPEN_WORLD)
    def get_alphafold_structure(uniprot_id: str) -> str:
        """Get the predicted 3D structure of a protein from AlphaFold."""
        alphafold_client = get_alphafold_client()
        if not alphafold_client:
            return "Error: AlphaFold Client is not initialized."

        try:
            result = alphafold_client.get_prediction(uniprot_id)
            if "error" in result:
                return f"Error: {result['error']}"

            output = [f"### AlphaFold Structure: {result['uniprot_id']}"]
            output.append(f"**Entry ID:** {result.get('entry_id', 'N/A')}")
            output.append(f"**Gene:** {result.get('gene', 'N/A')}")
            output.append(f"**Organism:** {result.get('organism', 'N/A')}")
            output.append(f"**Sequence Length:** {result.get('sequence_length', 0)} aa")
            output.append(f"**Model Version:** {result.get('latest_version', 1)}")
            output.append("---")
            output.append("**Download Links:**")
            output.append(f"- PDB: {result.get('pdb_url', 'N/A')}")
            output.append(f"- PAE Image: {result.get('pae_image_url', 'N/A')}")
            return "\n".join(output)
        except Exception as exc:
            return f"Error getting AlphaFold structure: {exc}"
