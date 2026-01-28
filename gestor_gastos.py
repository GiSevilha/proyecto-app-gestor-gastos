import json
import os
from gasto import Gasto
from PySide6.QtCore import QDate

class GestorDeGastos:
    def __init__(self):
        self._gastos = []

    def agregar_gasto(self, gasto):
        self._gastos.append(gasto)

    def obtener_gastos(self):
        return list(self._gastos)

    def calcular_total(self):
        return sum(gasto.cantidad for gasto in self._gastos)

    def gastos_por_categoria(self):
        resumen = {}
        for gasto in self._gastos:
            categoria = gasto.categoria
            resumen[categoria] = resumen.get(categoria, 0) + gasto.cantidad
        return resumen

    def convertir_gasto_diccionario(self, gasto):
        return {
            "concepto": gasto.concepto,
            "cantidad": gasto.cantidad,
            "categoria": gasto.categoria,
            "fecha": gasto.fecha.toString("yyyy-MM-dd")
        }

    def guardar_gasto(self, ruta="gastos.json"):
        datos = [self.convertir_gasto_diccionario(gasto) for gasto in self._gastos]

        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

    def cargar_desde_archivo(self, ruta="gastos.json"):

        # comprobar si existe
        if not os.path.exists(ruta):
            self._gastos = []
            return

        # si el archivo está vacío, no intento cargar el json
        if os.path.getsize(ruta) == 0:
            self._gastos=[]
            return

        # abrir y leer el archivo
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except json.JSONDecodeError:
            self._gastos=[]
            return

        # reconstruir los objetos gasto
        self._gastos=[]
        for dato in datos:
            gasto = Gasto(
                concepto=dato["concepto"],
                cantidad=dato["cantidad"],
                categoria=dato["categoria"],
                fecha=QDate.fromString(dato["fecha"], "yyyy-MM-dd"))

            self._gastos.append(gasto)

