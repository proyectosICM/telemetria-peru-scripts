import json
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"Conectado con código de resultado {rc}")

def send_to_mqtt(data, broker="192.168.0.204", port=1883, topic="prueba"):
    def on_publish(client, userdata, mid):
        print(f"Mensaje publicado con id {mid}")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(broker, port, 60)
    client.loop_start()  # Empezar el loop para mantener la conexión

    try:
        result = client.publish(topic, json.dumps(data))
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            print(f"Error al publicar: {result.rc}")
        else:
            #print(f"Datos enviados al topic MQTT '{topic}': {json.dumps(data, indent=4)}")
            print(f"Datos enviados al topic MQTT '{topic}'")
    except Exception as e:
        print(f"Error al enviar los datos al broker MQTT: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
