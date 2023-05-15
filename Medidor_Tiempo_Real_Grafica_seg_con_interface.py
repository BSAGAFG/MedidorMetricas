import psutil
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time
import tkinter as tk
import threading
import openpyxl
import xlsxwriter


def obtener_uso_recursos():
    uso_cpu = psutil.cpu_percent() if cpu_var.get() else None
    uso_ram = psutil.virtual_memory().percent if ram_var.get() else None
    return uso_cpu, uso_ram

def update_graph(cpu_data, ram_data, time_data, ax, fig):
    if not plt.fignum_exists(fig.number):
        fig, ax = plt.subplots()
        plt.ion()
        plt.show()

    ax.clear()
    if cpu_data and ram_data:
        ax.plot(time_data, cpu_data, label='Uso de CPU (%)')
        ax.plot(time_data, ram_data, label='Uso de RAM (%)')
    elif cpu_data:
        ax.plot(time_data[:len(cpu_data)], cpu_data, label='Uso de CPU (%)')
    elif ram_data:
        ax.plot(time_data[:len(ram_data)], ram_data, label='Uso de RAM (%)')
    ax.set_xlabel('Tiempo (s) desde el inicio de la prueba')
    ax.set_ylabel('Porcentaje de uso')
    ax.legend()
    plt.draw()
    
#Esta solución permite que el gráfico se actualice desde el hilo principal utilizando app.after(). De esta manera, podrás detener e iniciar la prueba sin problemas.
def update_graph_wrapper(cpu_data, ram_data, time_data, ax, fig):
    if not plt.fignum_exists(fig.number):
        app.after(0, lambda: update_graph(cpu_data, ram_data, time_data, ax, fig))
    else:
        update_graph(cpu_data, ram_data, time_data, ax, fig)
    

#Linea para agregar linea de tiempo al almacenar la data
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

def ejecutar_prueba(prueba_tiempo, stop_event, cpu_var, ram_var):
    # Lista para almacenar los datos
    datos = []

    # Configurar gráfico en tiempo real
    fig, ax = plt.subplots()
    plt.ion()
    plt.show()

    # Obtener y mostrar datos de uso de recursos en tiempo real durante la prueba
    cpu_data = []
    cpu_data_per_core = []
    ram_data = []
    time_datos = []
    time_data = []
    start_time = datetime.now()

    while not stop_event.is_set():
        #uso_cpu = psutil.cpu_percent() if cpu_var.get() else None
        uso_cpu = None
        uso_cpu_per_core = None
        if cpu_var.get():
            uso_cpu_per_core = psutil.cpu_percent(percpu=True)
            uso_cpu = sum(uso_cpu_per_core) / len(uso_cpu_per_core)

        uso_ram = psutil.virtual_memory().percent if ram_var.get() else None
        elapsed_time = (datetime.now() - start_time).total_seconds()
        timestamp_datos = datetime.now().strftime("%Y%m%d-%H-%M-%S-%f")[:-3]
        #datos.append([elapsed_time, uso_cpu, uso_ram] + uso_cpu_per_core if uso_cpu_per_core else [])
        #datos.append([elapsed_time, uso_cpu, uso_ram])
        
        if uso_cpu_per_core is not None:
            datos.append([timestamp_datos, elapsed_time, uso_cpu, uso_ram] + uso_cpu_per_core)
        else:
            datos.append([timestamp_datos, elapsed_time, uso_cpu, uso_ram])
        
        if uso_cpu is not None:
            cpu_data.append(uso_cpu)
        if uso_cpu_per_core is not None:
            cpu_data_per_core.append(uso_cpu_per_core)
        if uso_ram is not None:
            ram_data.append(uso_ram)
        time_data.append(elapsed_time)

        update_graph_wrapper(cpu_data, ram_data, time_data, ax, fig)
        plt.pause(1)

        if prueba_tiempo is not None and elapsed_time >= prueba_tiempo:
            break

    # Convertir la lista de datos en un DataFrame de pandas
    #columnas = ['Tiempo (s) desde el inicio de la prueba', 'Uso de CPU (%)', 'Uso de RAM (%)']
    #df = pd.DataFrame(datos, columns=columnas)
    
    # Convertir la lista de datos en un DataFrame de pandas
    num_cores = len(uso_cpu_per_core) if uso_cpu_per_core is not None else 0
    core_columns = [f'Uso de CPU Núcleo {i} (%)' for i in range(num_cores)]
    columnas = ['Fecha y hora de la prueba', 'Tiempo (s) desde el inicio de la prueba', 'Uso de CPU promedio (%)', 'Uso de RAM (%)'] + core_columns
    df = pd.DataFrame(datos, columns=columnas)
    
    # Guardar el DataFrame en un archivo CSV
    #df.to_csv(f'uso_recursos_{timestamp}.csv', index=False)
    
    # Guardar el DataFrame en un archivo Excel
    workbook = xlsxwriter.Workbook(f'uso_recursos_{timestamp}.xlsx')
    worksheet = workbook.add_worksheet()
    # Escribir los encabezados en la hoja de trabajo
    for col_num, valor in enumerate(columnas):
        worksheet.write(0, col_num, valor)
    # Escribir los datos en la hoja de trabajo
    for row_num, row_data in enumerate(datos):
        for col_num, valor in enumerate(row_data):
            worksheet.write(row_num + 1, col_num, valor)
    workbook.close()
    
    # Guardar el gráfico final
    plt.savefig(f'grafico_uso_recursos_{timestamp}.png')

    plt.ioff()
    
    plt.close(fig)

def iniciar_prueba():
    # Leer el tiempo de la prueba ingresado por el usuario
    try:
        prueba_tiempo = int(entry_tiempo.get())
    except ValueError:
        tk.messagebox.showerror("Error", "Por favor, ingrese un número entero válido.")
        return

    stop_event.clear()
    threading.Thread(target=ejecutar_prueba, args=(prueba_tiempo, stop_event, cpu_var, ram_var)).start()



def detener_prueba():
    stop_event.set()

# Crear la ventana de la aplicación
app = tk.Tk()
app.title("Monitoreo de recursos")
cpu_var = tk.BooleanVar()
cpu_check = tk.Checkbutton(app, text="Monitorear uso de CPU", variable=cpu_var)
cpu_check.pack(padx=10, pady=10)

ram_var = tk.BooleanVar()
ram_check = tk.Checkbutton(app, text="Monitorear uso de RAM", variable=ram_var)
ram_check.pack(padx=10, pady=10)

# Crear una etiqueta y un campo de entrada para el tiempo de la prueba
label_tiempo = tk.Label(app, text="Tiempo de la prueba (s):")
label_tiempo.pack(padx=10, pady=10)
entry_tiempo = tk.Entry(app)
entry_tiempo.pack(padx=10, pady=10)

# Crear un botón para iniciar la prueba
start_button = tk.Button(app, text="Iniciar prueba", command=iniciar_prueba)
start_button.pack(padx=20, pady=20)

# Crear un botón para detener la prueba
stop_event = threading.Event()
start_button = tk.Button(app, text="Detener prueba", command=detener_prueba)
start_button.pack(padx=20, pady=20)

# Iniciar la aplicación
app.mainloop()
