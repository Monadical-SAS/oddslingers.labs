# [OddSlingers Labs](https://labs.oddslingers.com)

Simple static website generator in Flask for OddSlingers Labs.

All content metadata is stored in `content.json`.

Templates are in: `templates/`
Static files are in: `templates/`

## Common Tasks

### Adding a new Post

1. upload post as markdown to https://docs.oddslingers.com
2. click "Publish", and get the public url, like `https://docs.oddslingers.com/s/Skcz_hUhM`
3. edit `content.json` to add metadata for new post, including public url
4. rebuild site
5. new post should appear on articles page

### Adding a new Page

1. edit 'content.json' to add metadata for new page, including url
2. add new template `html` file to `templates/`
3. add link to new page in navbar: see `base.html` `<nav>` section
4. rebuild site
5. new page should appear in navbar


### Editing existing Post/Page

1. edit 'content.json' to reflect new metadata
2. edit any relevant templates
3. rebuild site
4. new page should appear in navbar

## Command Line Interface

### Run the Server

```bash
./app.py
```

### Get a list of the build urls

```bash
./app.py --pages
./app.py --posts
```

### Build the Static Site

```bash
./build
```
Static HTMML output will be produced in `output/`, and can be rsyned to a server using:

`rsync -r output/ labs.oddslingers.com:/opt/labs.oddslingers.com/output`

## Stack

The static site generator is build using Flask + Jinja2 and wget to save the output as static html.
