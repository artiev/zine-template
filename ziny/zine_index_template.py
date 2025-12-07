import logging

from ziny.zine_image_metadata import ZineImageMetadata

logger = logging.getLogger('Zine Index Template')
logger.setLevel(logging.INFO)

class ZineIndexTemplate(object):
    
    def __init__(self) -> None:
        self.meta = None

    def configure(self, meta:ZineImageMetadata) -> None:
        """
        Map image metadata object to this template.
        """
        self.meta = meta # Shallow
    
    def get_template(self) -> str:
        """
        Pull all parts of the templates from individual builders.
        """
        tpl = self.get_header_and_thumbnail_template()
        tpl += self.get_title_and_description_template()
        tpl += self.get_metadata_template()
        tpl += self.get_footer_template()

        return tpl

    def get_header_and_thumbnail_template(self) -> str:
        """
        Build index thumbnail minipage in latex. Start metadata minipage.
        """

        tpl = "\\begin{minipage}{0.25\\textwidth}\n"
        tpl += f"\t\\includegraphics[width=40mm, keepaspectratio]{{{self.meta.thumbnail_path}}}\n"
        tpl += "\\end{minipage}\n"
        tpl += "\\hfill\n"
        tpl += "\\begin{minipage}{0.70\\textwidth}\n"
        tpl += "\t\\raggedright\n"

        return tpl

    def get_title_and_description_template(self) -> str:
        """
        Build index title and description (if any).
        """
        
        tpl = f"\t\\par \\raisebox{{-0.1\\height}}{{\\faImage[regular]}}~\\textbf{{Photo \\#{self.meta.id}}}"
        tpl += "$\\cdot$"
        tpl += f"Page~\\pageref{{img:{self.meta.image_path}}} $\\cdot$ {self.meta.timestamp}\n"

        if self.meta.description:
            tpl += f"\t\\par {self.meta.description}\n"
            tpl += "\t\\vspace{0.25cm}\n"

        return tpl
    
    def get_metadata_template(self) -> str:
        """
        Build index metadata.
        """
        
        tpl = str()
        tpl = f"\t\\par {self.meta.make} {self.meta.model}\n"
        tpl += f"\t\\par {self.meta.lens_make} {self.meta.lens_model}\n"
        tpl += f"\t\\par {self.meta.aperture} $\\cdot$ {self.meta.speed} $\\cdot$ ISO {self.meta.iso}\n"
        tpl += f"\t\\par {self.meta.program} $\\cdot$ {self.meta.metering_mode} Metering {self.meta.exposure_compensation} stop\n"
        return tpl
    
    def get_footer_template(self) -> str:
        """
        Close metadata minipage.
        """
        
        tpl = "\\end{minipage}\n"
        tpl += "\\vspace{0.5cm}\n\n"

        return tpl