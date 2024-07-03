# SPDX-License-Identifier: Apache-2.0
from collections import namedtuple
from docutils.parsers.rst import Directive, directives
from docutils import nodes


class blueconfig_value(nodes.Element):
    pass


class BlueConfigValue(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'type': directives.unchanged,
                   'required': directives.unchanged,
                   'unit': directives.unchanged,
                   'description': directives.unchanged,
                   }

    def run(self):
        resultnode = blueconfig_value()
        self.options['key'] = self.arguments[0]
        resultnode.options = self.options
        return [resultnode]


BlueConfigSectionInfo = namedtuple('BlueConfigSectionInfo',
                                   'name, description, docname, targetid')


class blueconfig_section(nodes.General, nodes.Element):
    pass


class BlueConfigSection(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'description': directives.unchanged,
                   }

    def _make_table(self, rows):
        def create_table_row(row_cells):
            row = nodes.row()
            for cell in row_cells:
                row += nodes.entry('', nodes.paragraph(text=cell))
            return row

        header = ('Key', 'Description', 'Type', 'Required', 'Unit', )
        colwidths = (2, 3, 1, 1, 1)

        assert len(header) == len(colwidths)
        tgroup = nodes.tgroup(cols=len(header))
        for c in colwidths:
            tgroup += nodes.colspec(colwidth=c)
        tgroup += nodes.thead('', create_table_row(header))
        tbody = nodes.tbody()
        tgroup += tbody
        for row in rows:
            tbody += create_table_row((row.options['key'],
                                       row.options['description'],
                                       row.options['type'],
                                       row.options['required'],
                                       row.options['unit']))

        table = nodes.table('', tgroup)
        return table

    def run(self):
        env = self.state.document.settings.env
        if not hasattr(env, 'all_blueconfig_sections'):
            env.all_blueconfig_sections = []

        name = self.arguments[0]
        description = self.options['description']
        targetid = "blueconfigsection-%d" % env.new_serialno('blueconfig_section')

        node = nodes.Element()
        self.state.nested_parse(self.content, self.content_offset, node)

        section_info = BlueConfigSectionInfo(name, description, env.docname, targetid)
        env.all_blueconfig_sections.append(section_info)

        children = []
        for child in node:
            if isinstance(child, blueconfig_value):
                children.append(child)

        resultnode = nodes.section(ids=[targetid])
        resultnode += [nodes.title(text=name),
                       nodes.paragraph(text=description),
                       self._make_table(children),
                       ]

        return [resultnode]


class blueconfig_section_index(nodes.Element):
    pass


class BlueConfigSectionIndex(Directive):
    '''create a place-holder for an index'''

    def run(self):
        return [blueconfig_section_index('')]


def process_blueconfig_section_index(app, doctree, fromdocname):
    env = app.builder.env

    for node in doctree.traverse(blueconfig_section_index):
        references = []
        for section in env.all_blueconfig_sections:
            ref = nodes.reference(section.name, section.name)
            ref['refdocname'] = section.docname
            ref['refuri'] = app.builder.get_relative_uri(
                fromdocname, section.docname) + '#' + section.targetid

            para = nodes.paragraph('', '', ref)
            item = nodes.list_item('', para, nodes.paragraph(text=section.description))
            references.append(item)

        content = nodes.bullet_list('', *references)
        node.replace_self(content)


def setup(app):
    app.add_node(blueconfig_section_index)
    app.add_directive('blueconfig_section_index', BlueConfigSectionIndex)

    app.add_node(blueconfig_section)
    app.add_directive('blueconfig_section', BlueConfigSection)
    app.add_config_value('blueconfig_section', {}, 'env')

    app.add_node(blueconfig_value)
    app.add_directive('blueconfig_value', BlueConfigValue)

    app.connect('doctree-resolved', process_blueconfig_section_index)
