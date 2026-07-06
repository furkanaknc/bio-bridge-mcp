from pathlib import Path

from structure.analyzer import analyze_pdb_text
from structure.converter import convert_to_obj, convert_to_stl, ensure_outputs_dir
from structure.downloader import fetch_pdb_text
from structure.mesh import analyze_mesh, build_structure_mesh


def analyze_pdb_id(
    pdb_id: str,
    create_obj: bool = False,
    representation: str = "spheres",
    file_format: str = "obj",
    subdivisions: int = 1,
) -> dict:
    pdb_text = fetch_pdb_text(pdb_id)
    summary = analyze_pdb_text(pdb_text)
    summary["pdb_id"] = pdb_id.upper()
    summary["structure_files"] = {"pdb": _relative_output_path(save_pdb_text(pdb_id, pdb_text))}

    if create_obj:
        artifact = export_mesh_artifact(
            pdb_text,
            pdb_id=pdb_id,
            protein_name=summary["protein"],
            representation=representation,
            file_format=file_format,
            subdivisions=subdivisions,
        )
        summary["artifacts"] = {file_format: artifact["path"]}
        summary["mesh"] = artifact["mesh"]

    return summary


def convert_pdb_id(
    pdb_id: str,
    representation: str = "spheres",
    file_format: str = "obj",
    subdivisions: int = 1,
) -> dict:
    pdb_text = fetch_pdb_text(pdb_id)
    summary = analyze_pdb_text(pdb_text)
    artifact = export_mesh_artifact(
        pdb_text,
        pdb_id=pdb_id,
        protein_name=summary["protein"],
        representation=representation,
        file_format=file_format,
        subdivisions=subdivisions,
    )
    return {
        "pdb_id": pdb_id.upper(),
        "protein": summary["protein"],
        "representation": representation,
        "format": file_format,
        "artifacts": {
            file_format: artifact["path"],
            "pdb": _relative_output_path(save_pdb_text(pdb_id, pdb_text)),
        },
        "atoms": summary["atoms"],
        "chains": summary["chains"],
        "residues": summary["residues"],
        "ligands": summary["ligands"],
        "mesh": artifact["mesh"],
    }


def convert_structure_file(
    pdb_file: str,
    representation: str = "spheres",
    file_format: str = "obj",
    subdivisions: int = 1,
) -> dict:
    input_path = Path(pdb_file)
    pdb_text = input_path.read_text(encoding="utf-8")
    summary = analyze_pdb_text(pdb_text)
    artifact = export_mesh_artifact(
        pdb_text,
        pdb_id=input_path.stem,
        protein_name=summary["protein"],
        representation=representation,
        file_format=file_format,
        subdivisions=subdivisions,
    )
    return {
        "source": str(input_path),
        "protein": summary["protein"],
        "representation": representation,
        "format": file_format,
        "artifacts": {file_format: artifact["path"]},
        "atoms": summary["atoms"],
        "chains": summary["chains"],
        "residues": summary["residues"],
        "ligands": summary["ligands"],
        "mesh": artifact["mesh"],
    }


def _relative_output_path(path: str) -> str:
    output_path = Path(path)
    try:
        return str(output_path.relative_to(Path(__file__).resolve().parents[2]))
    except ValueError:
        return str(output_path)


def export_mesh_artifact(
    pdb_text: str,
    pdb_id: str,
    protein_name: str,
    representation: str,
    file_format: str,
    subdivisions: int = 1,
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
        raise ValueError("file_format must be 'obj' or 'stl'.")

    mesh_vertices, mesh_faces = _mesh_arrays_for_analysis(
        pdb_text,
        representation=representation,
        subdivisions=subdivisions,
    )
    return {
        "path": _relative_output_path(path),
        "mesh": analyze_mesh(mesh_vertices, mesh_faces),
    }


def save_pdb_text(pdb_id: str, pdb_text: str) -> str:
    output_path = ensure_outputs_dir() / f"{pdb_id.lower()}.pdb"
    output_path.write_text(pdb_text, encoding="utf-8")
    return str(output_path)


def _mesh_arrays_for_analysis(
    pdb_text: str,
    representation: str,
    subdivisions: int = 1,
):
    if representation == "atoms":
        return build_structure_mesh(pdb_text, representation="spheres", subdivisions=0)
    return build_structure_mesh(pdb_text, representation=representation, subdivisions=subdivisions)
