"""
Datos de costeo de equipos basados en Turton et al. (2018), Apéndice A.
Analysis, Synthesis, and Design of Chemical Processes, 5th Edition.
Base CEPCI = 397 (Septiembre 2001).
"""

# ============================================================
# CEPCI históricos (2001-2024)
# ============================================================
CEPCI = {
    2001: 397.0,
    2002: 395.6,
    2003: 402.0,
    2004: 444.2,
    2005: 468.2,
    2006: 499.6,
    2007: 525.4,
    2008: 575.4,
    2009: 521.9,
    2010: 550.8,
    2011: 585.7,
    2012: 584.6,
    2013: 567.3,
    2014: 576.1,
    2015: 556.8,
    2016: 541.7,
    2017: 567.5,
    2018: 603.1,
    2019: 607.5,
    2020: 596.2,
    2021: 708.0,
    2022: 816.0,
    2023: 797.9,
    2024: 800.8,
}

CEPCI_BASE = 397.0  # Septiembre 2001

# ============================================================
# Categorías y equipos: K1, K2, K3, unidades, rango [min, max]
# Ecuación: log10(Cp°) = K1 + K2*log10(A) + K3*(log10(A))^2
# ============================================================
EQUIPMENT = {
    "Intercambiadores de calor": {
        "Floating head": {
            "K1": 4.8306, "K2": -0.8509, "K3": 0.3187,
            "units": "Área (m²)", "min": 10, "max": 1000,
        },
        "Fixed tube sheet": {
            "K1": 4.3247, "K2": -0.3030, "K3": 0.1634,
            "units": "Área (m²)", "min": 10, "max": 1000,
        },
        "U-tube": {
            "K1": 4.1884, "K2": -0.2503, "K3": 0.1974,
            "units": "Área (m²)", "min": 10, "max": 1000,
        },
        "Kettle reboiler": {
            "K1": 4.4646, "K2": -0.5277, "K3": 0.3955,
            "units": "Área (m²)", "min": 10, "max": 100,
        },
        "Double pipe": {
            "K1": 3.3444, "K2": 0.2745, "K3": -0.0472,
            "units": "Área (m²)", "min": 1, "max": 10,
        },
        "Multiple pipe": {
            "K1": 2.7652, "K2": 0.7282, "K3": 0.0783,
            "units": "Área (m²)", "min": 10, "max": 100,
        },
        "Bayonet": {
            "K1": 4.2768, "K2": -0.0495, "K3": 0.1431,
            "units": "Área (m²)", "min": 10, "max": 1000,
        },
        "Air cooler": {
            "K1": 4.0336, "K2": 0.2341, "K3": 0.0497,
            "units": "Área (m²)", "min": 10, "max": 10000,
        },
        "Flat plate": {
            "K1": 4.6656, "K2": -0.1557, "K3": 0.1547,
            "units": "Área (m²)", "min": 10, "max": 1000,
        },
        "Spiral plate": {
            "K1": 4.6561, "K2": -0.2947, "K3": 0.2207,
            "units": "Área (m²)", "min": 1, "max": 100,
        },
        "Scraped wall": {
            "K1": 3.7803, "K2": 0.8569, "K3": 0.0349,
            "units": "Área (m²)", "min": 2, "max": 20,
        },
        "Spiral tube": {
            "K1": 3.9912, "K2": 0.0668, "K3": 0.2430,
            "units": "Área (m²)", "min": 1, "max": 100,
        },
        "Teflon tube": {
            "K1": 3.8062, "K2": 0.8924, "K3": -0.1671,
            "units": "Área (m²)", "min": 1, "max": 10,
        },
    },
    "Torres": {
        "Torre empacada/platos": {
            "K1": 3.4974, "K2": 0.4485, "K3": 0.1074,
            "units": "Volumen (m³)", "min": 0.3, "max": 520,
        },
    },
    "Platos (trays)": {
        "Sieve": {
            "K1": 2.9949, "K2": 0.4465, "K3": 0.3961,
            "units": "Área (m²)", "min": 0.07, "max": 12.3,
        },
        "Valve": {
            "K1": 3.3322, "K2": 0.4838, "K3": 0.3434,
            "units": "Área (m²)", "min": 0.7, "max": 10.5,
        },
        "Demisters": {
            "K1": 3.2353, "K2": 0.4838, "K3": 0.3434,
            "units": "Área (m²)", "min": 0.7, "max": 10.5,
        },
    },
    "Reactores": {
        "Autoclave": {
            "K1": 4.5587, "K2": 0.2986, "K3": 0.0020,
            "units": "Volumen (m³)", "min": 1, "max": 15,
        },
        "Fermenter": {
            "K1": 4.1052, "K2": 0.5320, "K3": -0.0005,
            "units": "Volumen (m³)", "min": 0.1, "max": 35,
        },
        "Jacketed agitated": {
            "K1": 4.1052, "K2": 0.5320, "K3": -0.0005,
            "units": "Volumen (m³)", "min": 0.1, "max": 35,
        },
        "Jacketed nonagitated": {
            "K1": 3.3496, "K2": 0.7235, "K3": 0.0025,
            "units": "Volumen (m³)", "min": 5, "max": 45,
        },
    },
    "Recipientes a presión": {
        "Horizontal": {
            "K1": 3.5565, "K2": 0.3776, "K3": 0.0905,
            "units": "Volumen (m³)", "min": 0.1, "max": 628,
        },
        "Vertical": {
            "K1": 3.4974, "K2": 0.4485, "K3": 0.1074,
            "units": "Volumen (m³)", "min": 0.3, "max": 520,
        },
    },
    "Tanques": {
        "API fixed roof": {
            "K1": 4.8509, "K2": -0.3973, "K3": 0.1445,
            "units": "Volumen (m³)", "min": 90, "max": 30000,
        },
        "API floating roof": {
            "K1": 5.9567, "K2": -0.7585, "K3": 0.1749,
            "units": "Volumen (m³)", "min": 1000, "max": 40000,
        },
    },
    "Bombas": {
        "Centrifugal": {
            "K1": 3.3892, "K2": 0.0536, "K3": 0.1538,
            "units": "Potencia (kW)", "min": 1, "max": 300,
        },
        "Positive displacement": {
            "K1": 3.4771, "K2": 0.1350, "K3": 0.1438,
            "units": "Potencia (kW)", "min": 1, "max": 100,
        },
        "Reciprocating": {
            "K1": 3.8696, "K2": 0.3161, "K3": 0.1220,
            "units": "Potencia (kW)", "min": 0.1, "max": 200,
        },
    },
    "Compresores": {
        "Centrifugal/axial/reciprocating": {
            "K1": 2.2897, "K2": 1.3604, "K3": -0.1027,
            "units": "Potencia (kW)", "min": 450, "max": 3000,
        },
        "Rotary": {
            "K1": 5.0355, "K2": -1.8002, "K3": 0.8253,
            "units": "Potencia (kW)", "min": 18, "max": 950,
        },
    },
    "Hornos": {
        "Reformer furnace": {
            "K1": 3.0680, "K2": 0.6597, "K3": 0.0194,
            "units": "Duty (kW)", "min": 3000, "max": 100000,
        },
        "Pyrolysis furnace": {
            "K1": 2.3859, "K2": 0.9721, "K3": -0.0206,
            "units": "Duty (kW)", "min": 3000, "max": 100000,
        },
        "Nonreactive fired heater": {
            "K1": 7.3488, "K2": -1.1666, "K3": 0.2028,
            "units": "Duty (kW)", "min": 1000, "max": 100000,
        },
    },
    "Turbinas": {
        "Axial gas turbine": {
            "K1": 2.7051, "K2": 1.4398, "K3": -0.1776,
            "units": "Potencia (kW)", "min": 100, "max": 4000,
        },
        "Radial gas/liquid expander": {
            "K1": 2.2476, "K2": 1.4965, "K3": -0.1618,
            "units": "Potencia (kW)", "min": 100, "max": 1500,
        },
        "Steam turbine (drive)": {
            "K1": 2.6259, "K2": 1.4398, "K3": -0.1776,
            "units": "Potencia (kW)", "min": 70, "max": 7500,
        },
    },
}

