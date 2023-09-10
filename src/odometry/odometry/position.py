#ROS CLIENT LIBRARY FOR PYTHON
import rclpy 

#HANDLES THE CREATION OF NODES
from rclpy.node import Node


#ENABLE USAGE OF THE STRING MESSAGE TYPE
from std_msgs.msg import String

#LIBRARY FOR SERIAL COMUNICATION
import serial
import time
#LIBRARY FOR MULTITHREADING
import threading as th
#library for the GUI
import tkinter as tk

#OPEN THE SERIAL CONNECTION:

baud_rate=115200


#create a minimalpublisher class which is a subclass of the node class
class Position(Node):
    def __init__(self,serial_port):
        super().__init__('Position') #initialize the node class
        #create a publsiher with a String msg and the topic name "position_info" with 10 of qos
        self.serial_port = serial_port # Retrieve the parameter's value as a string      
        self.publisher_=self.create_publisher(String, 'position_info',10)
        timer_period=0.5 #the period of time we'll publish the msg
        self.timer=self.create_timer(timer_period,self.timer_callback)
        self.x=0
        self.ser= serial.Serial(self.serial_port,baud_rate)
        time.sleep(1)
        self.msg= String()
        self.msg.data= "X: %d" %self.x
        #initialize a counter variable
        self.i=0
    def timer_callback(self):
        #this fuction gets called every 0.5

            #self.x=int(self.ser.readline())   

  
            #set the message's data
        self.msg.data= "X: %d" %self.x

            #Publish the message to the topic
        self.publisher_.publish(self.msg)

            #display the msg on the console

        self.get_logger().info('Publishing: "%s" '%self.msg.data)

            #increment the counter by 1
class GUIApp:
    def __init__(self,root,position_publisher) :
        self.root = root
        self.root.title("Serial Communication Control")

        self.position_publisher = position_publisher

        self.start_button = tk.Button(root, text="Start Serial Communication ", command=self.start_serial)
        self.start_button.pack()

        self.stop_button = tk.Button(root, text="Stop Comunicating (REBOOT ESP32)", command=self.stop_publisher)
        self.stop_button.pack()


        self.esp32_label = tk.Label(root, text="ESP32 Value: N/A")
        self.esp32_label.pack()

        self.publisher_label = tk.Label(root, text="Publisher Message: N/A")
        self.publisher_label.pack()   
    def start_serial(self):
        if self.position_publisher.x==0:
                self.position_publisher.ser.write("S".encode('utf-8')) #start the communication
                time.sleep(0.5)
        self.position_publisher.i+=1

    def stop_publisher(self):
        self.position_publisher.i=0
        self.position_publisher.ser.write("R".encode('utf-8')) #Restart the esp32 to prepare it to start again (once the node is launch again)
        time.sleep(2)
        self.position_publisher.ser.close()
        time.sleep(1)
        pass

def main(args=None):
    try:
        #initialize the rclpy library
        rclpy.init(args=args)        
          # Retrieve the serial_port parameter value
        serial_port= '/dev/ttyUSB0'  # Default value  
        if args:
           if '--serial_port' in args:
                arg_index = args.index('--serial_port')  # Find the index of '--serial_port'
                if arg_index + 1 < len(args):
                    serial_port = args[arg_index + 1]  # Get the value after '--serial_port'
        position_publisher=Position(serial_port)
        root = tk.Tk()
        app = GUIApp(root, position_publisher)
        def ros_thread(): #hilo de ros
            rclpy.spin(position_publisher) #it will spin, executing everr 500 ms
            rclpy.shutdown()
        def update_labels():
            while True:
                # Update ESP32 value label
                esp32_value = position_publisher.x
                app.esp32_label.config(text=f"ESP32 Value: {esp32_value}")

                # Update Publisher message label
                publisher_msg = position_publisher.msg.data if position_publisher.msg else "N/A"
                app.publisher_label.config(text=f"Publisher Message: {publisher_msg}")

                root.update()  # Update the Tkinter GUI
                time.sleep(0.3)  # Update every 100 milliseconds
        def communication():
            while True:
                if position_publisher.x>0 and position_publisher.i>0 and not position_publisher.ser.is_open:
                    position_publisher.ser=serial.Serial(position_publisher.serial_port,baud_rate)
                    time.sleep(1)           
                    position_publisher.ser.write("S".encode('utf-8')) #start the communication
                    time.sleep(0.5)
                if position_publisher.ser.is_open and position_publisher.i>0:
                    position_publisher.x=int(position_publisher.ser.readline())
                time.sleep(0.5)
        thread_ros = th.Thread(target=ros_thread)
        thread_labels = th.Thread(target=update_labels)
        thread_communication=th.Thread(target=communication)
        thread_ros.start()
        thread_labels.start()
        thread_communication.start()

        root.mainloop()       
        #Spin the node so the call back fuction is called

        rclpy.spin(position_publisher)

        #destroy the node explicity
    except KeyboardInterrupt:
        #shutdown the ROS client library for python
        #position_publisher.ser.write("R".encode('utf-8')) #Restart the esp32 to prepare it to start again (once the node is launch again)
        #time.sleep(2) #2 secondes for reset
        position_publisher.ser.close() #CLOSE THE SERIAL CONNECTION
        position_publisher.get_logger().info("IT'S DONE!")
        position_publisher.destroy_node()
        root.destroy()
        rclpy.shutdown()



if __name__=="__main__":
    main()

