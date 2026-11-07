"""COSTIQ: estimación de costos de equipo de proceso (Turton et al., 2018).

Uso mínimo::

    from costiq import cost, plant_summary

    e101 = cost("hx_floating_head", 170, material="CS/CS", pressure=5,
                pressure_option="both")
    print(e101.CBM, e101.at(800.8))
"""

from .data import CATEGORIES, CEPCI, CEPCI_BASE, EQUIPMENT, EQUIPMENT_LIST
from .engine import (
    QUOTE_KEY, CostError, CostResult, Notice, PlantSummary, cost, plant_summary,
    pressure_factor, purchased_cost, quoted_cost, superheat_factor, tray_area,
    tray_quantity_factor, vessel_pressure_factor, vessel_volume,
)

__version__ = "2.1.0"

__all__ = [
    "CATEGORIES", "CEPCI", "CEPCI_BASE", "EQUIPMENT", "EQUIPMENT_LIST",
    "QUOTE_KEY", "CostError", "CostResult", "Notice", "PlantSummary", "cost",
    "plant_summary", "pressure_factor", "purchased_cost", "quoted_cost",
    "superheat_factor", "tray_area", "tray_quantity_factor",
    "vessel_pressure_factor", "vessel_volume",
    "__version__",
]
