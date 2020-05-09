# Cdocs
## A super simple contextual help library.

**Cdocs** is intended to help manage files for use in contextual help systems. The library knows how to find docs given a path. The expected use is to create an endpoint to retrieve docs from at runtime, or to pull docs into an app build.

Cdocs stores documentation as text files in a directory tree. Files are Jinja templates containing whatever doc format you prefer. Cdocs applies tokens to the templates, if found. Files can be concatenated or composed.

Cdocs can also be used to find text strings referred to as labels. Labels are stored as (non-template) JSON files in the same directory tree. The expected use is to find a JSON structure of labels for UI elements that would be seen in the same screen contextual help is available for.

Docs are stored in two directory trees: public and internal. The public tree is for your docs writers to store their content. Internal is for defaults and is expected to not be widely accessible. Requests for labels and tokens are aggregated from every directory below root, starting from the requested path.  The values found lowest in the directory tree win. Public values win over internal values.

Use *config/config.ini* to set the documentation root directory, file extension, etc.

Cdocs has several ways of getting content:
- **get_doc**: docs at paths like */x/y/z* with the physical file being at *[root]/x/y/z.[ext]*. This is the "default" doc for the path. The result text will be treated as a jinja template. The template will receive a dict created from all the *[tokens].json* files from the doc's directory up to the root, and the same from the same directory under the internal tree.
- **get_labels**: labels as json for paths like */x/y/z* found as *[root]/x/y/z/labels.json*
- **get_doc**: docs at paths like */x/y/z#name* found as *[root]/x/y/z/name.[ext]*. These docs are processed in the same way as the default doc.
- **get_concat_doc**: docs as concats of files for paths like */x/y/z* found as *[root]/x/y/z/page.txt* where page.txt is a list of simple doc names to be concatenated. Simple doc names are the same as docs named by the *#name* path suffix. The files to be concatenated must be in the directory pointed to by the path.
- **get_compose_doc**: docs as jinja files at paths like */x/y/z/page.html* that compose pages where docs are pulled in using jinja expressions like:
*{{ get_doc('/app/home/teams/todos/assignee#edit_assignee') }}*
*get_compose_doc* requires the compose template be *.xml*, *.html* or *.md*. A compose doc could be referenced by a concat file, or vice versa, but the reference will only include the file contents; it will not be transformed.

### TODO:
- indicate a transformer for default and #name docs. E.g. to transform xml > md, md > html, etc.
- think about if all docs should be able to pull in other docs, not just the compose docs.
- think about if concat and compose docs should be transformed before being included in the other type. e.g. if /x/y/z/concat.txt included /x/compose.html then compose.html would be rendered before being concatenated.
- create a Flask Api for requesting docs and labels





