from datetime import datetime
import random
import json

class PRGenerator:
    def __init__(self, nivel_usuario, estilo_aprendizaje, problemas_detectados, objetivos, duracion_semanas):
        self.nivel_usuario = nivel_usuario
        self.estilo_aprendizaje = estilo_aprendizaje
        self.problemas_detectados = problemas_detectados
        self.objetivos = objetivos
        self.duracion_semanas = duracion_semanas
        self.fecha_generacion = datetime.now().strftime("%Y-%m-%d")

    def diagnostico(self):
        resumen = f"Usuario con nivel {self.nivel_usuario} y estilo de aprendizaje {self.estilo_aprendizaje}.\n"
        if self.problemas_detectados:
            resumen += "Se detectaron las siguientes dificultades cognitivas/emocionales:\n"
            for p in self.problemas_detectados:
                resumen += f" - {p}\n"
        else:
            resumen += "No se reportan dificultades cognitivas significativas.\n"
        return resumen

    def definir_estrategias(self):
        estrategias = []

        if "ansiedad matemática" in self.problemas_detectados:
            estrategias.append("Terapia breve enfocada en desensibilización emocional y ejercicios de respiración antes de actividades algebraicas.")
        
        if "dificultad en razonamiento abstracto" in self.problemas_detectados:
            estrategias.append("Uso de representaciones visuales y manipulables para mejorar el pensamiento simbólico.")

        if self.estilo_aprendizaje == "visual":
            estrategias.append("Uso intensivo de mapas conceptuales, videos, esquemas y animaciones para introducir problemas.")
        elif self.estilo_aprendizaje == "auditivo":
            estrategias.append("Audios explicativos, discusiones guiadas y narración de problemas en voz alta.")
        elif self.estilo_aprendizaje == "kinestésico":
            estrategias.append("Resolución de problemas mediante simulaciones, juegos interactivos y dramatización matemática.")

        estrategias.append("Seguimiento semanal por parte de un tutor con feedback personalizado.")
        estrategias.append("Evaluaciones formativas automatizadas basadas en IA.")
        
        return estrategias

    def generar_actividades(self):
        base_actividades = [
            "Resolver sistemas de ecuaciones aplicados a la vida cotidiana.",
            "Crear y representar gráficamente funciones lineales y cuadráticas.",
            "Simular situaciones reales con variables y restricciones algebraicas.",
            "Gamificación: juegos matemáticos para resolver acertijos algebraicos.",
            "Proyectos: diseñar un presupuesto familiar usando ecuaciones.",
            "IA simbólica: resolver problemas con ayuda de un asistente basado en reglas."
        ]
        random.shuffle(base_actividades)
        return base_actividades[:self.duracion_semanas]

    def generar_plan(self):
        return {
            "fecha_generacion": self.fecha_generacion,
            "diagnostico": self.diagnostico(),
            "objetivos_personalizados": self.objetivos,
            "estrategias_intervencion": self.definir_estrategias(),
            "actividades_por_semana": self.generar_actividades(),
            "duracion_plan": f"{self.duracion_semanas} semanas"
        }

    def exportar_plan(self, formato='json'):
        plan = self.generar_plan()
        if formato == 'json':
            return json.dumps(plan, indent=4, ensure_ascii=False)
        elif formato == 'txt':
            texto = f"PLAN DE RECOMENDACIÓN - Pensamiento Algebraico\nGenerado el: {plan['fecha_generacion']}\n\n"
            texto += f"Diagnóstico:\n{plan['diagnostico']}\n"
            texto += f"Objetivos:\n" + "\n".join(f" - {o}" for o in plan["objetivos_personalizados"]) + "\n"
            texto += "Estrategias de intervención:\n" + "\n".join(f" - {e}" for e in plan["estrategias_intervencion"]) + "\n"
            texto += "Actividades por semana:\n" + "\n".join(f"Semana {i+1}: {a}" for i, a in enumerate(plan["actividades_por_semana"])) + "\n"
            texto += f"Duración estimada del plan: {plan['duracion_plan']}"
            return texto
        else:
            raise ValueError("Formato no soportado. Usa 'json' o 'txt'.")
