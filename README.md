# SecurityApp-server
This is a mobile and a web-based application that can be used to back up data directly from the phone to the laptop or any device. </br>
Apart from backing up phone data to the laptop, one can make use of Android Permissions  such as Camera,Phone,GPS system to remotely access one's device from the internet </br>
# Installation and setup
The setup for the webserver is simple once you clone this repository  into your local device in the same folder you cloned the repository run </br> 
<code> pip run requirements.txt </code>
</br>
then create a Firebase project and the credentials in the config section. For more information regarding how to create a Firebase project please look up the information
here: <a href="https://console.firebase.google.com/">Firebase Console </a>
</br>
In a  new command prompt if using Windows run
</br>
<code> ipconfig </code>
to know which IP address your device is running on remember to change the IP address of  your local device.</br>
# Running the Server 
</br> 
To run the server type </br>
<code> python3 -m flask run -h YOUR_IP_ADDRESS -p 5000 </code>
</br>
Remember to change your IP_ADDRESS to the IP ADDRESS your device currently is running on.

