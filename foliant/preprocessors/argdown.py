'''
Argdown diagrams preprocessor for Foliant documenation authoring tool.
'''

import re

from hashlib import md5
from pathlib import Path
from pathlib import PosixPath
from subprocess import CalledProcessError
from subprocess import PIPE
from subprocess import STDOUT
from subprocess import run

from foliant.contrib.combined_options import CombinedOptions
from foliant.contrib.combined_options import Options
from foliant.preprocessors.utils.preprocessor_ext import BasePreprocessorExt
from foliant.preprocessors.utils.preprocessor_ext import allow_fail


class Preprocessor(BasePreprocessorExt):
    defaults = {
        'cache_dir': '.diagramscache/argdown',
        'as_image': True,
        'converter_path': 'argdown',
        'format': 'png',
        'params': {},
        'fix_svg_size': False,
    }
    tags = ('argdown',)
    embeddable = ('svg', 'dot', 'graphml')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = Options(self.options,
                              defaults=self.defaults)

        self._cache_path = self.project_path / self.config['cache_dir']

        self.logger = self.logger.getChild('argdown')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    def _get_command(self,
                     options: CombinedOptions,
                     diagram_src_path: PosixPath,
                     diagram_path: PosixPath) -> str:
        '''Construct the image generation command.

        :param options: a CombinedOptions object with tag and config options
        :param diagram_src_path: Path to the diagram source file
        :param diagram_src_path: Path to the diagram output file

        :returns: Complete image generation command
        '''

        components = [options['converter_path'] + ' map']
        components.append(f'--format {options["format"]}')

        for param_name, param_value in options['params'].items():
            if param_value is True:
                components.append(f'--{param_name}')
            else:
                components.append(f'--{param_name}="{param_value}"')

        components.append(f'{diagram_src_path} {self._cache_path}')

        return ' '.join(components)

    def _get_result(self, diagram_path: PosixPath, config: CombinedOptions):
        '''Get either image ref or raw image code depending on as_image option'''
        if config['format'] in self.embeddable and not config['as_image']:
            with open(diagram_path, 'r') as f:
                source = f.read()
                return f'<div>{source}</div>' if config['format'] == 'svg' else source
        else:
            return f'![{config.get("caption", "")}]({diagram_path.absolute().as_posix()})'

    def _fix_svg_size(self, svg_path: PosixPath):
        '''insert 100% instead of hardcoded height and width attributes'''

        self.logger.debug(f'Fixing svg size for {svg_path}')

        p_width = r'(<svg .*?width=").+?(")'
        p_height = r'(<svg .*?height=").+?(")'

        with open(svg_path, encoding='utf8') as f:
            content = f.read()

        result = re.sub(p_width, r'\g<1>100%\g<2>', content)
        result = re.sub(p_height, r'\g<1>100%\g<2>', result)

        with open(svg_path, 'w', encoding='utf8') as f:
            f.write(result)

    @allow_fail('Error while processing argdown tag.')
    def _process_diagrams(self, block) -> str:
        '''
        Process argdown tag.
        Save Argdown diagram body to .argdown file, generate an image from it,
        and return the image ref.

        If the image for this diagram has already been generated, the existing version
        is used.

        :returns: Image ref
        '''
        tag_options = self.get_options(block.group('options'))
        options = CombinedOptions({'config': self.options,
                                   'tag': tag_options},
                                  priority='tag')
        body = block.group('body')

        self.logger.debug(f'Processing Argdown diagram, options: {options}, body: {body}')

        body_hash = md5(f'{body}'.encode())
        body_hash.update(str(options.options).encode())

        diagram_src_path = self._cache_path / f'{body_hash.hexdigest()}.argdown'

        self.logger.debug(f'Diagram definition file path: {diagram_src_path}')

        diagram_path = diagram_src_path.with_suffix(f'.{options["format"]}')

        self.logger.debug(f'Diagram image path: {diagram_path}')

        if diagram_path.exists():
            self.logger.debug('Diagram image found in cache')

            return self._get_result(diagram_path, options)

        diagram_src_path.parent.mkdir(parents=True, exist_ok=True)

        with open(diagram_src_path, 'w', encoding='utf8') as diagram_src_file:
            diagram_src_file.write(body)

            self.logger.debug(f'Diagram definition written into the file')

        command = self._get_command(options, diagram_src_path, diagram_path)
        self.logger.debug(f'Constructed command: {command}')
        result = run(command, shell=True, stdout=PIPE, stderr=PIPE)
        if result.returncode == 0:
            self.logger.debug(f'Diagram image saved')

            if options['format'] == 'svg' and options['fix_svg_size']:
                self._fix_svg_size(diagram_path)

            return self._get_result(diagram_path, options)
        else:
            self._warning(f'Processing of Argdown diagram failed.',
                          context=self.get_tag_context(block),
                          debug_msg=result.stderr.decode())
            return block.group(0)

    def apply(self):
        self._process_tags_for_all_files(self._process_diagrams)
        self.logger.info('Preprocessor applied')
