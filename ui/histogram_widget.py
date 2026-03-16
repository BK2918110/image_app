# ui/histogram_widget.py
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class HistogramCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # Create a figure with a white background to match our Light Modern Theme
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#FFFFFF')
        self.axes = fig.add_subplot(111)
        
        # Style the plot for a cleaner, modern look
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['left'].set_color('#D1D5DB')
        self.axes.spines['bottom'].set_color('#D1D5DB')
        self.axes.tick_params(colors='#6B7280')
        self.axes.set_xlabel('Pixel Intensity (0 - 255)', color='#6B7280')
        self.axes.set_ylabel('Pixel Count', color='#6B7280')
        
        super().__init__(fig)

    def plot_histogram(self, hist_data):
        self.axes.clear()
        
        # Redraw styling after clear
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['left'].set_color('#D1D5DB')
        self.axes.spines['bottom'].set_color('#D1D5DB')
        self.axes.tick_params(colors='#6B7280')
        
        # Plot the bar graph
        self.axes.bar(range(256), hist_data, color='#2563EB', width=1.0)
        self.axes.set_xlim([0, 256])
        self.draw()

    def clear_plot(self):
        self.axes.clear()
        self.draw()