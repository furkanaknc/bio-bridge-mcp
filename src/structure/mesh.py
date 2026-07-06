from collections import Counter
from math import sqrt

import numpy as np
from Bio.PDB import PDBParser
from io import StringIO


VDW_RADII = {
    "H": 1.20,
    "C": 1.70,
    "N": 1.55,
    "O": 1.52,
    "S": 1.80,
    "P": 1.80,
    "FE": 1.80,
    "MG": 1.73,
    "ZN": 1.39,
    "CA": 1.94,
}


def build_structure_mesh(
    pdb_text: str,
    representation: str = "spheres",
    subdivisions: int = 1,
) -> tuple[np.ndarray, np.ndarray]:
    if representation not in {"spheres", "surface"}:
        raise ValueError("Mesh export supports 'spheres' or 'surface' representations.")

    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("structure", StringIO(pdb_text))
    template_vertices, template_faces = generate_icosphere(subdivisions=subdivisions)

    all_vertices = []
    all_faces = []
    vertex_offset = 0

    for atom in structure.get_atoms():
        center = np.array(atom.coord, dtype=float)
        radius = VDW_RADII.get((atom.element or "").strip().upper(), 1.50)
        vertices = template_vertices * radius + center
        faces = template_faces + vertex_offset
        all_vertices.append(vertices)
        all_faces.append(faces)
        vertex_offset += len(vertices)

    if not all_vertices:
        return np.empty((0, 3), dtype=float), np.empty((0, 3), dtype=int)

    return np.vstack(all_vertices), np.vstack(all_faces)


def generate_icosphere(subdivisions: int = 1) -> tuple[np.ndarray, np.ndarray]:
    t = (1.0 + sqrt(5.0)) / 2.0
    vertices = np.array(
        [
            (-1, t, 0),
            (1, t, 0),
            (-1, -t, 0),
            (1, -t, 0),
            (0, -1, t),
            (0, 1, t),
            (0, -1, -t),
            (0, 1, -t),
            (t, 0, -1),
            (t, 0, 1),
            (-t, 0, -1),
            (-t, 0, 1),
        ],
        dtype=float,
    )
    vertices /= np.linalg.norm(vertices, axis=1)[:, np.newaxis]

    faces = np.array(
        [
            (0, 11, 5),
            (0, 5, 1),
            (0, 1, 7),
            (0, 7, 10),
            (0, 10, 11),
            (1, 5, 9),
            (5, 11, 4),
            (11, 10, 2),
            (10, 7, 6),
            (7, 1, 8),
            (3, 9, 4),
            (3, 4, 2),
            (3, 2, 6),
            (3, 6, 8),
            (3, 8, 9),
            (4, 9, 5),
            (2, 4, 11),
            (6, 2, 10),
            (8, 6, 7),
            (9, 8, 1),
        ],
        dtype=int,
    )

    for _ in range(subdivisions):
        midpoint_cache = {}
        new_faces = []

        def midpoint_index(i: int, j: int) -> int:
            key = tuple(sorted((i, j)))
            if key in midpoint_cache:
                return midpoint_cache[key]

            midpoint = (vertices[i] + vertices[j]) / 2.0
            midpoint /= np.linalg.norm(midpoint)

            midpoint_cache[key] = len(vertex_list)
            vertex_list.append(midpoint)
            return midpoint_cache[key]

        vertex_list = vertices.tolist()
        for tri in faces:
            a = midpoint_index(tri[0], tri[1])
            b = midpoint_index(tri[1], tri[2])
            c = midpoint_index(tri[2], tri[0])
            new_faces.extend(
                [
                    (tri[0], a, c),
                    (tri[1], b, a),
                    (tri[2], c, b),
                    (a, b, c),
                ]
            )

        vertices = np.array(vertex_list, dtype=float)
        faces = np.array(new_faces, dtype=int)

    return vertices, faces


def analyze_mesh(vertices: np.ndarray, faces: np.ndarray) -> dict:
    if len(vertices) == 0 or len(faces) == 0:
        return {
            "vertices": 0,
            "faces": 0,
            "surface_area": 0.0,
            "watertight": False,
            "bbox_min": [0.0, 0.0, 0.0],
            "bbox_max": [0.0, 0.0, 0.0],
        }

    triangles = vertices[faces]
    cross_products = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    areas = 0.5 * np.linalg.norm(cross_products, axis=1)

    edge_counts = Counter()
    for face in faces:
        edges = [
            tuple(sorted((int(face[0]), int(face[1])))),
            tuple(sorted((int(face[1]), int(face[2])))),
            tuple(sorted((int(face[2]), int(face[0])))),
        ]
        edge_counts.update(edges)

    watertight = all(count == 2 for count in edge_counts.values())

    return {
        "vertices": int(len(vertices)),
        "faces": int(len(faces)),
        "surface_area": round(float(np.sum(areas)), 3),
        "watertight": watertight,
        "bbox_min": [round(float(v), 3) for v in np.min(vertices, axis=0)],
        "bbox_max": [round(float(v), 3) for v in np.max(vertices, axis=0)],
    }