# ============================================================
# B1, B2 para ecuación de módulo desnudo (Eq. A.4)
# CBM = Cp° * (B1 + B2 * FM * FP)
# ============================================================
B1B2 = {
    "Intercambiadores de calor": {
        "Double pipe": {"B1": 1.74, "B2": 1.55},
        "Multiple pipe": {"B1": 1.74, "B2": 1.55},
        "Scraped wall": {"B1": 1.74, "B2": 1.55},
        "Spiral tube": {"B1": 1.74, "B2": 1.55},
        "Fixed tube sheet": {"B1": 1.63, "B2": 1.66},
        "Floating head": {"B1": 1.63, "B2": 1.66},
        "U-tube": {"B1": 1.63, "B2": 1.66},
        "Bayonet": {"B1": 1.63, "B2": 1.66},
        "Kettle reboiler": {"B1": 1.63, "B2": 1.66},
        "Teflon tube": {"B1": 1.63, "B2": 1.66},
        "Air cooler": {"B1": 0.96, "B2": 1.21},
        "Flat plate": {"B1": 0.96, "B2": 1.21},
        "Spiral plate": {"B1": 0.96, "B2": 1.21},
    },
    "Recipientes a presión": {
        "Horizontal": {"B1": 1.49, "B2": 1.52},
        "Vertical": {"B1": 2.25, "B2": 1.82},
    },
    "Torres": {
        "Torre empacada/platos": {"B1": 2.25, "B2": 1.82},
    },
    "Bombas": {
        "Centrifugal": {"B1": 1.89, "B2": 1.35},
        "Positive displacement": {"B1": 1.89, "B2": 1.35},
        "Reciprocating": {"B1": 1.89, "B2": 1.35},
    },
}

