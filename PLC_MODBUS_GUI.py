#
# import the client implementation
#
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import logging
import time
import PySimpleGUI as sg

#
# configure the client logging
#
FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)

#
# Modbus unit to talk to
#

MODBUS_ADDR = "192.168.8.202"  # IP address of PLC
MODBUS_PORT = 502


def get_adc(temp):
    m = (800 - 200) / (90 - 50)  # 200-800 adc = 2V-8V = 50F-90F
    b = 200 - (m * 50)
    y = m * temp + b
    return int(y)


def get_degrees_f(adc):
    m = (90 - 50) / (800 - 200)
    b = 50 - (m * 200)
    y = (m * adc) + b
    return y


def convert_f_to_c(f_temp):
    return (f_temp - 32.0) * (5.0 / 9.0)


def convert_f_to_k(f_temp):
    return 273.5 + ((f_temp - 32.0) * (5.0 / 9.0))


def run_sync_client():
    #
    # Connect to the PLC
    #
    client = ModbusClient(MODBUS_ADDR, port=MODBUS_PORT)
    client.connect()
    log.info(client)

    #
    # Print an info message
    #
    log.info("Assert %I0.0 on PLC to exit this program.")

    #
    # Put our addresses in variables so we can reference them by a meaningful name
    #
    M0ADDR = 0
    M1ADDR = 1
    M2ADDR = 2
    M3ADDR = 3
    M4ADDR = 4
    M5ADDR = 5
    M6ADDR = 6
    M7ADDR = 7
    M8ADDR = 8
    M9ADDR = 9
    MW0ADDR = 0
    MW1ADDR = 1
    MW2ADDR = 2
    MW3ADDR = 3

    temp_sel = 0
    window_open = 0
    heater = 'OFF'
    set_point = 70
    fan = 'FAN AUTO'

    # Initialize Temp Alarm
    alarm_threshold = float(85)
    alarm_adc_threshold = get_adc(alarm_threshold)
    wr = client.write_register(MW0ADDR, alarm_adc_threshold)
    assert not wr.isError()


    time.sleep(1)

    while True:
        #
        # Read %M7; if set, assert %M0 then break out of the loop
        #
        rr = client.read_coils(M7ADDR, 1)
        assert not rr.isError()
        if rr.bits[0]:
            rq = client.write_coil(M0ADDR, 1)
            assert not rq.isError()
            log.info(f"Breaking out of loop")
            break

        while True:
            rr = client.read_coils(M9ADDR, 1)
            assert not rr.isError()
            if rr.bits[0]:
                temp_sel += 1
                if temp_sel % 3 == 0:
                    temp_sel = 0
                break
            else:
                break

        while True:
            rr = client.read_coils(M1ADDR, 1)
            assert not rr.isError()
            if rr.bits[0]:
                log.info("HIGH TEMP ALERT")
                break
            else:
                break

        #
        # Read the values of the output register holding the ADC value
        #
        log.info(f"Reading ADC value from %MW2")
        rr = client.read_holding_registers(MW2ADDR, 1)
        assert not rr.isError()
        adc_value = rr.registers[0]
        log.info(f"ADC value = {adc_value}")
        temp_f = get_degrees_f(float(adc_value))
        temp_c = convert_f_to_c(float(temp_f))
        temp_k = convert_f_to_k(float(temp_f))
        temp_value = [temp_f, temp_c, temp_k]
        temp_value = tuple([float("{0:.2f}".format(n)) for n in temp_value])
        temp_units = [u'\N{DEGREE SIGN}F', u'\N{DEGREE SIGN}C', 'K']
        log.info(f"Temp = {temp_value[temp_sel]}{temp_units[temp_sel]}")

        current_temp = get_degrees_f((adc_value))


        sg.ChangeLookAndFeel('Dark')
        layout = [[sg.Text('Heater Status:', justification='center', font=("Helvetica", 12), relief=sg.RELIEF_RIDGE),
                   sg.Text(heater, key='-HEATER-')],
                  [sg.Text('Current Temp:', justification='center', font=("Helvetica", 12), relief=sg.RELIEF_RIDGE),
                   sg.Text(current_temp, key='-OUTPUT-')],
                  [sg.Text('Set Point:', justification='center', font=("Helvetica", 12), relief=sg.RELIEF_RIDGE),
                   sg.Text(set_point, key='-SETPOINT-')],
                  [sg.Button('DOWN'), sg.Button('UP')],
                  [sg.Text('Fan:', justification='center', font=("Helvetica", 12), relief=sg.RELIEF_RIDGE),
                   sg.Combo(['AUTO', 'FAN ON', 'FAN OFF'])],
                  [sg.Exit()]]

        if window_open == 0:
            window = sg.Window('Temperature Window', layout)
            window_open = 1

        event, values = window.read(timeout = 100)

        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        if event == 'DOWN':
            set_point -= 1
            window['-SETPOINT-'].update(set_point)
        elif event == 'UP':
            set_point += 1
            window['-SETPOINT-'].update(set_point)
        if set_point > current_temp:
            heater = 'ON'
            window['-HEATER-'].update(heater)
        else:
            heater = 'OFF'
            window['-HEATER-'].update(heater)

        if event == 'AUTO':
            while True:
                rr = client.read_coils(M6ADDR, 1)
                assert not rr.isError()
                if rr.bits[0]:
                    client.write_coil(M2ADDR, 1)
                    log.info("FAN AUTO ON")
                    break
                else:
                    client.write_coil(M2ADDR, 0)
                    log.info("FAN AUTO OFF")
                    break
        elif event == 'FAN ON':
            client.write_coil(M2ADDR, 1)
            log.info("FAN ON")
        elif event == 'FAN OFF':
            client.write_coil(M2ADDR, 0)
            log.info("FAN OFF")

        window['-OUTPUT-'].update(f'{current_temp: .2f}')

        #
        # Write set temp to register 1
        #
        wr = client.write_register(MW3ADDR, get_adc(set_point))
        assert not wr.isError()
    #
    # close the client
    #
    window.close()
    client.close()
    log.info(f'Exiting')

if __name__ == '__main__':
    run_sync_client()