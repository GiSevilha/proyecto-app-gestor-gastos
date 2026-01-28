from PySide6.QtCore import QDate, Qt, QLocale
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, \
    QDateEdit, QComboBox, QMessageBox, QLabel, QTableWidget, QTableWidgetItem
from gasto import Gasto
from gestor_gastos import GestorDeGastos
from PySide6.QtWidgets import QStackedWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtGui import QActionGroup
from PySide6.QtGui import QIcon


class Interfaz(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("icons/icono.png"))
        self.setWindowTitle("Gestor de Gastos")
        self.setGeometry(300, 200, 500, 500)

        # estilo
        self.setStyleSheet("""
            QWidget {
                font-family: Segoe UI;
                font-size: 11pt;
            }

            QMainWindow {
                background-color: #f5f6fa;
            }

            QPushButton {
                background-color: #4a6cf7;
                color: white;
                border-radius: 6px;
                padding: 8px;
            }

            QPushButton:hover {
                background-color: #3b5bdb;
            }

            QLineEdit, QComboBox, QDateEdit {
                border: 1px solid #dcdde1;
                border-radius: 5px;
                padding: 6px;
                background-color: white;
            }

            QTableWidget {
                background-color: white;
                border: none;
            }

            QHeaderView::section {
                background-color: #f1f2f6;
                padding: 6px;
                border: none;
                font-weight: bold;
            }

            QLabel {
                color: #2f3640;
            }
        """)

        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout(widget_central)

        # crear el menu
        barra_menu=self.menuBar()

        # menu archivo
        menu_archivo = barra_menu.addMenu("Archivo")
        accion_nuevo = menu_archivo.addAction("Nuevo registro")
        accion_salir = menu_archivo.addAction("Salir")

        accion_nuevo.triggered.connect(self.nuevo_registro)
        accion_salir.triggered.connect(self.close)

        # menu ver
        menu_ver = barra_menu.addMenu("Ver")
        grupo_vistas = QActionGroup(self)
        grupo_vistas.setExclusive(True)
        accion_tabla = menu_ver.addAction("Ver tabla de gastos")
        accion_tabla.setCheckable(True)
        accion_grafico = menu_ver.addAction("Gráfico de gastos")
        accion_grafico.setCheckable(True)
        grupo_vistas.addAction(accion_tabla)
        grupo_vistas.addAction(accion_grafico)

        # Vista inicial
        accion_tabla.setChecked(True)
        accion_tabla.triggered.connect(self.mostrar_tabla)
        accion_grafico.triggered.connect(self.mostrar_grafico)

        # menu editar
        menu_editar = barra_menu.addMenu("Editar")
        accion_eliminar = menu_editar.addAction("Eliminar último gasto añadido")
        accion_eliminar.triggered.connect(self.eliminar_ultimo_gasto)

        # menu ayuda
        menu_ayuda = barra_menu.addMenu("Ayuda")
        accion_acerca = menu_ayuda.addAction("Acerca de")
        accion_acerca.triggered.connect(self.mostrar_acerca_de)

        # llamo al método que crea los campos
        self.crear_formulario(layout_principal)

        # Botón para probar que funciona
        btn = QPushButton("Añadir gasto")
        btn.clicked.connect(self.add_gasto)
        layout_principal.addWidget(btn)

        # cambiar la visibilidad entre tabla y gráfico
        self.stacked = QStackedWidget()
        layout_principal.addWidget(self.stacked)

        # tabla
        self.vista_tabla = QWidget()
        layout_tabla = QVBoxLayout(self.vista_tabla)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(
            ["Concepto", "Fecha", "Cantidad (€)", "Categoría"]
        )
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)

        layout_tabla.addWidget(self.tabla)
        self.stacked.addWidget(self.vista_tabla)

        # gráfico
        self.vista_grafico = QWidget()
        layout_grafico = QVBoxLayout(self.vista_grafico)
        self.figura = Figure()
        self.canvas = FigureCanvas(self.figura)
        layout_grafico.addWidget(self.canvas)
        self.stacked.addWidget(self.vista_grafico)

        self.total = QLabel("Total gastado: 0.00 €")
        self.total.setAlignment(Qt.AlignRight)
        layout_principal.addWidget(self.total)

        # llamo al gestor de gastos
        self.gestor = GestorDeGastos()
        self.gestor.cargar_desde_archivo()
        self.actualizar_tabla()
        self.actualizar_total()

    def crear_formulario(self, layout_padre):
        """
        método encargado de recoger los datos
        :return: gasto
        """

        layout_form = QFormLayout()

        # ---campo concepto---
        self.concepto = QLineEdit()
        self.concepto.setPlaceholderText("Ej: Alquiler/Hipoteca")
        layout_form.addRow("Concepto:", self.concepto)

        # ---campo fecha---
        self.fecha=QDateEdit()
        # al hacer True, el campo parecerá un QLineEdit normal, pero al hacer clic abrirá el calendario
        self.fecha.setCalendarPopup(True)
        self.fecha.setDate(QDate.currentDate()) # fecha de hoy por defecto
        self.fecha.setDisplayFormat("dd/MM/yyyy") # formato
        layout_form.addRow("Fecha:", self.fecha)

        # ---campo cantidad (solo float)---
        self.cantidad=QLineEdit()
        self.cantidad.setPlaceholderText("0.00")
        # confirgurar el validador de números
        validador=QDoubleValidator(0.0, 999999.99, 2) # min, max, decimales
        validador.setNotation(QDoubleValidator.StandardNotation)
        validador.setLocale(QLocale(QLocale.English)) # fuerzo punto como decimal en lugar de la coma
        self.cantidad.setValidator(validador)

        def corregir_coma(texto):
            if "," in texto:
                # reemplaza la coma por punto
                posicion_cursor = self.cantidad.cursorPosition()
                nueva_cantidad = texto.replace(",", ".")
                self.cantidad.setText(nueva_cantidad)
                self.cantidad.setCursorPosition(posicion_cursor)

        self.cantidad.textChanged.connect(corregir_coma) # conectar la señal con el método
        layout_form.addRow("Cantidad:", self.cantidad)

        # --- categoria ---
        self.categoria = QComboBox()
        # lista de opciones
        categorias=[
            "Comida", "Transporte", "Ocio", "Suministros",
            "Casa", "Seguros", "Suscripciones",
            "Préstamos", "Otros"
        ]

        # añado las opciones al desplegable
        self.categoria.addItems(categorias)
        layout_form.addRow("Categoría:", self.categoria)

        # Añado este layout al principal
        layout_padre.addLayout(layout_form)

    def procesar_formulario(self):
        # leer datos del formulario
        concepto=self.concepto.text().strip()
        cantidad_texto=self.cantidad.text().strip()
        fecha=self.fecha.date()
        categoria=self.categoria.currentText()

        # validar si no está vacío o si es valido
        if not concepto:
            QMessageBox.warning(self, "Campo vacío", "El concepto no puede estar vacío.")
            return

        if not cantidad_texto:
            QMessageBox.warning(self, "Campo vacío", "La cantidad no puede estar vacía.")
            return

        try:
            cantidad=float(cantidad_texto)
        except ValueError:
            QMessageBox.warning(self, "Cantidad inválida", "La cantidad introducida no es válida.")
            return

        if cantidad <= 0:
            QMessageBox.warning(self,"Cantidad incorrecta", "La cantidad debe ser mayor que 0.")
            return

        # crear el objeto gasto
        gasto = Gasto(
            concepto=concepto,
            cantidad=cantidad,
            fecha=fecha,
            categoria=categoria
        )

        self.concepto.clear()
        self.cantidad.clear()
        self.fecha.setDate(QDate.currentDate())
        self.categoria.setCurrentIndex(0)

        # devuelve el gasto
        return gasto

    def add_gasto(self):
        gasto = self.procesar_formulario()

        if gasto is None:
            return

        self.gestor.agregar_gasto(gasto)
        self.gestor.guardar_gasto()
        self.actualizar_tabla()
        self.actualizar_total()

    def actualizar_total(self):
        total = self.gestor.calcular_total()
        self.total.setText(f"Total gastado: {total:.2f} €")

    def nuevo_registro(self):
        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            "¿Seguro que quieres eliminar todos los gastos?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.No:
            return

        self.gestor._gastos.clear()
        self.gestor.guardar_gasto()

        self.actualizar_tabla()
        self.actualizar_total()

    def eliminar_ultimo_gasto(self):
        if not self.gestor.obtener_gastos():
            QMessageBox.information(
                self,
                "Sin gastos",
                "No hay gastos para eliminar."
            )
            return

        self.gestor._gastos.pop()
        self.gestor.guardar_gasto()

        self.actualizar_tabla()
        self.actualizar_total()

    def mostrar_acerca_de(self):
        QMessageBox.information(
            self,
            "Acerca de",
            "Gestor de Gastos Personales\n\n"
            "Aplicación desarrollada en Python con PySide6.\n"
            "Permite registrar, visualizar y analizar gastos personales.\n\n"
            "Autor: Giovanna S\n"
            "Curso: 2º DAM"
        )

    def mostrar_tabla(self):
        self.stacked.setCurrentWidget(self.vista_tabla)

    def actualizar_tabla(self):
        gastos = self.gestor.obtener_gastos()
        self.tabla.setRowCount(len(gastos))

        for fila, gasto in enumerate(gastos):
            self.tabla.setItem(fila, 0, QTableWidgetItem(gasto.concepto))
            self.tabla.setItem(
                fila, 1,
                QTableWidgetItem(gasto.fecha.toString("dd/MM/yyyy"))
            )
            self.tabla.setItem(
                fila, 2,
                QTableWidgetItem(f"{gasto.cantidad:.2f}")
            )
            self.tabla.setItem(fila, 3, QTableWidgetItem(gasto.categoria))

    def mostrar_grafico(self):
        datos = self.gestor.gastos_por_categoria()

        if not datos:
            QMessageBox.information(
                self,
                "Sin datos",
                "No hay gastos para mostrar en el gráfico."
            )
            return

        self.actualizar_grafico(datos)
        self.stacked.setCurrentWidget(self.vista_grafico)

    def actualizar_grafico(self, datos):
        self.figura.clear()
        ax = self.figura.add_subplot(111)
        ax.pie(datos.values(), labels=datos.keys(), autopct="%1.1f%%")
        ax.set_title("Distribución de gastos")
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication([])
    ventana = Interfaz()
    ventana.show()
    app.exec()
