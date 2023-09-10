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
serial_port='/dev/ttyUSB0'

#create a minimalpublisher class which is a subclass of the node class
class Position(Node):
    def __init__(self):
        super().__init__('Position') #initialize the node class
        #create a publsiher with a String msg and the topic name "position_info" with 10 of qos
        self.publisher_=self.create_publisher(String, 'position_info',10)
        timer_period=0.5 #the period of time we'll publish the msg
        self.timer=self.create_timer(timer_period,self.timer_callback)
        self.x=0
        self.ser= serial.Serial(serial_port,baud_rate)
        time.sleep(2)
        #initialize a counter variable
        self.i=0
    
    def timer_callback(self):
        #this fuction gets called every 0.5
        if self.i>0:
            self.x=int(self.ser.readline())
        msg= String() #create a String msg
        #set the message's data
        msg.data= "X: %d" %self.x

        #Publish the message to the topic
        self.publisher_.publish(msg)

        #display the msg on the console

        self.get_logger().info('Publishing: "%s" '%msg.data)

        #increment the counter by 1
class GUIApp:
    def __init__(self,root,position_publisher) :
        self.root = root
        self.root.title("Serial Communication Control")

        self.position_publisher = position_publisher

        self.start_button = tk.Button(root, text="Start Serial Communication", command=self.start_serial)
        self.start_button.pack()

        self.stop_button = tk.Button(root, text="Stop Publisher Node", command=self.stop_publisher)
        self.stop_button.pack()

        self.reboot_button = tk.Button(root, text="Reboot ESP32", command=self.reboot_esp32)
        self.reboot_button.pack()

        self.esp32_label = tk.Label(root, text="ESP32 Value: N/A")
        self.esp32_label.pack()

        self.publisher_label = tk.Label(root, text="Publisher Message: N/A")
        self.publisher_label.pack()   
    def start_serial(self):
        self.position_publisher.i+=1
        self.position_publisher.ser.write('S'.encode('utf-8'))
        time.sleep(2)

    def stop_publisher(self):
        pass
    def reboot_esp32(self):
        # Reboot the ESP32 (you may need to implement this)
        # You can call your ESP32 reboot code from here
        pass



def main(args=None):
    try:
        #initialize the rclpy library
        rclpy.init(args=args)

        #Create the node
        position_publisher=Position()
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
                time.sleep(5)  # Update every 100 milliseconds

        thread_ros = th.Thread(target=ros_thread)
        thread_labels = th.Thread(target=update_labels)

        thread_ros.start()
        thread_labels.start()

        root.mainloop()       
        #Spin the node so the call back fuction is called

        rclpy.spin(position_publisher)

        #destroy the node explicity
    except KeyboardInterrupt:
        #shutdown the ROS client library for python
        position_publisher.ser.write("R".encode('utf-8')) #Restart the esp32 to prepare it to start again (once the node is launch again)
        time.sleep(2) #2 secondes for reset
        position_publisher.ser.close() #CLOSE THE SERIAL CONNECTION
        position_publisher.get_logger().info("IT'S DONE!")
        position_publisher.destroy_node()
        rclpy.shutdown()



if __name__=="__main__":
    main()

