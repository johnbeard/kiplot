# KiPlot

KiPlot is a program which helps you to plot your KiCad PCBs to output
formats easily, repeatable, and most of all, scriptably. This means you
can use a Makefile to export your KiCad PCBs just as needed.

For example, it's common that you might want for each board rev:

* Check DRC one last time (currently not possible)
* Gerbers, drills and drill maps for a fab in their favourite format
* Fab docs for the assembler
* Pick and place files

You want to do this in a one-touch way, and make sure everything you need to
do so it securely saved in version control, not on the back of an old
datasheet.

KiPlot lets you do this.

As a side effect of providing a scriptable plot driver for KiCad, KiPlot also
allows functional testing of KiCad plot functions, which would otherwise be 
somewhat unwieldy to write.

## Developing

Set up a virtualenv:

```
virtualenv --python /usr/bin/python2.7 ~/venv/kiplot
source ~/venv/kiplot/bin/activate
```

Install `kiplot` with `pip -e`:

```
cd path/to/kiplot
pip install -e .
```

This doesn't include the `pcbnew` Python package - that is assumed to
be accessible to the program. You might need to add it to the `PYTHONPATH`.

You might also need to set `LD_LIBRARY_PATH` (you need to be able to load
`libkicad_3dsg.so`).

For example, if you installed in `~/local/kicad`, you might have:

```
export PYTHONPATH=~/local/kicad/lib/python2.7/site-packages
export LD_LIBRARY_PATH=~/local/kicad/lib64
```

If you've installed "normally", you should not need to do this.

## Testing

There are some tests. Run them with pytest:

```
pytest
```

# TODO list

There are some things that still need work:

* DRC checking - that can't be done over the Python interface yet. If/when
  this is added to KiCad, KiPlot will be able to also be used for DRC
  functional tests instead of a complex additonal test harness in C++.
