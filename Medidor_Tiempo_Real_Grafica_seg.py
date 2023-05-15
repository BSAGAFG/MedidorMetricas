import psutil
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time

# Función para obtener el porcentaje de uso de CPU y RAM
def obtener_uso_recursos():
    uso_cpu = psutil.cpu_percent()
    uso_ram = psutil.virtual_memory().percent
    return uso_cpu, uso_ram

# Lista para almacenar los datos
datos = []

# Configurar gráfico en tiempo real
plt.ion()
fig, ax = plt.subplots()
cpu_line, = ax.plot([], [], label='Uso de CPU (%)')
ram_line, = ax.plot([], [], label='Uso de RAM (%)')
ax.set_xlabel('Tiempo (s) desde el inicio de la prueba')
ax.set_ylabel('Porcentaje de uso')
ax.legend()
plt.xticks(rotation=45)
fig.tight_layout()

# Función para actualizar el gráfico en tiempo real
def update_graph(cpu_data, ram_data, time_data):
    cpu_line.set_xdata(time_data)
    cpu_line.set_ydata(cpu_data)
    ram_line.set_xdata(time_data)
    ram_line.set_ydata(ram_data)
    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw()
    fig.canvas.flush_events()

# Obtener y mostrar datos de uso de recursos en tiempo real durante 60 segundos
cpu_data = []
ram_data = []
time_data = []
start_time = datetime.now()

for i in range(60):
    uso_cpu, uso_ram = obtener_uso_recursos()
    elapsed_time = (datetime.now() - start_time).total_seconds()
    datos.append([elapsed_time, uso_cpu, uso_ram])
    cpu_data.append(uso_cpu)
    ram_data.append(uso_ram)
    time_data.append(elapsed_time)

    update_graph(cpu_data, ram_data, time_data)
    time.sleep(1)

# Convertir la lista de datos en un DataFrame de pandas
columnas = ['Tiempo (s) desde el inicio de la prueba', 'Uso de CPU (%)', 'Uso de RAM (%)']
df = pd.DataFrame(datos, columns=columnas)

# Guardar el DataFrame en un archivo CSV
df.to_csv('uso_recursos.csv', index=False)

# Guardar el gráfico final
plt.savefig('grafico_uso_recursos.png')
plt.ioff()
plt.show()
