import numpy as np
from itertools import product
import re
import pandas as pd
import xarray as xr
from copy import deepcopy
from PIL import ImageColor

nonelist = [None for _ in range(8)]


def rgb2hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def get_minor_major(line):
    line = line.lower()
    major = line.split("}")[0].split("{")[-1]
    minors = line.split("minor{")[-1].replace("}", "").split(",")
    return {"major": major, "minors": minors}


def get_percentages(line):
    liths = line.split("]")[:-1]
    shares = [part.split("[")[-1] for part in liths]
    shares = ["9" in part for part in shares]
    liths = [lith.split(" [")[0] for lith in liths]
    liths = [re.sub(r"[^a-zA-Z0-9 ]", "", lith).lower() for lith in liths]
    for i, lith in enumerate(liths):
        lith = re.sub(r"[^a-zA-Z0-9 ]", "", lith).lower()
        if lith[0] == " ":
            lith = lith[1:]
            liths[i] = lith

    result = dict()
    result["minors"] = [lith for i, lith in enumerate(liths) if not shares[i]]
    result["major"] = liths[shares.index(True)]
    return result


class Lith:

    index = [
        "major",
        "minor1",
        "minor2",
        "minor3",
        "others1",
        "others2",
        "others3",
        "colors",
    ]

    def __init__(self, lith=None, /, comp=None):

        if comp is None:
            self.composition = dict(major=None, minors=None, others=None)
        else:
            self.composition = comp

        self._colors = np.zeros((0, 3))

        if lith is not None:
            assert isinstance(lith, pd.Series)
            self.interpret_macrostrat(lith, inplace=True)

    def interpret_macrostrat(
        self,
        col: pd.Series,
        inplace=False,
        return_best_info=False,
    ):
        """
        Takes a 'lith' column from the macrostrat database and
        puts all found lithographies into the dictionary self.composition

        If the API call gives no information about the share of
        each component to the total, the item is None

        If a sediment is tagged as major or minor, this will be used as
        item in self.composition

        If a percentage range is given, this range is the item

        Args:
            col(pd.Series): Series of sediments
                            obtained at coords from macrostrat API
            inplace(bool): as in Pandas objects
            return_best_info(bool): if True, returns index of best information
        """

        best_info = None

        for i, entry in col.iteritems():
            minor_major = None

            entry = entry.lower()
            if "major" in entry:
                minor_major = get_minor_major(entry)
                self.composition.update(minor_major)
                best_info = i

            elif "%" in entry:
                minor_major = get_percentages(entry)
                self.composition.update(minor_major)
                best_info = i

            else:
                entry = re.sub(r"[^a-zA-Z0-9 ]", "", entry)
                entry = entry.replace(" and", "")
                liths = [lith for lith in entry.split(" ") if len(lith) > 0]

                if isinstance(self.composition["others"], list):
                    self.composition["others"] = list(
                        set(self.composition["others"] + liths)
                    )
                else:
                    self.composition["others"] = liths

                if best_info is None:
                    best_info = i

        returns = list()
        if not inplace:
            returns.append(self)
        if return_best_info:
            returns.append(best_info)
        if returns:
            return returns

    def __repr__(self):
        return f"Lithology composition: \n {self.composition}"

    @property
    def empty(self):
        """Returns True if no information has been passed to self.composition"""
        return bool(len([val for val in self.composition.values() if val is not None]))

    @property
    def thermal_conductivity(self):
        """Returns thermal conductivity as mean and variance"""
        raise NotImplementedError("implement me")

    @property
    def thermal_capacity(self):
        """Returns thermal capacity as mean and variance"""
        raise NotImplementedError("implement me")

    @property
    def colors(self):
        """Returns the average of obtained colors"""
        if self._colors.shape[0] > 0:
            return self._colors.mean(axis=0).astype(int)
        else:
            return np.zeros(3).astype(int)

    @colors.setter
    def colors(self, value):
        """appends new color to stack of colors"""
        self._colors = np.vstack([self._colors, value])

    @property
    def major(self):
        """Returns major lithology"""
        return self.composition["major"]

    @major.setter
    def major(self, value):
        """Sets major lithology"""
        assert isinstance(value, str) or value is None
        self.composition["major"] = value

    @property
    def minors(self):
        """returns minor lithologies"""
        return self.composition["minors"]

    @minors.setter
    def minors(self, value):
        """sets minor lithologies"""
        if not isinstance(value, list):
            value = [value]
        else:
            value = [val for val in value if val is not None]
        self.composition["minors"] = value

    @property
    def others(self):
        """returns unordered lithologies"""
        return self.composition["others"]

    @others.setter
    def others(self, value):
        """sets unordered lithologies"""
        if not isinstance(value, list):
            value = [value]
        else:
            value = [val for val in value if val is not None]
        self.composition["others"] = value

    def tolist(self):
        """
        composition and colors from self are returned as a list in order
        [major, minor1, minor2, minor3, other1, other2, other3, color]
        """

        aslist = deepcopy(nonelist)
        aslist[0] = self.major
        if not self.minors is None:
            aslist[1 : 1 + min(len(self.minors), 3)] = self.minors[:3]
        if not self.others is None:
            aslist[4 : 4 + min(len(self.others), 3)] = self.others[:3]
        aslist[-1] = rgb2hex(*self.colors)

        return aslist

    @classmethod
    def from_list(cls, lithlist):
        """
        Creates a Lith object from a list in order
        [major, minor1, minor2, minor3, others1, others2, others3, color]
        """

        instance = cls()
        instance.major = lithlist[0]
        instance.minors = lithlist[1:4]
        instance.others = lithlist[4:7]
        instance.colors = ImageColor.getcolor(lithlist[-1], "RGB")

        return instance

    @classmethod
    def to_dataset(cls, data):
        """
        Transforms a xr.DataArray of Lith objects into a xr.Dataset with
        str entries that are the list version of Lith objects (see the 'tolist()'
        method)
        The resulting dataset can be stored as a netcdf file

        Args:
            data(xr.DataArray): entries must be Lith objects

        Returns:
            xr.Dataset with Lith.index as vars. Coords are copied from da

        """
        assert isinstance(data, xr.DataArray)

        coords = data.coords
        shape = data.shape

        da_np = data.to_numpy()
        hold = np.zeros((8,) + data.shape).astype(str)

        for i, j in product(range(shape[0]), range(shape[1])):
            hold[:, i, j] = da_np[i, j].tolist()

        return xr.Dataset(
            data_vars={
                var_name: (["x", "y"], hold[i]) for i, var_name in enumerate(Lith.index)
            },
            coords=coords,
        )

    @classmethod
    def to_dataarray(cls, data):
        """
        Takes an xr.Dataset and merges the variables Lith.index to a single
        xr.DataArray, which is returned. Note the resulting xr.DataArray can
        not be saved anymore

        Args:
            data(xr.Dataset): dataset containing Lith.index as variables

        Returns
            xr.DataArray:
        """

        assert isinstance(data, xr.Dataset)
        assert set(cls.index).issubset(list(data.variables))

        shape = data[cls.index[0]].shape
        coords = data[cls.index[0]].coords

        data_np = np.array([data[var_name] for var_name in Lith.index])
        result = np.zeros(shape, dtype=Lith)

        for i, j in product(range(shape[0]), range(shape[1])):
            result[i, j] = Lith.from_list(data_np[:, i, j])

        return xr.DataArray(result, coords=coords)


def get_random_lith():
    """Passes a lithography oject, randomly filled out as it
    might be after a Macrostrat call"""

    lith = Lith()
    stones = ["limestone", "clay", "carbonated rock", "sedimentary", "plutonic rock"]

    if np.random.rand() > 0.3:
        lith.major = np.random.choice(stones)
    lith.minors = np.random.choice(stones, size=np.random.randint(0, 4)).tolist()
    lith.others = np.random.choice(stones, size=np.random.randint(0, 4)).tolist()
    lith.colors = np.random.randint(0, 256, size=(3))

    return lith
