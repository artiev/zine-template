python generate.py
pdflatex front.tex
pdflatex content.tex
pdflatex content.tex
pdflatex spine.tex
pdflatex back.tex
pdflatex cover.tex
pdflatex web.tex

mkdir -p print
rm -f -r print/*

mkdir -p web
rm -f -r web/*

mv web.pdf web/zine.pdf
mv *.pdf print/

rm -f *.aux *.log *.fls *.out *.fdb_latexmk
rm -f template/*.aux