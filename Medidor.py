import psutil
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time

# Función para obtener el porcentaje de uso de CPU y RAM
def obtener_uso_recursos():
    uso_cpu = psutil.cpu_percent()
    uso_ram = psutil.virtual_memory().percent
    fecha_hora = datetime.now()
    return uso_cpu, uso_ram, fecha_hora

# Lista para almacenar los datos
datos = []

# Obtener datos de uso de recursos durante un minuto
for _ in range(60):
    uso_cpu, uso_ram, fecha_hora = obtener_uso_recursos()
    datos.append([fecha_hora, uso_cpu, uso_ram])
    time.sleep(1)

# Convertir la lista de datos en un DataFrame de pandas
columnas = ['Fecha y hora', 'Uso de CPU (%)', 'Uso de RAM (%)']
df = pd.DataFrame(datos, columns=columnas)

# Guardar el DataFrame en un archivo CSV
df.to_csv('uso_recursos.csv', index=False)

# Generar el gráfico
fig, ax = plt.subplots()
ax.plot(df['Fecha y hora'], df['Uso de CPU (%)'], label='Uso de CPU (%)')
ax.plot(df['Fecha y hora'], df['Uso de RAM (%)'], label='Uso de RAM (%)')
ax.set_xlabel('Fecha y hora')
ax.set_ylabel('Porcentaje de uso')
ax.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('grafico_uso_recursos.png')
plt.show()


obtener_uso_recursos()