from traitlets import Dict
import ipywidgets

from menpowidgets.abstract import MenpoWidget
from menpowidgets.style import (format_box, format_font,
                                map_styles_to_hex_colours)


class NICPResultWidget(MenpoWidget):
    def __init__(self, render_function=None, style='minimal'):
        # Set default options
        default_options = {'mask': ('mask_normals', 'mask_edges'),
                           'mode': 'surface'}

        # Create widgets
        self.mask_wid = ipywidgets.SelectMultiple(options={
            'Normals': 'mask_normals',
            'Edges': 'mask_edges'
        })
        self.mask_wid.value = default_options['mask']
        self.mask_wid.height = '2cm'
        self.mask_wid.width = '3cm'
        self.mode_wid = ipywidgets.RadioButtons(options={
            'Surface Representation': 'surface',
            'Distance Vectors': 'distance_vec',
            'Deformation Vectors': 'deformation_per_iter'
        })
        self.mode_wid.value = default_options['mode']

        # Group widgets
        children = [self.mask_wid, self.mode_wid]
        super(NICPResultWidget, self).__init__(
            children, Dict, default_options,
            render_function=render_function, orientation='horizontal',
            align='start')

        # Set values
        self.add_callbacks()

        # Set style
        self.predefined_style(style)

    def _save_options(self, change):
        self.selected_values = {
            'mask': self.mask_wid.value,
            'mode': self.mode_wid.value}

    def add_callbacks(self):
        r"""
        Function that adds the handler callback functions in all the widget
        components, which are necessary for the internal functionality.
        """
        self.mask_wid.observe(self._save_options, names='value',
                              type='change')
        self.mode_wid.observe(self._save_options, names='value', type='change')

    def remove_callbacks(self):
        r"""
        Function that removes all the internal handler callback functions.
        """
        self.mask_wid.unobserve(self._save_options, names='value',
                                type='change')
        self.mode_wid.unobserve(self._save_options, names='value',
                                type='change')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Possible widget style options::

                'success', 'info', 'warning', 'danger', '', None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : `str` (see below), optional
            The font family to be used. Example options::

                'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                'helvetica'

        font_size : `int`, optional
            The font size.
        font_style : `str` (see below), optional
            The font style. Example options::

                'normal', 'italic', 'oblique'

        font_weight : See Below, optional
            The font weight. Example options::

                'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                'extra bold', 'black'
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.mask_wid, font_family, font_size, font_style,
                    font_weight)
        format_font(self.mode_wid, font_family, font_size, font_style, font_weight)


    def predefined_style(self, style):
        r"""
        Function that sets a predefined style on the widget.

        Parameters
        ----------
        style : `str` (see below)
            Style options:

                ============= ============================
                Style         Description
                ============= ============================
                ``'minimal'`` Simple black and white style
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ============================
        """
        if style == 'minimal':
            self.style(box_style=None, border_visible=True,
                       border_colour='black', border_style='solid',
                       border_width=1, border_radius=0, padding='0.2cm',
                       margin='0.3cm', font_family='', font_size=None,
                       font_style='', font_weight='')
        elif (style == 'info' or style == 'success' or style == 'danger' or
                      style == 'warning'):
            self.style(box_style=style, border_visible=True,
                       border_colour=map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding='0.2cm', margin='0.3cm', font_family='',
                       font_size=None, font_style='', font_weight='')
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')
