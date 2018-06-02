
import pcbnew


class LayerOptions(object):
    """
    Common options that all layer outputs have
    """
    def __init__(self):
        self._line_width = None
        self.exclude_edge_layer = False
        self.exclude_pads_from_silkscreen = False

    @property
    def line_width(self):
        return self._line_width

    @line_width.setter
    def line_width(self, value):
        """
        Set the line width, in mm
        """
        self._line_width = pcbnew.FromMM(value)


class GerberOptions(LayerOptions):

    def __init__(self):

        super(GerberOptions, self).__init__()

        self.subtract_mask_from_silk = False
        self.use_protel_extensions = False


class DrillOptions(object):

    def __init__(self):
        self.map_options = None
        self.report_options = None

    @property
    def generate_map(self):
        return self.map_options is not None

    @property
    def generate_report(self):
        return self.report_options is not None


class ExcellonOptions(DrillOptions):

    def __init__(self):

        super(ExcellonOptions, self).__init__()

        self.metric_units = True
        self.minimal_header = False
        self.mirror_y_axis = False


class DrillReportOptions(object):

    def __init__(self):
        self.filename = None


class DrillMapOptions(object):

    def __init__(self):
        self.type = None


class OutputOptions(object):

    GERBER = 'gerber'
    EXCELLON = 'excellon'

    def __init__(self, otype):
        self.type = otype

        if otype == self.GERBER:
            self.type_options = GerberOptions()
        elif otype == self.EXCELLON:
            self.type_options = ExcellonOptions()
        else:
            self.type_options = None


class LayerInfo(object):

    def __init__(self, layer, is_inner):

        self.layer = layer
        self.is_inner = is_inner


class LayerConfig(object):

    def __init__(self, layer):

        # the Pcbnew layer
        self.layer = layer
        self.suffix = ""
        self.desc = "desc"


class PlotOutput(object):

    def __init__(self, name, description, otype, options):
        self.name = name
        self.description = description
        self.outdir = None
        self.options = options

        self.layers = []


class PlotConfig(object):

    def __init__(self):

        self._outputs = []
        self.outdir = None

    def add_output(self, new_op):
        self._outputs.append(new_op)

    @property
    def outputs(self):
        return self._outputs
