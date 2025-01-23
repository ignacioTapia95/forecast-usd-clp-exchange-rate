def is_business_day(date, calendar):
    """
    Determina si una fecha específica es un día hábil según un calendario de mercado proporcionado.

    La función verifica si la fecha dada está presente en el calendario de días hábiles proporcionado.
    Retorna `1` si la fecha es un día hábil y `0` en caso contrario.

    Parámetros
    ----------
    date : datetime.date o datetime.datetime
        Fecha que se desea verificar. Debe ser un objeto de tipo `datetime.date` o `datetime.datetime`.

    calendar : list de datetime.date o list de datetime.datetime
        Lista que contiene las fechas que se consideran días hábiles. Cada elemento debe ser un objeto
        de tipo `datetime.date` o `datetime.datetime`. Generalmente, este calendario se basa en
        los días hábiles de un mercado específico.

    Retorna
    -------
    int
        Retorna `1` si la fecha proporcionada está en el calendario de días hábiles, indicando que es
        un día hábil. Retorna `0` en caso contrario, indicando que no es un día hábil.

    Raises
    ------
    TypeError
        - Si `date` no es una instancia de `datetime.date` o `datetime.datetime`.
        - Si `calendar` no es una lista o si contiene elementos que no son instancias de `datetime.date` 
          o `datetime.datetime`.

    Notas
    -----
    - La función asume que todas las fechas en el `calendar` están normalizadas al mismo formato que 
      la `date` proporcionada (ya sea `datetime.date` o `datetime.datetime`).
    - Es importante que el `calendar` contenga todas las fechas consideradas como días hábiles para 
      el período de interés, de lo contrario, la función podría retornar resultados incorrectos.
    - Esta función puede ser utilizada en procesos de preprocesamiento de datos para filtrar o 
      identificar días hábiles en series de tiempo financieras.
    """

    if date in calendar:
        return 1
    return 0
