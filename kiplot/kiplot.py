"""
Main Kiplot code
"""

import logging
import os

from . import plot_config as PCfg

try:
    import pcbnew
except ImportError:
    logging.error("Failed to import pcbnew Python module."
                  " Do you need to add it to PYTHONPATH?")
    raise


class Plotter(object):
    """
    Main Plotter class - this is what will perform the plotting
    """

    def __init__(self, cfg):
        self.cfg = cfg

    def plot(self, brd_file):
        logging.debug("Starting plot of board {}".format(brd_file))

        board = pcbnew.LoadBoard(brd_file)

        logging.debug("Board loaded")

        for op in self.cfg.outputs:

            logging.debug("Processing output: {}".format(op.name))

            # fresh plot controller
            pc = pcbnew.PLOT_CONTROLLER(board)

            if self._output_is_layer(op):
                self._do_layer_plot(board, pc, op)
            elif self._output_is_drill(op):
                self._do_drill_plot(board, pc, op)
            else:
                raise ValueError("Don't know how to plot type {}"
                                 .format(op.options.type))

            pc.ClosePlot()

    def _output_is_layer(self, output):

        return output.options.type in [PCfg.OutputOptions.GERBER]

    def _output_is_drill(self, output):

        return output.options.type in [PCfg.OutputOptions.EXCELLON]

    def _get_plot_format(self, output):
        """
        Gets the Pcbnew plot format for a given KiPlot output type
        """

        if output.options.type == PCfg.OutputOptions.GERBER:
            return pcbnew.PLOT_FORMAT_GERBER

        raise ValueError("Don't know how to translate plot type: {}"
                         .format(output.options.type))

    def _do_layer_plot(self, board, plot_ctrl, output):

        self._configure_plot_ctrl(plot_ctrl, output)

        layer_cnt = board.GetCopperLayerCount()

        # plot every layer in the output
        for l in output.layers:

            layer = l.layer
            suffix = l.suffix
            desc = l.desc

            # for inner layers, we can now check if the layer exists
            if layer.is_inner:

                if layer.layer < 1 or layer.layer >= layer_cnt - 1:
                    raise ValueError(
                        "Inner layer {} is not valid for this board"
                        .format(layer.layer))

            # Set current layer
            plot_ctrl.SetLayer(layer.layer)

            # Plot single layer to file
            plot_format = self._get_plot_format(output)
            plot_ctrl.OpenPlotfile(suffix, plot_format, desc)
            logging.debug("Plotting layer {} to {}".format(
                            layer.layer, plot_ctrl.GetPlotFileName()))
            plot_ctrl.PlotLayer()

    def _do_drill_plot(self, board, plot_ctrl, output):

        pass

    def _configure_gerber_opts(self, po, output):

        # true if gerber
        po.SetUseGerberAttributes(True)

        assert(output.options.type == PCfg.OutputOptions.GERBER)
        gerb_opts = output.options.type_options

        po.SetSubtractMaskFromSilk(gerb_opts.subtract_mask_from_silk)
        po.SetUseGerberProtelExtensions(gerb_opts.use_protel_extensions)

    def _configure_plot_ctrl(self, plot_ctrl, output):

        logging.debug("Configuring plot controller for output")

        po = plot_ctrl.GetPlotOptions()

        opts = output.options.type_options

        # Set some important plot options:
        po.SetPlotFrameRef(False)
        # Line width for items without one defined
        po.SetLineWidth(opts.line_width)

        po.SetAutoScale(False)  # do not change it
        po.SetScale(1)  # do not change it
        po.SetMirror(False)

        po.SetExcludeEdgeLayer(opts.exclude_edge_layer)
        po.SetPlotPadsOnSilkLayer(not opts.exclude_pads_from_silkscreen)
        po.SetUseAuxOrigin(opts.use_aux_axis_as_origin)

        po.SetUseGerberAttributes(False)

        if output.options.type == PCfg.OutputOptions.GERBER:
            self._configure_gerber_opts(po, output)

        # Disable plot pad holes
        po.SetDrillMarksType(pcbnew.PCB_PLOT_PARAMS.NO_DRILL_SHAPE)
        # Skip plot pad NPTH when possible: when drill size and shape == pad size
        # and shape
        # usually sel to True for copper layers
        po.SetSkipPlotNPTH_Pads(False)

        # outdir is a combination of the config and output
        outdir = os.path.join(self.cfg.outdir, output.outdir)

        logging.debug("Output destination: {}".format(outdir))

        po.SetOutputDirectory(outdir)
