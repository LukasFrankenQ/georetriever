from attrdict import AttrDict
import numpy as np

# from Ericsson (1985)
thermal_conductivity_database = AttrDict(
    {
        "granite": (3.55, 0.3316),
        "pegmatite": (3.55, 0.3316),
        "syenite": (2.75, 0.2806),
        "diorite": (2.75, 0.2806),
        "gabbro": (2.75, 0.2806),
        "diabase": (2.8, 0.2551),
        "sandstone": (4.0, 0.5102),
        "clayshale": (2.6, 0.4592),
        "limestone": (2.35, 0.3316),
        "quartzite": (6.0, 0.5102),
        "gneiss": (3.6, 0.5612),
        "leptite": (3.7, 0.5102),
        "marble": (3.0, 0.2551),
        "siltstone": (2.5, 0.2551),  # this is tentative
    }
)

# suboptimal method for generic tc
thermal_conductivity_database["generic"] = tuple(
    (
        np.around(
            np.vstack(list(thermal_conductivity_database.values())).mean(axis=0),
            decimals=4,
        )
    )
)
