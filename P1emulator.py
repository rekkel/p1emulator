from datetime import datetime
from dsmr_emulator import DSMREmulator
from guizero import App, Text, TextBox, PushButton, Combo, Box, ButtonGroup, CheckBox
import io
import random
import serial
import threading
import time
import traceback

FONT = 'Quicksand'

v_energy_import_t1 = 23214
v_energy_import_t2 = 53814
v_energy_export_t1 = 24210
v_energy_export_t2 = 24210


class EmulatorApp(App):
    def __init__(self):
        super().__init__(title='SMR5 P1 modulator', bg = 'white')
        self.tk.attributes("-fullscreen",True)
        self._stop = None
        self._send_p1_message_thread = None

        header = add_text(self, 'SMR5 P1 modulator', 'top', 20)
        self.app_message = add_text(self, 'Specify your P1 message and press \'Send P1 message(s) now\n', align = 'top')

        start_stop_box = Box(self, width = 'fill', align = 'bottom')
        space = add_text(start_stop_box, '', 'top', 5)
        sendButton = add_pushbutton(start_stop_box, self.send_p1_message, "Send P1 message(s) now",
                                    'right', '#33cc33')
        stopButton = add_pushbutton(start_stop_box, self.stop, 'Stop', 'right')
        exitButton = add_pushbutton(start_stop_box, exit, 'Exit')

        buttons_box = Box(self, 'fill', align = 'bottom')
        space2 = add_text(buttons_box, '', 'top', 6)
        self.row_choice = add_buttongroup(buttons_box, [['Fixed', 'F'], ['Random', 'R']], 'R', 'right')
        button_group_desc = add_text(buttons_box, ' Generate:', 'right')
        intervalMenuDescription = add_text(buttons_box, 'Message interval (sec):')
        self.intervalMenu = add_combo(buttons_box, [10, 1], 'left')
        amountMenuDescription = add_text(buttons_box, " Message amount:")
        self.amountMenu = add_combo(buttons_box, [1000000, 100000, 10000, 1000, 100, 10, 1], width = 7)

        export_box = Box(self, width = 'fill', align = 'bottom')
        export_box.bg = '#e6e6e6'
        space3 = add_text(export_box, '', 'bottom', 6)

        message_box = EmulatorBox(self, '', align = 'bottom')
        self.message = message_box.add_controls('Message ', 'EAN00000012345678;;;;;;', 1, 1, width = 29)
        self.export_l1 = add_checkbox(message_box, text="Export L1", grid = [4,1])
        self.export_l2 = add_checkbox(message_box, text="Export L2", grid = [5,1])
        self.export_l3 = add_checkbox(message_box, text="Export L3", grid = [6,1])

        input_box_fixed = EmulatorBox(self, 'Fixed', 'left')
        self.input_l1_u = input_box_fixed.add_controls('U L1', 230, 1, 1)
        self.input_l2_u = input_box_fixed.add_controls('U L2', 230, 1, 2)
        self.input_l3_u = input_box_fixed.add_controls('U L3', 230, 1, 3)
        self.input_l1_i = input_box_fixed.add_controls('I L1', 3, 1, 4)
        self.input_l2_i = input_box_fixed.add_controls('I L2', 3, 1, 5)
        self.input_l3_i = input_box_fixed.add_controls('I L3', 3, 1, 6)

        input_box_random = EmulatorBox(self, 'Random', 'right')
        self.input_l1_u_min = input_box_random.add_controls('U L1 min', 220, 1, 1)
        self.input_l2_u_min = input_box_random.add_controls('U L2 min', 220, 1, 2)
        self.input_l3_u_min = input_box_random.add_controls('U L3 min', 220, 1, 3)
        self.input_l1_i_min = input_box_random.add_controls('I L1 min', 3, 1, 4)
        self.input_l2_i_min = input_box_random.add_controls('I L2 min', 3, 1, 5)
        self.input_l3_i_min = input_box_random.add_controls('I L3 min', 3, 1, 6)
        self.input_l1_u_max = input_box_random.add_controls('U L1 max', 240, 3, 1)
        self.input_l2_u_max = input_box_random.add_controls('U L2 max', 240, 3, 2)
        self.input_l3_u_max = input_box_random.add_controls('U L3 max', 240, 3, 3)
        self.input_l1_i_max = input_box_random.add_controls('I L1 max', 25, 3, 4)
        self.input_l2_i_max = input_box_random.add_controls('I L2 max', 25, 3, 5)
        self.input_l3_i_max = input_box_random.add_controls('I L3 max', 25, 3, 6)

        self.display()

    def build_p1_message(self):
        global v_energy_import_t1
        global v_energy_import_t2
        global v_energy_export_t1
        global v_energy_export_t2

        d = create_dsmr_emulator_with_defaults(self)
        d.timestamp = datetime.now().astimezone()
        if self.row_choice.value == "F":
            d.voltage_l1 = float(self.input_l1_u.value)
            d.voltage_l2 = float(self.input_l2_u.value)
            d.voltage_l3 = float(self.input_l3_u.value)
            d.current_l1 = float(self.input_l1_i.value)
            d.current_l2 = float(self.input_l2_i.value)
            d.current_l3 = float(self.input_l3_i.value)
        elif self.row_choice.value == "R":
            d.voltage_l1 = random.randrange(int(self.input_l1_u_min.value), int(self.input_l1_u_max.value) + 1, 1)
            d.voltage_l2 = random.randrange(int(self.input_l2_u_min.value), int(self.input_l2_u_max.value) + 1, 1)
            d.voltage_l3 = random.randrange(int(self.input_l3_u_min.value), int(self.input_l3_u_max.value) + 1, 1)
            d.current_l1 = random.randrange(int(self.input_l1_i_min.value), int(self.input_l1_i_max.value) + 1, 1)
            d.current_l2 = random.randrange(int(self.input_l2_i_min.value), int(self.input_l2_i_max.value) + 1, 1)
            d.current_l3 = random.randrange(int(self.input_l3_i_min.value), int(self.input_l3_i_max.value) + 1, 1)
        d.power_import_l1, d.power_import_l2, d.power_import_l3, d.power_export_l1, d.power_export_l2, d.power_export_l3 = 0,0,0,0,0,0 
        if self.export_l1.value:
            d.power_export_l1 = max(0, (d.voltage_l1 * d.current_l1))
        else:    
            d.power_import_l1 = max(0, (d.voltage_l1 * d.current_l1))
        if self.export_l2.value == True:
            d.power_export_l2 = max(0, (d.voltage_l2 * d.current_l2))
        else:    
            d.power_import_l2 = max(0, (d.voltage_l2 * d.current_l2))
        if self.export_l3.value == True:
            d.power_export_l3 = max(0, (d.voltage_l3 * d.current_l3))
        else:    
            d.power_import_l3 = max(0, (d.voltage_l3 * d.current_l3))
            
        v_energy_import_t1 += 1
        v_energy_import_t2 += 2
        v_energy_export_t1 += 3
        v_energy_export_t2 += 4
        d.energy_import_t1 =  v_energy_import_t1
        d.energy_import_t2 =  v_energy_import_t2
        d.energy_export_t1 =  v_energy_export_t1
        d.energy_export_t2 =  v_energy_export_t2


        #d.energy_import_t1 = (d.power_import_l1 + d.power_import_l2 + d.power_import_l3) / 2
        #d.energy_import_t2 = (d.power_import_l1 + d.power_import_l2 + d.power_import_l3) / 2
        #d.energy_export_t1 = (d.power_export_l1 + d.power_export_l2 + d.power_export_l3) / 2
        #d.energy_export_t2 = (d.power_export_l1 + d.power_export_l2 + d.power_export_l3) / 2
        d.power_import = d.power_import_l1 + d.power_import_l2 + d.power_import_l3
        d.power_export = d.power_export_l1 + d.power_export_l2 + d.power_export_l3
        return d

    def send_p1_message(self):
        if not self._send_p1_message_thread:
            self._stop = threading.Event()
            
            def run():
                for _ in range(int(self.amountMenu.value)):
                    if self._stop.isSet():
                        break
                    d = self.build_p1_message()
                    try:
                        with serial.Serial("/dev/ttyUSB0", baudrate=115200) as s:
                            text_stream = io.StringIO(d.telegram)
                            for line in text_stream.readlines():
                                #print(line, end="")
                                s.write(line.encode('ascii'))
                                time.sleep(0.005)
                        print("Message verstuurd")
                        self.app_message.value = 'Message sent at: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n'
                        self._stop.wait(float(self.intervalMenu.value) - (38 * 0.005))
                    except:
                        print(traceback.format_exec())
                self.stop()
            self._send_p1_message_thread = threading.Thread(target=run)
            self._send_p1_message_thread.start()    
        
        elif not self._send_p1_message_thread.isAlive():
            self.stop()
            self.send_p1_message()

    def stop(self):
        if self._send_p1_message_thread: 
            self._stop.set()
            self._send_p1_message_thread.join(1)
            self._send_p1_message_thread = None

