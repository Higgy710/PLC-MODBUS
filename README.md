![PLC Setup](https://user-images.githubusercontent.com/47610444/144299678-3d659c47-d216-4762-afab-4b155440861d.jpg)


# Objectives:
1. Design an op amp circuit that converts the output of the TMP17 Temperature Transducer made by Analog Devices to a voltage suitable for our PLC. Specifically, design it so that it converts a temperature range of `50degF to 90degF` into a voltage range of `2VDC to 8VDC`.
2. Use `PyModbus` to comunicate with PLC through TCP using MODPUS protocol and stuctured text/ladder logic in Machine Expert – Basic.
3. Use `PySimpleGUI` to create an human machine interface(HMI) for the heater controller.

## Objective 1:


![TMP17_Amplifier_Calculations](https://user-images.githubusercontent.com/47610444/144166698-c0334b92-2cfb-48a7-b86d-a38cd2a1a60f.png)


![TMP17_Signal_Conditioner_Circuit](https://user-images.githubusercontent.com/47610444/144166707-6ba3ac67-1e1e-43d4-94af-9fe4e3c6f1da.png)


The circuit was constructed on a breadboard and connected to the PLC's analog input.

This circuit was enclosed in a cardboard box with a light bulb being used as a heating element and a fan to ensure an even tempurature distribution.

The light bulb is controlled connected to a relay that can be controlled via an input on the PLC.


## Objective 2:

### Requirements:
1.	Determine the ADC integer values corresponding to 50°F through 90°F.
3.	At one second intervals, use MODBUS to read the integer values from the temperature sensing circuit connected ADC.
5.	In your python program, convert these values to their temperature in Fahrenheit and display them on the terminal at their one second intervals.
6.	Detect if digital input %I0.1 is HIGH. Each time it is pressed, your python program should toggle between displaying temperature in Fahrenheit, to Celsius, to Kelvin, and back to Fahrenheit.
7.	In your ladder logic, determine if your ADC reads a temperature greater than the value stored in %MW0, it should make output %Q0.1 HIGH until it drops below that value.
8.	At launch, your PLC should set %MW0 to 85°F.
9.	Your pymodbus program should check if the ladder logic has detected the temperature alarm condition. If the temperature has been exceeded, it should display "HIGH TEMP ALERT"
10.	Your pymodbus program should send an adjustable alarm temperature threshold to %MW0 every time it starts. For now, the alarm temperature can be stored as a constant in your program and this constant must be a float in degrees Fahrenheit. You will need to convert it to the corresponding integer ADC value before sending it to the PLC.

### Procedure:

1.	The analog input range of the PLC is 0VDC  to 10VDC. The temperature sensing circuit corresponds 2V to 50°F and 8V to 90°F. Usually the values for a 10-bit ADC would be 0-1024 but in our case the ADC range was 0-1000. So, 50°F equates to 200 and 90°F equates to 800.

2.	The potentiometer was on the 2nd ADC input of the PLC, meaning it’s IW0.1 in Machine Expert. In figure 1, the python code for reading the MODBUS ADC value is shown. On Rung 10 in figure 2 below, it’s shown that the ADC value from IW0.1 is stored in register MW2.

![image](https://user-images.githubusercontent.com/47610444/144168350-97eaabce-88b9-4b08-b9ce-1ca1023988ee.png)


*Figure 1: Python: Reading a value from the ADC*

![image](https://user-images.githubusercontent.com/47610444/144168670-1cb5b831-b334-48e0-b9ce-57fae23e22f2.png)
![image](https://user-images.githubusercontent.com/47610444/144168636-dfdbce36-e0f3-4072-881c-50d57b4d3f43.png)

*Figure 2: PLC Ladder Logic & Structured Text for Part 2*

3.	Figure 3 below shows the coding for converting the ADC value from the MW2 register to °F and figure 4 shows them being displayed to the terminal, in one second intervals.

![image](https://user-images.githubusercontent.com/47610444/144168462-23ab81ee-0363-4f52-b426-a6b9e5a167bb.png)

*Figure 3: Python code to convert ADC to °F*

![image](https://user-images.githubusercontent.com/47610444/144168473-81b7f508-196f-4ed8-a390-83843ebc3038.png)

*Figure 4: Displays temp values to terminal*

4.	The detection of %I0.1 being pressed is shown in figure 2 on rung 8. Figures 5 and 6 below show the python code for determining if memory bit M9 has been tripped and changes the units from °F to °C to K.

![image](https://user-images.githubusercontent.com/47610444/144168777-dedb1ccc-454f-465c-a2a3-4fcb73dc74b5.png)
 
*Figure 5: Python code for changing temperature units*

![image](https://user-images.githubusercontent.com/47610444/144168788-af4c8002-dafe-49d6-817b-4118c928dd34.png)

*Figure 6: Conversion from °F to °C to K*

5.	Rung 11 in figure 2 determines if the ADC value from IW0.1 is greater than the value stored in register MW0.

7.	Figure 7 shows the python code for setting register MW0 to the alarm threshold.

![image](https://user-images.githubusercontent.com/47610444/144168823-f6c1c14b-a8a1-4121-a957-f0ec58e51e04.png)
 
*Figure 7: Writing the threshold value to MW0*

7.	Figure 8 below shows the python code for turning on the LED on Q0.1 and displaying “HIGH TEMP ALERT” to the terminal.

![image](https://user-images.githubusercontent.com/47610444/144168885-f404f340-6089-4e9c-a827-aee0cb5c5258.png)

*Figure 8: Turn on LED and display “HIGH TEMP ALERT”*

8.	Show in figure 7. This block of code is outside of the main loop.

![image](https://user-images.githubusercontent.com/47610444/144168941-b518ed72-2ad1-4bfb-8ebc-0e2269d494c6.png)

*Figure 9: ADC and temp values displayed on terminal*



## Objective 3:

![PySimpleGUI Screenshot](https://user-images.githubusercontent.com/47610444/144169043-c2a7829e-10b5-4e78-907b-42257944d79d.png)

Figure 10: Results of PySimpleGUI

Mini HVAC system:
![Mini HVAC system](https://user-images.githubusercontent.com/47610444/144299720-2cd91826-5fd5-43bc-b5aa-35dd97a051d7.jpg)

Mini HVAC system with heater on:
![Heater on](https://user-images.githubusercontent.com/47610444/144299718-e7aa18c6-0eff-4ccd-853b-fe7c4dfa9791.jpg)


## Work in progress: Implement a PID system
