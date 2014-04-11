##ADB Controller
A CherryPy / Python based frontend for controlling the Android Debugging Bridge (ADB). 

#####Requirements:
* Python 2.7
* ADB from the Android SDK *(accessible via $PATH)*
* Android Debugging enabled on device
#####Usage:
1. Download
2. Connect Tablet via USB
3. Run adb_controller.py *(Browser will open automatically)*
#####Features:
* Reboot device
* Keyboard control
* Navigation control *(Arrows, Back, Home, etc)*
* Send custom commands through *adb shell*
* Send custom text through *adb input text*
* Screenshot dumped directly from device with each command
* Supports touch simulation, click an area of screenshot to simulate screen touch on device (Android version 4.1.1+)
* Support key input via form inputs on frontend for other versions of Android.
* Open direct to screens on device
* Easily add additional controls

##### Limits:
* First device found is target device. Multiple devices selector is for display only, you cannot select a device from this drop down as a target.
* APK installation form commented out until such time as full paths are accessible via file browser form control

Tested on Linux & Windows 7 with Python 2.7.6

##### Why?
My kids broke their tablet screens which I replaced with a cheap perspex non-touch alternative and turned them into eBook readers. It is also easier than locating/using a OTG cabled mouse/keyboard when they need them updated.

sairuk
http://www.mameau.com/
