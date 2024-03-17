# Redactable-blockchains
## Overview
This project focuses on the implementation and evaluation of redactable blockchain systems. Redactable blockchains allow for the modification and removal of specific data from the blockchain while preserving the integrity and security of the overall system. The project comprises three repositories, BlockSim_Ateniese, BlockSim_Deuber, and BlockSim_Puddu. Each repository contains the implementation of a pioneer solution among the redaction approaches:  chameleon hash-based, voting-based and mutation redaction. By reproducing and comparing the results, as well as conducting new experiments, researchers can further study and analyze different redactable blockchain systems.

## How to Run the Project?

1. I would recommend [PyCharm](https://www.jetbrains.com/pycharm/) as the *IDE* to run the code.
2. Once you have cloned or downloaded the project, open it with PyCharm.

```
git clone
```

3. In an `import` statement of a Python file, click a package which is not yet imported. You can also run the following code to install the packages. [See details](https://www.jetbrains.com/help/pycharm/managing-dependencies.html#apply_dependencies)

```
pip install openpyxl
pip install xlsxwriter
pip install pandas
pip install numpy
```

4. Configure the Python interpreter in PyCharm. [See details](https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html)
5. Explore the modules and packages:
   - Adjust the input parameters in the InputConfig.py file.
   - Configure the results and statistical parameters in Statistics.py.
   - The Models module contains the implementation of the redactable blockchain.
6. Run the Main.py to start the simulation.
7. Try with different input parameters and see how the results change.

## Experimental Framework
The simulations in this project are conducted using the [BlockSim simulator](https://github.com/maher243/BlockSim). BlockSim is an open-source simulator specifically designed for blockchain systems. It provides intuitive simulation constructs and allows for customization to support multiple blockchain design and deployment scenarios. 

## References
- [Deuber, D., Magri, B., & Thyagarajan, S. A. K. (2019, May). Redactable blockchain in the permissionless setting. In 2019 IEEE Symposium on Security and Privacy (SP) (pp. 124-138). IEEE.](https://ieeexplore.ieee.org/abstract/document/8835372)
- [Ateniese, G., Magri, B., Venturi, D., & Andrade, E. (2017, April). Redactable blockchain–or–rewriting history in bitcoin and friends. In 2017 IEEE European symposium on security and privacy (EuroS&P) (pp. 111-126). IEEE.](https://ieeexplore.ieee.org/abstract/document/7961975/)
- [Puddu, I., Dmitrienko, A., & Capkun, S. (2017). $\mu $ chain: How to Forget without Hard Forks. Cryptology ePrint Archive.](https://eprint.iacr.org/2017/106)