# ============================================================
# Factores de material FM (de Figura A.18)
# Para equipos con B1, B2
# ============================================================
FM_HEAT_EXCHANGERS_SHELL_TUBE = {
    # Para S&T: floating head, fixed tube, U-tube, bayonet, kettle, double pipe, multiple pipe, scraped wall, spiral tube
    "CS/CS": 1.00,
    "CS/Cu": 1.35,
    "Cu/Cu": 1.69,
    "CS/SS": 1.81,
    "SS/SS": 2.73,
    "CS/Ni alloy": 2.68,
    "Ni alloy/Ni alloy": 3.73,
    "CS/Ti": 3.17,
    "Ti/Ti": 4.63,
}

FM_AIR_COOLER = {
    "CS": 1.00,
    "Al": 1.00,
    "SS": 2.17,
}

FM_PLATE_HX = {
    # Flat plate y spiral plate
    "CS": 1.00,
    "Cu": 1.35,
    "SS": 2.45,
    "Ni alloy": 2.68,
    "Ti": 4.63,
}

FM_VESSELS = {
    "CS": 1.00,
    "SS clad": 1.75,
    "SS": 3.12,
    "Ni alloy clad": 3.63,
    "Ni alloy": 6.44,
    "Ti clad": 4.71,
    "Ti": 7.89,
}

FM_PUMPS_RECIP = {
    "Cast iron": 1.00,
    "CS": 1.40,
    "Cu alloy": 1.50,
    "SS": 2.20,
    "Ni alloy": 3.50,
    "Ti": 9.60,
}

FM_PUMPS_PD = {
    "Cast iron": 1.00,
    "CS": 1.40,
    "Cu alloy": 1.50,
    "SS": 2.20,
    "Ni alloy": 3.50,
    "Ti": 9.60,
}

FM_PUMPS_CENTRIFUGAL = {
    "Cast iron": 1.00,
    "CS": 1.35,
    "SS": 2.00,
    "Ni alloy": 3.50,
}

# Mapeo de equipo a su tabla FM
FM_MAP = {
    "Intercambiadores de calor": {
        "Floating head": FM_HEAT_EXCHANGERS_SHELL_TUBE,
        "Fixed tube sheet": FM_HEAT_EXCHANGERS_SHELL_TUBE,
        "U-tube": FM_HEAT_EXCHANGERS_SHELL_TUBE,
        "Kettle reboiler": FM_HEAT_EXCHANGERS_SHELL_TUBE,
        "Double pipe": FM_HEAT_EXCHANGERS_SHELL_TUBE,
        "Multiple pipe": FM_HEAT_EXCHANGERS_SHELL_TUBE,
        "Bayonet": FM_HEAT_EXCHANGERS_SHELL_TUBE,
        "Scraped wall": FM_HEAT_EXCHANGERS_SHELL_TUBE,
        "Spiral tube": FM_HEAT_EXCHANGERS_SHELL_TUBE,
        "Air cooler": FM_AIR_COOLER,
        "Flat plate": FM_PLATE_HX,
        "Spiral plate": FM_PLATE_HX,
        "Teflon tube": {"Teflon": 1.00},
    },
    "Recipientes a presión": {
        "Horizontal": FM_VESSELS,
        "Vertical": FM_VESSELS,
    },
    "Torres": {
        "Torre empacada/platos": FM_VESSELS,
    },
    "Bombas": {
        "Centrifugal": FM_PUMPS_CENTRIFUGAL,
        "Positive displacement": FM_PUMPS_PD,
        "Reciprocating": FM_PUMPS_RECIP,
    },
}

