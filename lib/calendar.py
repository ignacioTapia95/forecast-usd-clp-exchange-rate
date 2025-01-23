import pandas_market_calendars as mcal
from datetime import timedelta


def get_market_calendar(
    market: str,
    date_interval: list[str, str]
):
    """
    Obtiene el calendario de días hábiles para un mercado específico dentro de un intervalo de fechas.

    La función utiliza el calendario del mercado proporcionado por el módulo `mcal` para generar una 
    lista de fechas hábiles dentro del rango especificado. Adicionalmente, incrementa cada fecha en un 
    día para ajustar el calendario según necesidades específicas.

    Parámetros
    ----------
    market : str
        Identificador del mercado financiero para el cual se desea obtener el calendario. 
        Debe ser compatible con los calendarios disponibles en el módulo `mcal`.

    date_interval : list[str, str]
        Lista que contiene dos cadenas de caracteres representando las fechas de inicio y fin 
        del intervalo en formato 'YYYY-MM-DD'. La primera posición debe ser la fecha de inicio 
        y la segunda la fecha de fin.

    Retorna
    -------
    list[datetime.datetime]
        Lista de objetos `datetime` que representan los días hábiles del mercado especificado 
        dentro del intervalo de fechas proporcionado, cada uno incrementado en un día.

    Raises
    ------
    ValueError
        - Si `date_interval` no contiene exactamente dos elementos.
        - Si las fechas proporcionadas no están en el formato correcto o son inválidas.
        - Si el identificador de `market` no corresponde a ningún calendario disponible en `mcal`.

    Notas
    -----
    - La función depende del módulo `mcal`, que debe estar previamente importado y configurado.
      Asegúrate de que `mcal` está correctamente instalado y contiene el calendario para el 
      `market` especificado.
    - La frecuencia utilizada para la generación del rango de fechas es diaria ("1D").
    - El incremento de un día a cada fecha puede ajustarse según las necesidades específicas 
      del análisis o modelado.
    - Es importante verificar que el intervalo de fechas proporcionado contenga al menos tres 
      fechas hábiles para evitar posibles errores en análisis posteriores que requieran 
      múltiples fechas.

    Ejemplo
    -------
    ```python
    import pandas as pd
    from datetime import datetime, timedelta
    import mcal  # Asegúrate de que el módulo `mcal` está instalado y configurado

    # Definir el intervalo de fechas
    intervalo = ['2023-01-01', '2023-01-10']

    # Obtener el calendario para el mercado 'NYSE'
    calendario_nyse = get_market_calendar('NYSE', intervalo)

    print(calendario_nyse)
    # Salida esperada (ejemplo):
    # [
    #     datetime.datetime(2023, 1, 2, 0, 0),
    #     datetime.datetime(2023, 1, 3, 0, 0),
    #     datetime.datetime(2023, 1, 4, 0, 0),
    #     datetime.datetime(2023, 1, 5, 0, 0),
    #     datetime.datetime(2023, 1, 6, 0, 0),
    #     datetime.datetime(2023, 1, 9, 0, 0),
    #     datetime.datetime(2023, 1, 10, 0, 0)
    # ]
    ```

    En este ejemplo:
    - Se define un intervalo de fechas del 1 de enero de 2023 al 10 de enero de 2023.
    - Se obtiene el calendario de días hábiles para el mercado 'NYSE' dentro de ese intervalo.
    - Cada fecha en el calendario resultante ha sido incrementada en un día según la lógica de la función.

    """
    calendar = mcal.get_calendar(market)
    calendar = calendar.date_range_htf(
        start=date_interval[0], end=date_interval[1], frequency="1D")

    calendar = [date + timedelta(days=1) for date in calendar]
    return calendar
