from enum import Enum, unique
from types import DynamicClassAttribute

class LabelledIntEnum(int, Enum):
    """
    Provides the equivalent of an IntEnum with each enumeration being labelled with a string.
    eg. ONE = 1, 'One' --> cls.ONE.value is 1 | cls.label is 'One'
    """

    def __new__(cls, value:int, label:str):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj._label = label
        return obj
    

    @DynamicClassAttribute
    def label(self):
        return self._label

@unique
class WhiteBalance(LabelledIntEnum):

    UNKNOWN = -1, 'Unknown' # Not defined in EXIF 'standard'
    AUTO = 0, 'Auto'
    MANUAL = 1, 'Manual'

@unique
class ExposureProgram(LabelledIntEnum):

    UNKNOWN = 0, 'Unknown'
    MANUAL = 1, 'Manual'
    NORMAL_PROGRAM = 2, 'Normal'
    APERTURE_PRIORITY = 3, 'Aperture Priority'
    SHUTTER_PRIORITY = 4, 'Shutter Priority'
    CREATIVE_PROGRAM = 5, 'Creative (DOF Priority)'
    ACTION_PROGRAM = 6, 'Action (SS Priority)'
    PORTRAIT_MODE = 7, 'Portrait (Bokeh Priority)'
    LANDSCAPE_MODE = 8, 'Landscape (Infinity Priority)'

@unique
class ExposureMode(LabelledIntEnum):

    UNKNOWN = -1, 'Unknown' # Not defined in EXIF 'standard'
    AUTO_EXPOSURE = 0, 'Auto'
    MANUAL_EXPOSURE = 1, 'Manual'
    AUTO_BRACKET = 2, 'Auto Bracket'

@unique
class MeteringMode(LabelledIntEnum):

    UNKNOWN = 0, 'Unknown'
    AVERAGE = 1, 'Average'
    CENTER_WEIGHTED_AVERAGE = 2, 'Center Weighted Average'
    SPOT = 3, 'Spot'
    MULTI_SPOT = 4, 'Multi Spot'
    MATRIX = 5, 'Matrix'
    PARTIAL = 6, 'Partial'
    OTHER = 255, 'Other'
