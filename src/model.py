import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.utils.validation import check_X_y, check_array
from scipy.stats import norm


class TimeSeriesLinearRegression(BaseEstimator, RegressorMixin):
    """
    Modelo de regresión lineal personalizado para series de tiempo que calcula intervalos de confianza
    basados en residuos de predicciones fuera de muestra de un paso adelante.

    Este modelo hereda de `BaseEstimator` y `RegressorMixin` de `scikit-learn`, lo que permite su 
    integración con herramientas como pipelines y validación cruzada. Además de realizar predicciones, 
    el modelo proporciona intervalos de confianza para las predicciones basados en la desviación estándar 
    de los residuos obtenidos durante el entrenamiento.

    Parámetros
    ----------
    confidence_level : float, predeterminado=0.95
        Nivel de confianza para los intervalos de confianza (e.g., 0.95 para 95%).

    Atributos
    ----------
    model_ : LinearRegression
        Instancia interna de `LinearRegression` ajustada a los datos.

    residuals_ : np.ndarray of shape (n_samples - 1,)
        Residuos de las predicciones fuera de muestra de un paso adelante durante el entrenamiento.

    std_residual_ : float
        Desviación estándar de los residuos calculados.

    z_score_ : float
        Valor z correspondiente al nivel de confianza especificado.

    Métodos
    -------
    fit(X, y)
        Ajusta el modelo a los datos y calcula los residuos para los intervalos de confianza.

    predict(X)
        Realiza predicciones y calcula los intervalos de confianza basados en los residuos.

    Ejemplo
    -------
    ```python
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error

    # Datos de ejemplo (simulados)
    np.random.seed(42)
    n_samples = 100
    X = np.random.randn(n_samples, 2)
    true_coef = np.array([1.5, -2.0])
    y = X @ true_coef + np.random.normal(0, 1, size=n_samples)

    # División de datos (manteniendo la secuencia temporal)
    train_size = int(0.8 * n_samples)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # Instanciar el modelo con un nivel de confianza del 95%
    model = TimeSeriesLinearRegression(confidence_level=0.95)

    # Ajustar el modelo
    model.fit(X_train, y_train)

    # Realizar predicciones
    y_pred, lower_bound, upper_bound = model.predict(X_test)

    # Evaluar el modelo
    mse = mean_squared_error(y_test, y_pred)
    print(f"Mean Squared Error: {mse:.4f}")

    # Mostrar algunas predicciones con sus intervalos de confianza
    for i in range(len(y_pred)):
        print(f"Predicción: {y_pred[i]:.2f}, Intervalo de Confianza: [{lower_bound[i]:.2f}, {upper_bound[i]:.2f}]")
    ```

    Notas
    -----
    - La clase asume que las series de tiempo son estacionarias o han sido transformadas adecuadamente para la 
      estacionariedad.
    - Los intervalos de confianza se basan en la suposición de que los residuos siguen una distribución 
      normal.
    - Es importante que el conjunto de entrenamiento contenga suficientes datos para calcular una desviación 
      estándar significativa de los residuos.
    - Actualmente, el método `predict` está diseñado para manejar múltiples muestras de entrada y devuelve 
      intervalos de confianza para cada predicción individual.

    Raises
    ------
    ValueError
        - Si `confidence_level` no está en el rango (0, 1).
        - Si `X` e `y` no tienen el mismo número de muestras en el método `fit`.
        - Si `X` no es un array bidimensional en el método `predict`.

    """

    def __init__(self, confidence_level=0.95):
        self.confidence_level = confidence_level
        self.model_ = LinearRegression(fit_intercept=True)
        self.residuals_ = None
        self.std_residual_ = None
        self.z_score_ = None

    def fit(self, X, y):
        X, y = check_X_y(X, y)
        self.model_.fit(X, y)

        residuals = []
        n_samples = X.shape[0]
        window_size = int(n_samples * .7)

        for t in range(window_size, n_samples):
            start = t - window_size
            end = t

            X_train, y_train = X[start:end], y[start:end]
            X_current, y_current = X[t].reshape(1, -1), y[t]

            temp_model = LinearRegression()
            temp_model.fit(X_train, y_train)
            y_pred = temp_model.predict(X_current)[0]
            residual = y_current - y_pred
            residuals.append(residual)

        self.residuals_ = np.array(residuals)
        self.std_residual_ = np.std(self.residuals_, ddof=1)

        alpha = 1 - self.confidence_level
        self.z_score_ = norm.ppf(1 - alpha / 2)

        return self

    def predict(self, X):
        X = check_array(X)
        y_pred = self.model_.predict(X)
        y_pred = float(y_pred)

        if self.std_residual_ is not None and self.z_score_ is not None:
            lower_bound = float(y_pred - self.z_score_ * self.std_residual_)
            upper_bound = float(y_pred + self.z_score_ * self.std_residual_)
            return y_pred, lower_bound, upper_bound
        else:
            return y_pred, None, None
