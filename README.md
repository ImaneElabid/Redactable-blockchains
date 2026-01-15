# Redactable Blockchains: A Systematic Survey of Techniques, Taxonomies, and Benchmarks  



## Overview

This repository provides the source code and experimental framework used to simulate, evaluate, and reproduce the experimental results presented in the associated survey paper on **redactable blockchain systems**.

Redactable blockchains enable the modification or removal of specific blockchain data (e.g., transactions or blocks) while preserving cryptographic consistency, auditability, and chain validity. Such functionality is essential for regulatory compliance (e.g., GDPR), error correction, and controlled data removal in decentralized systems.

The framework implements and evaluates three representative and widely cited redactable blockchain designs:

- **Ateniese et al.** — Chameleon hash–based redaction  
- **Deuber et al.** — Voting-based redaction in permissionless blockchains  
- **Puddu et al.** — Mutation-based redaction ($\mu$chain)

Each approach is implemented as an independent module to ensure isolation, comparability, and extensibility.



## Implemented Models

- `RBC_Ateniese/` — Chameleon hash–based redactable blockchain  
- `RBC_Deuber/` — Voting-based redactable blockchain  
- `RBC_Puddu/` — Mutation-based redactable blockchain ($\mu$chain)



## Key Features

- *Modular simulation architecture*: Easily switch between different redactable blockchain models.
- *Configurable experimental parameters*: Change network size, transaction rates, block intervals, rewards, redaction policies, and more via `InputsConfig.py`.
- *Cryptographic primitives (chameleon hashes)*: Implements cryptographic primitives for redactable blocks.
- *Secret sharing mechanisms*: Supports multi-party redaction with Shamir’s Secret Sharing and related cryptographic tools.
- *Decentralized voting protocols*: Implements permissionless, decentralized redaction based on block voting.
- *Mutation and selective data removal*: Simulates data mutation and selective transaction removal.
- *Experimental logging and statistics*: Results are logged and can be exported for further analysis; includes block statistics, mining rewards, redaction performance, and timing metrics.
- *Extensible design*: Based on [BlockSim simulator](https://github.com/maher243/BlockSim), making it easy to add new blockchain models or extend current ones.



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



## Installation

```bash
git clone <anon-repo-url>
cd Redactable-blockchains
pip install -r requirements.txt
```



## Reproducing Experimental Results

#### 1. Performance time (Fig. 7, Fig. 10, Fig. 11)

- Update the configuration file as in the figure:

  ```python
  model = 1 # Bitcoin model
  total_nodes = 1000
  enable_redaction = True
  redaction_attempts = 1
  redactions = 1
  simulation_duration = 5000
  simulation_runs = 10
  ```

- Execute the main script for the redaction models:

  - `python RBC_Ateniese/Main.py`
  - `python RBC_Deuber/Main.py`
  - `python RBC_Puddu/Main.py`

- For baseline use configuration file with `enable_redaction = False`

- Simulation results, including performance metrics and statistics, will be printed to the console and saved to the `Results/` directory in Excel and CSV formats.

#### 2. Impact of validators count on redaction time (Fig.9)

- Update the configuration file as in the figure:

  `````
  miner_fraction = 0.1 # 0.1, 0.3, 0.5, ...
  `````

- Execute the main script for the voting-based model:
  - `python RBC_Ateniese/Main.py`
- Collect the Execution time and reduction time (s)

#### 3. Storage evolution of $\mu$chain (Fig. 12)

- Update the configuration file as in the figure:

  `````
  simulation_duration = 50000
  `````

- Execute the main script for the voting-based model:
  - `python RBC_Puddu/Main.py`
- Collect the size of the chain (mb)

#### 4. Energy Consumption estimation (Fig. 13)

To measure the energy consumption of the each of the models, run the following command:

`./run.sh -c 0 -p avg -r 10 -d 2 -e "python RBC_Deuber/Main.py"`

`./run.sh -c 0 -p avg -r 10 -d 2 -e "python RBC_Deuber/Main.py"`

`./run.sh -c 0 -p avg -r 10 -d 2 -e "python RBC_Puddu/Main.py"`

For more detail about the energy script run the command: `./run.sh --help`



## References

- [Deuber, D., Magri, B., & Thyagarajan, S. A. K. (2019, May). Redactable blockchain in the permissionless setting. In 2019 IEEE Symposium on Security and Privacy (SP) (pp. 124-138). IEEE.](https://ieeexplore.ieee.org/abstract/document/8835372)
- [Ateniese, G., Magri, B., Venturi, D., & Andrade, E. (2017, April). Redactable blockchain–or–rewriting history in bitcoin and friends. In 2017 IEEE European symposium on security and privacy (EuroS&P) (pp. 111-126). IEEE.](https://ieeexplore.ieee.org/abstract/document/7961975/)
- [Puddu, I., Dmitrienko, A., & Capkun, S. (2017). $\mu$ chain: How to Forget without Hard Forks. Cryptology ePrint Archive.](https://eprint.iacr.org/2017/106)



## License

This simulator is intended for academic research and educational use. Refer to individual source files for license details.
