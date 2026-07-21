"""The car-purchase example from PROMETHEE.pdf, used as an in-app demo and as
the reference dataset in tests/test_core.py."""
from __future__ import annotations

import pandas as pd

from promethee_core.model import Alternative, Criterion, Direction, PreferenceFunctionType, ProblemData

ALTERNATIVE_NAMES = ["A1", "A2", "A3", "A4", "A5", "A6"]

ALTERNATIVE_DESCRIPTIONS = {
    "A1": "Tourism B",
    "A2": "Luxury 1",
    "A3": "Tourism A",
    "A4": "Luxury 2",
    "A5": "Economic",
    "A6": "Sport",
}

RAW_DATA = {
    "Price": [25500, 38000, 26000, 35000, 15000, 29000],
    "Power": [85, 90, 75, 85, 50, 110],
    "Consumption": [7.0, 8.5, 8.0, 9.0, 7.5, 9.0],
    "Habitability": [4, 4, 3, 5, 2, 1],
    "Comfort": [3, 5, 3, 4, 1, 2],
}


def car_purchase_example() -> ProblemData:
    alternatives = [
        Alternative(name=name, description=ALTERNATIVE_DESCRIPTIONS[name]) for name in ALTERNATIVE_NAMES
    ]
    criteria = [
        Criterion(name="Price", direction=Direction.MIN, weight=1.0,
                  preference_function=PreferenceFunctionType.V_SHAPE, p=15000),
        Criterion(name="Power", direction=Direction.MAX, weight=1.0,
                  preference_function=PreferenceFunctionType.LINEAR, q=5, p=30),
        Criterion(name="Consumption", direction=Direction.MIN, weight=1.0,
                  preference_function=PreferenceFunctionType.V_SHAPE, p=2),
        Criterion(name="Habitability", direction=Direction.MAX, weight=1.0,
                  preference_function=PreferenceFunctionType.LEVEL, q=1, p=2.5),
        Criterion(name="Comfort", direction=Direction.MAX, weight=1.0,
                  preference_function=PreferenceFunctionType.LEVEL, q=0.5, p=2.5),
    ]
    values = pd.DataFrame(RAW_DATA, index=ALTERNATIVE_NAMES)
    return ProblemData(
        name="Car purchase (Visual PROMETHEE sample)",
        description="Choosing a car among 6 alternatives on price, power, consumption, "
        "habitability and comfort. From the PROMETHEE reference material.",
        alternatives=alternatives,
        criteria=criteria,
        values=values,
    )
