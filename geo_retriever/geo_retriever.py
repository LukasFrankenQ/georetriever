from heatflow import get_heatflow

class GeoRetriever:
    def __init__(self, coords=(-1.761873755588998, 54.9503096017342)):
        
        self.coords = coords
        self.quants = ['heatflow']
        
    def retrieve(self):

        data_bundle = dict()

        if 'heatflow' in self.quants:
            data_bundle['heatflow'] = get_heatflow(self.coords)            

        return data_bundle 
       

if __name__ == '__main__':         
    from pprint import pprint
    golden = GeoRetriever()
    pprint(golden.retrieve())