import unittest
import os
from PySide6.QtCore import QDate
from gestor_gastos import GestorDeGastos
from gasto import Gasto


class TestGestorDeGastos(unittest.TestCase):

    def setUp(self):
        """Se ejecuta antes de cada test"""
        self.gestor = GestorDeGastos()

    def test_agregar_gasto(self):
        gasto = Gasto(
            concepto="Comida",
            cantidad=10.0,
            fecha=QDate.currentDate(),
            categoria="Comida"
        )

        self.gestor.agregar_gasto(gasto)

        self.assertEqual(len(self.gestor.obtener_gastos()), 1)

    def test_calcular_total(self):
        gasto1 = Gasto("Comida", 10.0, QDate.currentDate(), "Comida")
        gasto2 = Gasto("Ocio", 20.0, QDate.currentDate(), "Ocio")

        self.gestor.agregar_gasto(gasto1)
        self.gestor.agregar_gasto(gasto2)

        total = self.gestor.calcular_total()
        self.assertEqual(total, 30.0)

    def test_guardar_y_cargar_gastos(self):
        ruta = "test_gastos.json"

        gasto = Gasto(
            concepto="Transporte",
            cantidad=15.0,
            fecha=QDate.currentDate(),
            categoria="Transporte"
        )

        self.gestor.agregar_gasto(gasto)
        self.gestor.guardar_gasto(ruta)

        nuevo_gestor = GestorDeGastos()
        nuevo_gestor.cargar_desde_archivo(ruta)

        self.assertEqual(len(nuevo_gestor.obtener_gastos()), 1)
        self.assertEqual(nuevo_gestor.obtener_gastos()[0].concepto, "Transporte")

        # Limpiar archivo de test
        if os.path.exists(ruta):
            os.remove(ruta)


if __name__ == "__main__":
    unittest.main()