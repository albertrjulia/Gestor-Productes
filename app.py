from tkinter import ttk
from tkinter import *
import sqlite3
import os
import sys

# Si necesitas manejar otros formatos de imagen como JPEG, usa Pillow
try:
    from PIL import Image, ImageTk
    PIL_INSTALLED = True
except ImportError:
    PIL_INSTALLED = False

class Producto:
    def __init__(self, root):
        self.ventana = root
        self.ventana.title("App Gestor de Productos")
        self.ventana.resizable(1, 1)

        # Cargar el ícono con manejo de errores
        try:
            icon_path = self.resource_path('recursos/icon.png')  # Asegúrate de que sea un archivo PNG
            if PIL_INSTALLED:
                self.icono = ImageTk.PhotoImage(Image.open(icon_path))  # Usamos Pillow si está disponible
            else:
                self.icono = PhotoImage(file=icon_path)  # Solo acepta .png, .pgm, o .ppm
            self.ventana.iconphoto(False, self.icono)
        except Exception as e:
            print(f"Error cargando el ícono: {e}")

        # Creación del contenedor Frame principal
        frame = LabelFrame(self.ventana, text="Registrar un nuevo Producto")
        frame.grid(row=0, column=0, columnspan=3, pady=20)

        # Label Nombre
        self.etiqueta_nombre = Label(frame, text="Nombre: ")
        self.etiqueta_nombre.grid(row=1, column=0)

        # Entry Nombre
        self.nombre = Entry(frame)
        self.nombre.focus()
        self.nombre.grid(row=1, column=1)

        # Label Precio
        self.etiqueta_precio = Label(frame, text="Precio: ")
        self.etiqueta_precio.grid(row=2, column=0)

        # Entry Precio
        self.precio = Entry(frame)
        self.precio.grid(row=2, column=1)

        # Botón Añadir Producto
        self.boton_aniadir = ttk.Button(frame, text="Guardar Producto", command=self.add_producto)
        self.mensaje = Label(text='', fg='red')
        self.mensaje.grid(row=3, column=0, columnspan=2, sticky=W + E)
        self.boton_aniadir.grid(row=3, columnspan=2, sticky=W + E)

        # Tabla de Productos
        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri', 11))
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 13, 'bold'))
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])

        self.tabla = ttk.Treeview(height=20, columns=2, style="mystyle.Treeview")
        self.tabla.grid(row=4, column=0, columnspan=2)
        self.tabla.heading('#0', text='Nombre', anchor=CENTER)
        self.tabla.heading('#1', text='Precio', anchor=CENTER)

        # Botones Eliminar y Editar
        boton_eliminar = ttk.Button(text='ELIMINAR', command=self.del_producto)
        boton_eliminar.grid(row=5, column=0, sticky=W + E)
        boton_editar = ttk.Button(text='EDITAR', command=self.edit_producto)
        boton_editar.grid(row=5, column=1, sticky=W + E)

        # Obtener productos al iniciar la aplicación
        self.get_productos()

    # Ruta de la base de datos usando resource_path
    db = None  # Inicializamos db en None

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller crea una carpeta temporal y guarda el path en _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def db_consulta(self, consulta, parametros=()):
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            resultado = cursor.execute(consulta, parametros)
            con.commit()
            return resultado

    def get_productos(self):
        self.db = self.resource_path('database/productos.db')  # Usamos resource_path para obtener la ruta de la base de datos
        registros_tabla = self.tabla.get_children()
        for fila in registros_tabla:
            self.tabla.delete(fila)
        query = 'SELECT * FROM producto ORDER BY nombre DESC'
        registros_db = self.db_consulta(query)
        for fila in registros_db:
            self.tabla.insert('', 0, text=fila[1], values=fila[2])

    def validacion_nombre(self):
        nombre = self.nombre.get()
        return len(nombre) != 0

    def validacion_precio(self):
        precio = self.precio.get()
        return len(precio) != 0

    def add_producto(self):
        if self.validacion_nombre() and self.validacion_precio():
            query = 'INSERT INTO producto VALUES(NULL, ?, ?)'
            parametros = (self.nombre.get(), self.precio.get())
            self.db_consulta(query, parametros)
            self.mensaje['text'] = f'Producto {self.nombre.get()} añadido con éxito'
            self.nombre.delete(0, END)
            self.precio.delete(0, END)
            self.get_productos()
        else:
            self.mensaje['text'] = 'El nombre y el precio son obligatorios'

    def del_producto(self):
        self.mensaje['text'] = ''
        try:
            nombre = self.tabla.item(self.tabla.selection())['text']
        except IndexError:
            self.mensaje['text'] = 'Por favor, seleccione un producto'
            return
        query = 'DELETE FROM producto WHERE nombre = ?'
        self.db_consulta(query, (nombre,))
        self.mensaje['text'] = f'Producto {nombre} eliminado con éxito'
        self.get_productos()

    def edit_producto(self):
        self.mensaje['text'] = ''
        try:
            nombre = self.tabla.item(self.tabla.selection())['text']
            old_precio = self.tabla.item(self.tabla.selection())['values'][0]
        except IndexError:
            self.mensaje['text'] = 'Por favor, seleccione un producto'
            return

        self.ventana_editar = Toplevel()
        self.ventana_editar.title("Editar Producto")
        self.ventana_editar.resizable(1, 1)

        # Intentar cargar el ícono
        try:
            icon_path = self.resource_path('recursos/icon.png')  # Usar el ícono de nuevo
            if PIL_INSTALLED:
                self.icono_editar = ImageTk.PhotoImage(Image.open(icon_path))
            else:
                self.icono_editar = PhotoImage(file=icon_path)
            self.ventana_editar.iconphoto(False, self.icono_editar)
        except Exception as e:
            print(f"Error cargando el ícono de edición: {e}")

        # Añadir título
        titulo = Label(self.ventana_editar, text='Edición de Productos', font=('Calibri', 50, 'bold'))
        titulo.grid(column=0, row=0)

        # Creación del contenedor Frame
        frame_ep = LabelFrame(self.ventana_editar, text="Editar el siguiente Producto")
        frame_ep.grid(row=1, column=0, columnspan=20, pady=20)

        # Nombre antiguo
        self.etiqueta_nombre_anituguo = Label(frame_ep, text="Nombre antiguo: ")
        self.etiqueta_nombre_anituguo.grid(row=2, column=0)

        self.input_nombre_antiguo = Entry(frame_ep, textvariable=StringVar(self.ventana_editar, value=nombre), state='readonly')
        self.input_nombre_antiguo.grid(row=2, column=1)

        # Nombre nuevo
        self.etiqueta_nombre_nuevo = Label(frame_ep, text="Nombre nuevo: ")
        self.etiqueta_nombre_nuevo.grid(row=3, column=0)

        self.input_nombre_nuevo = Entry(frame_ep)
        self.input_nombre_nuevo.grid(row=3, column=1)
        self.input_nombre_nuevo.focus()

        # Precio antiguo
        self.etiqueta_precio_anituguo = Label(frame_ep, text="Precio antiguo: ")
        self.etiqueta_precio_anituguo.grid(row=4, column=0)

        self.input_precio_antiguo = Entry(frame_ep, textvariable=StringVar(self.ventana_editar, value=old_precio), state='readonly')
        self.input_precio_antiguo.grid(row=4, column=1)

        # Precio nuevo
        self.etiqueta_precio_nuevo = Label(frame_ep, text="Precio nuevo: ")
        self.etiqueta_precio_nuevo.grid(row=5, column=0)

        self.input_precio_nuevo = Entry(frame_ep)
        self.input_precio_nuevo.grid(row=5, column=1)

        # Botón Actualizar Producto
        self.boton_actualizar = ttk.Button(frame_ep, text="Actualizar Producto", command=lambda:
        self.actualizar_productos(self.input_nombre_nuevo.get(),
                                  self.input_nombre_antiguo.get(),
                                  self.input_precio_nuevo.get(),
                                  self.input_precio_antiguo.get()))
        self.boton_actualizar.grid(row=6, columnspan=2, sticky=W + E)

    def actualizar_productos(self, nuevo_nombre, antiguo_nombre, nuevo_precio, antiguo_precio):
        producto_modificado = False
        query = 'UPDATE producto SET nombre = ?, precio = ? WHERE nombre = ? AND precio = ?'
        if nuevo_nombre != '' and nuevo_precio != '':
            parametros = (nuevo_nombre, nuevo_precio, antiguo_nombre, antiguo_precio)
            producto_modificado = True
        elif nuevo_nombre != '' and nuevo_precio == '':
            parametros = (nuevo_nombre, antiguo_precio, antiguo_nombre, antiguo_precio)
            producto_modificado = True
        elif nuevo_nombre == '' and nuevo_precio != '':
            parametros = (antiguo_nombre, nuevo_precio, antiguo_nombre, antiguo_precio)
            producto_modificado = True

        if producto_modificado:
            self.db_consulta(query, parametros)
            self.ventana_editar.destroy()
            self.mensaje['text'] = f'El producto {antiguo_nombre} ha sido actualizado con éxito'
            self.get_productos()
        else:
            self.ventana_editar.destroy()
            self.mensaje['text'] = f'El producto {antiguo_nombre} NO ha sido actualizado'

if __name__ == '__main__':
    root = Tk()
    app = Producto(root)
    root.mainloop()
