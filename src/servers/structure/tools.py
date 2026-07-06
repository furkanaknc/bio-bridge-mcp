from structure.service import analyze_pdb_id, convert_pdb_id, convert_structure_file


def register_structure_tools(mcp):
    @mcp.tool()
    def convert_structure_to_obj(
        pdb_file: str,
        representation: str = "spheres",
        file_format: str = "obj",
        subdivisions: int = 1,
    ) -> dict:
        """Convert a local PDB file into an OBJ or STL mesh artifact."""
        try:
            return convert_structure_file(
                pdb_file,
                representation=representation,
                file_format=file_format,
                subdivisions=subdivisions,
            )
        except Exception as exc:
            return {"error": str(exc)}

    @mcp.tool()
    def convert_pdb_id_to_obj(
        pdb_id: str,
        representation: str = "spheres",
        file_format: str = "obj",
        subdivisions: int = 1,
    ) -> dict:
        """Download a PDB structure from RCSB and export it as an OBJ or STL mesh."""
        try:
            return convert_pdb_id(
                pdb_id,
                representation=representation,
                file_format=file_format,
                subdivisions=subdivisions,
            )
        except Exception as exc:
            return {"error": str(exc)}

    @mcp.tool()
    def analyze_structure(
        pdb_id: str,
        create_obj: bool = False,
        representation: str = "spheres",
        file_format: str = "obj",
        subdivisions: int = 1,
    ) -> dict:
        """Analyze a PDB entry and optionally produce a real mesh artifact."""
        try:
            return analyze_pdb_id(
                pdb_id,
                create_obj=create_obj,
                representation=representation,
                file_format=file_format,
                subdivisions=subdivisions,
            )
        except Exception as exc:
            return {"error": str(exc)}
