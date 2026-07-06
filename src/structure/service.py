from pathlib import Path

from structure.analyzer import analyze_pdb_text
from structure.backends import export_mesh
from structure.converter import ensure_outputs_dir
from structure.downloader import fetch_pdb_text
from structure.pymol_backend import pymol_available, render_png_with_pymol, save_pymol_session


def analyze_pdb_id(
    pdb_id: str,
    create_obj: bool = False,
    representation: str = "spheres",
    file_format: str = "obj",
    backend: str = "internal",
    subdivisions: int = 1,
    selection: str = "all",
) -> dict:
    pdb_text = fetch_pdb_text(pdb_id)
    summary = analyze_pdb_text(pdb_text)
    summary["pdb_id"] = pdb_id.upper()
    summary["structure_files"] = {"pdb": _relative_output_path(save_pdb_text(pdb_id, pdb_text))}
    summary["backend"] = backend
    summary["pymol_available"] = pymol_available()

    if create_obj:
        artifact = export_mesh_artifact(
            pdb_text,
            pdb_id=pdb_id,
            protein_name=summary["protein"],
            representation=representation,
            file_format=file_format,
            backend=backend,
            subdivisions=subdivisions,
            selection=selection,
        )
        summary["artifacts"] = {file_format: artifact["path"]}
        summary["mesh"] = artifact["mesh"]

    return summary


def convert_pdb_id(
    pdb_id: str,
    representation: str = "spheres",
    file_format: str = "obj",
    backend: str = "internal",
    subdivisions: int = 1,
    selection: str = "all",
) -> dict:
    pdb_text = fetch_pdb_text(pdb_id)
    summary = analyze_pdb_text(pdb_text)
    artifact = export_mesh_artifact(
        pdb_text,
        pdb_id=pdb_id,
        protein_name=summary["protein"],
        representation=representation,
        file_format=file_format,
        backend=backend,
        subdivisions=subdivisions,
        selection=selection,
    )
    return {
        "pdb_id": pdb_id.upper(),
        "protein": summary["protein"],
        "representation": representation,
        "format": file_format,
        "backend": artifact["backend"],
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
    backend: str = "internal",
    subdivisions: int = 1,
    selection: str = "all",
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
        backend=backend,
        subdivisions=subdivisions,
        selection=selection,
    )
    return {
        "source": str(input_path),
        "protein": summary["protein"],
        "representation": representation,
        "format": file_format,
        "backend": artifact["backend"],
        "artifacts": {file_format: artifact["path"]},
        "atoms": summary["atoms"],
        "chains": summary["chains"],
        "residues": summary["residues"],
        "ligands": summary["ligands"],
        "mesh": artifact["mesh"],
    }


def render_structure_image(
    pdb_id: str,
    representation: str = "cartoon",
    selection: str = "all",
    width: int = 1600,
    height: int = 1200,
    ray: bool = True,
) -> dict:
    pdb_text = fetch_pdb_text(pdb_id)
    summary = analyze_pdb_text(pdb_text)
    image_path = render_png_with_pymol(
        pdb_text,
        pdb_id=pdb_id,
        representation=representation,
        selection=selection,
        width=width,
        height=height,
        ray=ray,
    )
    return {
        "pdb_id": pdb_id.upper(),
        "protein": summary["protein"],
        "backend": "pymol",
        "representation": representation,
        "selection": selection,
        "artifacts": {
            "png": _relative_output_path(image_path),
            "pdb": _relative_output_path(save_pdb_text(pdb_id, pdb_text)),
        },
    }


def export_structure_session(
    pdb_id: str,
    representation: str = "cartoon",
    selection: str = "all",
) -> dict:
    pdb_text = fetch_pdb_text(pdb_id)
    summary = analyze_pdb_text(pdb_text)
    session_path = save_pymol_session(
        pdb_text,
        pdb_id=pdb_id,
        representation=representation,
        selection=selection,
    )
    return {
        "pdb_id": pdb_id.upper(),
        "protein": summary["protein"],
        "backend": "pymol",
        "representation": representation,
        "selection": selection,
        "artifacts": {
            "pse": _relative_output_path(session_path),
            "pdb": _relative_output_path(save_pdb_text(pdb_id, pdb_text)),
        },
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
    backend: str = "internal",
    subdivisions: int = 1,
    selection: str = "all",
) -> dict:
    export_result = export_mesh(
        pdb_text,
        pdb_id=pdb_id,
        protein_name=protein_name,
        representation=representation,
        file_format=file_format,
        backend=backend,
        subdivisions=subdivisions,
        selection=selection,
    )
    return {
        "path": _relative_output_path(export_result["path"]),
        "mesh": export_result["mesh"],
        "backend": export_result["backend"],
    }


def save_pdb_text(pdb_id: str, pdb_text: str) -> str:
    output_path = ensure_outputs_dir() / f"{pdb_id.lower()}.pdb"
    output_path.write_text(pdb_text, encoding="utf-8")
    return str(output_path)
