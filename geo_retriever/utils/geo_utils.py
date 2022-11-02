import re

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
    def __init__(self):
        
        self.composition = dict()        

    def interpret_macrostrat(self, col, inplace=False):
        """
        Takes a 'lith' column from the macrostrat database and 
        puts all found lithographies into the dictionary self.composition

        If the API call gives no information about the share of
        each component to the total, the item is None
        
        If a sediment is tagged as major or minor, this will be used as 
        item in self.composition
        
        If a percentage range is given, this range is the item
       
        Args:
            col(pd.Series): Series of sediments obtained at coords from macrostrat API
        
        """


        print("-------------------")

        for i, entry in col.iteritems():
            minor_major = None
            
            if 'sedimentary rock' in entry:
                self.composition['sedimentary rock'] = None
                continue

            entry = entry.lower()
            if 'major' in entry:
                minor_major = get_minor_major(entry)
            
            elif '%' in entry:
                minor_major = get_percentages(entry)
            
            else:
            
                entry = re.sub(r'[^a-zA-Z0-9 ]', '', entry)
                entry = entry.replace(' and', '')
                liths = [lith for lith in entry.split(' ') if len(lith) > 0]

            if minor_major is None:
                for rock in liths:
                    if rock not in self.composition:
                        self.composition[rock] = None
            else:
                self.composition[minor_major['major']] = 'major'            
                self.composition = {**self.composition, **{lith: 'minor' for lith in minor_major['minors']}}
        
        # print(col)
        # print(self.composition)
 
        if not inplace:
            return self



    def __repr__(self):
        return f"Major: {self.composition}"