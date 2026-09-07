# Automated IEC 61400-1 DLC 1.1 Load Assessment using OpenFAST & TurbSim

Automated **TurbSim–OpenFAST–Python workflow** for DLC 1.1 simulations of the **NREL 5-MW reference wind turbine** under normal turbulent wind conditions.

## Overview

This project automates the workflow from turbulent wind-field generation to aeroelastic simulation and load post-processing.

**Workflow:**

TurbSim → Wind Fields → OpenFAST → Load Extraction → Statistical Analysis → Load Envelopes

## Simulation Setup

- **Reference turbine:** NREL 5-MW
- **Design Load Case:** DLC 1.1
- **Wind model:** Normal Turbulence Model (NTM)
- **Wind speeds:** 5, 7, 9, 11, 13, 15, 19, 23 m/s
- **Simulation cases:** 39
- **Simulation duration:** 10 minutes per case
- **Tools:** TurbSim, OpenFAST, Python

### DLC 1.1 Case Matrix

IEC 61400-1 specifies **6 simulations per wind speed below \(V_r - 2\)** and **15 simulations per wind speed from \(V_r - 2\) to cut-out**.

For this project, a **reduced turbulence-seed set** was used to limit computational time, storage requirements, and repository size while retaining the overall DLC 1.1 simulation workflow.

| Wind Speed [m/s] | Seeds Used | Cases |
|---:|:---:|---:|
| 5  | 1–3 | 3 |
| 7  | 1–3 | 3 |
| 9  | 1–3 | 3 |
| 11 | 1–6 | 6 |
| 13 | 1–6 | 6 |
| 15 | 1–6 | 6 |
| 19 | 1–6 | 6 |
| 23 | 1–6 | 6 |
| **Total** | | **39** |

> **Note:** The reduced seed set is used for engineering/research demonstration and does not represent the full IEC 61400-1 simulation population.

## Automation

Python scripts are used to automate:

- TurbSim input generation
- Wind-speed and turbulence-seed case setup
- OpenFAST case configuration
- Batch aeroelastic simulations
- File and case management
- Simulation error handling

## Post-Processing

The Jupyter notebook contains the complete analysis workflow:

- Case-wise maximum, minimum, mean, standard deviation and RMS
- Extreme-load matrix
- Maximum loads across turbulence seeds
- Load envelopes across wind speeds
- Statistical extreme-load estimation
- Comparison of simulated and statistical extremes

### Statistical Extreme-Load Treatment

A simplified statistical treatment is used:

**Statistical extreme = Mean + 2 × Standard Deviation (σ)**

> This statistical treatment is intended for engineering/research demonstration and is **not an IEC-certified extreme-load assessment**.

## Repository Structure

```text
openfast-dlc1.1-load-assessment/
│
├── README.md
│
├── scripts/
│   ├── generate_turbsim_cases.py
│   ├── run_openfast_cases.py
│   └── helpers.py
│
├── templates/
│   ├── OpenFAST/
│   └── TurbSim/
│
├── notebooks/
│   └── DLC1_1_analysis.ipynb
│
├── samples/
│   └── WS11_Seed01.outb
│
└── .gitignore
