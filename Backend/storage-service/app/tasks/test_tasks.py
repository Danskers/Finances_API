
from app.celery_app import celery_app


@celery_app.task
def sumar(a, b):
    resultado = a + b

    print(f"Resultado de la tarea: {resultado}")

    return resultado
