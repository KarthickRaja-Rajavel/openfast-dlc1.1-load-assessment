from pathlib import Path
import subprocess


# ============================================================
# USER SETTINGS
# ============================================================

# Path to TurbSim executable
TURBSIM_EXE = Path("bin/TurbSim_x64.exe")

# Master TurbSim input file
TEMPLATE_INP = Path("Template/windfield.inp")

# Where simulation cases will be created
SIMULATION_DIR = Path("Wind_inflow_files")

# Wind speeds [m/s]
WIND_SPEEDS = [5, 7, 9, 11, 13, 15, 19, 23]

# IEC 61400-1:2019:
#   Below Vr-2:      6 simulations per wind speed
#   Vr-2 to cut-out: 15 simulations per wind speed
# Reduced seed set used here to limit computational/storage requirements.

LOW_WIND_SEEDS = [1, 2, 3]              # IEC: 6; reduced to 3
HIGH_WIND_SEEDS = [4, 5, 6]             # IEC: 15; reduced to 6

# ============================================================
# FUNCTION: MODIFY TURBSIM INPUT
# ============================================================

def create_turbsim_input(template_text, wind_speed, seed):

    text = template_text

    # Replace values marked with placeholders
    text = text.replace("{{SEED}}", str(seed))
    text = text.replace("{{UREF}}", str(wind_speed))

    return text


# ============================================================
# MAIN
# ============================================================

def main():

    # Check that required files exist
    if not TURBSIM_EXE.exists():
        raise FileNotFoundError(
            f"TurbSim executable not found:\n{TURBSIM_EXE}"
        )

    if not TEMPLATE_INP.exists():
        raise FileNotFoundError(
            f"TurbSim template not found:\n{TEMPLATE_INP}"
        )

    # Read template once
    template_text = TEMPLATE_INP.read_text()

    # ========================================================
    # WIND SPEED LOOP
    # ========================================================

    for wind_speed in WIND_SPEEDS:

        print("\n" + "=" * 60)
        print(f"STARTING WIND SPEED: {wind_speed} m/s")
        print("=" * 60)

        # ====================================================
        # SEED LOOP
        # ====================================================
        if wind_speed <= 9:   # Vr - 2 = 11.4 - 2 = 9.4 m/s
            SEEDS = LOW_WIND_SEEDS
        else :
            SEEDS = LOW_WIND_SEEDS + HIGH_WIND_SEEDS

        for seed in SEEDS:

            print("\n" + "-" * 60)
            print(f"Wind speed = {wind_speed} m/s")
            print(f"Seed       = {seed}")
            print("-" * 60)

            # ------------------------------------------------
            # Create folder
            # ------------------------------------------------

            case_dir = (
                SIMULATION_DIR
                / f"WS{wind_speed:02d}"
                / f"Seed{seed:02d}"
            )

            case_dir.mkdir(parents=True, exist_ok=True)

            # ------------------------------------------------
            # Create input file
            # ------------------------------------------------

            input_name = (
                f"90m_{wind_speed:02d}mps_twr_seed{seed:02d}.inp"
            )

            input_file = case_dir / input_name

            input_text = create_turbsim_input(
                template_text,
                wind_speed,
                seed
            )

            input_file.write_text(input_text)

            print(f"Created: {input_file}")

            # ------------------------------------------------
            # Run TurbSim
            # ------------------------------------------------

            print("Running TurbSim...")

            result = subprocess.run(
                [
                    str(TURBSIM_EXE.resolve()),
                    input_file.name
                ],
                cwd=case_dir,
                capture_output=True,
                text=True
            )

            # Print TurbSim output
            print(result.stdout)

            if result.stderr:
                print("TurbSim errors/warnings:")
                print(result.stderr)

            # ------------------------------------------------
            # Check whether TurbSim succeeded
            # ------------------------------------------------

            if result.returncode != 0:

                print(
                    f"ERROR: TurbSim failed for "
                    f"{wind_speed} m/s, Seed {seed}"
                )

                print("Stopping automation.")

                return

            # ------------------------------------------------
            # Check BTS file
            # ------------------------------------------------

            # TurbSim normally uses the input root name
            # for the output file.
            expected_bts = case_dir / (
                f"90m_{wind_speed:02d}mps_twr_seed{seed:02d}.bts" 
            )

            if expected_bts.exists():

                print(
                    f"SUCCESS: BTS generated:\n"
                    f"{expected_bts}"
                )

            else:

                print(
                    "WARNING: TurbSim finished, but expected "
                    f"BTS file was not found:\n{expected_bts}"
                )

                print("Stopping automation.")

                return

        # ====================================================
        # ALL SEEDS COMPLETED FOR THIS WIND SPEED
        # ====================================================

        print("\n" + "=" * 60)
        print(
            f"ALL SEEDS COMPLETED FOR {wind_speed} m/s"
        )
        print("=" * 60)


    # ========================================================
    # EVERYTHING COMPLETED
    # ========================================================

    print("\n" + "=" * 60)
    print("ALL TURBSIM SIMULATIONS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
