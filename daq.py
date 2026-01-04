from datetime import datetime
from labjack import ljm
import csv
import sys
import fun

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

class DAQWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Live Labjack DAQ')
        self.resize(800, 600)

        # Layout
        layout =  QVBoxLayout(self)
        self.tempLabel = QLabel('Temperature -- °F')
        self.pressLabel = QLabel('Pressure -- PSI')
        self.startButton = QPushButton('Stream')
        self.stopButton = QPushButton('Stop')

        layout.addWidget(self.tempLabel)
        layout.addWidget(self.pressLabel)
        layout.addWidget(self.startButton)
        layout.addWidget(self.stopButton)

        # Plot
        self.plotWidget = pg.PlotWidget(title = 'Live Temperature & Pressure')
        self.plotWidget.addLegend()
        layout.addWidget(self.plotWidget)

        self.tempCurve = self.plotWidget.plot(pen = 'r', name = 'Temp °F')
        self.pressCurve = self.plotWidget.plot(pen = 'b', name = 'Pressure PSI')

        # Plot Data
        self.times = []
        self.temps = []
        self.pressures = []

        # Update Window
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)

        # Start / End
        self.startButton.clicked.connect(self.start_stream)
        self.stopButton.clicked.connect(self.stop_stream)

        self.handle = None

    def start_stream(self):
        self.handle = ljm.openS('ANY', 'ANY', 'ANY')
        self.IN_NAMES = ['AIN0', 'AIN2']
        self.NUM_IN_CHANNELS = len(self.IN_NAMES)

        self.scanList = ljm.namesToAddresses(self.NUM_IN_CHANNELS, self.IN_NAMES)[0]
        self.scanRate = 1000
        self.scansPerRead = int(self.scanRate / 2)

        ljm.eWriteName(self.handle, 'AIN2_RANGE', 0.01)
        ljm.eWriteName(self.handle, 'AIN2_NEGATIVE_CH', 3)

        ljm.eStreamStart(self.handle, self.scansPerRead, self.NUM_IN_CHANNELS, self.scanList, self.scanRate)

        self.timer.start(100)

        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)

        self.csvfile = open('ain_log.csv', 'w', newline='')
        self.writer = csv.writer(self.csvfile)
        self.writer.writerow(['Timestamp', 'AIN0 (V)', 'Pressure (PSI)', 'AIN2 (V)', 'Temperature (°F)'])

        print('Streaming started...')

    def update_data(self):
        if not self.handle:
            return

        ret = ljm.eStreamRead(self.handle)
        data = ret[0]

        for i in range(self.scansPerRead):
            ain0 = data[i * self.NUM_IN_CHANNELS]
            ain2 = data[i * self.NUM_IN_CHANNELS + 1]
            psi = fun.voltage_to_psi(ain0)
            temp = fun.voltage_to_fahrenheit(ain2)
            timestamp = datetime.now().strftime('%H:%M:%S')

            self.writer.writerow([timestamp, ain0, psi, ain2, temp])

            self.times.append(len(self.times))
            self.temps.append(temp)
            self.pressures.append(psi)

            # Update To Most Recent Data Points
            if len(self.times) > 500:
                self.times = self.times[500:]
                self.temps = self.temps[500:]
                self.pressures = self.pressures[500:]

        self.tempLabel.setText(f'Temperature: {temp:.2f} °F')
        self.pressLabel.setText(f'Pressure: {psi:.2f} PSI')

        self.tempCurve.setData(self.times, self.temps)
        self.pressCurve.setData(self.times, self.pressures)

    def stop_stream(self):
        if self.handle:
            self.timer.stop()
            ljm.eStreamStop(self.handle)
            ljm.close(self.handle)
            self.handle = None
            print('Stream stopped.')

        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)

        if hasattr(self, 'csvfile'):
            self.csvfile.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DAQWindow()
    window.show()
    sys.exit(app.exec_())
