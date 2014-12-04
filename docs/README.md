PyEconLab Documentation
=======================

This is the documentation for PyEconLab

Currently this is a built document. The following command should be issued at the root level of the repo: 

``sphinx-apidoc -o docs pyeconlab``.

**Note:** ``-f`` may need to be specified to overwrite the generated rst pages

Docstring Reminders
-------------------

To conform with ``NumPy`` documentation the following should be followed. 

Notes should we added as sphinx directives

```
.. note:: Deprecated in PyEconLab 0.1
	`function` will be removed in PyEconLab 0.2, as it will be replaced by `newfunction`
```

Parameters for Functions and Methods

```
Parameters
----------
x : type
    Description of parameter `x`.
```

Future Work
-----------
  1. Construct a ``make.py`` file for building the documentation (similar to Pandas). This may or may not replace the sphinx MakeFile

References
----------
  1. [NumPy Documentation Style Guide](<https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt>)
  1. [Markdown Syntax](http://daringfireball.net/projects/markdown/syntax)
  1. [RestructuredText Quick Reference](http://docutils.sourceforge.net/docs/user/rst/quickref.html)