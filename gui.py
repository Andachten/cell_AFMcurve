from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import PySimpleGUI as sg

sg.ChangeLookAndFeel('DefaultNoMoreNagging')
from DataYee6 import datapro
import os
from layout import layout_main

dp = datapro()


def PyplotGGPlotSytleSheet():
    import numpy as np

    # Fixing random state for reproducibility
    np.random.seed(19680801)

    fig, axes = plt.subplots(ncols=2, nrows=2)
    ax1, ax2, ax3, ax4 = axes.ravel()

    # scatter plot (Note: `plt.scatter` doesn't use default colors)
    x, y = np.random.normal(size=(2, 200))
    ax1.plot(x, y, 'o')

    # sinusoidal lines with colors from default color cycle
    L = 2 * np.pi
    x = np.linspace(0, L)
    ncolors = len(plt.rcParams['axes.prop_cycle'])
    shift = np.linspace(0, L, ncolors, endpoint=False)
    for s in shift:
        ax2.plot(x, np.sin(x + s), '-')
    ax2.margins(0)

    # bar graphs
    x = np.arange(5)
    y1, y2 = np.random.randint(1, 25, size=(2, 5))
    width = 0.25
    ax3.bar(x, y1, width)
    ax3.bar(x + width, y2, width,
            color=list(plt.rcParams['axes.prop_cycle'])[2]['color'])
    ax3.set_xticks(x + width)
    ax3.set_xticklabels(['a', 'b', 'c', 'd', 'e'])

    # circles with colors from default color cycle
    for i, color in enumerate(plt.rcParams['axes.prop_cycle']):
        xy = np.random.normal(size=2)
        ax4.add_patch(plt.Circle(xy, radius=0.3, color=color['color']))
    ax4.axis('equal')
    ax4.margins(0)
    fig = plt.gcf()  # get the figure to show
    return fig


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def delete_figure_agg(figure_agg):
    figure_agg.get_tk_widget().forget()
    plt.close('all')


def pack_methods(values):
    methods = dict(mark=eval(values['1-1-5']),
                   todir=values['Browse0'],
                   src=values['Browse'],
                   peaknumber=[int(values['1-1-2']), int(values['1-1-3'])],
                   xrange=[float(values['1-2-3']), float(values['1-2-4'])],
                   lp=[float(values['1-2-5']), float(values['1-2-6'])],
                   peakheight=[float(values['1-2-1']), float(values['1-2-2'])],
                   UseModel=values['1-1-6'],
                   modeldir='model.pkl',
                   fittingratio=values['1-2-7'],
                   AIEval=1
                   )
    return methods


def methods_cre():
    window2 = sg.Window('DataYee', layout_main(sg), default_element_size=(30, 5), resizable=True, finalize=True)
    while True:
        event, values = window2.read()
        if event == sg.WIN_CLOSED or event == 'Cancel' or event == 'Cancel0':
            return {0: 0}
            break
        if event == 'Export methods':
            try:
                window2.close()
                return eval(values['MLINE_KEY'])
            except:
                window2.close()
                return pack_methods(values)
            else:
                pass
        if event == 'Refresh':
            window2['MLINE_KEY'].update(pack_methods(values))
    window2.close()


menu_def = [['File', ['Open Project', 'Save Project', 'Exit']],
            ['Methods', ['Create Methods', 'Import Methods', 'Save Methods', 'Run'], ],
            ['Help', 'About...'], ]
figure_w, figure_h = 400, 500
# define the form layout
listbox_values = []
col_listbox = [
    [sg.Text('Current Methods:', font='Any 18')],
    [sg.Multiline('None', size=(27, 5), key='-MethodsML-', font='ANY 15')],
    [sg.Text('Peak.', font='Any 15'), sg.InputText('', size=(4, 1), key='-SELECT-', font='Any 18'),
     sg.Button('Delete', font='Any 15'), sg.Button('Reset', font='Any 15')],
    [sg.Button(u'⬅', size=(4, 1), font='Any 15'), sg.InputText('0', size=(3, 1), key='-INDEX-', font='Any 18'),
     sg.Text('/0', key='-COUNT-', size=(4, 1), font='Any 18'), sg.Button('➡', size=(4, 1), font='Any 15'),
     sg.Button('Goto', size=(4, 1), font='Any 15')]
]

col_multiline = sg.Col([[sg.MLine(size=(70, 35), key='-MULTILINE-')]])
col_canvas = sg.Col([[sg.Canvas(size=(figure_w, figure_h), key='-CANVAS-')]])
col_instructions = sg.Col([[sg.Pane([col_canvas, col_multiline], size=(700, 500))],
                           [sg.Text('Grab square above and slide upwards to view source code for graph')]])

layout = [[sg.Menu(menu_def, font=('ANY 15'))],
          [sg.Text('AFM Sigle Molecular Force Spectrum', font=('ANY 18'))],
          [sg.Col(col_listbox, justification='t'), col_instructions], ]

# create the form and show it without the plot
window = sg.Window('DataYEE6',
                   layout, resizable=True, finalize=True)

