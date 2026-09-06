from pathlib import Path
import sys

from helpers import (
    check_file_exists,
    create_case_folder,
    get_wind_file,
    update_inflowwind,
    copy_fst,
    update_fst_paths,
    run_openfast,
)


# ------------------------------------------------------------
# 5MW Baseline
# ------------------------------------------------------------
BASELINE_DIR = Path("5MW_Baseline")

WIND_DIR = BASELINE_DIR / "Wind" / "Wind_inflow_files"

INFLOW_TEMPLATE = (
    BASELINE_DIR
    / "Template"
    / "NRELOffshrBsline5MW_InflowWind_template.dat"
)

# ------------------------------------------------------------
# 5MW Land OpenFAST
# ------------------------------------------------------------
LAND_DIR = Path("5MW_Land_DLL_WTurb")

FST_TEMPLATE = (
    LAND_DIR
    / "Template"
    / "5MW_Land_DLL_WTurb_template.fst"
)

OUTPUT_DIR = LAND_DIR / "OpenFAST_Case_Outputs"

# ------------------------------------------------------------
# OpenFAST executable
# ------------------------------------------------------------

OPENFAST_EXE = Path("OpenFAST.exe")

# ------------------------------------------------------------
# OpenFAST module files
# ------------------------------------------------------------
AERODYN_FILE = (
    LAND_DIR
    / "NRELOffshrBsline5MW_Onshore_AeroDyn.dat"
)

ELASTODYN_FILE = (
    LAND_DIR
    / "NRELOffshrBsline5MW_Onshore_ElastoDyn.dat"
)

ELASTODYN_TOWER_FILE = (
    LAND_DIR
    / "NRELOffshrBsline5MW_Onshore_ElastoDyn_Tower.dat"
)

SERVODYN_FILE = (
    LAND_DIR
    / "NRELOffshrBsline5MW_Onshore_ServoDyn.dat"
)

BEAMDYN_FILE = (BASELINE_DIR / "NRELOffshrBsline5MW_BeamDyn.dat" )
# ------------------------------------------------------------
# Wind cases
# ------------------------------------------------------------
WIND_CASES = {
    5: 3,
    7: 3,
    9: 3,
    11: 6,
    13: 6,
    15: 6,
    19: 6,
    23: 6,
}

module_files = {
    "AeroFile": AERODYN_FILE,
    "EDFile": ELASTODYN_FILE,
    "ServoFile": SERVODYN_FILE,
    "InflowFile": INFLOW_TEMPLATE,
    "BDBldFile(1)": BEAMDYN_FILE,
    "BDBldFile(2)": BEAMDYN_FILE,
    "BDBldFile(3)": BEAMDYN_FILE,
}



# ============================================================
# Creating log file to capture openfast outputs
# ============================================================

log_file = OUTPUT_DIR / "OpenFAST_all_cases.log"

# Start a fresh log
log_file.write_bytes(b"")


# ============================================================
# CHECK ALL IMPORTANT FILES
# ============================================================

print("=" * 60)
print("OPENFAST AUTOMATION")
print("=" * 60)

check_file_exists(
    INFLOW_TEMPLATE,
    "InflowWind template"
)

check_file_exists(
    FST_TEMPLATE,
    "FST template"
)

check_file_exists(
    OPENFAST_EXE,
    "OpenFAST executable"
)

check_file_exists(
    AERODYN_FILE,
    "AeroDyn file"
)

check_file_exists(
    ELASTODYN_FILE,
    "ElastoDyn file"
)

check_file_exists(
    ELASTODYN_TOWER_FILE,
    "ElastoDyn Tower file"
)

check_file_exists(
    SERVODYN_FILE,
    "ServoDyn file"
)

check_file_exists(
    BEAMDYN_FILE,
    "BeamDyn file"
)

# ============================================================
# MAIN SIMULATION LOOP
# ============================================================

total_cases = sum(WIND_CASES.values())
case_number = 0
successful_cases = 0
failed_cases = 0
failed_case_names = []

print(f"\nTotal simulations: {total_cases}")

for wind_speed, number_of_seeds in WIND_CASES.items():

    for seed in range(1, number_of_seeds + 1):

        case_number += 1

        print("\n")
        print("=" * 60)
        print(
            f"CASE {case_number}/{total_cases}: "
            f"WS{wind_speed:02d} / Seed{seed:02d}"
        )
        print("=" * 60)

        # ----------------------------------------------------
        # TASK 1
        # Get BTS file and update InflowWind
        # ----------------------------------------------------

        wind_file = get_wind_file(
            WIND_DIR,
            wind_speed,
            seed
        )

        check_file_exists(
            wind_file,
            "Wind-field BTS file"
        )

        update_inflowwind(
            INFLOW_TEMPLATE,
            wind_file
        )

        # ----------------------------------------------------
        # TASK 2
        # Create case folder
        # ----------------------------------------------------

        case_folder = create_case_folder(
            OUTPUT_DIR,
            wind_speed,
            seed
        )

        print("\nCase folder:")
        print(case_folder)

        # ----------------------------------------------------
        # TASK 3
        # Copy and rename FST
        # ----------------------------------------------------

        case_fst = copy_fst(
            FST_TEMPLATE,
            case_folder,
            wind_speed,
            seed
        )

        # ----------------------------------------------------
        # TASK 4
        # Update module paths in FST
        # ----------------------------------------------------

        update_fst_paths(
            module_files,
            case_fst
        )

        # ----------------------------------------------------
        # TASK 5
        # Run OpenFAST
        # ----------------------------------------------------

        try:

            run_openfast(
                OPENFAST_EXE,
                case_fst,
                log_file
            )
            successful_cases += 1

        except Exception as error:

            failed_cases += 1
            failed_case_names.append(f"WS{wind_speed:02d} / Seed{seed:02d}")
            print("\n" + "!" * 60)
            print(
                f"CASE FAILED: "
                f"WS{wind_speed:02d} / Seed{seed:02d}"
            )
            print(error)
            print("!" * 60)

            # Continue with next case
            continue

        print(
            f"\nCASE COMPLETED: "
            f"WS{wind_speed:02d} / Seed{seed:02d}"
        )


# ============================================================
# FINISHED
# ============================================================

print("\n")
print("=" * 60)
print("ALL CASES PROCESSED")
print("=" * 60)

print("\n" + "=" * 60)
print("RUN SUMMARY")
print("=" * 60)

print(f"Total cases     : {total_cases}")
print(f"Successful      : {successful_cases}")
print(f"Failed          : {failed_cases}")

if failed_case_names:
    print("\nFailed cases:")

    for case in failed_case_names:
        print(f"  - {case}")
else:
    print("\nNo failed cases.")

# ============================================================
# CLOSE LOG FILE
# ============================================================

