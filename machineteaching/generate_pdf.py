from pylatex import Document, Section, Subsection, Figure, VerticalSpace, NoEscape, NewPage
from pylatex.base_classes import Environment
from pylatex.package import Package
import os

class Multicols(Environment):
    """A class to wrap LaTeX's Multicols environment."""

    packages = [Package('multicol')]
    escape = False
    content_separator = "\n"

class Verbatim(Environment):
    """A class to wrap LaTeX's Verbatim environment."""

    packages = [Package('verbatim')]
    escape = False
    content_separator = "\n"

class PDFReport(object):
    def __init__(self):
        self.doc = self.begin_pdf()

    def begin_pdf(self):
        geometry_options = {"tmargin": "1cm", "lmargin": "1cm",
                            "landscape":True}
        self.doc = Document(geometry_options=geometry_options)
        self.doc.packages.append(Package('float'))

        return self.doc

    def append_solution(self, solution_id, problem, solution):
        with self.doc.create(Multicols(arguments=[2])):
            image_filename = os.path.join(os.path.dirname('.'),
                                          'images/solution_%d.png' % solution_id)
            with self.doc.create(Section('Problem with solution %d' % solution_id,
                                         label="problem%d" % solution_id)):
                with self.doc.create(Subsection('TSNE representation',
                                           label="tsne%d" % solution_id)):
                    with self.doc.create(Figure(position='H')) as tsne:
                        tsne.add_image(image_filename, width=NoEscape(r'11cm'))
                        tsne.add_caption('TSNE 2d feature space')

                self.doc.append(VerticalSpace(NoEscape(r"\fill")))

                with self.doc.create(Subsection('Problem and Solution',
                                                label="solution%d" % solution_id)):
                    self.doc.append(problem)
                    with self.doc.create(Verbatim()):
                        self.doc.append(solution)
                self.doc.append(VerticalSpace(NoEscape(r"\fill")))
                self.doc.append(NewPage())

        return self.doc

    def generate_pdf(self, name):
        self.doc.generate_pdf(name, clean_tex=False)

    def generate_tex(self, name):
        self.doc.generate_tex(name)
