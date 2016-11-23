from collections import Sized
import IPython.display as ipydisplay
import ipywidgets
import numpy as np
from menpowidgets.style import map_styles_to_hex_colours
from menpowidgets.options import (AnimationOptionsWidget, TextPrintWidget,
                                  SaveMayaviFigureOptionsWidget)
from menpowidgets.tools import LogoWidget
from menpo.shape import ColouredTriMesh
from menpo.transform import AlignmentSimilarity

from .options import NICPResultWidget


def visualize_used_points(template, w_i_n, colour=(0.2, 0.8, 0.3)):
    colours = np.ones_like(template.points)
    colours[w_i_n, 0] = colour[0]
    colours[w_i_n, 1] = colour[1]
    colours[w_i_n, 2] = colour[2]
    return ColouredTriMesh(template.points, trilist=template.trilist,
                           colours=colours)


def view_landmark_displacement(source, target, renderer, group=None):
    from menpo3d.visualize.viewmayavi import MayaviVectorViewer3d
    source_lms = source.landmarks[group].lms
    target_lms = target.landmarks[group].lms

    # Align the source landmarks to the target as is done in the start of NICP
    source_lms = AlignmentSimilarity(source_lms,
                                     target_lms).apply(source_lms)

    source_lms.view(new_figure=False, marker_colour=(1, 1, 0))
    target_lms.view(new_figure=False, marker_colour=(1, 0, 0.5))

    points = source_lms.points
    diff = target_lms.points - source_lms.points
    MayaviVectorViewer3d(figure_id=renderer.figure, new_figure=False,
                         points=points, vectors=diff)


def deformation_visualization(current_instance, initial_instance, aligned_mesh,
                              renderer, group=None, mask=None):
    if mask is None:
        mask = np.ones(current_instance.n_points, dtype=np.bool)

    colour = (0.2, 0.8, 0.3)
    colours = np.ones_like(current_instance.points)
    colours[mask] = colour
    current_instance = ColouredTriMesh(current_instance.points,
                                       trilist=current_instance.trilist,
                                       colours=colours)
    r = current_instance.view(new_figure=False, figure_id=renderer.figure)
    view_landmark_displacement(initial_instance, aligned_mesh,
                               renderer, group=group)

    # return the colouredtrimesh actor (we need to clear it!)
    return r._actors[0]


def view_vector_distance(points, diff, figure=None, mask=None):
    from mayavi import mlab
    figure.scene.background = (0, 0, 0)
    if mask is not None:
        points = points[mask]
        diff = diff[mask]
    mlab.quiver3d(points[:, 0], points[:, 1], points[:, 2],
                  diff[:, 0], diff[:, 1], diff[:, 2], figure=figure)


def view_vector_deformation(points, deformation, figure=None, mask=None):
    from mayavi import mlab
    figure.scene.background = (0, 0, 0)
    if mask is not None:
        points = points[mask]
        deformation = deformation[mask]
    mlab.quiver3d(points[:, 0], points[:, 1], points[:, 2],
                  deformation[:, 0], deformation[:, 1], deformation[:, 2],
                  figure=figure)


def visualize_nicp(nicp_results, source, target, group=None, style='coloured',
                   browser_style='buttons'):
    # Ensure that the code is being run inside a Jupyter kernel!
    from menpowidgets.utils import verify_ipython_and_kernel
    verify_ipython_and_kernel()
    print('Initializing...')

    # Make sure that images is a list even with one image member
    if not isinstance(nicp_results, Sized):
        nicp_results = [nicp_results]

    # Get the number of results
    n_results = len(nicp_results)

    # Define the styling options
    if style == 'coloured':
        logo_style = 'info'
        widget_box_style = 'info'
        widget_border_radius = 10
        widget_border_width = 1
        animation_style = 'info'
        renderer_style = 'warning'
        save_figure_style = 'danger'
        info_style = 'info'
    else:
        logo_style = 'minimal'
        widget_box_style = ''
        widget_border_radius = 0
        widget_border_width = 0
        animation_style = 'minimal'
        renderer_style = 'minimal'
        save_figure_style = 'minimal'
        info_style = 'minimal'

    # Define render function
    def render_function(_):
        # Clear figure
        save_figure_wid.renderer.clear_figure()

        if hasattr(save_figure_wid, '__actor'):
            # manually clear the colourtrimesh for now!
            save_figure_wid.renderer.figure.scene.remove_actors(save_figure_wid.__actor)
            del save_figure_wid.__actor
        # Render instance
        id_ = result_number_wid.selected_values if n_results > 1 else 0

        # Get options
        render_options = nicp_opts_wid.selected_values

        mesh, info = nicp_results[id_]
        mask = None

        masks = [info[v] for v in render_options['mask']]

        mask = None
        if len(masks) == 1:
            mask = masks[0]
        elif len(masks) > 1:
            mask = np.logical_and(*masks)

        if render_options['mode'] == 'surface':
            actor = deformation_visualization(mesh, source, target,
                                              save_figure_wid.renderer,
                                              group=group, mask=mask)
            save_figure_wid.__actor = actor
        elif render_options['mode'] == 'distance_vec':
            view_vector_distance(mesh.points,
                                 info['nearest_points'] -
                                 mesh.points,
                                 mask=mask,
                                 figure=save_figure_wid.renderer.figure)
        elif render_options['mode'] == 'deformation_per_iter':
            view_vector_deformation(mesh.points,
                                    info['deformation_per_step'],
                                    mask=mask,
                                    figure=save_figure_wid.renderer.figure)

        update_info(info)

        save_figure_wid.renderer.force_draw()

    # Define function that updates the info text
    def update_info(info):
        text_per_line = [
            "> Stiffness Weight: {}".format(info['alpha']),
            "> Landmark Weight: {}".format(info['beta']),
            "> Omitted {:.2%}".format(info['prop_omitted']),
            "> Normal Error: {:.2%}".format(info['prop_omitted_norms'])
        ]
        info_wid.set_widget_state(text_per_line=text_per_line)

    # Group widgets
    info_wid = TextPrintWidget(text_per_line=[''] * 6, style=info_style)
    save_figure_wid = SaveMayaviFigureOptionsWidget(renderer=None,
                                                    style=save_figure_style)
    nicp_opts_wid = NICPResultWidget(render_function=render_function,
                                     style=renderer_style)

    if n_results > 1:
        # Result selection slider
        index = {'min': 0, 'max': n_results - 1, 'step': 1, 'index': 0}
        result_number_wid = AnimationOptionsWidget(
            index, render_function=render_function, index_style=browser_style,
            interval=0.5, description='NICP:', loop_enabled=True,
            continuous_update=False, style=animation_style)

        # Header widget
        header_wid = ipywidgets.HBox(
            children=[LogoWidget(style=logo_style), result_number_wid],
            align='start')
    else:
        # Header widget
        header_wid = LogoWidget(style=logo_style)

    options_box = ipywidgets.Tab(children=[info_wid, nicp_opts_wid,
                                           save_figure_wid])
    tab_titles = ['Info', 'Renderer', 'Export']
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    wid = ipywidgets.VBox(children=[header_wid, options_box], align='start')
    wid.margin = '0.2cm'

    # Set widget's style
    wid.box_style = widget_box_style
    wid.border_radius = widget_border_radius
    wid.border_width = widget_border_width
    wid.border_color = map_styles_to_hex_colours(widget_box_style)

    # Display final widget
    ipydisplay.display(wid)

    # Trigger initial visualization
    render_function({})
