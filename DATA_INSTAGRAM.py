import instaloader #Es una biblioteca para descargar datos de perfiles de Instagram, como seguidores, publicaciones, y más.
import pandas as pd #Biblioteca para análisis de datos estructurados para crear el archivo csv con los datos recopilados
import time #Manejar funciones relacionadas con el tiempo como pausas (time.sleep)
import matplotlib.pyplot as plt #Módulo para la creación de gráficos.
from instaloader.exceptions import ConnectionException, BadResponseException #Importa excepciones específicas de Instaloader que ayudan a manejar errores de Instagram, como problemas de conexión o respuestas erróneas del servidor.
# Configuración
print("*** Sistema de Scrapy en Instagram ***")
nombre_usuario = input("Ingrese su nombre de usuario (Instagram): ")  # Nombre de usuario de instagraam
contrasena_usuario = input("Ingrese la contraseña de su instagram: ")  # Contraseña de instagram
nombre_usuario_formateado = nombre_usuario.replace(" ", "_").lower()
output_csv = f"{nombre_usuario_formateado}_seguidores.csv"  # Nombre del archivo CSV
# Función para manejar errores y reintentar
def process_profile_with_retry(profile, retries=3): #Función que intenta acceder al perfil de un seguidor hasta un máximo de n=retries intentos
#Si falla al obtener el número de seguidores del perfil (debido a errores de conexión), espera 10 segundos antes de reintentar.
    for attempt in range(retries):
        try:
            return profile.followers
        except (ConnectionException, BadResponseException):
            print(f"Error al intentar acceder al perfil. Reintento {attempt + 1}/{retries}...")
            time.sleep(10)
#Si los intentos se agotan devuelve None
    print("No se pudo acceder al perfil después de múltiples intentos.")
    return None
# Crear instancia de Instaloader y autenticarse
loader = instaloader.Instaloader() #Para interactuar con instagram
#Intenta iniciar sesión con el usuario y contraseña. Si falla, imprime un mensaje de error y termina el programa.
try:
    loader.login(nombre_usuario, contrasena_usuario)
except Exception as e:
    print(f"Error al iniciar sesión: {e}")
    exit(1)
    # Obtener perfil principal
#Obtiene el perfil del usuario principal para acceder a su lista de seguidores. Si falla, muestra un mensaje de error y termina.
try:
    profile = instaloader.Profile.from_username(loader.context, nombre_usuario)
except Exception as e:
    print(f"Error al obtener el perfil principal: {e}")
    exit(1)
    # Descargar datos de los seguidores
#Intenta obtener la lista completa de seguidores del perfil. Si falla, imprime un error y termina el programa.
followers = []
try:
    print("Descargando lista de seguidores...")
    followers = list(profile.get_followers())
except Exception as e:
    print(f"Error al descargar la lista de seguidores: {e}")
    exit(1)
# Procesar y extraer información
#Lista vacía para almacenar la información de cada seguidor y comienza el procesamiento
data = []
print("Procesando seguidores de tus seguidores...")
#Itera sobre cada seguidor, imprime su progreso y utiliza process_profile_with_retry para obtener su número de seguidores.
for idx, person in enumerate(followers, start=1):
    print(f"{idx}/{len(followers)}: Procesando {person.username}...")
    followers_count = process_profile_with_retry(person)
#Si el número de seguidores se obtiene correctamente, se agrega al conjunto de datos y se guarda en un archivo CSV parcial.
    if followers_count is not None:
        data.append({"username": person.username, "followers": followers_count})

        # Guardar datos parciales en el CSV después de cada consulta
        # Guardar datos parciales en el CSV después de cada consulta
        pd.DataFrame(data).to_csv("C:/Users/MyVICTUS/Desktop/seguidores.csv", index=False, sep=';')

#Si hay errores, omite al seguidor y espera 2 segundos entre solicitudes para evitar ser bloqueado por Instagram.
    else:
        print(f"Saltando {person.username} debido a error.")

    time.sleep(2)  # Reducir el ritmo de solicitudes para evitar bloqueos

print(f"Datos parciales guardados en {output_csv}")

# Generar gráfico de barras
if data:  # Solo generar el gráfico si hay datos
    # Convertir a DataFrame
    df = pd.DataFrame(data)

    # Obtener el primer dígito de cada número de seguidores
    df["first_digit"] = df["followers"].astype(str).str[0].astype(int)

    # Contar la frecuencia de cada dígito
    digit_counts = df["first_digit"].value_counts().sort_index()

    # Crear el gráfico
    plt.bar(digit_counts.index, digit_counts.values, color="skyblue")
    plt.xlabel("Primer dígito")
    plt.ylabel("Frecuencia")
    plt.title("Distribución de seguidores por primer dígito (Ley de Benford)")
    plt.xticks(range(1, 10))
    plt.savefig("grafico_benford_seguidores.png")  # Guardar gráfico como imagen
    plt.show()
else:
    print("No se generó ningún gráfico porque no hay datos suficientes.")
