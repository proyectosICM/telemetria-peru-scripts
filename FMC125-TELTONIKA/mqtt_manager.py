import json
import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    pass  
    #print(f"Connected with result code {rc}")

def send_to_mqtt(data, broker="192.168.0.204", port=1883, topic="prueba"):
    def on_publish(client, userdata, mid):
        pass  
        #print(f"Posted message with id {mid}")

    data["timestamp"] = int(time.time()) 
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(broker, port, 60)
    client.loop_start()  # Empezar el loop para mantener la conexión

    try:
        result = client.publish(topic, json.dumps(data), qos=1, retain=True)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            print(f"Error publishing: {result.rc}")
        else:
            pass  
            #print(f"Data sent to MQTT topic '{topic}': {json.dumps(data, indent=4)}")
            #print(f"Data sent to MQTT topic '{topic}'")
    except Exception as e:
        print(f"Error sending data to MQTT broker: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
