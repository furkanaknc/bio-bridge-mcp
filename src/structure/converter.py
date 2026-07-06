from pathlib import Path

import numpy as np

from structure.mesh import build_structure_mesh


OUTPUTS_DIR = Path(__file__).resolve().parents[2] / "outputs"


def ensure_outputs_dir() -> Path:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUTS_DIR


def convert_to_obj(
    pdb_text: str,
    output_name: str,
    protein_name: str = "Unknown",
    representation: str = "spheres",
    subdivisions: int = 1,
) -> str:
    if representation == "atoms":
        return convert_atoms_to_obj(pdb_text, output_name, protein_name=protein_name)

    output_path = ensure_outputs_dir() / output_name
    if output_path.suffix.lower() != ".obj":
        output_path = output_path.with_suffix(".obj")

    vertices, faces = build_structure_mesh(
        pdb_text,
        representation=representation,
        subdivisions=subdivisions,
    )

    lines = [
        f"# Bio-Bridge OBJ export",
        f"# Protein: {protein_name}",
        f"# Representation: {representation}",
    ]

    for x, y, z in vertices:
        lines.append(f"v {x:.3f} {y:.3f} {z:.3f}")
    for a, b, c in faces:
        lines.append(f"f {a + 1} {b + 1} {c + 1}")

    lines.append(f"# Vertices: {len(vertices)}")
    lines.append(f"# Faces: {len(faces)}")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(output_path)


def convert_to_stl(
    pdb_text: str,
    output_name: str,
    protein_name: str = "Unknown",
    representation: str = "spheres",
    subdivisions: int = 1,
) -> str:
    if representation == "atoms":
        raise ValueError("STL export requires a mesh representation such as 'spheres' or 'surface'.")

    output_path = ensure_outputs_dir() / output_name
    if output_path.suffix.lower() != ".stl":
        output_path = output_path.with_suffix(".stl")

    vertices, faces = build_structure_mesh(
        pdb_text,
        representation=representation,
        subdivisions=subdivisions,
    )

    lines = [f"solid {protein_name or 'structure'}"]
    for face in faces:
        v1, v2, v3 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
        normal = np.cross(v2 - v1, v3 - v1)
        norm = np.linalg.norm(normal)
        if norm:
            normal = normal / norm
        else:
            normal = np.array([0.0, 0.0, 0.0])

        lines.append(f"  facet normal {normal[0]:.6f} {normal[1]:.6f} {normal[2]:.6f}")
        lines.append("    outer loop")
        lines.append(f"      vertex {v1[0]:.6f} {v1[1]:.6f} {v1[2]:.6f}")
        lines.append(f"      vertex {v2[0]:.6f} {v2[1]:.6f} {v2[2]:.6f}")
        lines.append(f"      vertex {v3[0]:.6f} {v3[1]:.6f} {v3[2]:.6f}")
        lines.append("    endloop")
        lines.append("  endfacet")
    lines.append(f"endsolid {protein_name or 'structure'}")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(output_path)


def convert_atoms_to_obj(
    pdb_text: str,
    output_name: str,
    protein_name: str = "Unknown",
) -> str:
    from io import StringIO
    from Bio.PDB import PDBParser

    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("structure", StringIO(pdb_text))

    output_path = ensure_outputs_dir() / output_name
    if output_path.suffix.lower() != ".obj":
        output_path = output_path.with_suffix(".obj")

    lines = [
        f"# Bio-Bridge OBJ export",
        f"# Protein: {protein_name}",
        "# Representation: atoms",
    ]

    vertex_count = 0
    for atom in structure.get_atoms():
        x, y, z = atom.coord
        element = (atom.element or "").strip() or atom.get_name().strip()
        lines.append(f"v {x:.3f} {y:.3f} {z:.3f}")
        lines.append(f"# atom {atom.get_full_id()[2]}:{atom.get_parent().resname}:{atom.get_name()}:{element}")
        vertex_count += 1

    lines.append(f"# Vertices: {vertex_count}")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(output_path)