class EmulatorBox(Box):
    def __init__(self, parent, box_title, align):
        super().__init__(parent, width = 'fill', height = 'fill', layout='grid', align = align)
        self.bg = '#e6e6e6'

        self.header = add_text(self, box_title, grid = [0, 0])

    def add_controls(self, description, value, row, column, width = 10, height = 1, size = 14, font = FONT):                
        Text(self, description, size = size, font = font, grid=[row, column]) 
        text_box = TextBox(self, width = width, height = height, multiline = True, text = value, grid = [row + 1, column])
        text_box.bg = 'white'
        text_box.font = font
        text_box.text_size = size
        return text_box

def add_checkbox(app, text, align = 'right', size = 13, font = FONT, grid = []):
    if grid:
        checkbox = CheckBox(app, text = text, align = align, grid = grid)
    else:
        checkbox = CheckBox(app, text = text, align = align)
    checkbox.font = font
    checkbox.text_size = size
    checkbox.bg = 'white'
    return checkbox

def add_text(app, text, align = 'left', size = 13, font = FONT, grid = []):
    if grid:
        return Text(app, text, size = size, font = font, grid = grid, align = align)
    else:  # niet per se nodig, maar dan vermijd je de warnings
        return Text(app, text, size = size, font = font, align = align)


def add_combo(app, options, align = 'left', width = 2, size = 13, font = FONT): 
        combo = Combo(app, options, width = width, align = align)
        combo.font = font
        combo.bg = 'white'
        combo.text_size = size
        return combo