# ============================================================
# FBM fijos (de Figura A.19 y Tabla A.7)
# Para equipos sin B1, B2 (CBM = Cp° * FBM)
# ============================================================
FBM_FIXED = {
    "Compresores": {
        "Centrifugal/axial/reciprocating": {
            "CS": 2.15,
            "SS": 5.80,
            "Ni alloy": 11.50,
        },
        "Rotary": {
            "CS": 2.15,
            "SS": 5.80,
            "Ni alloy": 11.50,
        },
    },
    "Hornos": {
        "Reformer furnace": {
            "CS": 2.19,
            "Alloy steel": 2.47,
            "SS": 2.75,
        },
        "Pyrolysis furnace": {
            "CS": 2.19,
            "Alloy steel": 2.47,
            "SS": 2.75,
        },
        "Nonreactive fired heater": {
            "CS": 2.19,
            "Alloy steel": 2.47,
            "SS": 2.75,
        },
    },
    "Turbinas": {
        "Axial gas turbine": {
            "CS": 3.40,
            "SS": 6.10,
            "Ni alloy": 11.70,
        },
        "Radial gas/liquid expander": {
            "CS": 3.40,
            "SS": 6.10,
            "Ni alloy": 11.70,
        },
        "Steam turbine (drive)": {
            "CS": 3.40,
            "SS": 6.10,
            "Ni alloy": 11.70,
        },
    },
    "Reactores": {
        "Autoclave": {"Default": 4.00},
        "Fermenter": {"Default": 4.00},
        "Jacketed agitated": {"Default": 4.00},
        "Jacketed nonagitated": {"Default": 4.00},
    },
    "Tanques": {
        "API fixed roof": {"Default": 1.00},
        "API floating roof": {"Default": 1.00},
    },
    "Platos (trays)": {
        "Sieve": {
            "CS": 1.00,
            "SS": 1.83,
            "Ni alloy": 3.20,
        },
        "Valve": {
            "CS": 1.00,
            "SS": 1.83,
            "Ni alloy": 3.20,
        },
        "Demisters": {
            "SS": 1.00,
            "Fluorocarbon": 1.85,
            "Ni alloy": 2.40,
        },
    },
}

