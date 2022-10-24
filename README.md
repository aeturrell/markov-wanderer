# Markov Wanderer

This is the repo behind the [Markov Wanderer blog](https://aeturrell.github.io/markov-wanderer/).

To build the blog, the prerequisites are:

- an installation of [Quarto](https://quarto.org/)
- an installation of [conda](https://conda.io/) or [miniconda](https://docs.conda.io/en/latest/miniconda.html)
- (optional) an installation of [mamba](https://github.com/mamba-org/mamba), which makes conda much faster.

To create the Python environment, run

```bash
conda env create -f environment.yml
```

on the command line. To run subsequent commands you should have the "blog" conda environment activated, ie you should have run

```bash
conda activate blog
```

To preview the blog in local browser files, run

```bash
quarto preview
```

To publish the blog, it's

```bash
quarto publish
```