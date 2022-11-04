import numpy as np
import re
import pandas as pd

def get_minor_major(line):
    line = line.lower()
    major = line.split('}')[0].split('{')[-1]
    minors = line.split('minor{')[-1].replace('}', '').split(',')
    return {"major": major, "minors": minors}


def get_percentages(line):
    liths = line.split(']')[:-1]
    shares = [part.split('[')[-1] for part in liths]
    shares = ['9' in part for part in shares]
    liths = [lith.split(' [')[0] for lith in liths]
    liths = [re.sub(r'[^a-zA-Z0-9 ]', '', lith).lower() for lith in liths]
    for i, lith in enumerate(liths):
        lith = re.sub(r'[^a-zA-Z0-9 ]', '', lith).lower() 
        if lith[0] == ' ':
            lith = lith[1:]
            liths[i] = lith

    result = dict()
    result["minors"] = [lith for i, lith in enumerate(liths) if not shares[i]] 
    result["major"] = liths[shares.index(True)]
    
    return result


class Lith:
    def __init__(self, lith=None, /, comp=None):
        
        if comp is None:
            self.composition = dict(major=None, minors=None, others=None) 
        else:
            self.composition = comp

        self._colors = np.zeros((0, 3))
        
        if lith is not None:
            assert isinstance(lith, pd.Series)
            self.interpret_macrostrat(lith, inplace=True)


    def interpret_macrostrat(self, 
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
            if 'major' in entry:
                minor_major = get_minor_major(entry)
                self.composition.update(minor_major)
                best_info = i
            
            elif '%' in entry:
                minor_major = get_percentages(entry)
                self.composition.update(minor_major)
                best_info = i
            
            else:
                entry = re.sub(r'[^a-zA-Z0-9 ]', '', entry)
                entry = entry.replace(' and', '')
                liths = [lith for lith in entry.split(' ') if len(lith) > 0]

                if isinstance(self.composition["others"], list):
                    self.composition["others"] = list(set(self.composition["others"] + liths))
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
        return f"Lithology object with composition: \n {self.composition}"

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
            return self._colors.mean(axis=0)
        else:
            return np.zeros(3)
    
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
        assert isinstance(value, str)
        self.composition["major"] = value

    @property
    def minors(self):
        """returns minor lithologies""" 
        return self.composition["minors"]
    
    @minors.setter
    def major(self, value):
        """sets minor lithologies""" 
        assert isinstance(value, list)
        self.composition["minors"] = value

    @property
    def others(self):
        """returns unordered lithologies""" 
        return self.composition["others"]
    
    @others.setter
    def others(self, value):
        """sets unoredered lithologies""" 
        assert isinstance(value, list)
        self.composition["others"] = value