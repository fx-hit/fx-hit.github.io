# Fuxiang Yang Homepage

Personal homepage and resume source for Fuxiang Yang (杨富祥), PhD student at Harbin Institute of Technology.

Live site: [fx-hit.github.io](https://fx-hit.github.io)

## Directory

```text
.
|-- index.html                 # Homepage entry for GitHub Pages
|-- assets/
|   |-- css/styles.css          # Site styles
|   |-- images/avatar.png       # Profile photo
|   `-- js/main.js              # Language toggle and page interactions
|-- resume/
|   |-- fuxiang-yang-resume.md  # Resume source in Markdown
|   `-- fuxiang-yang-resume.pdf # Generated resume PDF
`-- scripts/
    `-- build_resume_pdf.py     # Markdown-to-PDF resume builder
```

## Resume PDF

The resume PDF is generated from `resume/fuxiang-yang-resume.md`.

```bash
python3 scripts/build_resume_pdf.py
```

Custom input and output paths are also supported:

```bash
python3 scripts/build_resume_pdf.py path/to/resume.md path/to/resume.pdf
```

The builder uses local Google Chrome through Playwright and writes temporary HTML files under `tmp/`, which is ignored by Git.
