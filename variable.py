class Variable:
    """
    Clase que representa una variable con atributos iniciales, tamaño, dirección y palabra asignada.
    """

    def __init__(self, cols, fils, tam, d, dom):
        """
        Constructor de la clase Variable.

        Args:
            cols (int): Valor inicial de las columnas.
            fils (int): Valor inicial de las filas.
            tam (int): Tamaño de la variable.
            d (str): Dirección de la variable.
        """
        self.ini_w = cols
        self.ini_h = fils
        self.tamano = tam
        self.dir = d
        self.palabra = ""  # Palabra asignada inicialmente es None
        self.dominio = dom
        self.podados = []

    def setPalabra(self, palabra):
        """
        Establece la palabra asignada a la variable.

        Args:
            palabra (str): Palabra asignada a la variable.
        """
        self.palabra = palabra

    def getPalabra(self):
        """
        Obtiene la palabra asignada a la variable.

        Returns:
            str: Palabra asignada a la variable.
        """
        return self.palabra

    def __str__(self):
        """
        Representación en cadena de la variable.

        Returns:
            str: Representación en cadena de la variable.
        """
        return f"Variable: (ini_w={self.ini_w}, ini_h={self.ini_h}, tamano={self.tamano}, dir={self.dir}, palabra={self.palabra}, dominio={self.dominio})"
