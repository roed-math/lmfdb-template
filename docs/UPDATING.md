# Keeping up to date

Improvements reach your website in two ways.

## 1. lmfdb-utils: most improvements

Nearly all the code of the website (page layout, style sheet, search forms
and results, downloads, statistics, knowls, users) is in the lmfdb-utils
package, which the LMFDB uses too.  When the LMFDB improves it, update the
package:

```
sage -pip install --upgrade -r requirements.txt
```

Once lmfdb-utils is published on PyPI, `requirements.txt` allows the
versions that should work without changes to your website (the same minor
version, `>=0.1,<0.2`); until then it installs it from git, and
`sage -pip install --force-reinstall --no-deps -r requirements.txt` gets the
latest commit.  A new minor version (`0.2`) may need changes
to your website: they are listed in the
[lmfdb-utils changelog](https://github.com/LMFDB/lmfdb/blob/main/packages/lmfdb-utils/CHANGELOG.md);
change the line in `requirements.txt`, update, and run the tests.

To be told about new versions, enable Dependabot on your repository (it reads
`requirements.txt`, and opens a pull request for each new version, which the
tests then check).  The template's own tests also run every week against the
lmfdb-utils of the LMFDB's main branch, to catch changes before they are
released.

Because your templates and static files take precedence over the package's,
a page you replaced entirely (rather than filling in its blocks) stays as it
is: compare it with the package's version from time to time.

## 2. The template: occasionally

The files of the template itself (scripts, configuration, the layout
templates in `website/templates`, documentation) change less often.  Since
your website started as a clone of the template, git can merge those changes:

```
git fetch template
git log --oneline main..template/main    # what changed
git merge template/main
```

(If you cloned without renaming `origin`, add the remote first:
`git remote add template https://github.com/LMFDB/lmfdb-template.git`.)

Conflicts happen only in files that both you and the template changed, and
mostly in a few lines: the template keeps what you are expected to change
(`website/site.py`, `colors.py`, `templates/index.html`, `sidebar.yaml`, your
sections) separate from what it changes, and its example section is in its
own directory, which you can delete (`git rm -r website/sections/example
knowls/example.yaml scripts/load_example.py`, and remove it from
`website/app.py`, `sidebar.yaml` and the tests) once you have sections of
your own.  Changes needing manual steps (a new setting, a change to the
database) are described in the template's commit messages and in
[the template's changelog](../CHANGELOG.md).

If you started from GitHub's "Use this template" button, your repository
does not share the template's history; `git merge --allow-unrelated-histories
template/main` connects them once, with conflicts to resolve in every file you
changed.

## Contributing back

An improvement useful to other websites (a new search box, a fix to a
template, a better style) belongs in lmfdb-utils, in the
[LMFDB repository](https://github.com/LMFDB/lmfdb) (`packages/lmfdb-utils`),
so that it reaches the LMFDB and every website built on it; improvements to
the template itself go to
[LMFDB/lmfdb-template](https://github.com/LMFDB/lmfdb-template).
