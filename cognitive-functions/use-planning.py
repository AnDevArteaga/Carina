from planning import PRGenerator
if __name__ == "__main__":
    planificador = PRGenerator(
        nivel_usuario="intermedio",
        estilo_aprendizaje="visual",
        problemas_detectados=["ansiedad matemática", "dificultad en razonamiento abstracto"],
        objetivos=["Mejorar la confianza al resolver ecuaciones", "Aplicar álgebra a situaciones reales", "Reducir la ansiedad ante problemas complejos"],
        duracion_semanas=4
    )

    pr_json = planificador.exportar_plan(formato='json')
    print(pr_json)

    # Para imprimir en texto plano:
    # pr_txt = planificador.exportar_plan(formato='txt')
    # print(pr_txt)
