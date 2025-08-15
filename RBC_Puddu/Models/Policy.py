import time
from InputsConfig import InputsConfig as p

class Policy(object):
    def __init__(self,
                 mutators= [0],
                 extenders= None or [],
                 time = time.time()+p.simulation_duration,
                 size=0.000546
                 ):
        self.mutators = mutators or []
        self.extenders = extenders or []
        self.time = time
        self.size = size

