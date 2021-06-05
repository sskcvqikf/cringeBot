all:
	latexmk -pdf -xelatex --shell-escape -outdir=build

clear:
	latexmk -c

plaintext:
	mkdir -p build/
	pandoc main.tex --wrap=none -t plain -o build/main.txt

docx:
	mkdir -p build/
	pandoc main.tex -o build/main.docx
