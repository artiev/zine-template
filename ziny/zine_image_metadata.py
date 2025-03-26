import json
import logging
from datetime import datetime

from PIL.TiffImagePlugin import IFDRational
from PIL.ExifTags import Base

from ziny.zine_exif_constants import WhiteBalance, ExposureProgram, ExposureMode, MeteringMode

logger = logging.getLogger('Zine Image Metadata')
logger.setLevel(logging.INFO)

class ZineImageMetadata():
    """
    Creates human-readable representations of the photo metadata.
    The step of translating the input intot he final formatted attribute is 
    called "inferance" althrough sometimes the inpout and output have the 
    correct format already.
    """

    def __init__(self, id=None, image=None, timestamp=None, 
                 make=None, model=None, lens_make=None, lens_model=None, 
                 aperture=None, speed=None, iso=None, 
                 expocomp=None, program=None, metering_mode=None, wb_mode=None):
        
        self.id=id
        self.image=image
        self.timestamp=timestamp
        self.make=make
        self.model=model
        self.lens_make=lens_make
        self.lens_model=lens_model
        self.aperture=aperture
        self.speed=speed
        self.iso=iso
        self.exposure_compensation=expocomp
        self.program=program
        self.metering_mode=metering_mode
        self.white_balance = wb_mode

        self.sidecar_data = dict()

        logger.debug(f'ID: {self.id}')
        logger.debug(f'Image Path: {self.image}')
        self.load_substitution_dictionary('dictionary.json')

    def _substitute_and_sanitize(self, something:str) -> str:

        if self._substitutions is not None:
            for sub in self._substitutions:
                something = something.replace(sub['original'], sub['substitution'])
        
        # Special cases and escaping
        something = something.replace('&', '\&')

        return something

    def to_dict(self) -> dict:

        td = dict(
            id = self.id,
            image = self.image,
            timestamp = self.timestamp,
            make = self.make,
            model = self.model,
            lens_make = self.lens_make,
            lens_model = self.lens_model,
            aperture = self.aperture,
            speed = self.speed,
            iso = self.iso,
            exposure_compensation = self.exposure_compensation,
            program = self.program,
            metering_mode = self.metering_mode,
            white_balance = self.white_balance
        )

        return td
    
    def set_id(self, id:int) -> None:
        self.id = id

    def parse_exif_data(self, exifdata) -> None:
        """
        Extract the relevant exif data.
        """
        
        self.infer_iso(exifdata.get(Base.ISOSpeedRatings.value))
        self.infer_timestamp(exifdata.get(Base.DateTimeOriginal.value))
        self.infer_speed_fraction(exifdata.get(Base.ExposureTime.value))
        self.infer_aperture(exifdata.get(Base.FNumber.value))
        self.infer_exposure_compensation_fraction(exifdata.get(Base.ExposureBiasValue.value))
        self.infer_make_and_model(exifdata.get(Base.Make.value), exifdata.get(Base.Model.value))
        self.infer_lens_make_and_model(exifdata.get(Base.LensMake.value), exifdata.get(Base.LensModel.value))
        self.infer_metering(exifdata.get(Base.MeteringMode.value))
        self.infer_program(exifdata.get(Base.ExposureProgram.value))
        self.infer_white_balance(exifdata.get(Base.WhiteBalance.value))
    
    def infer_iso(self, sensitivity) -> None:

        # Nothing to infer
        self.iso = sensitivity

        logger.debug(f'ISO: {self.iso}')

    def infer_program(self, program) -> None:

        self.program = ExposureProgram.UNKNOWN
        for enum in ExposureProgram:
            if program == enum.value:
                self.program = enum.label
        
        logger.debug(f'Program: {self.program}')

    def infer_metering(self, mode) -> None:

        self.metering_mode = MeteringMode.UNKNOWN
        for enum in MeteringMode:
            if mode == enum.value:
                self.metering_mode = enum.label

        logger.debug(f'Metering mode: {self.metering_mode}')

    def infer_exposure_compensation_fraction(self, bias:float) -> None:

        exposure_compensation_absolute = abs(bias)
        eca_integer = int(exposure_compensation_absolute)
        eca_floating = exposure_compensation_absolute % 1

        exposure_compensation = str(eca_integer)
        if eca_floating > 0:
            eca_thirds = int(eca_floating / 0.33)
            if eca_integer == 0:
                exposure_compensation = '{}/3'.format(eca_thirds)
            else:
                exposure_compensation += ' and {}/3'.format(eca_thirds)


        if bias > 0:
            exposure_compensation = '+' + exposure_compensation
        elif bias < 0:
            exposure_compensation = '-' + exposure_compensation

        self.exposure_compensation = exposure_compensation
        logger.debug(f'Exposure Compensation: {self.exposure_compensation}')

    def infer_white_balance(self, wb:str, temperature:int = None) -> None:

        self.white_balance = WhiteBalance.UNKNOWN
        for enum in WhiteBalance:
            if wb == enum.value:
                self.white_balance = enum.label
        
        if self.white_balance is WhiteBalance.UNKNOWN:
            logger.warning('White Balance could not be inferred. Verify output.')


        logger.debug(f'White balance: {self.white_balance}')

        # Not supported yet
        self.temperature = temperature
        logger.debug(f'Temperature: {self.temperature}')

    def infer_make_and_model(self, make:str, model:str) -> None:

        self.make = self._substitute_and_sanitize(make)
        logger.debug(f'Camera Make: {self.make}')
        self.model = self._substitute_and_sanitize(model)
        logger.debug(f'Camera Model: {self.model}')

    def infer_lens_make_and_model(self, lens_make:str, lens_model:str) -> None:

        self.lens_make = self._substitute_and_sanitize(lens_make)
        logger.debug(f'Lens Make: {self.lens_make}')
        self.lens_model = self._substitute_and_sanitize(lens_model)
        logger.debug(f'Lens Model: {self.lens_model}')

    def infer_timestamp(self, ts) -> None:
        timestamp = datetime.strptime(ts,  '%Y:%m:%d %H:%M:%S')
        timestamp = datetime.strftime(timestamp, '%B %Y')
        self.timestamp = timestamp
        logger.debug(f'Timestamp: {self.timestamp}')

    def infer_speed_fraction(self, exposure_time) -> None:

        speed = f'{0:.{2}f} sec'.format(exposure_time)
        if exposure_time < 1:
            speed = '1/{0:.0f} sec'.format(int(1.0 / exposure_time))

        self.speed = speed
        logger.debug(f'Speed: {self.speed}')

    def infer_aperture(self, f_number:IFDRational) -> None:

        aperture = 'No Aperture Information'
        if f_number.denominator != 0:
            floating_f_number = f_number.numerator / f_number.denominator
            aperture = 'f/{0:.1f}'.format(floating_f_number)

        self.aperture = aperture
        logger.debug(f'Aperture: {self.aperture}')

    def extract_sidecar_data(self, sidecar_file_path:str) -> None:

        try:
            with open(sidecar_file_path) as scf:
                logger.info(f'Loading sidecar data from `{sidecar_file_path}`')
                self.sidecar  = json.load(scf)

                for key, value in self.sidecar.items():
                    logger.debug(f'Additional information `{key}` contained in sidecar: {value}')

        except Exception as err:
            logger.error('Sidecar data file could not be loaded. Verify output.')
            logger.debug(err.msg)



    def load_substitution_dictionary(self, dictionary_file_path = 'dictionary.json'):

        try:
            with open(dictionary_file_path) as dico:
                logger.debug(f'Substitution dictionary loaded ({dictionary_file_path}).')
                substitutions = json.load(dico)
        except:
            substitutions = None
            logger.warning('Substitution dictionary could not be loaded. Verify output.')

        self._substitutions = substitutions
