# Installing ConText

Note: as indicated below, I've begun working on an installation method that does not require installing Python. This should support 
Windows, Mac and Linux users. The functionality will be the same. Currently you need to use Conc to build your corpora 
and then run ConText to work with them, so you need Python currently. Once building corpora is added to ConText I will 
work to release a more straightforward install method. 

## Installation instructions (Mirrors README text on installation)

ConText launches a web browser in "app mode". You will need Chromium (or Chrome) installed with the current version.  

ConText is currently [released as a pip-installable package](https://pypi.org/project/contextapp/). Other installation methods are coming soon.  

To install via pip, [setup a new Python 3.11+ environment](https://github.com/polsci/ConText/blob/main/installation.md#python-setup) and run the following command:  

```bash
pip install contextapp
```

ConText/Conc requires installation of a Spacy model. For example, for English:  

```bash
python -m spacy download en_core_web_sm
```

## Python Setup

If you are new to Python, a good way to get this setup is to [install Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install). 
This creates a "base" Python environment. A good practice is to create a new environment for new projects (or at least those that are likely to require different versions of packages).
After installing Miniconda, you should have an "Anaconda Prompt" terminal available. Start that and run the following commands to create a new environment called `context`:

```bash
conda create -n context python=3.11
conda activate context
```

You can then install ConText using the instructions above. 

Each time you want to use ConText, you should start the Anaconda prompt and the context enivironment with:

```bash
conda activate context
```

Note: deactivating the environment is done with `conda deactivate`.

## Windows Subsystem for Linux (WSL) 

If you are using Windows Subsystem for Linux (WSL) you will need to install a browser and setup your distribution to invoke it. This will depend on the distribution you are using. 

On Ubuntu (the default WSL distribution) you can install Chromium with:

```bash
sudo snap install chromium
```

Then set the `BROWSER` environment variable to invoke Chromium. 
Do this by adding the following line to `.bashrc` (e.g. `nano ~/.bashrc`) or `.zshrc`:
```bash
export BROWSER="chromium %s"
```

## Notes for installing on older machines

Notes: Conc installs the Polars library. If you are using an older pre-2013 machines, you will need to install Polars without optimisations for modern CPUs. Notes on this are available in the [Conc installation documentation](https://geoffford.nz/conc/tutorials/install.html#pre-2013-cpu-install-polars-with-support-for-older-machines).  