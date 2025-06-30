# ConText

A browser-based concordancer and language analysis application.  

ConText is a new tool allowing you to to analyze corpora through a browser-based interface. Rather than separating out reports views, ConText uses hyperlinks to allow you to navigate connections between keywords, collocates, clusters, and specific texts. ConText is relevant for corpus linguistic analysis, data scientists working with text, and academics who want a knew way to engage with their texts. 

ConText is in active development and is currently released as a Python package. ConText builds on [Conc](https://github.com/polsci/conc), a Python library for corpus analysis. ConText can be used as a graphical user interface to analyse corpora with Conc. More updates, including a video tutorial and installers for different operating systems, are coming soon. I welcome your feedback and I'm keen to help if you have problems. The easiest way to make contact about ConText is to [raise an issue](https://github.com/polsci/ConText/issues/new).

This repository builds on work done in 2020 on a Python library, Jupyter Notebook and Dash application for the Mapping LAWS project. This work prototyped a browser-based alternative to desktop applications for corpus analysis. Ideas for this tool originated during my PhD thesis, which developed a browser-based analysis tool around a corpus of parliamentary discourse enabling rapid queries, new forms of analysis and browseable connections between different levels of analysis.  

## Screenshots and features

| | |
|:-------------------------:|:-------------------------:|
|<img alt="Initial corpus view, with keywords and corpus information prominent" src="https://github.com/polsci/ConText/blob/main/assets/01-corpus-keyness-and-info.png?raw=true">  Initial corpus view, with keywords and corpus information prominent |  <img alt="Navigate from keywords to token-based view, with Concordance and Clusters" src="https://github.com/polsci/ConText/blob/main/assets/02-from-keywords-to-concordance.png?raw=true"> Navigate from keywords to token-based view, with Concordance and Clusters |
|<img alt="Multiple views of the data are available" src="https://github.com/polsci/ConText/blob/main/assets/03-switch-views-concordance-plot.png?raw=true">  Multiple views of the data are available |  <img alt="Switching corpora is easy, allowing quick access to different comparisons" src="https://github.com/polsci/ConText/blob/main/assets/04-switch-corpora.png?raw=true"> Switching corpora is easy, allowing quick access to different comparisons|
|<img alt="Search and re-ordering is alaways accessible" src="https://github.com/polsci/ConText/blob/main/assets/05-searching-for-economy.png?raw=true">  Search and re-ordering is alaways accessible |  <img alt="Switch from clusters to collocates" src="https://github.com/polsci/ConText/blob/main/assets/06-switch-to-view-collocates.png?raw=true"> Switch from clusters to collocates|
|<img alt="Navigate from concordances and concordance plots to the position within the text" src="https://github.com/polsci/ConText/blob/main/assets/07-navigate-the-texts.png?raw=true">  Navigate from concordances and concordance plots to the position within the text |  <img alt="Click on specific clusters to narrow the view" src="https://github.com/polsci/ConText/blob/main/assets/08-narrow-and-focus.png?raw=true"> Click on specific clusters to narrow the view|

## Acknowledgements

Conc is developed by [Dr Geoff Ford](https://geoffford.nz/).

Work to create ConText has been made possible by
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

Above all, thanks to my family for their love, patience and kindness.

## Design principles

### Embed ConText

A key principle is to embed context from the texts, corpus and beyond into the application. This includes design choices to make the text, metadata and origin of the text visible and accessible. The text corpus can be navigated (and read) via a concordancer that sits alongside the text. To aide the researcher in interpretation, quantifications are directly linked to the texts they relate to. 

### Efficiency

The software prioritises speed through pre-processing via [Conc](https://github.com/polsci/conc). Intensive processing (tokenising, creating indexes, pre-computing useful counts) happens when the corpus is first built. This is done once and stored. This speeds up subsequent queries and statistical calculations. 

### A browseable corpus

The frontend uses web technologies to make different views of the corpus available in an interactive, playful way. The interface is minimal and lightweight. The interface uses hyperlinks to open up pathways for analysis allowing navigation between levels of analysis. You can quickly switch corpora and reference corpora facilitating straightforward comparative analysis.

## Installation

ConText launches a web interface. You will need Chromium (or Chrome) installed.  

ConText is currently [released as a pip-installable package](https://pypi.org/project/contextapp/). Other installation methods are coming soon.  

To install via pip, setup a new Python 3.11+ environment and run the following command:  

```bash
pip install contextapp
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

