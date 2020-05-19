# Cdocs
## A super simple contextual help library.

**Cdocs** is intended to help manage files for use in contextual help systems. The library knows how to find docs given a path. Paths should mirror a logical or physical structure of the application. This way docs are easy find and map cleanly to the way the app works.

The expected use of Cdocs is to create an endpoint to retrieve in-context help docs from at runtime, or to pull docs into an app build. In principle and with some custom code, Cdocs could be used as a lightweight general purpose help and manual system; however, that is not its intended use.

Cdocs stores documentation as text files in a directory tree. Files are Jinja templates containing whatever doc format you prefer. Cdocs applies tokens to the templates if ```tokens.json``` containing dict are found. Files can be concatenated and/or composed.

Cdocs can also be used to find text strings referred to as labels. Labels are stored as (non-template) json files containing dict in the same directory tree. The expected use is to find a JSON structure of labels for UI elements that would be seen in the same screen contextual help is available for.

Requests for labels and tokens are aggregated from every directory below root, starting from the requested path.  The values found lowest in the directory tree win.

You may configure as many docs directory trees as you find useful. Multi tree requests go against a Context object that implements the MultiContextDocs ABC and returns docs by searching the trees in the order they appear in config.ini. You may limit each directory tree to certain file types. Each root is self-contained, meaning that labels and tokens used in doc file transformations are found and applied only within their directory tree, and that the paths found in concat and compose files are resolved only in the same tree. However, multi-context requests for labels return labels aggregated from all trees. If this is not desireable, use the MultiContextDocs interface passing in only the roots you want labels from.

Cdocs will return binary files based on a limited set of known file types. Currently the types are 'gif', 'jpeg', 'jpg', 'png', 'pdf'.

Use a *config.ini* to set the root directories, file extension, etc. The default location for the config file is ```os.getcwd()/config/config.ini```. You can pass a different path in the Cdocs constructor. The contents should be similar to this:
```
# docs section lists the doc directory roots. use as many as you need.
[docs]
   public = /Users/davidkershaw/dev/cdocs/docs/example
   internal = /Users/davidkershaw/dev/cdocs/docs/internal
# accepts limits the file types handled by each root. root names passed to the context will be filtered according to this list.
[accepts]
   public = cdocs
   internal = gif,png,jpeg
# you can configure defaults to point to a file to return if a doc is not found. if not configured, the response to a path that doesn't exist is None.
[defaults]
   notfound = internal/404
# format section currently only used to indicate the extension of files found using /x/y/z paths
[formats]
   ext = xml
# filenames section lets you change the names of the tokens and labels files, set the name anchor char (hashmark), and the on the fly concatination char (plus)
[filenames]
   tokens = tokens.json
   labels = labels.json
   hashmark = #
   plus = +
```

Cdocs has several ways of getting content:
 - **get_doc**: docs at paths like ```/x/y/z``` with the physical file being at ```[root]/x/y/z.[ext]```. This is the "default" doc for the path.

     The resulting text will be treated as a jinja template. The template will receive a dict created from all the *[tokens].json* files from the doc's directory up to the first level below root, and from the same starting point under the internal tree. The tokens dict will also have all the labels from the ```labels.json``` files found by crawling up the directory trees from the same point. Labels are added to the tokens dict with keys like ```label__[label_key]```. *Note that a good choice of word separator char for tokens and labels keys is the underscore.*

     Docs can be incorporated in other docs using jinja expressions like: ```{{ get_doc('/app/home/teams/todos/assignee#edit_assignee') }}```.
     This functionality is essentially the same as the more specific *get_compose_doc* method, below.

     Paths may not have periods in them.

     You may use '+' (or the config value at [filenames][plus]) to concat docs from the same path on the fly. For e.g.
```/x/y/z#name+new_name+edit_name``` would return the doc at ```/x/y/z/name.xml``` + ```/x/y/z/new_name.xml``` + ```/x/y/z/edit_name.xml```, with a space char joining them.
 - **get_doc**: docs at paths like ```/x/y/z#name``` found as ```[root]/x/y/z/name.[ext]```. These docs are processed in the same way as the default doc. The name separator can be configured to be a different character by adding a [hashmark] value to the config ini file under [filenames].
 - **get_concat_doc**: docs as concats of files for paths like ```/x/y/z``` found as ```[root]/x/y/z/page.concat``` where page.concat is a list of simple doc names to be concatenated. Simple doc names are the same as docs named by the *#name* path suffix. The files to be concatenated may be anywhere in the document tree.
 - **get_compose_doc**: docs as jinja files at paths like ```/x/y/z/page.html``` that compose pages where docs are pulled in using jinja expressions like:
```{{ get_doc('/app/home/teams/todos/assignee#edit_assignee') }}```.
*get_compose_doc* requires the compose template be *.xml*, *.html* or *.md*. A compose doc could be referenced by a concat file, or vice versa, but the reference will only include the file contents; it will not be transformed.
 - **get_labels**: labels as json dicts for paths like ```/x/y/z``` found as ```[root]/x/y/z/labels.json```. Labels are transformed in the same way as docs, except that the keys of the json dict are individual templates. A label can pull in a doc in the same way that a doc is embedded in a compose doc. Labels that pull in docs are tricky because the docs pulled in may or may not correctly handle any label replacements used with tokens.json, depending on any circular references.

Creating a Cdocs endpoint using Flask might look something like:
```
app = Flask(__name__)
api = Api(app)
@app.route('/cdocs/&lt;path:cdocspath&gt;')
def cdocs(cdocspath:str):
     cdocs = Cdocs(PATH)
     return cdocs.get_doc(cdocspath)
```

Flask won't have access to an anchor appended to a URL by a hashmark. (E.g. ```http://a.com/x/y/z#name```). To work around that you can add a [filenames][hashmark] setting to the config.ini with a different character.  E.g.:
```
[filenames]
 hashmark = *
```

The same endpoint using all of a set of docs directory trees configured in config.ini might look like:
```
app = Flask(__name__)
api = Api(app)
@app.route('/cdocs/&lt;path:cdocspath&gt;')
def cdocs(cdocspath:str):
     metadata = ContextMetaData()
     context = Context(metadata)
     return context.get_doc(cdocspath)
```
An endpoint implementation might want to search certain trees based on the locale of the request, a version name, a product name, an author, etc.

### TODO:
- Configure a transformer for default and #name docs. (And concat and compose?) E.g. to automatically transform xml > md, md > html, etc.
- Think about if concat and compose docs should be transformed before being included in the other type. e.g. if /x/y/z/concat.txt included /x/compose.html then compose.html would be rendered before being concatenated.



