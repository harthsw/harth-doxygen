Harth-Doxygen
=============

This is a Python tool which can converted [Doxygen] style comments
embedded in C++ or [Harth] source text into [Hugo] style markdown.

## How It Works

* Either:
  * [Harth] source code is read by [Harth]'s compiler and similar C++ suitable for [Doxygen] is output.
  * The C++ source code is read directly by [Doxygen].
* [Doxygen] extracts the comments and source meta data and outputs this in XML files.
* This tool reads the XML and outputs [Hugo] style markdown, in multiple output content files.
* [Hugo] uses the [Harth] [Hugo] theme styles and CSS (based on Bootstrap) to render the markdown as HTML.

## How It Should Work

Eventually:

* [Harth] should do most of the above work internally:
  * Reading C++ or [Harth] source.
  * Extracting documentation and source meta data.
  * Rendering this as [Hugo] style markdown.

* [Harth] would always required a conforming style and [Hugo] to post-process the output into HTML.
* Typically the output would be processed once when the static website is generated.

[Harth]: http://www.harth-lang.org/
[Hugo]: http://gohugo.io/
[Doxygen]: http://doxygen.org/


