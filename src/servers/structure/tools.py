from structure.service import (
    analyze_pdb_id,
    convert_pdb_id,
    convert_structure_file,
    export_structure_session,
    render_structure_image,
)


def register_structure_tools(mcp):
    @mcp.tool()
    def convert_structure_to_obj(
        pdb_file: str,
        representation: str = "spheres",
        file_format: str = "obj",
        backend: str = "internal",
        subdivisions: int = 1,
        selection: str = "all",
    ) -> dict:
        """Convert a local PDB file into an OBJ or STL mesh artifact."""
        try:
            return convert_structure_file(
                pdb_file,
                representation=representation,
                file_format=file_format,
                backend=backend,
                subdivisions=subdivisions,
                selection=selection,
            )
        except Exception as exc:
            return {"error": str(exc)}

    @mcp.tool()
    def convert_pdb_id_to_obj(
        pdb_id: str,
        representation: str = "spheres",
        file_format: str = "obj",
        backend: str = "internal",
        subdivisions: int = 1,
        selection: str = "all",
    ) -> dict:
        """Download a PDB structure from RCSB and export it as an OBJ or STL mesh."""
        try:
            return convert_pdb_id(
                pdb_id,
                representation=representation,
                file_format=file_format,
                backend=backend,
                subdivisions=subdivisions,
                selection=selection,
            )
        except Exception as exc:
            return {"error": str(exc)}

    @mcp.tool()
    def analyze_structure(
        pdb_id: str,
        create_obj: bool = False,
        representation: str = "spheres",
        file_format: str = "obj",
        backend: str = "internal",
        subdivisions: int = 1,
        selection: str = "all",
    ) -> dict:
        """Analyze a PDB entry and optionally produce a real mesh artifact."""
        try:
            return analyze_pdb_id(
                pdb_id,
                create_obj=create_obj,
                representation=representation,
                file_format=file_format,
                backend=backend,
                subdivisions=subdivisions,
                selection=selection,
            )
        except Exception as exc:
            return {"error": str(exc)}

    @mcp.tool()
    def render_structure_image_tool(
        pdb_id: str,
        representation: str = "cartoon",
        selection: str = "all",
        width: int = 1600,
        height: int = 1200,
        ray: bool = True,
    ) -> dict:
        """Render a PNG snapshot of a structure using the PyMOL backend."""
        try:
            return render_structure_image(
                pdb_id,
                representation=representation,
                selection=selection,
                width=width,
                height=height,
                ray=ray,
            )
        except Exception as exc:
            return {"error": str(exc)}

    @mcp.tool()
    def export_structure_session_tool(
        pdb_id: str,
        representation: str = "cartoon",
        selection: str = "all",
    ) -> dict:
        """Export a PyMOL session file for a structure view."""
        try:
            return export_structure_session(
                pdb_id,
                representation=representation,
                selection=selection,
            )
        except Exception as exc:
            return {"error": str(exc)}
