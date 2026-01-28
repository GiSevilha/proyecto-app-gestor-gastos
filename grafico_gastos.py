from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class VentanaGrafico(QWidget):
    def __init__(self, datos, titulo):
        super().__init__()
        self.setWindowTitle(titulo)
        self.resize(400, 400)

        layout = QVBoxLayout(self)

        figura = Figure()
        canvas = FigureCanvas(figura)
        layout.addWidget(canvas)

        ax = figura.add_subplot(111)

        if datos:
            ax.pie(datos.values(), labels=datos.keys(), autopct="%1.1f%%")
        else:
            ax.text(0.5, 0.5, "No hay datos", ha="center", va="center")

        canvas.draw()