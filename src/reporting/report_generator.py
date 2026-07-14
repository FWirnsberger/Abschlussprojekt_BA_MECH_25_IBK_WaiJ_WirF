import logging
import subprocess   #damit Latex von diesem Programm aus aufgerufen werden kann3

from pathlib import Path 


class ReportGenerator:
    """
    Hier wird der Latex Bericht erstellt (erweiterbar) und anschließend als PDF exportiert.
    """

    def __init__(self, output_directory: str, title: str = "Auswertung der Fahrradsimulation") -> None:
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents= True, exist_ok= True)  # Ordner für Bericht wird erstellt, falls noch nicht vorhanden
        self.title = title
        self.figures: list[dict[str, str]] = []     #Infos der Grafiken (Name, Pfad) werden hier gespeichert


    def add_figure(self, image_path: Path, caption: str, label: str) -> None:
        """
        Hier wird die Grafik zum Bericht hinzugefügt

        Argumente:
            image_path: Dateipfad der Bilddatei
            caption: Bildunterschrift
            label: Latex kennung 
        """
        absolute_path = image_path.resolve() #resolve() ist eine Methode von Pathlib, sie wandelt einen Pfad in einen absoluten Pfad um
        latex_path = absolute_path.as_posix()   #as_posix() Methoode von Pathlib, macht aus Backslash normale Schrägstriche für Latex (/ wegen Division)

        self.figures.append(
            {
                "path": latex_path,
                "caption": caption,
                "label": label,
            }
        )

    def create_tex_file(self) -> Path:
        """
        hier wird die Latex Datei erstellt

        Return:
            Pfad zur erzeugten .tex Datei
        """

        tex_path = self.output_directory / "report.tex"     #Speicherort der tex Datei angeben ohne die Datei selbst zu erstellen
        latex_content = self.create_latex_content()

        tex_path.write_text(latex_content, encoding="utf-8")    #Latex Quellcode wird als utf 8 kodierte Datei in report.tex geschrieben

        logging.info(f"LaTeX-Datei wurde erstellt: {tex_path}")

        return tex_path
    
    def export_pdf(self, tex_path: Path) -> Path:
        """
        mit pdflatex wird die tex Datei kompiliert und in der Funktion anschliesend als PDF exportiert

        Argumente: 
            tex_path: Pfad zur tex Datei, welche kompiliert werden soll

        Returns:
            Path: Pfad zur PDF Datei
        """
        try:
            subprocess.run(
                [
                    "pdflatex",                     #startet Latex-Compiler
                    "-interaction=nonstopmode",     #Latex läuft ohne Benutzereingabe und kompiliert trotz Fehler weiter
                    tex_path.name,                  #hier wird der Dateiname übergeben
                ],
                cwd=self.output_directory,          #hier wird der Arbeitsordner auf den Ausgabeordner gesetzt
                check=True,                         #wenn durch pdflatex (beim kompilieren) ein Fehler auftritt, wird pdflatex abgebrochen und geht beim except-Block weiter
            )
        except FileNotFoundError as error:
            raise RuntimeError(                     #falls kein Latex Compiler installiert ist
                "pdflatex wurde nicht gefunden."
                "Bitte installiere MiKTeX."
            ) from error
        
        except subprocess.CalledProcessError as error:
            raise RuntimeError(                     #falls pdflatex gefunden wurde, beim kompilieren aber ein Fehler auftritt
                "Beim erstellen der PDF-Datei ist ein Latex Fehler aufgetreten."
                "Bitte Überprüfe die Datei report.log"
            ) from error                            #speichert den Error der die exception ausgelöst hat
        
        pdf_path = self.output_directory / "report.pdf"
        logging.info(f"PDF-Datei erstellt: {pdf_path}")
        return pdf_path
    

    def create_latex_content(self) -> str:
        """
        Hier wird der Latex Code zum kompilieren erstellt, als String
        """
        figure_code = ""        # ein leere String, hier wird später der gesamte Latex Code der Grafiken gespeichert

        for figure in self.figures:     #jede Grafik der Liste self.figures wird iteriert
            #rf steht für raw String und f-String
            figure_code += rf"""       

\begin{{figure}}[htbp]
    \centering
    \includegraphics[width=0.95\textwidth]{{{figure["path"]}}}
    \caption{{{figure["caption"]}}}
    \label{{{figure["label"]}}}
\end{{figure}}

\clearpage
"""

        return rf"""
\documentclass[12pt,a4paper]{{article}}

\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage[ngerman]{{babel}}
\usepackage{{graphicx}}
\usepackage{{float}}
\usepackage{{geometry}}

\geometry{{
    left=25mm,
    right=25mm,
    top=25mm,
    bottom=25mm
}}

\title{{{self.title}}}
\author{{Jonas Waid und Fabian Wirnsberger}}
\date{{\today}}

\begin{{document}} 

% Ein richtiges Titelblatt kann später hier ergänzt werden.
\maketitle

\tableofcontents
\clearpage

\section{{Grafische Auswertung}}

Die folgenden Diagramme zeigen ausgewählte Verläufe während der Fahrt.

{figure_code}       %hier werden die Grafiken eingefügt

\end{{document}}
"""