canvas_elem = window['-CANVAS-']
multiline_elem = window['-MULTILINE-']
figure_agg = None
Mthds = str(dp.log['methods'])
while True:
    window['-MethodsML-'].update(Mthds)
    dp.log['methods'] = eval(Mthds)
    if 'site' not in dir() and 'length' not in dir():
        fig = PyplotGGPlotSytleSheet()
        figure_agg = draw_figure(
            window['-CANVAS-'].TKCanvas, fig)

    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break

    if figure_agg:
        # ** IMPORTANT ** Clean up previous drawing before drawing again
        delete_figure_agg(figure_agg)
    if event == 'Open Project':
        filename = sg.popup_get_file('file to open', no_window=True)
        if filename.endswith('.pkl'):
            dp.load(filename)
            listbox_values = list(dp.log['result']['keep'])
            length = len(listbox_values)
            Mthds = str(dp.log['methods'])
            site = 0
            window['-INDEX-'].update('{}'.format(site + 1))
            window['-COUNT-'].update('/{}'.format(length))
        else:
            continue
    if event == 'Save Project':
        filename = sg.popup_get_text('FileName')
        cur_dir = dp.log['methods']['todir']
        if not os.path.exists(cur_dir) and cur_dir != '':
            os.makedirs(cur_dir)
        if type(filename) is str and filename.endswith('.pkl') and 'dp' in dir():
            dp.save(os.path.join(cur_dir, filename))
        else:
            sg.popup('File Name Wrong!')
    if event == 'Create Methods':
        methods = methods_cre()
        dp.log['methods'] = methods
        Mthds = str(methods)
        if Mthds == 'None':
            Mthds = str({0: 0})

    if event == 'Import Methods':
        filename = sg.popup_get_file('file to open', no_window=True)
        try:
            dp.load_methods(filename)
        except:
            sg.popup('File Name Wrong!')
        Mthds = str(dp.log['methods'])
    if event == 'Save Methods':
        filename = sg.popup_get_text('FileName')
        cur_dir = dp.log['methods']['todir']
        if not os.path.exists(cur_dir) and cur_dir != '':
            os.makedirs(cur_dir)
        if type(filename) is str and filename.endswith('.methods') and 'dp' in dir():
            dp.save_methods(os.path.join(cur_dir, filename))
        else:
            sg.popup('File Name Wrong!')
    if event == 'Run':
        '''
        dp.GetFileName()
        count = len(dp.filename_lst)
        layout_pro = [[sg.Text('Progress meter')],
          [sg.ProgressBar(count, orientation='h', size=(20, 20), key='progbar')],
          [sg.Cancel()]]
        window_pro = sg.Window('Progress Meter', layout_pro)
        for i,_ in dp.main():
            event_pro, _ = window_pro.read(timeout=0)
            if event_pro == 'Cancel' or event_pro == sg.WIN_CLOSED:
                break
            window_pro['progbar'].update_bar(i + 1)
        window_pro.close()
        listbox_values=list(dp.log['result']['keep'])
        length = len(listbox_values)
        Mthds = str(dp.log['methods'])
        site = 0
        window['-INDEX-'].update('{}'.format(site+1))
        window['-COUNT-'].update('/{}'.format(length))
        '''
        try:
            dp.GetFileName()
            count = len(dp.filename_lst)
            layout_pro = [[sg.Text('Progress meter')],
                          [sg.ProgressBar(count, orientation='h', size=(20, 20), key='progbar')],
                          [sg.Cancel()]]
            window_pro = sg.Window('Progress Meter', layout_pro)
            for i, _ in dp.main():
                event_pro, _ = window_pro.read(timeout=0)
                if event_pro == 'Cancel' or event_pro == sg.WIN_CLOSED:
                    break
                window_pro['progbar'].update_bar(i + 1)
            window_pro.close()
            listbox_values = list(dp.log['result']['keep'])
            length = len(listbox_values)
            Mthds = str(dp.log['methods'])
            site = 0
            window['-INDEX-'].update('{}'.format(site + 1))
            window['-COUNT-'].update('/{}'.format(length))
        except Exception as err:
            window_pro.close()
            sg.popup(err)

    if event == u'⬅' and 'length' in dir() and len(listbox_values) != 0:
        if site > 0:
            site = site - 1
        else:
            site = 0
        window['-INDEX-'].update('{}'.format(site + 1))
    if event == u'➡' and 'length' in dir() and len(listbox_values) != 0:
        if site < length - 1:
            site = site + 1
        else:
            site = length - 1
        window['-INDEX-'].update('{}'.format(site + 1))
    if event == 'Goto':
        site_ = int(values['-INDEX-'])
        if 'length' in dir() and site_ > 0 and site_ <= length:
            site = site_ - 1
            window['-INDEX-'].update('{}'.format(site + 1))
    if event == 'Reset' and 'site' in dir() and 'length' in dir():
        dp.reset(site)
    if event == 'Delete' and 'site' in dir() and 'length' in dir():
        dp.cur_convert_False(site, values['-SELECT-'])
    if 'site' in dir() and 'length' in dir() and site >= 0 and site < length:
        fig = dp.graph_(site)  # call function to get the figure
        figure_agg = draw_figure(
            window['-CANVAS-'].TKCanvas, fig)  # draw the figure
        ms = dp.extract_info(site)
        window['-MULTILINE-'].update(ms)
if 'site' in dir() and 'length' in dir():
    del site, length
window.close()
