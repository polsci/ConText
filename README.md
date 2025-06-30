# ConText

A browser-based concordancer and language analysis application.  

This repository builds on work done in 2020 on a Python library, Jupyter Notebook and Dash application for the Mapping LAWS project. This work prototyped a browser-based alternative to desktop applications for corpus analysis. Ideas for this tool originated during my PhD thesis, which developed a browser-based analysis tool around a corpus of parliamentary discourse enabling rapid queries, new forms of analysis and browseable connections between different levels of analysis.  

ConText builds on [Conc](https://github.com/polsci/conc), a Python library for corpus analysis.  

## Acknowledgements

Conc is developed by [Dr Geoff Ford](https://geoffford.nz/).

Work to create this Python library has been made possible by
funding/support from:

- “Mapping LAWS: Issue Mapping and Analyzing the Lethal Autonomous
  Weapons Debate” (Royal Society of New Zealand’s Marsden Fund Grant
  19-UOC-068)  
- “Into the Deep: Analysing the Actors and Controversies Driving the
  Adoption of the World’s First Deep Sea Mining Governance” (Royal
  Society of New Zealand’s Marsden Fund Grant 22-UOC-059)
- Sabbatical, University of Canterbury, Semester 1 2025.

Thanks to the Mapping LAWS project team for their support and feedback
as first users of ConText.

Dr Ford is a researcher with [Te Pokapū Aronui ā-Matihiko \| UC Arts
Digital Lab (ADL)](https://artsdigitallab.canterbury.ac.nz/). Thanks to
the ADL team and the ongoing support of the University of Canterbury’s
Faculty of Arts who make work like this possible.

## Design principles

### Embed ConText

A key principle is to embed context from the texts, corpus and beyond into the application. This includes design choices to make the text, metadata and origin of the text visible and accessible. The text corpus can be navigated (and read) via a concordancer that sits alongside the text. To aide the researcher in interpretation, quantifications are directly linked to the texts they relate to. 

### Efficiency

The software prioritises speed through pre-processing via [Conc](https://github.com/polsci/conc). Intensive processing (tokenising, creating indexes, pre-computing useful counts) happens when the corpus is first built. This is done once and stored. This speeds up subsequent queries and statistical calculations. The frontend is minimal and lightweight and uses web technologies for interactivity. The interface opens up pathways for analysis by allowing navigation between levels of analysis and allowing researchers to quickly switch corpora and reference corpora to allow intuitive, comparitive exporation.

## Installation

ConText launches a web interface. You will need Chromium (or Chrome) installed.  

ConText is currently [released as a pip-installable package](https://pypi.org/project/getcontext/). Other installation methods are coming soon.  

To install via pip, setup a new Python 3.11+ environment and run the following command:  

```bash
pip install getcontext
```

ConText/Conc requires installation of a Spacy model. For example, for English:  

```bash
python -m spacy download en_core_web_sm
```

Notes: Conc installs the Polars library. If you are using an older pre-2013 machines, you will need to install Polars without optimisations for modern CPUs. Notes on this are available in the [Conc installation documentation](https://geoffford.nz/conc/tutorials/install.html#pre-2013-cpu-install-polars-with-support-for-older-machines).  

## Using ConText

To use ConText currently you need to [build your corpora using Conc from text files or CSV sources](https://geoffford.nz/conc/tutorials/recipes.html). You should have a corpus and reference corpus. Conc provides [sample corpora to download and build](https://geoffford.nz/conc/api/corpora.html#build-sample-corpora).  

To allow ConText to find them when it starts up store the created corpora in the same parent directory.  

Run ConText like this ...  

```bash
ConText --corpora /path/to/directory/with/processed/corpora/
```

To run the application in debug mode (relevant for development or diagnosing problems), use the following command:   

```bash
ConText --corpora /path/to/directory/with/processed/corpora/ --mode development
```

A video tutorial on how to use ConText is coming soon.  

## Credit

- Prototype styling is based on a Plotly Dash Stylesheet (MIT License)  
- Icons are via [Ionicons](https://ionic.io/ionicons)  

### Coming soon

- Pypi release  
- Video tutorial  
- run as an application on Windows/Linux/Mac  
- allow configuration of settings for all reports  
- updates of corpus/reference corpus will only refresh current page to allow comparing token-level results between corpora  
- json settings file for context to preserve state between loads  
- update html title on url changes  
- loading indicator via hx-indicator  
- record session in a json file per session  
- tooltips for buttons and other functionality  
- preferences (e.g. when expand reference corpus - remember that across session and store in json)  
- highlighty interface  
- make concordance plot lines clickable to text view
- add ngram frequencies
- links in collocation report --> conc: contextual restriction for concordances with +

