from fastapi import FastAPI, UploadFile, File, Form, Depends
from typing import Optional
from pydantic import BaseModel
import shutil
import os
import uuid
import orm.repo as repo #funciones para hacer consultas a la BD
import orm.esquemas as esquemas
from sqlalchemy.orm import Session
from orm.config import generador_sesion #generador de sesiones

# creación del servidor
app = FastAPI()

#definición de la base del usuario
class UsuarioBase(BaseModel):
    nombre:Optional[str]=None
    edad:int
    domicilio:str    
    
usuarios = [{
    "id": 0,
    "nombre": "Homero Simpson",
    "edad": 40,
    "domicilio": "Av. Simpre Viva"
}, {
    "id": 1,
    "nombre": "Marge Simpson",
    "edad": 38,
    "domicilio": "Av. Simpre Viva"
}, {
    "id": 2,
    "nombre": "Lisa Simpson",
    "edad": 8,
    "domicilio": "Av. Simpre Viva"
}, {
    "id": 3,
    "nombre": "Bart Simpson",
    "edad": 10,
    "domicilio": "Av. Simpre Viva"
}]


# decorator
@app.get("/")
def hola_mundo():
    print("invocando a ruta /")
    respuesta = {
        "mensaje": "hola mundo!"
    }

    return respuesta


@app.get("/usuarios/{id}/compras/{id_compra}")
def compras_usuario_por_id(id: int, id_compra: int):
    print("buscando compra con id:", id_compra, " del usuario con id:", id)
    # simulamos la consulta
    compra = {
        "id_compra": 787,
        "producto": "TV",
        "precio": 14000
    }

    return compra

@app.get("/usuarios/{id}")
def usuario_por_id(id:int,sesion:Session=Depends(generador_sesion)):
    print("Api consultando usuario por id")
    return repo.usuario_por_id(sesion, id)

@app.get("/usuarios/{id}/fotos")
def fotos_por_id_usr(id:int,sesion:Session=Depends(generador_sesion)):
    print("API consultando fotos del usuario ", id)
    return repo.fotos_por_id_usuario(sesion, id)

@app.get("/usuarios/{id}/compras")
def fotos_por_id_usr(id:int,sesion:Session=Depends(generador_sesion)):
    print("API consultando compras del usuario ", id)
    return repo.compras_por_id_usuario(sesion, id)

@app.get("/usuarios")
def lista_usuarios(sesion:Session=Depends(generador_sesion)):
    print("API consultando todos los usuarios")
    return repo.devuelve_usuarios(sesion)
#def lista_usuarios(*,lote:int=10,pag:int,orden:Optional[str]=None): #parametros de consulta ?lote=10&pag=1
#    print("lote:",lote, " pag:", pag, " orden:", orden)
#    #simulamos la consulta
#    return usuarios

@app.post("/usuarios")
def guardar_usuario(usuario:UsuarioBase, parametro1:str):
    print("usuario a guardar:", usuario, ", parametro1:", parametro1)
    #simulamos guardado en la base.
    
    usr_nuevo = {}
    usr_nuevo["id"] = len(usuarios)
    usr_nuevo["nombre"] = usuario.nombre
    usr_nuevo["edad"] = usuario.edad
    usr_nuevo["domicilio"] = usuario.domicilio

    usuarios.append(usuario)

    return usr_nuevo

#@app.put("/compras/{id}")
#@app.put("/fotos/{id}")
@app.put("/usuario/{id}")
def actualizar_usuario(id:int,info_usuario:esquemas.UsuarioBase,sesion:Session=Depends(generador_sesion)):
    return repo.actualiza_usuario(sesion,id,info_usuario)
    
@app.delete("/usuario/{id}")
def borrar_usuario(id:int, sesion:Session=Depends(generador_sesion)):
    #1.- borro compras del usuario
    #repo.borrar_compras_por_id_usuario(sesion,id)
    #2.-borro foto del usuario
    #repo.borrar_fotos_por_id_usuario(sesion,id)
    repo.borra_usuario_por_id(sesion,id)
    return {"usuario_borrado", "ok"}

## Peticiones de compras
@app.get("/compras/{id}")
def compra_por_id(id:int, sesion:Session=Depends(generador_sesion)):
    print("Buscando compra por id")
    return repo.compra_por_id(sesion, id)

# "/compras?id_usuario={id_usr}&precio={p}"
@app.get("/compras")
def lista_compras(id_usuario:int,precio:float,sesion:Session=Depends(generador_sesion)):
    print("/compras?id_usuario={id_usr}&precio={p}")
    return repo.devuelve_compras_por_usuario_precio(sesion,id_usuario,precio)

## Peticiones de fotos
@app.get("/fotos/{id}")
def foto_por_id(id:int, sesion:Session=Depends(generador_sesion)):
    print("Buscando foto por id")
    return repo.foto_por_id(sesion,id)

@app.get("/fotos")
def lista_fotos(sesion:Session=Depends(generador_sesion)):
    print("API consultando todas las fotos")
    return repo.devuelve_fotos(sesion)

@app.post("/fotos")
async def guardar_foto(titulo:str=Form(None), descripcion:str=Form(...), foto:UploadFile=File(...)):
    print("titulo:", titulo)
    print("descripcion:", descripcion)

    home_usuario=os.path.expanduser("~")
    nombre_archivo=uuid.uuid4().hex  #generamos nombre único en formato hexadecimal
    extension = os.path.splitext(foto.filename)[1]
    ruta_imagen=f'{home_usuario}/fotos-ejemplo/{nombre_archivo}{extension}'
    print("guardando imagen en ruta:", ruta_imagen)

    with open(ruta_imagen,"wb") as imagen:
        contenido = await foto.read() #read funciona de manera asyncrona
        imagen.write(contenido)

    return {"titulo":titulo, "descripcion":descripcion, "foto":foto.filename}
