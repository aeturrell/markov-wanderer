---
date: "2021-11-04"
layout: post
title: Setting up R in Visual Studio Code
categories: [code, rstats]
---

This post will show you how to set up Visual Studio Code as an integrated development environment for the statistical language R. This will include some useful features such as:

- plots that appear within a VS Code panel
- a language server with autocomplete
- syntax highlighting of R code in console and scripts
- interactive window development

Of course, RStudio has all of these features for R too. However, Visual Studio Code does a lot more than just R, and has tons of cutting edge integrated development environment features that we'd like to make use of.

The prerequisites are:

1. An installation of the R language
2. An installation of Python
3. Visual Studio Code
4. The R extension for Visual Studio Code

Steps:

1. Install the Python package [radian](https://github.com/randy3k/radian), which provides multiline editing and rich syntax highlighting. It sells itself as "A 21 century R console". The installation can be achieved by running `conda install -c conda-forge radian` on the command line, if you manage your Python environments with conda, or `pip install -U radian` if you use pip.
2. Start up R (wherever) and run `install.packages("languageserver")` to install a language server.
3. Also `install.packages("httpgd")` to install the plot viewer.
4. Hit <kbd>Ctrl</kbd> (command on mac) + <kbd>,</kbd> in Visual Studio Code to open up the settings. Then make the following changes: enable R Bracketed Paste, R Session Watcher, and R: Always Use ActiveTerminal.
5. Now we want to make plots show up automatically within Visual Studio Code. If you don't have an R profile on your computer already, create it with `touch ~/.Rprofile`. You can check if you have it already using `ls -a ~`.
6. Use `code ~/.Rprofile` to open the Rprofile file. Add the following code to it:

```R
if (interactive() && Sys.getenv("RSTUDIO") == "") {
  Sys.setenv(TERM_PROGRAM = "vscode")
  if ("httpgd" %in% .packages(all.available = TRUE)) {
    options(vsc.plot = FALSE)
    options(device = function(...) {
      httpgd::hgd(silent = TRUE)
      .vsc.browser(httpgd::hgd_url(history = FALSE), viewer = "Beside")
    })
  }
  source(file.path(Sys.getenv(if (.Platform$OS.type == "windows") "USERPROFILE" else "HOME"), ".vscode-R", "init.R"))
}
```

7. In the terminal window of VS Code, type `radian` to bring up the R console.
8. Create an R script. Why not try writing `hist(trees$Height, breaks = 10, col = "orange")` in it? Then use <kbd>Ctrl</kbd> (command on mac) + <kbd>⏎</kbd> to send the line of code to the console. You should see your plot appear!

Tips:

- You can find the workspace viewer under the `R` tab on the left-hand side of VS Code along with the Help Pages.
- To bring up the variable explorer, use `View(data)` where data is an object containing data.
- Interactive plotly charts work, as does a webviewer (eg for Shiny apps; try `shiny::runExample("01_hello")`)
- Help pages can be revealed via `?symbol` in the console

You can find more information on the R extension for VS Code [here](https://github.com/REditorSupport/vscode-R).