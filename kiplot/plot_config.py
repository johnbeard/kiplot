
import pcbnew

from . import error


class KiPlotConfigurationError(error.KiPlotError):
    pass


class LayerOptions(object):
    """
    Common options that all layer outputs have
    """

    AUTO_SCALE = 0

    def __init__(self):

        self.exclude_edge_layer = False
        self.exclude_pads_from_silkscreen = False
        self.plot_sheet_reference = False

        self._supports_line_width = False
        self._line_width = None

        self._supports_aux_axis_origin = False
        self._use_aux_axis_as_origin = False

        # override for scalable formats
        self._supports_scaling = False

        self._auto_scale = False
        self._scaling = 1

        self._supports_mirror = False
        self._mirror_plot = False

        self._supports_negative = False
        self._negative_plot = False

        self._supports_drill_marks = False
        self._drill_marks = pcbnew.PCB_PLOT_PARAMS.NO_DRILL_SHAPE

    @property
    def line_width(self):
        return self._line_width

    @line_width.setter
    def line_width(self, value):
        """
        Set the line width, in mm
        """
        if self._supports_line_width:
            self._line_width = pcbnew.FromMM(value)
            print("Set LW %d" % self._line_width)
        else:
            raise KiPlotConfigurationError(
                    "This output doesn't support setting line width")

    @property
    def auto_scale(self):
        return self._auto_scale

    @property
    def scaling(self):
        return self._scaling

    @scaling.setter
    def scaling(self, val):
        """
        Set scaling, if possible. AUTO_SCALE to set auto scaling
        """

        if self._supports_scaling:

            if val == self.AUTO_SCALE:
                self._scaling = 1
                self._auto_scale = True
            else:
                self._scaling = val
                self._auto_scale = False
        else:
            raise KiPlotConfigurationError(
                   "This Layer output does not support scaling")

    @property
    def mirror_plot(self):
        return self._mirror_plot

    @mirror_plot.setter
    def mirror_plot(self, val):

        if self._supports_mirror:
            self._mirror_plot = val
        else:
            raise KiPlotConfigurationError(
                   "This Layer output does not support mirror plotting")

    @property
    def negative_plot(self):
        return self._mirror_plot

    @negative_plot.setter
    def negative_plot(self, val):

        if self._supports_mirror:
            self._mirror_plot = val
        else:
            raise KiPlotConfigurationError(
                   "This Layer output does not support negative plotting")

    @property
    def drill_marks(self):
        return self._drill_marks

    @drill_marks.setter
    def drill_marks(self, val):

        if self._supports_drill_marks:

            try:
                drill_mark = {
                    'none': pcbnew.PCB_PLOT_PARAMS.NO_DRILL_SHAPE,
                    'small': pcbnew.PCB_PLOT_PARAMS.SMALL_DRILL_SHAPE,
                    'full': pcbnew.PCB_PLOT_PARAMS.FULL_DRILL_SHAPE,
                }[val]
            except KeyError:
                raise KiPlotConfigurationError(
                        "Unknown drill mark type: {}".format(val))

            self._drill_marks = drill_mark
        else:
            raise KiPlotConfigurationError(
                   "This Layer output does not support drill marks")

    @property
    def use_aux_axis_as_origin(self):
        return self._use_aux_axis_as_origin

    @use_aux_axis_as_origin.setter
    def use_aux_axis_as_origin(self, val):

        if self._supports_aux_axis_origin:
            self._use_aux_axis_as_origin = val
        else:
            raise KiPlotConfigurationError(
                   "This Layer output does not support using the auxiliary"
                   " axis as the origin")


class GerberOptions(LayerOptions):

    def __init__(self):

        super(GerberOptions, self).__init__()

        self._supports_line_width = True
        self._supports_aux_axis_origin = True

        self.subtract_mask_from_silk = False
        self.use_protel_extensions = False
        self.create_gerber_job_file = False

        # either 5 or 6
        self._gerber_precision = None

    @property
    def gerber_precision(self):
        return self._gerber_precision

    @gerber_precision.setter
    def gerber_precision(self, val):
        """
        Set gerber precision: either 4.5 or 4.6
        """
        if val == 4.5:
            self._gerber_precision = 5
        elif val == 4.6:
            self._gerber_precision = 6
        else:
            raise KiPlotConfigurationError(
                    "Bad Gerber precision : {}".format(val))


class HpglOptions(LayerOptions):

    def __init__(self):

        super(HpglOptions, self).__init__()

        self._pen_width = None

    @property
    def pen_width(self):
        return self._pen_width

    @pen_width.setter
    def pen_width(self, pw_mm):
        self._pen_width = pcbnew.FromMM(pw_mm)


class PsOptions(LayerOptions):

    def __init__(self):

        super(PsOptions, self).__init__()

        self._supports_mirror = True
        self._supports_negative = True
        self._supports_scaling = True
        self._supports_drill_marks = True
        self._supports_line_width = True

        self.scale_adjust_x = 1.0
        self.scale_adjust_y = 1.0

        self._width_adjust = 0

    @property
    def width_adjust(self):
        return self._width_adjust

    @width_adjust.setter
    def width_adjust(self, width_adjust_mm):
        self._width_adjust = pcbnew.FromMM(width_adjust_mm)


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
    POSTSCRIPT = 'ps'
    EXCELLON = 'excellon'

    def __init__(self, otype):
        self.type = otype

        if otype == self.GERBER:
            self.type_options = GerberOptions()
        elif otype == self.POSTSCRIPT:
            self.type_options = PsOptions()
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
