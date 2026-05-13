#!/usr/bin/env python

''' Openoffice odt wrapper objects
'''

import time
import yaml
from pathlib import Path
from odf import opendocument

from helper.config_service import ConfigService
from helper.logger import *
from odt.odt_util import *


def load_default_specs(nesting_level=0):
    default_spec_dir = Path(__file__).resolve().parents[2] / 'misc'
    specs = {}

    for spec_file in ['page-specs.yml', 'font-specs.yml', 'style-specs.yml']:
        spec_path = default_spec_dir / spec_file
        if spec_path.exists():
            specs.update(yaml.safe_load(open(spec_path, 'r', encoding='utf-8')) or {})
        else:
            warn(f"default spec file [{spec_path}] not found", nesting_level=nesting_level)

    return specs

class OdtHelper(object):

    ''' constructor
    '''
    def __init__(self, spec_list, nesting_level=0):
        self._odt = opendocument.load(ConfigService()._odt_template)
        spec_list = spec_list or {}
        default_specs = load_default_specs(nesting_level=nesting_level+1)

        # specs to config
        ConfigService()._page_specs = spec_list.get('page-spec') or default_specs.get('page-spec', {})
        ConfigService()._margin_specs = spec_list.get('margin-spec') or default_specs.get('margin-spec', {})
        ConfigService()._font_specs = spec_list.get('font-spec') or default_specs.get('font-spec', {})
        ConfigService()._style_specs = {}
        for style_key, style_spec in (spec_list.get('style-spec') or default_specs.get('style-spec', {})).items():
            transfomed_style_spec = transform_nested_dict(data=style_spec, mapping_schema=STYLE_TRANSFORMATION_MAP, nesting_level=nesting_level+1)
            ConfigService()._style_specs[style_key] = transfomed_style_spec
        


    ''' generate and save the odt
    '''
    def generate_and_save(self, section_list, nesting_level=0):
        self.start_time = int(round(time.time() * 1000))
        info(msg=f"generating odt ..", nesting_level=nesting_level)

        # font specs
        trace(f"registering fonts from conf/font-spec.yml", nesting_level=nesting_level+1)
        for k, v in ConfigService()._font_specs.items():
            if k != 'default':
                register_font(odt=self._odt, font_name=k, font_spec=v, nesting_level=nesting_level+2)

        # override styles
        trace(f"processing custom styles from conf/style-specs.yml", nesting_level=nesting_level+1)
        for k, v in ConfigService()._style_specs.items():
            update_style(odt=self._odt, style_key=k, style_spec=v, custom_styles=ConfigService()._style_specs, nesting_level=nesting_level+2)
        
        # process the sections
        section_list_to_odt(odt=self._odt, section_list=section_list, nesting_level=nesting_level+1)

        self.end_time = int(round(time.time() * 1000))
        info(msg=f"generated  odt .. {(self.end_time - self.start_time)/1000} seconds", nesting_level=nesting_level)

        # save the odt document
        output_odt_path = ConfigService()._output_odt_path
        info(msg=f"saving odt .. {output_odt_path}", nesting_level=nesting_level)
        self.start_time = int(round(time.time() * 1000))
        self._odt.save(output_odt_path)
        self.end_time = int(round(time.time() * 1000))
        info(msg=f"saved  odt .. {(self.end_time - self.start_time)/1000} seconds", nesting_level=nesting_level)

        # update indexes
        info(msg=f"updating index .. {output_odt_path}", nesting_level=nesting_level)
        self.start_time = int(round(time.time() * 1000))
        update_indexes(self._odt, output_odt_path, nesting_level=nesting_level+1)
        self.end_time = int(round(time.time() * 1000))
        info(msg=f"updated  index .. {(self.end_time - self.start_time)/1000} seconds", nesting_level=nesting_level)
