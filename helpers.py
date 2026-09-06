
from pathlib import Path
import shutil
import subprocess
import re
import sys
import os


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def check_file_exists(path: Path, description: str):
    """Stop the script if an important file does not exist."""

    if not path.exists():
        print(f"\nERROR: {description} not found:")
        print(path)
        sys.exit(1)


def create_case_folder(output_dir: Path, wind_speed: int, seed: int) -> Path:
    """Create WSxx/Seedxx case directory."""

    ws_folder = output_dir / f"WS{wind_speed:02d}"
    seed_folder = ws_folder / f"Seed{seed:02d}"

    seed_folder.mkdir(parents=True, exist_ok=True)

    return seed_folder


def get_wind_file(wind_dir: Path, wind_speed: int, seed: int) -> Path:
    """Return the correct TurbSim BTS file."""

    filename = (
        f"90m_{wind_speed:02d}mps_twr_seed{seed:02d}.bts"
    )

    wind_file = (
        wind_dir
        / f"WS{wind_speed:02d}"
        / f"Seed{seed:02d}"
        / filename
    )

    return wind_file


def update_inflowwind(inflow_template: Path, wind_file: Path):
    """
    Update the existing InflowWind template with
    the current BTS wind-file path.

    The template itself is modified.
    """

    print("\nUpdating InflowWind file...")

    # Read template
    text = inflow_template.read_text(encoding="utf-8")

    # --------------------------------------------------------
    # Convert wind file path to a path relative to the
    # location of the InflowWind file.
    # --------------------------------------------------------

    relative_wind_path = os.path.relpath(
    wind_file,
    inflow_template.parent
    )

    # OpenFAST generally works well with forward slashes
    relative_wind_path = Path(relative_wind_path).as_posix()

    # --------------------------------------------------------
    # Find FileName_BTS line
    # --------------------------------------------------------

    pattern = re.compile(
        r'^(\s*)"[^"]*"(\s+FileName_BTS\b.*)$',
        re.MULTILINE
    )

    match = pattern.search(text)

    if not match:
        raise RuntimeError(
            "Could not find FileName_BTS in the InflowWind file."
        )

    # --------------------------------------------------------
    # Build the new line
    # --------------------------------------------------------

    new_line = (
        f'{match.group(1)}'
        f'"{relative_wind_path}"'
        f'{match.group(2)}'
    )

    # --------------------------------------------------------
    # Replace the old FileName_BTS line
    # --------------------------------------------------------

    text = pattern.sub(new_line, text, count=1)

    # Write the updated InflowWind file
    inflow_template.write_text(
        text,
        encoding="utf-8"
    )
    
    print(f"Wind file set to:")
    print(f"  {relative_wind_path}")
    


def copy_fst(fst_template : Path, case_folder: Path, wind_speed: int, seed: int) -> Path:
    """Copy and rename FST template."""

    case_fst = case_folder / f"5MW_Land_DLL_WTurb_WS{wind_speed:02d}_Seed{seed:02d}.fst"

    shutil.copy2(fst_template, case_fst)

    print("\nFST copied:")
    print(f"  {case_fst}")

    return case_fst


def update_fst_paths(module_files: dict, case_fst: Path):
    """
    Update AeroDyn, ElastoDyn, ServoDyn, Inflow and BeamDyn paths
    in the case-specific FST file.
    """

    print("\nUpdating FST module paths...")

    text = case_fst.read_text(
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Calculate paths relative to the case FST
    # --------------------------------------------------------

    for keyword, module_path in module_files.items():

        relative_path = os.path.relpath(
        module_path,
        case_fst.parent
        )

        relative_path = Path(relative_path).as_posix()

        # Search for:
        #
        # "something"    AeroFile
        #
        # and replace only the filename.

        pattern = re.compile(
            rf'^(\s*)"[^"]*"(\s+{re.escape(keyword)}.*)$',
            re.MULTILINE
        )

        match = pattern.search(text)

        if not match:
            print(
                f"WARNING: Could not find {keyword} "
                f"in {case_fst.name}"
            )
            continue

        new_line = (
            f'{match.group(1)}'
            f'"{relative_path}"'
            f'{match.group(2)}'
        )

        text = pattern.sub(
            new_line,
            text,
            count=1
        )

        print(
            f"  {keyword} → {relative_path}"
        )

    # Write updated FST
    case_fst.write_text(
        text,
        encoding="utf-8"
    )


def run_openfast(openfast_exe: Path ,case_fst: Path, log_file: Path):
    """Run OpenFAST and wait until simulation finishes."""

    print("\n" + "=" * 60)
    print("RUNNING OPENFAST")
    print("=" * 60)

    print(f"Input file:")
    print(case_fst)

    # --------------------------------------------------------
    # CASE HEADER — LOG FILE ONLY
    # --------------------------------------------------------
    case_name = case_fst.stem
    case_header = (
        "\n\n"
        + "=" * 70
        + "\n"
        + f"CASE: {case_name}\n"
        + f"FST : {case_fst}\n"
        + "=" * 70
        + "\n\n"
    )

    with open(log_file, "ab") as log:
        log.write(case_header.encode("utf-8"))
        log.flush()

    # --------------------------------------------------------
    # Run OpenFAST
    #
    # cwd = case directory
    # This is important because OpenFAST creates output
    # files relative to the case.
    # --------------------------------------------------------
    
    process = subprocess.Popen(
        [
            str(openfast_exe.resolve()),
            str(case_fst.name)
        ],
        cwd=case_fst.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
    )

    # --------------------------------------------------------
    # Display OpenFAST output immediately while also
    # saving the complete output to the common log file.
    # --------------------------------------------------------

    with open(log_file, "ab") as log:

        while True:

            byte = process.stdout.read(64)

            if not byte:
                break

            # Save raw byte to global log
            log.write(byte)
            log.flush()

            # Send raw byte directly to terminal
            sys.stdout.buffer.write(byte)
            sys.stdout.buffer.flush()

    process.wait()

    if process.returncode != 0:

        print("\nERROR: OpenFAST failed.")

        raise RuntimeError(
            f"OpenFAST returned error code "
            f"{process.returncode}"
        )

    print("\nOpenFAST completed successfully.")