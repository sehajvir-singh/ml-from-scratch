from .jepa import JEPA
from .kan import KAN
from .lireca import LiReCA
from .liquid import Liquid
from .nca import NCA
from .trm import TRM

MODELS = {"trm": TRM, "nca": NCA, "jepa": JEPA, "liquid": Liquid, "kan": KAN, "lireca": LiReCA}
