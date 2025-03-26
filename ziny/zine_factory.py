import os
import logging

from PIL import Image

from ziny.zine_image_metadata import ZineImageMetadata

logger = logging.getLogger('Zine Factory')
logger.setLevel(logging.INFO)


class ZineFactory():

    content_template = """
    \\begin{{figure}}
    \\centering
    \\phantomsection\\label{{img:{image}}}
    \\includegraphics[height=\\textheight, width=160mm, keepaspectratio]{{{image}}}%
    \\end{{figure}}
    """

    index_template = """
    \\begin{{minipage}}{{0.25\\textwidth}}
    \\includegraphics[width=43mm, keepaspectratio]{{{image}}}
    \\end{{minipage}}
    \\hfill
    \\begin{{minipage}}{{0.70\\textwidth}}
    \\raggedright
    \\par \\raisebox{{-0.1\\height}}{{\\faImage[regular]}}~\\textbf{{Photo \\#{id}}} $\\cdot$ Page~\\pageref{{img:{image}}} $\\cdot$ {timestamp}
    \\par {make} {model}
    \\par {lens_make} {lens_model}
    \\par {aperture} $\cdot$ {speed} $\cdot$ ISO {iso}
    \\par {program} $\cdot$ {metering_mode} Metering {exposure_compensation} stop
    \\end{{minipage}}
    \\vspace{{0.5cm}}
    """

    # Visibility: default, hidden
    # Layout: auto, single (single image on page)
    # Position: auto, top, bottom (only if layout=single)
    # Order: order photos
    sidecar_template = """{
        "visibility": "default",
        "layout": "auto",
        "position": "auto"
    }"""

    def __init__(self, image_folder:str):

        self.image_folder = image_folder
        self.library = dict()
        self.library_keys = list()

    def scan(self):
        """
        Lists all image files in the input_dir folder. Sorted by name.
        """

        logger.info(f'Scanning folder `{self.image_folder}`')

        self.library.clear()
        self.library_keys.clear()
        id = 1 # Start at 1 like normal human beings.

        for root, _, files in os.walk(self.image_folder):

            # Sorting images to create a first indexing
            for file in sorted(files):

                # Leaving the front page image alone.
                if file.endswith('front.jpg'):
                    logger.info('Found reserved image name `front.jpg` during scan. Ignored.')

                # Processing any non-reserved images
                elif file.endswith('.jpg'):
                    relative_image_path = os.path.join(root, file)
                    logger.info(f'Found image `{relative_image_path}`')

                    # Create ZineImageMetadata from reading out EXIF data
                    meta = self.extract_metadata_from_exif_data(relative_image_path, id)
                    meta.set_id(id)

                    # Load any additional metadata from sidecar file. Or create it if missing.
                    relative_sidecar_path = self.get_sidecar_file_path(relative_image_path)
                    if not self.is_sidecar_file_found(relative_sidecar_path):
                        logger.warning(f'No Sidecar file found for this image. Creating one based on template.' )
                        self.create_sidecar_file_from_template(relative_sidecar_path)
                    
                    meta.extract_sidecar_data(relative_sidecar_path)

                    # Add image data to library
                    self.library_keys.append(relative_image_path)
                    self.library[relative_image_path] = meta
                    id += 1
        
        logger.info(f'Scanning completed. A total of {len(self.library_keys)} entries were added to the library.')

    def get_sidecar_file_path(self, relative_image_file_path:str) -> str:
        """
        Return sidecar file path based on image file path.
        """
        return relative_image_file_path + '.json'
    
    def is_sidecar_file_found(self, relative_sidecar_file_path:str) -> str:
        """
        Check for JSON sidecar file. If it doesn't exist, create it.
        """

        verdict = False
        if os.path.exists(relative_sidecar_file_path):
            verdict = True

        return verdict
    
    def create_sidecar_file_from_template(self, sidecar_file_path:str) -> None:
        """
        Create a sidecar file from the template.
        """

        with open(sidecar_file_path, 'w') as sidecar_file:
            sidecar_file.write(self.sidecar_template)


    def extract_metadata_from_exif_data(self, image_path, id:int = 0) -> ZineImageMetadata:

        with Image.open(image_path) as imgfile:
                exifdata = imgfile._getexif()
                
        meta = ZineImageMetadata(id, image_path)
        meta.parse_exif_data(exifdata)

        return meta
    
    def generate_thumbnails(self):
        """
        Generate index thumbnail images from the main image library to use in the Photo Index.
        """
        
        pass