# ============================================================
# Factores de presión: C1, C2, C3
# Ecuación: log10(FP) = C1 + C2*log10(P) + C3*(log10(P))^2
# P en barg. Si FP < 1 → FP = 1
# ============================================================
PRESSURE_FACTORS = {
    "Intercambiadores de calor": {
        "Floating head": [
            {"range": (-0.5, 5), "C1": 0, "C2": 0, "C3": 0, "side": "shell"},
            {"range": (5, 140), "C1": 0.03881, "C2": -0.11272, "C3": 0.08183, "side": "shell"},
            {"range": (-0.5, 5), "C1": 0, "C2": 0, "C3": 0, "side": "tube"},
            {"range": (5, 140), "C1": -0.00164, "C2": -0.00627, "C3": 0.01230, "side": "tube"},
        ],
        "Fixed tube sheet": [
            {"range": (-0.5, 5), "C1": 0, "C2": 0, "C3": 0, "side": "shell"},
            {"range": (5, 140), "C1": 0.03881, "C2": -0.11272, "C3": 0.08183, "side": "shell"},
            {"range": (-0.5, 5), "C1": 0, "C2": 0, "C3": 0, "side": "tube"},
            {"range": (5, 140), "C1": -0.00164, "C2": -0.00627, "C3": 0.01230, "side": "tube"},
        ],
        "U-tube": [
            {"range": (-0.5, 5), "C1": 0, "C2": 0, "C3": 0, "side": "shell"},
            {"range": (5, 140), "C1": 0.03881, "C2": -0.11272, "C3": 0.08183, "side": "shell"},
            {"range": (-0.5, 5), "C1": 0, "C2": 0, "C3": 0, "side": "tube"},
            {"range": (5, 140), "C1": -0.00164, "C2": -0.00627, "C3": 0.01230, "side": "tube"},
        ],
        "Bayonet": [
            {"range": (-0.5, 5), "C1": 0, "C2": 0, "C3": 0, "side": "shell"},
            {"range": (5, 140), "C1": 0.03881, "C2": -0.11272, "C3": 0.08183, "side": "shell"},
            {"range": (-0.5, 5), "C1": 0, "C2": 0, "C3": 0, "side": "tube"},
            {"range": (5, 140), "C1": -0.00164, "C2": -0.00627, "C3": 0.01230, "side": "tube"},
        ],
        "Kettle reboiler": [
            {"range": (-0.5, 5), "C1": 0, "C2": 0, "C3": 0, "side": "shell"},
            {"range": (5, 140), "C1": 0.03881, "C2": -0.11272, "C3": 0.08183, "side": "shell"},
            {"range": (-0.5, 5), "C1": 0, "C2": 0, "C3": 0, "side": "tube"},
            {"range": (5, 140), "C1": -0.00164, "C2": -0.00627, "C3": 0.01230, "side": "tube"},
        ],
        "Double pipe": [
            {"range": (-0.5, 40), "C1": 0, "C2": 0, "C3": 0},
            {"range": (40, 100), "C1": 0.6072, "C2": -0.9120, "C3": 0.3327},
            {"range": (100, 300), "C1": 13.1467, "C2": -12.6574, "C3": 3.0705},
        ],
        "Multiple pipe": [
            {"range": (-0.5, 40), "C1": 0, "C2": 0, "C3": 0},
            {"range": (40, 100), "C1": 0.6072, "C2": -0.9120, "C3": 0.3327},
            {"range": (100, 300), "C1": 13.1467, "C2": -12.6574, "C3": 3.0705},
        ],
        "Scraped wall": [
            {"range": (-0.5, 40), "C1": 0, "C2": 0, "C3": 0},
            {"range": (40, 100), "C1": 0.6072, "C2": -0.9120, "C3": 0.3327},
            {"range": (100, 300), "C1": 13.1467, "C2": -12.6574, "C3": 3.0705},
        ],
        "Spiral tube": [
            {"range": (-0.5, 150), "C1": 0, "C2": 0, "C3": 0, "side": "shell"},
            {"range": (150, 400), "C1": -0.4045, "C2": 0.1859, "C3": 0, "side": "shell"},
            {"range": (-0.5, 150), "C1": 0, "C2": 0, "C3": 0, "side": "tube"},
            {"range": (150, 400), "C1": -0.2115, "C2": 0.09717, "C3": 0, "side": "tube"},
        ],
        "Teflon tube": [
            {"range": (-0.5, 15), "C1": 0, "C2": 0, "C3": 0},
        ],
        "Air cooler": [
            {"range": (-0.5, 10), "C1": 0, "C2": 0, "C3": 0},
            {"range": (10, 100), "C1": -0.125, "C2": 0.15361, "C3": -0.02861},
        ],
        "Flat plate": [
            {"range": (-0.5, 19), "C1": 0, "C2": 0, "C3": 0},
        ],
        "Spiral plate": [
            {"range": (-0.5, 19), "C1": 0, "C2": 0, "C3": 0},
        ],
    },
    "Bombas": {
        "Centrifugal": [
            {"range": (-0.5, 10), "C1": 0, "C2": 0, "C3": 0},
            {"range": (10, 100), "C1": -0.3935, "C2": 0.3957, "C3": -0.00226},
        ],
        "Positive displacement": [
            {"range": (-0.5, 10), "C1": 0, "C2": 0, "C3": 0},
            {"range": (10, 100), "C1": -0.245382, "C2": 0.259016, "C3": -0.01363},
        ],
        "Reciprocating": [
            {"range": (-0.5, 10), "C1": 0, "C2": 0, "C3": 0},
            {"range": (10, 100), "C1": -0.245382, "C2": 0.259016, "C3": -0.01363},
        ],
    },
    "Hornos": {
        "Reformer furnace": [
            {"range": (-0.5, 10), "C1": 0, "C2": 0, "C3": 0},
            {"range": (10, 200), "C1": 0.1405, "C2": -0.2698, "C3": 0.1293},
        ],
        "Pyrolysis furnace": [
            {"range": (-0.5, 10), "C1": 0, "C2": 0, "C3": 0},
            {"range": (10, 200), "C1": 0.1017, "C2": -0.1957, "C3": 0.09403},
        ],
        "Nonreactive fired heater": [
            {"range": (-0.5, 10), "C1": 0, "C2": 0, "C3": 0},
            {"range": (10, 200), "C1": 0.1347, "C2": -0.2368, "C3": 0.1021},
        ],
    },
}

# ============================================================
# Método de costo de módulo para cada categoría
# "B1B2"   → CBM = Cp° * (B1 + B2*FM*FP)
# "FBM"    → CBM = Cp° * FBM  (o * FP si aplica)
# "FBM_FP" → CBM = Cp° * FBM * FP
# "vessel" → usa Eq. A.2 para FP
# "tray"   → CBM = Cp° * N * FBM * Fq
# ============================================================
COST_METHOD = {
    "Intercambiadores de calor": "B1B2",
    "Torres": "vessel",          # usa Eq. A.2 para FP + B1, B2
    "Platos (trays)": "tray",
    "Reactores": "FBM",
    "Recipientes a presión": "vessel",
    "Tanques": "FBM",
    "Bombas": "B1B2",
    "Compresores": "FBM",
    "Hornos": "FBM_FP",
    "Turbinas": "FBM",
}
