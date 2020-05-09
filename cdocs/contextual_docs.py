import abc

class ContextualDocs(metaclass=abc.ABCMeta):
    """ cdocs gets:
            - get_doc: docs at paths like /x/y/z with the physical file being
              at <root>/x/y/z.[ext]. this is the "default" doc for the path. the result
              text will be treated as a jinja template. the template will receive
              a dict created from all the [tokens].json files from the doc's directory
              up to the root, and the same from the same directory under the internal
              tree.
            - get_labels: labels as json for paths like /x/y/z found as <root>/x/y/z/labels.json
            - get_doc: docs at paths like /x/y/z#name found as <root>/x/y/z/name.[ext].
              these docs are processed in the same way as the default doc.
            - get_concat_doc: docs as concats of files for paths like /x/y/z found as
              <root>/x/y/z/page.txt where page.txt is a list of simple doc names
              to be concationated. simple doc names are the same as docs named
              by the #name path suffix. the files to be concationated must be
              in the directory pointed to by the path.
            - get_compose_doc: docs as jinja files at paths like /x/y/z/page.html that
              compose pages where docs are pulled in using jinja expressions like:
              {{ get_doc('/app/home/teams/todos/assignee#edit_assignee') }}
              get_compose_doc requires the compose template be .xml, .html or .md. a
              compose doc could be referenced by a concat file, or vice versa, but the
              reference will only include the file contents; it will not be transformed.
        TODO:
            - indicate a transformer for default and #name docs. e.g. to transform
              xml > md, md > html, etc.
            - think about if all docs should be able to pull in other docs, not just the
              compose docs.
            - think about if concat and compose docs should be transformed before being
              included in the other type. e.g. if /x/y/z/concat.txt included /x/compose.html
              then compose.html would be rendered before being concatinated.
            - create a flask api for requesting docs and labels
    """

    @abc.abstractmethod
    def get_concat_doc(self, path:str) -> str:
        pass

    @abc.abstractmethod
    def get_compose_doc(self, path:str) -> str:
        pass

    @abc.abstractmethod
    def get_doc(self, path:str) -> str:
        pass

    @abc.abstractmethod
    def get_labels(self, path:str) -> dict:
        pass



