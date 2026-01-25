from PySide6.QtWidgets import QMainWindow, QApplication


class Interfaz(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor de Gastos")
        self.setGeometry(300, 200, 100, 100)


if __name__ == "__main__":
    app = QApplication([])
    ventana = Interfaz()
    ventana.show()
    app.exec()