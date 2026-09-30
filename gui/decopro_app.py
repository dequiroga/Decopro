"""
    GUI App to run DecoPro

"""
import pathlib
import sys
import pandas as pd

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QPushButton,
    QTextEdit,
    QLabel,
    QFileDialog,
    QProgressBar
)
from decompaction import main
from libs import readers


class Worker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, data_df):
        super().__init__()
        self.data_df = data_df

    @Slot()
    def run(self):
        try:
            text_output = main(data_df=self.data_df)
            self.finished.emit(text_output)
        except Exception as e:
            self.error.emit(str(e))


class DataFrameModel(QAbstractTableModel):
    def __init__(self, dataframe):
        super().__init__()
        self.df = dataframe.copy()

    def rowCount(self, parent=QModelIndex()):
        return len(self.df)

    def columnCount(self, parent=QModelIndex()):
        return len(self.df.columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role in (
            Qt.ItemDataRole.DisplayRole,
            Qt.ItemDataRole.EditRole,
        ):
            value = self.df.iloc[index.row(), index.column()]
            return str(value)

        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role != Qt.ItemDataRole.EditRole or not index.isValid():
            return False

        self.df.iloc[index.row(), index.column()] = value
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.ItemIsEnabled

        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
        )

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return str(self.df.columns[section])

        return str(section + 1)

    def add_row(self):
        new_row = {column: "" for column in self.df.columns}

        self.beginInsertRows(
            QModelIndex(),
            len(self.df),
            len(self.df),
        )

        self.df.loc[len(self.df)] = new_row.values()

        self.endInsertRows()

    def remove_rows(self, rows):
        for row in sorted(rows, reverse=True):
            self.beginRemoveRows(QModelIndex(), row, row)
            self.df.drop(self.df.index[row], inplace=True)
            self.endRemoveRows()

        # Reset the DataFrame index after deleting rows
        self.df.reset_index(drop=True, inplace=True)


class MainWindow(QWidget):
    def __init__(self, dataframe):
        super().__init__()

        self.worker = None
        self.thread = None
        self.setWindowTitle("DecoPro")
        self.resize(800, 600)

        self.open_button = QPushButton("Load From CSV")
        self.open_button.clicked.connect(self.open_csv)

        # Model
        self.model = DataFrameModel(dataframe)

        # Table
        self.table = QTableView()
        self.table.setModel(self.model)

        # Allow selecting whole rows
        self.table.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QTableView.SelectionMode.ExtendedSelection
        )

        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate / "busy"
        self.progress.setVisible(False)

        # Buttons
        self.add_button = QPushButton("Add Row")
        self.remove_button = QPushButton("Remove Selected")
        self.submit_button = QPushButton("Submit")

        self.add_button.clicked.connect(self.add_row)
        self.remove_button.clicked.connect(self.remove_rows)
        self.submit_button.clicked.connect(self.submit)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()
        button_layout.addWidget(self.submit_button)


        # Output
        self.output_label = QLabel("Output:")
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
        layout.addWidget(self.output_label)
        layout.addWidget(self.output)
        layout.addWidget(self.progress)

        self.setLayout(layout)

    def open_csv(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load From CSV",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )

        if not filename:
            return

        try:

            data_df = readers.read_layer_data(data_path=pathlib.Path(filename))

            # Replace the current model with the new DataFrame
            self.model = DataFrameModel(data_df)
            self.table.setModel(self.model)

        except Exception as e:
            self.output.setPlainText(
                f"Error loading CSV:\n{e}"
            )

    def add_row(self):
        self.model.add_row()

        # Scroll to the newly added row
        last_row = self.model.rowCount() - 1
        self.table.scrollTo(
            self.model.index(last_row, 0)
        )

    def remove_rows(self):
        selection = self.table.selectionModel().selectedRows()

        rows = [index.row() for index in selection]

        if rows:
            self.model.remove_rows(rows)

    def submit(self):
        self.submit_button.setEnabled(False)
        self.progress.setVisible(True)
        self.output.clear()

        data_df = self.model.df.copy()

        self.thread = QThread()
        self.worker = Worker(data_df)

        self.worker.moveToThread(self.thread)

        # Start the worker
        self.thread.started.connect(self.worker.run)

        # Worker results
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)

        # Stop the thread after the worker finishes
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)

        # Delete worker after the thread has stopped
        self.thread.finished.connect(self.worker.deleteLater)

        # Clean up the thread itself
        self.thread.finished.connect(self.on_thread_finished)

        self.thread.start()

    def on_finished(self, text_output):
        self.output.setPlainText(text_output)

        self.progress.setVisible(False)
        self.submit_button.setEnabled(True)

    def on_error(self, error_message):
        self.output.setPlainText(f"Error\n{error_message}")

        self.progress.setVisible(False)
        self.submit_button.setEnabled(True)

    def on_thread_finished(self):
        self.thread.deleteLater()

        self.thread = None
        self.worker = None



if __name__ == "__main__":
    df = pd.DataFrame({
        "id": [],
        "h": [],
        "z2": [],
        "z1": [],
        "c": [],
        "phi_0": [],
    })
    app = QApplication(sys.argv)
    window = MainWindow(df)
    window.show()
    sys.exit(app.exec())
