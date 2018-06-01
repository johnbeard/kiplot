# KiPlot

KiPlot is a program which helps you to plot your KiCad PCBs to output
formats easily, repeatable, and most of all, scriptably. This means you
can use a Makefile to export your KiCad PCBs just as needed.

For example, it's common that you might want for each board rev:

* Check DRC one last time
* Gerbers, drills and drill maps for a fab in their favourite format
* Fab docs for the assembler
* Pick and place files

You want to do this in a one-touch way, and make sure everything you need to
do so it securely saved in version control, not on the back of an old
datasheet.

KiPlot lets you do this.

## Developing

Set up a virtualenv:

```
virtualenv --python /usr/bin/python2.7 ~/venv/kiplot
```

Install with `pip -e`:

```
cd path/to/kiplot
pip install -e .
```