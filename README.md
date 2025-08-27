# Redactable-blockchains
## Overview
This project provides an experimental framework for simulating and evaluating **redactable blockchain systems**. 
Redactable blockchains introduce the ability to modify or remove specific data from the blockchain such as transactions or blocks, while preserving the cryptographic integrity and auditability of the chain. This feature is crucial for compliance with privacy regulations (e.g., GDPR), error correction, and selective data removal in decentralized systems.
The framework implements three pioneering redactable blockchain approaches:

- **Ateniese et al. (Chameleon Hash-based Redaction)**
- **Deuber et al. (Voting-based Redaction)**
- **Puddu et al. ($\mu$chain Mutation-based Redaction)**

Each approach is implemented in its dedicated module under the directories `RBC_Ateniese`, `RBC_Deuber`, and `RBC_Puddu`.

## Features

- **Modular Simulation**: Easily switch between different redactable blockchain models.
- **Configurable Parameters**: Change network size, transaction rates, block intervals, rewards, redaction policies, and more via `InputsConfig.py`.
- **Chameleon Hash Functions**: Implements cryptographic primitives for redactable blocks.
- **Secret Sharing Schemes**: Supports multi-party redaction with Shamir’s Secret Sharing and related cryptographic tools.
- **Voting Mechanisms**: Implements permissionless, decentralized redaction based on block voting.
- **Mutation & Data Privacy**: Simulates data mutation and selective transaction removal.
- **Statistical Analysis**: Results are logged and can be exported for further analysis; includes block statistics, mining rewards, redaction performance, and timing metrics.
- **Extensible Design**: Based on [BlockSim simulator](https://github.com/maher243/BlockSim), making it easy to add new blockchain models or extend current ones.

## Directory Structure

```
Redactable-blockchains/
│
├── RBC_Ateniese/   # Ateniese et al. chameleon hash-based redaction
├── RBC_Deuber/     # Deuber et al. voting-based redaction
├── RBC_Puddu/      # Puddu et al. mutation-based redaction
├── Results/        # Output data and result files (created after simulation)
├── README.md       # This file
└── ...             # Supporting scripts and configs
```

## How to Run the Project

### 1. Install Requirements

Clone the repository and install dependencies:

```bash
git clone <repo-url>
cd Redactable-blockchains

pip install -r requirements.txt
# or, manually:
pip install openpyxl xlsxwriter pandas numpy
```
### 2. Configure Simulation

- Use [PyCharm](https://www.jetbrains.com/pycharm/) or your preferred Python IDE.
- Edit the `InputsConfig.py` file in your desired model directory (`RBC_Ateniese`, `RBC_Deuber`, `RBC_Puddu`):
  - Set simulation parameters, network size, model type, redaction options, and more.
- Explore cryptographic primitives in the `CH/` (Chameleon Hash) and `Models/` modules.

### 3. Run Simulation

- Execute the main script for the desired model:
  - `python RBC_Ateniese/Main.py`
  - `python RBC_Deuber/Main.py`
  - `python RBC_Puddu/Main.py`
- Simulation results, including performance metrics and statistics, will be printed to the console and saved to the `Results/` directory in Excel and CSV formats.

## References
- [Deuber, D., Magri, B., & Thyagarajan, S. A. K. (2019, May). Redactable blockchain in the permissionless setting. In 2019 IEEE Symposium on Security and Privacy (SP) (pp. 124-138). IEEE.](https://ieeexplore.ieee.org/abstract/document/8835372)
- [Ateniese, G., Magri, B., Venturi, D., & Andrade, E. (2017, April). Redactable blockchain–or–rewriting history in bitcoin and friends. In 2017 IEEE European symposium on security and privacy (EuroS&P) (pp. 111-126). IEEE.](https://ieeexplore.ieee.org/abstract/document/7961975/)
- [Puddu, I., Dmitrienko, A., & Capkun, S. (2017). $\mu $ chain: How to Forget without Hard Forks. Cryptology ePrint Archive.](https://eprint.iacr.org/2017/106)

## License

This simulator is intended for academic research and educational use. Refer to individual source files for license details.