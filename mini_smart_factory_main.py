from gpiozero import Servo, DistanceSensor, DigitalInputDevice
from time import sleep
import json
import datetime
import time
import random
from azure.iot.device import IoTHubDeviceClient, Message
from threading import Thread
import signal


contador = 0
machinespeed = 0
bad_boxes = 0
def infrarojos():
    global contador
    global machinespeed
    global bad_boxes
    from gpiozero import DigitalInputDevice
    from time import sleep

    # Configuración del pin GPIO para el servo motor
    SERVO_PIN = 12  # Cambia este número según tu conexi    

    # Configuración del pin GPIO para el sensor infrarrojo
    IR_PIN = 24  # Cambia esto según el pin GPIO al que conectaste el sensor
    TRIG_PIN = 20  # Pin GPIO conectado a TRIG
    ECHO_PIN = 16  # Pin GPIO conectado a ECHO

    # Inicializar el servo y asegurarse de que esté detenido
    servo = Servo(SERVO_PIN, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

    # Inicializar el sensor de distancia
    sensor = DistanceSensor(echo=ECHO_PIN, trigger=TRIG_PIN)

    # Inicializar el sensor infrarrojo
    sensor_ir = DigitalInputDevice(IR_PIN)

    print("Iniciando lectura del sensor infrarrojo...")

    try:
        
        detector= False
        detector_2 = False
    
        while True:

            
            servo.value = -0.3
            machinespeed= servo.value
            if sensor_ir.is_active:
                detector = False
                if detector_2:
                    bad_boxes += 1 
                    print(bad_boxes)
                detector_2 = False
            else:
                distancia = sensor.distance * 100  # Convertir a centímetros
                print(f"Distancia medida: {distancia:.2f} cm")
                if distancia >= 3:
                    detector_2 = True
                    
                if detector != True:
                    contador += 1
                    detector = True
                    print(contador)

            sleep(0.1)  # Pausa de medio segundo entre lecturas

    except KeyboardInterrupt:
        print("\nLectura interrumpida por el usuario. Saliendo...")
        servo.value = None
        sleep(1)
    finally:
        servo.value = None
        sleep(1)
        print("Programa terminado.")

# Replace with your IoT Hub device connection string
CONNECTION_STRING = "HostName=ra-develop-bobstconnect-01.azure-devices.net;DeviceId=LAUZHACKPI9;SharedAccessKey=weIlJS6KBonvI7XH7Hy8LermyLSSWC3edAIoTN++s44="

def send_telemetry():
    
    # Create an instance of the IoTHubDeviceClient
    global contador
    global machinespeed
    global bad_boxes
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    
    total_output_unit_count = 140
    total_working_energy = 0.0  # Simulate total energy consumption

    try:
        while True:
            
            total_output_unit_count = contador

            # Create telemetry data with the current UTC timestamp
            telemetry_data = {
                "telemetry": {
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "datasource": "10.0.4.41:80",
                    "machineid": "lauzhack-pi9",
                    "machinespeed": machinespeed,
                    "totaloutputunitcount": contador,
                    "totalbadboxes" : bad_boxes
                    #"totalworkingenergy": total_working_energy
                }
            }

            # Convert the telemetry data to JSON format
            telemetry_json = json.dumps(telemetry_data)

            # Create an IoT Hub Message from the JSON telemetry data
            message = Message(telemetry_json)
            message.content_type = "application/json"
            message.content_encoding = "utf-8"
            message.custom_properties["messageType"] = "Telemetry"

            # Send the message to Azure IoT Hub
            print("Sending message: {}".format(telemetry_json))
            client.send_message(message)
            print("Message successfully sent!")

            # Wait for 10 seconds before sending the next message
            time.sleep(1)
    except Exception as e:
        print("Error sending message: {}".format(e))
    
    finally:
        # Ensure to close the client after sending
        client.shutdown()

def parar():
    servo.value


if __name__ == "__main__":

    #send_telemetry()
        thread_infrarojos = Thread(target=infrarojos)
        thread_infrarojos.start()

        send_telemetry()


        

#infrarojos()
