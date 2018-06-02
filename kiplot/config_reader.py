"""
Class to read KiPlot config files
"""

import logging
import yaml
import os
import re

import pcbnew

from . import plot_config as PC


class CfgReader(object):

    def __init__(self):
        pass


class CfgYamlReader(CfgReader):

    class YamlError(Exception):
        pass

    def __init__(self):
        super(CfgYamlReader, self).__init__()

    def _check_version(self, data):

        try:
            version = data['kiplot']['version']
        except KeyError:
            raise self.YamlError("YAML config needs kiplot.version.")
            return None

        if version != 1:
            raise self.YamlError("Unknown KiPlot config version: {}"
                                 .format(version))
            return None

        return version

    def _get_required(self, data, key):

        try:
            val = data[key]
        except KeyError:
            raise self.YamlError("Value is needed for {}".format(key))

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
            raise self.YamlError("Unknown drill map type: {}".format(type_s))

        return mo

    def _parse_drill_report(self, report_opts):

        opts = PC.DrillReportOptions()

        opts.filename = self._get_required(report_opts, 'filename')

        return opts

    def _parse_out_opts(self, otype, options):

        po = PC.OutputOptions(otype)

        # options that apply to the specific output type
        to = po.type_options

        # common options - layer outputs
        if otype in ['gerber']:
            to.line_width = self._get_required(options, 'line_width')

            to.exclude_edge_layer = self._get_required(
                options, 'exclude_edge_layer')
            to.exclude_pads_from_silkscreen = self._get_required(
                options, 'exclude_pads_from_silkscreen')
            to.use_aux_axis_as_origin = self._get_required(
                options, 'use_aux_axis_as_origin')

        # common options - drill outputs
        if otype in ['excellon']:
            to.use_aux_axis_as_origin = self._get_required(
                options, 'use_aux_axis_as_origin')

            to.generate_map = 'map' in options
            to.generate_report = 'report' in options

            if to.generate_map:
                to.map_options = self._parse_drill_map(options['map'])

            if to.generate_map:
                to.report_options = self._parse_drill_report(options['report'])

        # set type-specific options
        if otype == 'gerber':
            to.subtract_mask_from_silk = self._get_required(
                options, 'subtract_mask_from_silk')
            to.use_protel_extensions = self._get_required(
                options, 'use_protel_extensions')

        if otype == 'excellon':
            to.metric_units = self._get_required(
                options, 'metric_units')
            to.mirror_y_axis = self._get_required(
                options, 'mirror_y_axis')
            to.minimal_header = self._get_required(
                options, 'minimal_header')
            to.pth_and_npth_single_file = self._get_required(
                options, 'pth_and_npth_single_file')

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
                raise self.YamlError("Malformed inner layer name: {}"
                                     .format(s))

            layer = PC.LayerInfo(int(m.group(1)), True)
        else:
            raise self.YamlError("Unknown layer name: {}".format(s))

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
            raise self.YamlError("Output needs a type")

        if otype not in ['gerber', 'excellon']:
            raise self.YamlError("Unknown output type: {}".format(otype))

        try:
            options = o_obj['options']
        except KeyError:
            raise self.YamlError("Output need to have options specified")

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
            raise self.YamlError("Error loading YAML")
            return None

        self._check_version(data)

        try:
            outdir = data['options']['basedir']
        except KeyError:
            outdir = ""

        # relative to CWD (absolute path overrides)
        outdir = os.path.join(os.getcwd(), outdir)

        cfg = PC.PlotConfig()

        cfg.outdir = outdir

        for o in data['outputs']:

            op_cfg = self._parse_output(o)
            cfg.add_output(op_cfg)

        return cfg
