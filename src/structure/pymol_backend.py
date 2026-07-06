from pathlib import Path

from structure.converter import ensure_outputs_dir


SUPPORTED_FORMATS = {"obj"}
SUPPORTED_REPRESENTATIONS = {"cartoon", "surface", "sticks", "spheres", "lines"}


def pymol_available() -> bool:
    try:
        import pymol2  # noqa: F401
    except ImportError:
        return False
    return True


def export_mesh_with_pymol(
    pdb_text: str,
    pdb_id: str,
    protein_name: str,
    representation: str,
    selection: str = "all",
) -> str:
    if representation not in SUPPORTED_REPRESENTATIONS:
        raise ValueError(
            "PyMOL backend supports cartoon, surface, sticks, spheres, or lines."
        )

    output_path = ensure_outputs_dir() / f"{pdb_id.lower()}_{representation}_pymol.obj"
    with _pymol_session(pdb_text, pdb_id, selection, representation) as cmd:
        cmd.save(str(output_path), selection)
    return str(output_path)


def render_png_with_pymol(
    pdb_text: str,
    pdb_id: str,
    representation: str = "cartoon",
    selection: str = "all",
    width: int = 1600,
    height: int = 1200,
    ray: bool = True,
) -> str:
    output_path = ensure_outputs_dir() / f"{pdb_id.lower()}_{representation}_pymol.png"
    with _pymol_session(pdb_text, pdb_id, selection, representation) as cmd:
        cmd.bg_color("white")
        cmd.orient(selection)
        cmd.png(str(output_path), width=width, height=height, ray=1 if ray else 0)
    return str(output_path)


def save_pymol_session(
    pdb_text: str,
    pdb_id: str,
    representation: str = "cartoon",
    selection: str = "all",
) -> str:
    output_path = ensure_outputs_dir() / f"{pdb_id.lower()}_{representation}.pse"
    with _pymol_session(pdb_text, pdb_id, selection, representation) as cmd:
        cmd.save(str(output_path))
    return str(output_path)


class _pymol_session:
    def __init__(self, pdb_text: str, pdb_id: str, selection: str, representation: str):
        self._pdb_text = pdb_text
        self._pdb_id = pdb_id
        self._selection = selection
        self._representation = representation
        self._session = None
        self.cmd = None

    def __enter__(self):
        try:
            import pymol2
        except ImportError as exc:
            raise RuntimeError(
                "PyMOL backend is not available. Install 'pymol-open-source' "
                "or use backend='internal'."
            ) from exc

        self._session = pymol2.PyMOL()
        self._session.start()
        self.cmd = self._session.cmd
        self.cmd.reinitialize()
        self.cmd.read_pdbstr(self._pdb_text, self._pdb_id)
        self.cmd.remove("solvent")
        self.cmd.hide("everything", "all")
        self.cmd.show(self._representation, self._selection)
        self.cmd.orient(self._selection)
        return self.cmd

    def __exit__(self, exc_type, exc, tb):
        if self._session is not None:
            self._session.stop()
        return False