def add_buttongroup(app, options, selected, align, size = 13, font = FONT, grid = []):
    if grid:
        buttongroup = ButtonGroup(app, options = options, selected = selected, horizontal = False, grid = grid, align = align)
    else:
        buttongroup = ButtonGroup(app, options = options, selected = selected, horizontal = True, align = align)
    buttongroup.font = font
    buttongroup.text_size = size
    return buttongroup


def add_pushbutton(app, command, text, align = 'left', bg = 'white', size = 15, font = FONT):
    pushbutton = PushButton(app, command = command, text = text, align = align)
    pushbutton.bg = bg
    pushbutton.font = font
    pushbutton.text_size = size
    return pushbutton

def create_dsmr_emulator_with_defaults(self):
    d = DSMREmulator(name="SMR5 P1 Emulator")
    d.identifier = "45414E3030303030303132333435363738"
    d.dsmr_version = 50
    d.tariff_indicator = 1
    d.num_power_failures = 8
    d.num_long_power_failures = 2
    d.power_failure_log = 2
    d.num_voltage_sags_l1 = 1
    d.num_voltage_sags_l2 = 1
    d.num_voltage_sags_l3 = 2
    d.num_voltage_swells_l1 = 0
    d.num_voltage_swells_l2 = 0
    d.num_voltage_swells_l3 = 0
    d.text_message = self.message.value.strip('\n')
    d.mbus_device_type = "003"
    d.mbus_equipment_id = 3232323241424344313233343536373839
    d.five_min_gas_reading = "12785.123"
    return d 

if __name__ == '__main__':
    app = EmulatorApp()
    exit()
