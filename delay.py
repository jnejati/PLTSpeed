import json
import pickle
from ripe.atlas.sagan import PingResult
from ripe.atlas.cousteau import Measurement, Probe

f  = open("./ping_data", "rb")
try:
    unpickler = pickle.Unpickler(f)
    ping_dict = unpickler.load()
except EOFError:
    pass
res= ping_dict['Fin24']['www.Fin24.com'][239]
res.rtt_median
