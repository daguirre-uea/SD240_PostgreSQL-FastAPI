from pydantic import BaseModel

#Definir el esquema usuario
class UsuarioBase(BaseModel):
    nombre:str
    edad:int
    domicilio:str
    email:str
    password:str