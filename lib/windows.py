import pandas as pd


def get_train_test_index(
        df: pd.DataFrame,
        ratio: float,
        method: str,
        steps_ahead: int = 1
) -> list[tuple[list[int], list[int]]]:
    """
    Genera pares de índices (train, test) para ventanas rodantes o expansivas 
    con un horizonte de predicción definido por `steps_ahead`.

    Parámetros:
    - df: DataFrame de pandas con la serie temporal.
    - ratio: proporción del total de datos que se usa como ventana inicial.
    - method: 'rolling' para ventana rodante o 'expanding' para ventana expansiva.
    - steps_ahead: horizonte de predicción en pasos.

    Retorna:
    - Una lista de tuplas (train_indices, test_indices), donde cada tupla corresponde
      a un conjunto de entrenamiento y los índices del conjunto de prueba.
    """
    indexes = []
    n = df.shape[0]

    init_size = int(n * ratio)

    for i in range(init_size, n - steps_ahead + 1):
        if method == "rolling":
            train_indices = list(range(i - init_size, i))
        elif method == "expanding":
            train_indices = list(range(0, i))
        else:
            raise ValueError("Invalid method. Use 'rolling' or 'expanding'")

        test_indices = list(range(i, i + steps_ahead))

        indexes.append((train_indices, test_indices))

    return indexes
