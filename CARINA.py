# CARINA o5

# la implementación sigue la lógica del Algoritmo 1 del documento, pero adaptada para Python y la arquitectura CARINA. El algoritmo en el documento describe una técnica de control metanivel con predicción de rendimiento en línea, donde:

# Se inicializa el tiempo y la historia de rendimiento (t ← 0, h ← [ ]).

# El algoritmo inicia la ejecución (A.Start()).

# Se monitorea periódicamente el rendimiento (while A.Running()).

# Se obtiene la calidad de la solución actual (q ← α.Quality()).

# Se actualiza el historial de rendimiento (h ← h ∪ q).

# Se proyecta el rendimiento futuro (p = Φ(h)).

# Se evalúa la condición de parada (if C(p) then A.Stop()).

# Se ejecuta el siguiente ciclo (t ← t + ∆t, Sleep(∆t)).

# Adaptaciones en el código ✔ Se ejecuta en paralelo (threading), permitiendo que anytime_planning genere el plan mientras stop_reasoning monitorea el razonamiento. ✔ La historia de rendimiento (performance_history) se usa para predecir la calidad futura, en lugar de un perfil precompilado. ✔ La condición de parada (stop_reasoning) sigue la comparación entre utilidad actual y proyectada, como en el documento. ✔ Se introduce una penalización del tiempo exponencial, alineando mejor el criterio de interrupción del razonamiento.

import time
import threading
import numpy as np

class SharedMemory:
    """Espacio de memoria compartida entre Object Level y Meta Level."""

    def __init__(self):
        self.memory = {}  # Almacén de datos cognitivos

    def update(self, key, value):
        """Actualiza un valor en la memoria compartida."""
        self.memory[key] = value

    def read(self, key):
        """Lee un valor de la memoria compartida."""
        return self.memory.get(key, None)

class ObjectLevel:
    """Nivel Cognitivo - Ejecuta funciones cognitivas y mantiene el modelo del mundo."""

    def __init__(self, shared_memory):
        self.shared_memory = shared_memory  # Acceso a memoria compartida
        self.current_plan = []
        self.running = True
        self.start_time = time.time()

    def performance_predictor(self):
        """Predice el rendimiento futuro basado en el historial."""
        history = self.shared_memory.read("performance_history")
        if history is None or len(history) < 2:
            return np.inf

        x = np.arange(len(history))
        y = np.array(history)

        coef = np.polyfit(x, np.log(y + 1), 1)
        predicted_next_quality = np.exp(coef[0] * (len(x) + 1) + coef[1]) - 1

        return predicted_next_quality

    def anytime_planning(self, goal):
        """Ejecuta planificación incremental mientras el razonamiento está activo."""
        while self.running:
            elapsed_time = time.time() - self.start_time
            new_step = f"Step {len(self.current_plan) + 1} towards {goal}"
            self.current_plan.append(new_step)

            self.shared_memory.update("performance_history", [len(self.current_plan)])
            self.shared_memory.update("current_quality", len(self.current_plan))

            time.sleep(0.5)

class MetaLevel:
    """Nivel Metacognitivo - Supervisa y controla el Object Level a través de model_of_the_self."""

    def __init__(self, shared_memory):
        self.shared_memory = shared_memory  # Acceso a memoria compartida
        self.model_of_the_self = {}

    def calculate_utility(self, quality, time_elapsed):
        """Calcula la utilidad penalizando el tiempo, asegurando valores numéricos."""
        intrinsic_value = float(quality)  # Convertir calidad a número
        time_cost = np.exp(time_elapsed * 0.05)  # Penalización exponencial
        return intrinsic_value - time_cost

    def update_model_of_the_self(self):
        """Actualiza el modelo interno con los valores del Object Level."""
        self.model_of_the_self["performance_history"] = self.shared_memory.read("performance_history")
        self.model_of_the_self["current_quality"] = self.shared_memory.read("current_quality")

    def stop_reasoning(self):
        """Detiene el razonamiento si la utilidad proyectada no mejora."""
        while True:
            time.sleep(1)
            self.update_model_of_the_self()

            elapsed_time = time.time() - self.shared_memory.read("start_time")
            predicted_quality = float(self.model_of_the_self.get("performance_history", [0])[-1])

            # Asegurar que los valores sean numéricos
            current_quality = float(self.model_of_the_self["current_quality"])
            predicted_quality = float(predicted_quality)

            utility_now = self.calculate_utility(current_quality, elapsed_time)
            utility_future = self.calculate_utility(predicted_quality, elapsed_time + 1)

            print(f"Utilidad actual: {utility_now}, Utilidad proyectada: {utility_future}")

            if utility_future <= utility_now:
                print("Stop Reasoning: La utilidad proyectada no mejora, deteniendo planificación.")
                self.shared_memory.update("goal", "stop")
                break


class CARINA:
    """Arquitectura Cognitiva con separación de Object Level y Meta Level."""

    def __init__(self):
        self.shared_memory = SharedMemory()
        self.shared_memory.update("start_time", time.time())

        self.object_level = ObjectLevel(self.shared_memory)
        self.meta_level = MetaLevel(self.shared_memory)

    def execute(self, goal):
        """Ejecuta planificación cognitiva y supervisión metacognitiva en paralelo."""
        self.shared_memory.update("goal", goal)

        planning_thread = threading.Thread(target=self.object_level.anytime_planning, args=(goal,))
        monitoring_thread = threading.Thread(target=self.meta_level.stop_reasoning)

        planning_thread.start()
        monitoring_thread.start()

        planning_thread.join()
        monitoring_thread.join()

        return self.shared_memory.read("performance_history")



class IntelligentTutoringSystem:
    def __init__(self):
        self.mind = CARINA()  # Instanciar la arquitectura CARINA

    def execute(self, goal):
        learning_plan = self.mind.execute(goal)
        return learning_plan

# Instanciación y ejecución del agente CARINA
tutor = IntelligentTutoringSystem()
goal = "Aprender inteligencia artificial"
learning_plan = tutor.execute(goal)
print(f"Plan final: {learning_plan}")