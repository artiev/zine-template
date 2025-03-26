"""
Generates the list of images to be included automatically
"""

import os, sys
import logging
from math import ceil
from exif import Image

from python.zine_image_metadata import ImageMetadata

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('Template')
input_dir = 'images_content/'
content_file = 'images.tex'
index_file = 'index.tex'

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

def find_jpg_files(directory):
    """
    Lists all image files in the input_dir folder. Sorted by name.
    """

    images = list()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('front.jpg'):
                pass
            elif file.endswith('.jpg'):
                relative_path = os.path.relpath(os.path.join(root, file), start=directory)
                images.append(relative_path)
                logger.info(f'Found image: {relative_path}')

    return sorted(images)

def generate_content(images:list) -> None:
    """
    Generates latex code for the Zine's main content, the pictures. Minimal layouting.
    """

    with open(content_file, 'w') as f:
        f.write(f'% File is automatically generated. Edits will be overwritten.\n\n')

        for id, image in enumerate(images):
            logger.info(f'Generating content\'s latex code for image: {image}')

            f.write(content_template.format(image=image))

    return


def generate_index(images:list):
    """
    Extracts, cleans and output the EXIF image information and miniature numbered images as an index.
    """

    with open(index_file, 'w') as f:
        f.write(f'% File is automatically generated. Edits will be overwritten.\n\n')
        
        for id, image in enumerate(images):

            logger.info(f'Generating index\'s latex code for image: {image}')

            with open(input_dir + image, 'rb') as imgfile:
                exifdata = Image(imgfile)

            id += 1 # Do not start at Zero

            meta = ImageMetadata(id, image)
            meta.infer_iso(exifdata.photographic_sensitivity)
            meta.infer_timestamp(exifdata.datetime_original)
            meta.infer_speed_fraction(exifdata.exposure_time)
            meta.infer_aperture(exifdata.aperture_value, exifdata.f_number)
            meta.infer_exposure_compensation_fraction(exifdata.exposure_bias_value)
            meta.infer_make_and_model(exifdata.make, exifdata.model)
            meta.infer_lens_make_and_model(exifdata.lens_make, exifdata.lens_model)
            meta.infer_metering(exifdata.metering_mode)
            meta.infer_program(exifdata.exposure_mode, exifdata.exposure_program)
            meta.infer_white_balance(exifdata.white_balance)

            f.write(
                index_template.format(**meta.to_dict())
            )

    return


def generate_library(images:list) -> None:
    """
    Extracts, cleans and output the EXIF image information and miniature numbered images as an index.
    """

    for id, image in enumerate(images):

        logger.info(f'Generating index\'s latex code for image: {image}')

        with open(input_dir + image, 'rb') as imgfile:
            exifdata = Image(imgfile)

        id += 1 # Do not start at Zero

        meta = ImageMetadata(id, image)
        meta.infer_iso(exifdata.photographic_sensitivity)
        meta.infer_timestamp(exifdata.datetime_original)
        meta.infer_speed_fraction(exifdata.exposure_time)
        meta.infer_aperture(exifdata.aperture_value, exifdata.f_number)
        meta.infer_exposure_compensation_fraction(exifdata.exposure_bias_value)
        meta.infer_make_and_model(exifdata.make, exifdata.model)
        meta.infer_lens_make_and_model(exifdata.lens_make, exifdata.lens_model)
        meta.infer_metering(exifdata.metering_mode)
        meta.infer_program(exifdata.exposure_mode, exifdata.exposure_program)
        meta.infer_white_balance(exifdata.white_balance)

    return

def main() -> int:
    images = find_jpg_files(input_dir)
    generate_content(images)
    generate_index(images)
    generate_library(images)
    return 0

if __name__ == '__main__':
    ret = main()
    sys.exit(ret)