[![](https://img.shields.io/pypi/v/foliantcontrib.argdown.svg)](https://pypi.org/project/foliantcontrib.argdown/) [![](https://img.shields.io/github/v/tag/foliant-docs/foliantcontrib.argdown.svg?label=github)](https://github.com/foliant-docs/foliantcontrib.argdown)

# Argdown Diagrams Preprocessor for Foliant

[Argdown](https://argdown.org/) is a modeling language for creating argument maps. This preprocessor takes Argdown diagram definitions in source markdown files and converts them into images on the fly during project build.

This preprocessor uses [Argdown Image Export package](https://github.com/christianvoigt/argdown/tree/master/packages/argdown-image-export) tool by [Christian Voigt](https://github.com/christianvoigt) to convert diagrams into images.

## Installation

```bash
$ pip install foliantcontrib.argdown
```

You will also need to install Argdown CLI and the Image Export package:

```bash
$ npm install -g @argdown/cli
$ npm install -g @argdown/image-export
```

## Config

To enable the preprocessor, add `argdown` to `preprocessors` section in the project config:

```yaml
preprocessors:
    - argdown
```

The preprocessor has a number of options:

```yaml
preprocessors:
    - argdown:
        cache_dir: !path .diagramscache/argdown
        converter_path: argdown
        format: png
        as_image: true
        params:
            no-title: true
        fix_svg_size: false
```

`cache_dir`
:   Path to the cache directory for the generated diagrams. It can be a path relative to the project root or a global one.

>   To save time during build, only new and modified diagrams are rendered. The generated images are cached and reused in future builds.

`converter_path`
:   Path to Argdown CLI. By default, it is assumed that you have the `argdown` command in your `PATH`, but if it is not the case you can define it here. Default: `argdown`

`format`
:   Output format of the diagram image. Available formats at the time of writing: `dot`, `graphml`, `svg`, `pdf`, `png`, `jpg`, `webp`. Default: `png`

`as_image`
:   If `true` — inserts the diagram into the document as Markdown-image. If `false` — inserts the source code of the diagram directly into the document (works only for `svg`, `dot` and `graphml` formats). Default: `true`

`params`
:   Params passed to the Argdown CLI map tool. Value of this option must be a YAML-mapping. Params which require values should be specified as `param: value`; params which don't require values should be specified as `param: true`.

> To see the full list of available params, run `argdown map --help`.

`fix_svg_size`
:   Works only with `svg` format and `as_image: false`. By default svg is embedded with hardcoded width and height so they may exceed the boundaries of your HTML page. If this option is set to `true` the svg width and height will be set to `100%` which will make it fit inside your content container. Default: `false`.


## Usage

To insert a diagram definition in your Markdown source, enclose it between `<argdown>...</argdown>` tags:

```html
Here’s the diagram:

<argdown>
===
title: The Core Argument of Populism
author: David Lanius
date: 27/10/2018
===


This is a recontruction of right-wing populist argumentation 
based on the electoral platform of the German party...
</argdown>
```

You can override preprocessor parameters in the tag options. For example if the format for diagrams is set to `png` in foliant.yml and you need one of your diagrams to render in svg, override the `format` option in the tag:

```html
SVG diagram:

<argdown format="svg">
...
</argdown>
```

Tags also have an exclusive option `caption` — the markdown caption of the diagram image.

```html
Diagram with a caption:

<argdown caption="Diagram of the opposing arguments">
...
</argdown>
```
