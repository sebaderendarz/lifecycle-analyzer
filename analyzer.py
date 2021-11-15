import csv
import openpyxl
from typing import List, Tuple, Union

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtGui import QColor, QPainter, QPalette
from PyQt5.QtWidgets import (
    QComboBox,
    QGridLayout,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from exceptions import NoDataException
from kaplan_meier import KaplanMeierAnalyzer
from weibull import WeibullAnalyzer


class Analyzer(QWidget):

    DEFAULT_CHART_DATA = []
    DEFAULT_MESSAGE = "Upload file with data to get Weibull and Kaplan-Meier analysis results"
    DEFAULT_WEIBULL_K = 0
    DEFAULT_WEIBULL_LAMBDA = 0
    DEFAULT_DATA_FILENAME = None

    def __init__(self, parent=None) -> None:
        super(Analyzer, self).__init__(parent)
        self.m_charts = []
        self.setDisplayValues()
        self.createInteractiveElements()
        self.connectSignals()
        self.createWeibullChart()
        self.createKaplanMeierChart()
        self.createLayout()
        self.updateUI()

    def setDisplayValues(
        self,
        fileName: Union[str, None] = None,
        message: Union[str, None] = None,
        dataTableWei: Union[list, None] = None,
        paramK: Union[str, None] = None,
        paramLambda: Union[str, None] = None,
        dataTableKaplan: Union[list, None] = None,
    ) -> None:
        self.m_dataFileName = fileName if fileName else Analyzer.DEFAULT_DATA_FILENAME
        self.m_message = message if message else Analyzer.DEFAULT_MESSAGE
        self.m_weibullDataTable = dataTableWei if dataTableWei else Analyzer.DEFAULT_CHART_DATA
        self.m_kaplanMeierDataTable = (
            dataTableKaplan if dataTableKaplan else Analyzer.DEFAULT_CHART_DATA
        )
        self.m_weibullParamK = paramK if paramK else Analyzer.DEFAULT_WEIBULL_K
        self.m_weibullParamLambda = paramLambda if paramLambda else Analyzer.DEFAULT_WEIBULL_LAMBDA

    def createInteractiveElements(self) -> None:
        self.m_themeComboBox = self.createThemeBox()
        self.m_animatedComboBox = self.createAnimationBox()
        self.m_legendComboBox = self.createLegendBox()
        self.m_uploadDataButton = self.createGetDataButton()
        self.m_messageLabel = self.createLabel(self.m_message)
        self.m_weibullParamKLabel = self.createLabel(str(self.m_weibullParamK))
        self.m_weibullParamLambdaLabel = self.createLabel(str(self.m_weibullParamLambda))

    def createThemeBox(self) -> QComboBox:
        themeComboBox = QComboBox()
        themeComboBox.addItem("Light", QChart.ChartThemeLight)
        themeComboBox.addItem("Blue Cerulean", QChart.ChartThemeBlueCerulean)
        themeComboBox.addItem("Dark", QChart.ChartThemeDark)
        themeComboBox.addItem("Brown Sand", QChart.ChartThemeBrownSand)
        themeComboBox.addItem("Blue NCS", QChart.ChartThemeBlueNcs)
        themeComboBox.addItem("High Contrast", QChart.ChartThemeHighContrast)
        themeComboBox.addItem("Blue Icy", QChart.ChartThemeBlueIcy)
        return themeComboBox

    def createAnimationBox(self) -> QComboBox:
        animationComboBox = QComboBox()
        animationComboBox.addItem("No Animations", QChart.NoAnimation)
        animationComboBox.addItem("GridAxis Animations", QChart.GridAxisAnimations)
        animationComboBox.addItem("Series Animations", QChart.SeriesAnimations)
        animationComboBox.addItem("All Animations", QChart.AllAnimations)
        return animationComboBox

    def createLegendBox(self) -> QComboBox:
        legendComboBox = QComboBox()
        legendComboBox.addItem("No Legend ", 0)
        legendComboBox.addItem("Legend Top", Qt.AlignTop)
        legendComboBox.addItem("Legend Bottom", Qt.AlignBottom)
        legendComboBox.addItem("Legend Left", Qt.AlignLeft)
        legendComboBox.addItem("Legend Right", Qt.AlignRight)
        return legendComboBox

    def createGetDataButton(self) -> QPushButton:
        return QPushButton(self.createButtonName("Upload Data"))

    def createButtonName(self, name: str) -> str:
        span = "".join([" " for x in range(20)])
        return span + name + span

    def createLabel(self, name: str) -> QLabel:
        return QLabel(name)

    def connectSignals(self) -> None:
        self.m_themeComboBox.currentIndexChanged.connect(self.updateUI)
        self.m_animatedComboBox.currentIndexChanged.connect(self.updateUI)
        self.m_legendComboBox.currentIndexChanged.connect(self.updateUI)
        self.m_uploadDataButton.clicked.connect(self.analyzeUploadedFile)

    @pyqtSlot()
    def updateUI(self):
        self.updateDisplayTheme()
        self.updateChartsAnimation()
        self.updateChartsLegendAlignment()
        self.updateTextAreas()
        self.updateCharts()

    def updateDisplayTheme(self) -> None:
        theme = self.m_themeComboBox.itemData(self.m_themeComboBox.currentIndex())
        if self.m_charts[0].chart().theme() != theme:
            for chartView in self.m_charts:
                chartView.chart().setTheme(theme)
            pal = self.window().palette()
            if theme == QChart.ChartThemeLight:
                pal.setColor(QPalette.Window, QColor(0xF0F0F0))
                pal.setColor(QPalette.WindowText, QColor(0x404044))
            elif theme == QChart.ChartThemeDark:
                pal.setColor(QPalette.Window, QColor(0x121218))
                pal.setColor(QPalette.WindowText, QColor(0xD6D6D6))
            elif theme == QChart.ChartThemeBlueCerulean:
                pal.setColor(QPalette.Window, QColor(0x40434A))
                pal.setColor(QPalette.WindowText, QColor(0xD6D6D6))
            elif theme == QChart.ChartThemeBrownSand:
                pal.setColor(QPalette.Window, QColor(0x9E8965))
                pal.setColor(QPalette.WindowText, QColor(0x404044))
            elif theme == QChart.ChartThemeBlueNcs:
                pal.setColor(QPalette.Window, QColor(0x018BBA))
                pal.setColor(QPalette.WindowText, QColor(0x404044))
            elif theme == QChart.ChartThemeHighContrast:
                pal.setColor(QPalette.Window, QColor(0xFFAB03))
                pal.setColor(QPalette.WindowText, QColor(0x181818))
            elif theme == QChart.ChartThemeBlueIcy:
                pal.setColor(QPalette.Window, QColor(0xCEE7F0))
                pal.setColor(QPalette.WindowText, QColor(0x404044))
            else:
                pal.setColor(QPalette.Window, QColor(0xF0F0F0))
                pal.setColor(QPalette.WindowText, QColor(0x404044))
            self.window().setPalette(pal)

    def updateChartsAnimation(self) -> None:
        options = QChart.AnimationOptions(
            self.m_animatedComboBox.itemData(self.m_animatedComboBox.currentIndex())
        )
        if self.m_charts[0].chart().animationOptions() != options:
            for chartView in self.m_charts:
                chartView.chart().setAnimationOptions(options)

    def updateChartsLegendAlignment(self) -> None:
        alignment = self.m_legendComboBox.itemData(self.m_legendComboBox.currentIndex())
        for chartView in self.m_charts:
            legend = chartView.chart().legend()
            if alignment == 0:
                legend.hide()
            else:
                legend.setAlignment(Qt.Alignment(alignment))
                legend.show()

    def updateTextAreas(self) -> None:
        self.m_messageLabel.setText(str(self.m_message))
        self.m_weibullParamKLabel.setText(str(self.m_weibullParamK))
        self.m_weibullParamLambdaLabel.setText(str(self.m_weibullParamLambda))

    def updateCharts(self) -> None:
        self.updateWeibullChart()
        self.updateKaplanMeierChart()

    def updateWeibullChart(self) -> None:
        self.m_weibullChart.removeAllSeries()
        series = QLineSeries()
        for point in self.m_weibullDataTable:
            series.append(point)
        series.setName("Probability of Survival")
        self.m_weibullChart.addSeries(series)
        # TODO Adjust axes. Default don't show data properly
        self.m_weibullChart.createDefaultAxes()

    def updateKaplanMeierChart(self) -> None:
        self.m_kaplanMeierChart.removeAllSeries()
        series = QLineSeries()
        for point in self.m_kaplanMeierDataTable:
            series.append(point)
        series.setName("Probability of Survival")
        self.m_kaplanMeierChart.addSeries(series)
        # TODO Adjust axes. Default don't show axes properly
        self.m_kaplanMeierChart.createDefaultAxes()

    def analyzeUploadedFile(self) -> None:
        fileName = self.getFileName()
        chartDataWei, paramK, paramLambda, chartDataKaplan, message = None, None, None, None, None
        if fileName:
            try:
                chartDataWei, paramK, paramLambda, chartDataKaplan = self.analyzeData(fileName)
                message = f"Analyzed file path: {fileName}"
            except NoDataException:
                message = "Upload file containing at least one row of data to be analyzed"
            except Exception as e:
                message = "Upload file containing data in valid format"
        self.setDisplayValues(fileName, message, chartDataWei, paramK, paramLambda, chartDataKaplan)
        self.updateUI()

    def getFileName(self) -> Union[str, None]:
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Open Data File", filter="Data files (*.csv *.xlsx)"
        )
        return fileName

    def analyzeData(self, fileName: str) -> Tuple[list, str, str, list]:
        if fileName.endswith(".xlsx"):
            return self.analyzeDataInXlsxFormat(fileName)
        return self.analyzeDataInCsvFormat(fileName)

    def analyzeDataInXlsxFormat(self, fileName: str) -> Tuple[list, str, str, list]:
        keys, data = self.getDataFromXlsxFile(fileName)
        serialized_data = self.serializeXlsxData(keys, data)
        return self.getWeiBullAndKaplanMeierResults(keys, serialized_data)

    def getDataFromXlsxFile(self, fileName: str) -> Tuple[list, list]:
        ws = openpyxl.load_workbook(fileName).active
        data = list(ws.iter_rows(values_only=True))
        if len(data) < 2:
            raise NoDataException
        return list(data[0]), data[1:]

    def serializeXlsxData(self, keys: list, data: list) -> list:
        serialized_data = []
        for record in data:
            serialized_record = {}
            for key, value in zip(keys, record):
                serialized_record[key] = int(value) if keys[-1] == key else value
            serialized_data.append(serialized_record)
        return serialized_data

    def getWeiBullAndKaplanMeierResults(
        self, keys: list, data: list
    ) -> Tuple[list, str, str, list]:
        chartDataWei, paramK, paramLambda = WeibullAnalyzer().analyze(keys, data)
        chartDataKaplan = KaplanMeierAnalyzer().analyze(keys, data)
        return chartDataWei, paramK, paramLambda, chartDataKaplan

    def analyzeDataInCsvFormat(self, fileName: str) -> Tuple[list, str, str, list]:
        keys, data = self.getDataFromCsvFile(fileName)
        serialized_data = self.serializeCsvData(keys, data)
        return self.getWeiBullAndKaplanMeierResults(keys, serialized_data)

    def getDataFromCsvFile(self, fileName: str) -> Tuple[List, List]:
        with open(fileName) as f:
            dict_reader = csv.DictReader(f, delimiter=";")
            data = list(dict_reader)
        if len(data) < 1:
            raise NoDataException
        return list(data[0].keys()), data

    def serializeCsvData(self, keys: list, data: list) -> list:
        for record in data:
            record[keys[-1]] = int(record[keys[-1]])
        return data

    def createWeibullChart(self) -> None:
        self.m_weibullChart = QChart()
        self.m_weibullChart.setTitle("Weibull")

    def createKaplanMeierChart(self) -> QChart:
        self.m_kaplanMeierChart = QChart()
        self.m_kaplanMeierChart.setTitle("Kaplan-Meier")

    def createLayout(self) -> None:
        baseLayout = QGridLayout()
        settingsLayout = QHBoxLayout()
        settingsLayout.addWidget(QLabel("Theme:"))
        settingsLayout.addWidget(self.m_themeComboBox)
        settingsLayout.addWidget(QLabel("Animation:"))
        settingsLayout.addWidget(self.m_animatedComboBox)
        settingsLayout.addWidget(QLabel("Legend:"))
        settingsLayout.addWidget(self.m_legendComboBox)
        settingsLayout.addWidget(self.m_uploadDataButton)
        settingsLayout.addStretch()
        baseLayout.addLayout(settingsLayout, 0, 0, 1, 2)

        messageLayout = QHBoxLayout()
        messageLayout.addWidget(QLabel("INFO: "))
        messageLayout.addWidget(self.m_messageLabel)
        messageLayout.addStretch()
        baseLayout.addLayout(messageLayout, 1, 0, 1, 2)

        weibullParamsLayout = QHBoxLayout()
        weibullParamsLayout.addWidget(QLabel("Weibull K: "))
        weibullParamsLayout.addWidget(self.m_weibullParamKLabel)
        weibullParamsLayout.addWidget(QLabel("Weibull λ: "))
        weibullParamsLayout.addWidget(self.m_weibullParamLambdaLabel)
        weibullParamsLayout.addStretch()
        baseLayout.addLayout(weibullParamsLayout, 2, 0, 1, 2)

        chartView = QChartView(self.m_weibullChart)
        chartView.setRenderHint(QPainter.Antialiasing, True)
        baseLayout.addWidget(chartView, 3, 0)
        self.m_charts.append(chartView)
        chartView = QChartView(self.m_kaplanMeierChart)
        chartView.setRenderHint(QPainter.Antialiasing, True)
        baseLayout.addWidget(chartView, 3, 1)
        self.m_charts.append(chartView)

        self.setLayout(baseLayout)


if __name__ == "__main__":
    import sys

    from PyQt5.QtWidgets import QApplication, QMainWindow

    app = QApplication(sys.argv)

    window = QMainWindow()
    widget = Analyzer()
    window.setCentralWidget(widget)
    window.resize(900, 600)
    window.show()

    sys.exit(app.exec_())
