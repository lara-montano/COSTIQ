# COSTIQ: An Open-Source Tool for Equipment Cost Estimation in Chemical Process Design

**COSTIQ** (*Costos en Ingenieria Quimica*) is a free, open-source, web-based tool for estimating purchase and installation costs of chemical process equipment, based on the methodology of Turton et al. (2018).

## Features

- **36 equipment types** across 10 categories (heat exchangers, towers, trays, reactors, pressure vessels, tanks, pumps, compressors, fired heaters, turbines)
- **5 costing methods:** B1B2, vessel (ASME), FBM, FBM-FP, tray
- **Pressure factors** via ASME vessel correlation (Eq. A.2) and tabulated correlations (Eq. A.3)
- **Material-of-construction factors** for each equipment type
- **CEPCI temporal updating** with 24 annual values (2001--2024)
- **Multi-equipment plant inventory** with grassroots cost estimation
- **Sensitivity analysis:** size, pressure, and material comparison
- **USD/MXN currency conversion** with configurable exchange rate
- **CSV export** of the complete plant inventory

## Installation

```bash
# Clone the repository
git clone https://github.com/lara-montano/COSTIQ.git
cd COSTIQ

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Requirements

- Python 3.9 or higher
- Streamlit >= 1.30
- Plotly >= 5.18
- Pandas >= 2.0

## Usage

Once running, COSTIQ opens in your web browser. Use the sidebar to:

1. Select equipment category and type
2. Enter capacity, material, and operating pressure
3. View the complete cost breakdown with equations and intermediate values
4. Add equipment to the plant inventory
5. Explore sensitivity analyses and cost evolution over time

## Methodology

All correlations and factors are from:

> Turton, R., Shaeiwitz, J. A., Bhattacharyya, D., & Whiting, W. B. (2018). *Analysis, Synthesis, and Design of Chemical Processes* (5th ed.). Prentice Hall. Appendix A.

Base CEPCI = 397 (September 2001).

## Citation

If you use COSTIQ in your research, please cite:

```
Lara-Montano, O. D., Gomez-Castro, F. I., & Martinez-Guido, S. I. (2026).
COSTIQ: An Open-Source Tool for Equipment Cost Estimation in Chemical Process Design.
SoftwareX. [Submitted]
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Authors

- **Oscar Daniel Lara-Montano** -- Universidad Autonoma de Queretaro (oscar.lara@uaq.mx)
- **Fernando Israel Gomez-Castro** -- Universidad de Guanajuato
- **Sergio Ivan Martinez-Guido** -- Universidad de Guanajuato
