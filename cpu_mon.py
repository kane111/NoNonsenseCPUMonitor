from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout

from kivy import Config

Config.set('graphics', 'width', '300')
Config.set('graphics', 'height', '200')
Config.set('graphics', 'resizable', False)

from kivymd.uix.label import MDLabel
from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsBase

from threading import Thread
import psutil
import time

'''
Declare some global variables that are going to be passed around.
'''

core_dict = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}
core_num = 8

battery_state = "Charging"
battery_capacity = "100"

stop_threads = False

'''
Load the KV files for tab content
'''

Builder.load_file('batteryTab.kv')
Builder.load_file('cpuTab.kv')

'''
Our functions that fetch the system parameters
Note that these functions are run in 
separate threads using the threading module.
'''


def get_cpu():
    global core_num, core_dict, stop_threads

    while True:
        time.sleep(0.3)
        cpu_use = psutil.cpu_percent(2, True)
        core_num = len(cpu_use)
        for i in range(core_num):
            core_dict.update({i + 1: cpu_use[i]})
        if stop_threads:
            print("stop")
            break


def get_battery():
    global battery_state, battery_capacity, stop_threads

    while True:
        time.sleep(0.3)
        battery_state = open("/sys/class/power_supply/BAT0/status", "r").readline().strip()
        battery_capacity = open("/sys/class/power_supply/BAT0/capacity", "r").readline().strip()
        if stop_threads:
            print("stop")
            break


'''
Our custom self-updating Labels. 
We are using the KivyMD library instead of the standard Kivy library
So, Labels are MDLabels and henceforth. 
'''


class CpuUsageCore(MDLabel):

    def __init__(self, core, **kwargs):
        super(CpuUsageCore, self).__init__(**kwargs)
        self.core = core
        self.text = "CPU " + str(self.core) + "    " + str(core_dict[self.core]) + "%"
        Clock.schedule_interval(self.update, 0.5)
        self.halign = 'center'

    def update(self, *args):
        self.text = "CPU " + str(self.core) + "    " + str(core_dict[self.core]) + "%"


class BatteryState(MDLabel):

    def __init__(self, **kwargs):
        super(BatteryState, self).__init__(**kwargs)
        self.text = battery_state
        Clock.schedule_interval(self.update, 1)
        self.halign = 'center'

    def update(self, *args):
        self.text = battery_state


class BatteryCapacity(MDLabel):

    def __init__(self, **kwargs):
        super(BatteryCapacity, self).__init__(**kwargs)
        self.text = battery_capacity
        Clock.schedule_interval(self.update, 1)
        self.halign = 'center'

    def update(self, *args):
        self.text = battery_capacity


'''
The Tabs in the KivyMD library are to be placed in the MDTabs container
Check main.kv file.
Also, check batteryTab.kv and cpuTab.kv for their structure.
'''


class CPUTab(FloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''


class BatteryTab(FloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''


'''
Grid created to accommodate and show info on different number of cores
for each computer
'''


class CpuWidget(GridLayout):

    def __init__(self, **kwargs):
        super(CpuWidget, self).__init__(**kwargs)
        self.id = 'cpuWidget'
        self.cols = 1
        for i in range(core_num):
            self.add_widget(CpuUsageCore(i + 1))


'''
We're using MDApp because we're using KivyMD. 
Also, I've defined some extra functions to add functionality
and practice safe-thread executions
'''


class MainApp(MDApp):
    global stop_threads

    def build(self):
        return Builder.load_file("main.kv")

    def on_start(self):
        self.root.ids.main_tabs.add_widget(BatteryTab())
        self.root.ids.main_tabs.add_widget(CPUTab())

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        instance_tab.ids.text = tab_text

    def on_stop(self):
        stop_threads = True


'''
Finally, execution!
'''

if __name__ == '__main__':
    get_cpu_thread = Thread(target=get_cpu)
    get_cpu_thread.daemon = True
    get_cpu_thread.start()

    get_battery_thread = Thread(target=get_battery)
    get_battery_thread.daemon = True
    get_battery_thread.start()

    MainApp().run()
