from structure.analyzer import analyze_pdb_text
from structure.converter import convert_to_obj, convert_to_stl
from structure.mesh import analyze_mesh, build_structure_mesh
from structure.pymol_backend import export_mesh_with_pymol


def export_mesh(
    pdb_text: str,
    pdb_id: str,
    protein_name: str,
    representation: str,
    file_format: str,
    backend: str = "internal",
    subdivisions: int = 1,
    selection: str = "all",
) -> dict:
    backend = backend.lower()
    if backend == "internal":
        return _export_internal(
            pdb_text,
            pdb_id,
            protein_name,
            representation,
            file_format,
            subdivisions,
        )
    if backend == "pymol":
        return _export_pymol(
            pdb_text,
            pdb_id,
            protein_name,
            representation,
            file_format,
            selection,
        )
    raise ValueError("backend must be 'internal' or 'pymol'.")


def _export_internal(
    pdb_text: str,
    pdb_id: str,
    protein_name: str,
    representation: str,
    file_format: str,
    subdivisions: int,
) -> dict:
    base_name = f"{pdb_id.lower()}_{representation}"
    if file_format == "obj":
        path = convert_to_obj(
            pdb_text,
            output_name=f"{base_name}.obj",
            protein_name=protein_name,
            representation=representation,
            subdivisions=subdivisions,
        )
    elif file_format == "stl":
        path = convert_to_stl(
            pdb_text,
            output_name=f"{base_name}.stl",
            protein_name=protein_name,
            representation=representation,
            subdivisions=subdivisions,
        )
    else:
        raise ValueError("Internal backend supports 'obj' or 'stl'.")

    mesh_vertices, mesh_faces = _mesh_arrays_for_analysis(
        pdb_text,
        representation=representation,
        subdivisions=subdivisions,
    )
    return {
        "path": path,
        "backend": "internal",
        "mesh": analyze_mesh(mesh_vertices, mesh_faces),
    }


def _export_pymol(
    pdb_text: str,
    pdb_id: str,
    protein_name: str,
    representation: str,
    file_format: str,
    selection: str,
) -> dict:
    if file_format != "obj":
        raise ValueError("PyMOL backend currently supports mesh export only as 'obj'.")

    path = export_mesh_with_pymol(
        pdb_text,
        pdb_id=pdb_id,
        protein_name=protein_name,
        representation=representation,
        selection=selection,
    )

    summary = analyze_pdb_text(pdb_text)
    return {
        "path": path,
        "backend": "pymol",
        "mesh": {
            "vertices": None,
            "faces": None,
            "surface_area": None,
            "watertight": None,
            "bbox_min": None,
            "bbox_max": None,
            "note": "PyMOL export generated the mesh artifact; mesh metrics are not computed in this backend.",
        },
        "summary": summary,
    }


def _mesh_arrays_for_analysis(
    pdb_text: str,
    representation: str,
    subdivisions: int = 1,
):
    if representation == "atoms":
        return build_structure_mesh(pdb_text, representation="spheres", subdivisions=0)
    return build_structure_mesh(pdb_text, representation=representation, subdivisions=subdivisions)
