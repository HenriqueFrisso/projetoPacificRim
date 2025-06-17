

class RepositorioPilotos:
    _pilotos_time = []

    @classmethod
    def adicionar(cls, piloto):
        cls._pilotos_time.append(piloto)

    @classmethod
    def listar(cls):
        return cls._pilotos_time
    
class RepositorioJaegers:
    _jaegers_time = []

    @classmethod
    def adicionar(cls, jaeger):
        cls._jaegers_time.append(jaeger)

    @classmethod
    def listar(cls):
        return cls._jaegers_time
    
class RepositorioKaijusDerrotados:
    _kaijus_derrotados = []

    @classmethod
    def adicionar(cls, kaiju):
        cls._kaijus_derrotados.append(kaiju)

    @classmethod
    def listar(cls):
        return cls._kaijus_derrotados