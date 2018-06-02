"""
Class to read KiPlot config files
"""

import logging
import yaml
import os
import re

import pcbnew

from . import plot_config as PC
from . import error


class CfgReader(object):

    def __init__(self):
        pass


class YamlError(error.KiPlotError):
    pass


class CfgYamlReader(CfgReader):

    def __init__(self):
        super(CfgYamlReader, self).__init__()

    def _check_version(self, data):

        try:
            version = data['kiplot']['version']
        except KeyError:
            raise YamlError("YAML config needs kiplot.version.")
            return None

        if version != 1:
            raise YamlError("Unknown KiPlot config version: {}"
                            .format(version))
            return None

        return version

    def _get_required(self, data, key):

        try:
            val = data[key]
        except KeyError:
            raise YamlError("Value is needed for {}".format(key))

        return val

    def _parse_drill_map(self, map_opts):

        mo = PC.DrillMapOptions()

        TYPES = {
            'hpgl': pcbnew.PLOT_FORMAT_HPGL,
            'ps': pcbnew.PLOT_FORMAT_POST,
            'gerber': pcbnew.PLOT_FORMAT_GERBER,
            'dxf': pcbnew.PLOT_FORMAT_DXF,
            'svg': pcbnew.PLOT_FORMAT_SVG,
            'pdf': pcbnew.PLOT_FORMAT_PDF
        }

        type_s = self._get_required(map_opts, 'type')

        try:
            mo.type = TYPES[type_s]
        except KeyError:
            raise YamlError("Unknown drill map type: {}".format(type_s))

        return mo

    def _parse_drill_report(self, report_opts):

        opts = PC.DrillReportOptions()

        opts.filename = self._get_required(report_opts, 'filename')

        return opts

    def _perform_config_mapping(self, otype, cfg_options, mapping_list, 
                                target):
        """
        Map a config dict onto a target object given a mapping list
        """

        for map_type in mapping_list:

            # if this output type matches the mapping specification:
            if otype in map_type['types']:

                # for each mapping:
                for key, mapping in map_type['options'].items():

                    # set the internal option as needed
                    if mapping['required'](cfg_options):

                        cfg_val = self._get_required(cfg_options, key)
                    elif key in cfg_options:
                        # not required but given anyway
                        cfg_val = cfg_options[key]
                    else:
                        continue

                    # transform the value if needed
                    if 'transform' in mapping:
                        cfg_val = mapping['transform'](cfg_val)

                    setattr(target, mapping['to'], cfg_val)

    def _parse_out_opts(self, otype, options):

        # mappings from YAML keys to type_option keys
        MAPPINGS = [
            {
                # Options for a general layer type
                'types': ['gerber'],
                'options': {
                    'exclude_edge_layer': {
                        'to': 'exclude_edge_layer',
                        'required': lambda opts: True,
                    },
                    'exclude_pads_from_silkscreen': {
                        'to': 'exclude_pads_from_silkscreen',
                        'required': lambda opts: True,
                    },
                    'use_aux_axis_as_origin': {
                        'to': 'use_aux_axis_as_origin',
                        'required': lambda opts: True,
                    },
                    'line_width': {
                        'to': 'line_width',
                        'required': lambda opts: True,
                    },
                },
            },
            {
                # Gerber only
                'types': ['gerber'],
                'options': {
                    'subtract_mask_from_silk': {
                        'to': 'subtract_mask_from_silk',
                        'required': lambda opts: True,
                    },
                    'use_protel_extensions': {
                        'to': 'use_protel_extensions',
                        'required': lambda opts: True,
                    },
                },
            },
            {
                # Drill files
                'types': ['excellon'],
                'options': {
                    'use_aux_axis_as_origin': {
                        'to': 'use_aux_axis_as_origin',
                        'required': lambda opts: True,
                    },
                    'map': {
                        'to': 'map_options',
                        'required': lambda opts: False,
                        'transform': self._parse_drill_map
                    },
                    'report': {
                        'to': 'report_options',
                        'required': lambda opts: False,
                        'transform': self._parse_drill_report
                    },
                },
            },
            {
                # Excellon drill files
                'types': ['excellon'],
                'options': {
                    'metric_units': {
                        'to': 'metric_units',
                        'required': lambda opts: True,
                    },
                    'pth_and_npth_single_file': {
                        'to': 'pth_and_npth_single_file',
                        'required': lambda opts: True,
                    },
                    'minimal_header': {
                        'to': 'minimal_header',
                        'required': lambda opts: True,
                    },
                    'mirror_y_axis': {
                        'to': 'mirror_y_axis',
                        'required': lambda opts: True,
                    },
                },
            },
        ]

        po = PC.OutputOptions(otype)

        # options that apply to the specific output type
        to = po.type_options

        self._perform_config_mapping(otype, options, MAPPINGS, to)

        print to, to.__dict__
        return po

    def _get_layer_from_str(self, s):
        """
        Get the pcbnew layer from a string in the config
        """

        D = {
            'F.Cu': pcbnew.F_Cu,
            'B.Cu': pcbnew.B_Cu,
            'F.Adhes': pcbnew.F_Adhes,
            'B.Adhes': pcbnew.B_Adhes,
            'F.Paste': pcbnew.F_Paste,
            'B.Paste': pcbnew.B_Paste,
            'F.SilkS': pcbnew.F_SilkS,
            'B.SilkS': pcbnew.B_SilkS,
            'F.Mask': pcbnew.F_Mask,
            'B.Mask': pcbnew.B_Mask,
            'Dwgs.User': pcbnew.Dwgs_User,
            'Cmts.User': pcbnew.Cmts_User,
            'Eco1.User': pcbnew.Eco1_User,
            'Eco2.User': pcbnew.Eco2_User,
            'Edge.Cuts': pcbnew.Edge_Cuts,
            'Margin': pcbnew.Margin,
            'F.CrtYd': pcbnew.F_CrtYd,
            'B.CrtYd': pcbnew.B_CrtYd,
            'F.Fab': pcbnew.F_Fab,
            'B.Fab': pcbnew.B_Fab,
        }

        layer = None

        if s in D:
            layer = PC.LayerInfo(D[s], False)
        elif s.startswith("Inner"):
            m = re.match(r"^Inner\.([0-9]+)$", s)

            if not m:
                raise YamlError("Malformed inner layer name: {}"
                                .format(s))

            layer = PC.LayerInfo(int(m.group(1)), True)
        else:
            raise YamlError("Unknown layer name: {}".format(s))

        return layer

    def _parse_layer(self, l_obj):

        l_str = self._get_required(l_obj, 'layer')
        layer_id = self._get_layer_from_str(l_str)
        layer = PC.LayerConfig(layer_id)

        layer.desc = l_obj['description'] if 'description' in l_obj else None
        layer.suffix = l_obj['suffix'] if 'suffix' in l_obj else ""

        return layer

    def _parse_output(self, o_obj):

        try:
            name = o_obj['name']
        except KeyError:
            raise self.YamlError("Output needs a name")

        try:
            desc = o_obj['description']
        except KeyError:
            desc = None

        try:
            otype = o_obj['type']
        except KeyError:
            raise YamlError("Output needs a type")

        if otype not in ['gerber', 'excellon']:
            raise YamlError("Unknown output type: {}".format(otype))

        try:
            options = o_obj['options']
        except KeyError:
            raise YamlError("Output need to have options specified")

        outdir = self._get_required(o_obj, 'dir')

        output_opts = self._parse_out_opts(otype, options)

        o_cfg = PC.PlotOutput(name, desc, otype, output_opts)
        o_cfg.outdir = outdir

        try:
            layers = o_obj['layers']
        except KeyError:
            layers = []

        for l in layers:
            o_cfg.layers.append(self._parse_layer(l))

        return o_cfg

    def read(self, fstream):
        """
        Read a file object into a config object

        :param fstream: file stream of a config YAML file
        """

        try:
            data = yaml.load(fstream)
        except yaml.YAMLError as e:
            raise YamlError("Error loading YAML")
            return None

        self._check_version(data)

        try:
            outdir = data['options']['basedir']
        except KeyError:
            outdir = ""

        cfg = PC.PlotConfig()

        for o in data['outputs']:

            op_cfg = self._parse_output(o)
            cfg.add_output(op_cfg)

        return cfg
