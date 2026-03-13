import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QDateEdit, QPushButton, QGroupBox, QMessageBox, QListWidget, QAbstractItemView, QFileDialog
)
from PyQt6.QtCore import QDate, Qt
import database

# Matplotlib integration
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import numpy as np

class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Filters Section
        filter_group = QGroupBox("Filter Dashboard")
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)

        # Date From
        date_from_vbox = QVBoxLayout()
        date_from_vbox.addWidget(QLabel("Date From:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        # Default to 7 days ago
        self.date_from.setDate(QDate.currentDate().addDays(-7))
        date_from_vbox.addWidget(self.date_from)

        # Date To
        date_to_vbox = QVBoxLayout()
        date_to_vbox.addWidget(QLabel("Date To:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        date_to_vbox.addWidget(self.date_to)

        # Class Filter (Multi-select list)
        class_vbox = QVBoxLayout()
        class_vbox.addWidget(QLabel("Classes (Hold Ctrl to select multiple):"))
        self.class_list = QListWidget()
        self.class_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        classes = ["11 Class (Boys)", "11 Class (Girls)", "12 Class (Boys)", "12 Class (Girls)"]
        self.class_list.addItems(classes)
        # Select all by default
        for i in range(self.class_list.count()):
            self.class_list.item(i).setSelected(True)
        # Restrict height so it doesn't take up too much vertical space
        self.class_list.setMaximumHeight(80) 
        class_vbox.addWidget(self.class_list)

        # Section Filter
        section_vbox = QVBoxLayout()
        section_vbox.addWidget(QLabel("Section:"))
        self.section_combo = QComboBox()
        self.section_combo.addItems(["All Sections", "PMB+PEB", "PCSB", "RMB+REB", "RCSB-1", "RCSB-2", "RICB"])
        section_vbox.addWidget(self.section_combo)

        # View Type Filter
        view_type_vbox = QVBoxLayout()
        view_type_vbox.addWidget(QLabel("Chart View:"))
        self.view_type_combo = QComboBox()
        self.view_type_combo.addItems([
            "Both (Numbers & Percentage)", 
            "Number of Students Only", 
            "Percentage Only"
        ])
        view_type_vbox.addWidget(self.view_type_combo)

        # Generate Button & Export Button
        btns_layout = QVBoxLayout()
        btns_layout.addWidget(QLabel("")) # Spacer
        
        btn_generate = QPushButton("Generate Report")
        btn_generate.setObjectName("actionButton")
        btn_generate.clicked.connect(self.generate_report)
        btns_layout.addWidget(btn_generate)
        
        btn_export = QPushButton("Export Data (CSV)")
        btn_export.clicked.connect(self.export_data)
        btns_layout.addWidget(btn_export)

        filter_layout.addLayout(date_from_vbox)
        filter_layout.addLayout(date_to_vbox)
        filter_layout.addLayout(class_vbox, stretch=2)
        filter_layout.addLayout(section_vbox)
        filter_layout.addLayout(view_type_vbox)
        filter_layout.addLayout(btns_layout)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Chart Section
        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        
        # Add interactive Matplotlib toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # Make background transparent to match modern dark theme
        self.figure.patch.set_facecolor('#1e1e1e')
        self.ax.set_facecolor('#1e1e1e')
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.current_df = None # Store latest df for export

    def generate_report(self):
        start_date = self.date_from.date().toString("yyyy-MM-dd")
        end_date = self.date_to.date().toString("yyyy-MM-dd")
        
        selected_classes = [item.text() for item in self.class_list.selectedItems()]
        section_filter = self.section_combo.currentText()

        # Fetch records. Using "All Classes" to bypass the single filter in database.py
        # We will filter in pandas for the multi-select
        data = database.get_attendance(start_date, end_date, "All Classes", section_filter)
        
        df = pd.DataFrame(data) if data else pd.DataFrame()
        
        # Filter dataframe by our multi-selected classes
        if not df.empty and selected_classes:
            df = df[df['class_name'].isin(selected_classes)]

        if df.empty:
            self.ax.clear()
            self.ax.set_title(f"No data available for selected filters.", color='white')
            # Reset modern styling
            self.ax.patch.set_facecolor('#1e1e1e')
            self.ax.tick_params(colors='white')
            self.canvas.draw()
            self.current_df = None
            QMessageBox.information(self, "No Data", "No attendance records found for the given criteria.")
            return

        self.current_df = df

        # Group by date to aggregate Presents and Absents across all selected classes
        grouped = df.groupby('date').agg({
            'total_students': 'sum',
            'presents': 'sum',
            'absents': 'sum'
        }).reset_index()

        grouped['percentage'] = (grouped['presents'] / grouped['total_students'] * 100).round(2)
        
        view_type = self.view_type_combo.currentText()

        # Clear entire figure to prevent overlapping twinx axes on re-renders
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.patch.set_facecolor('#1e1e1e')
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        
        # Plotting Setup
        dates = grouped['date'].tolist()
        presents = grouped['presents'].tolist()
        absents = grouped['absents'].tolist()
        percentages = grouped['percentage'].tolist()
        
        x = np.arange(len(dates))
        width = 0.35
        
        lines_handles = []
        lines_labels = []

        if view_type in ["Both (Numbers & Percentage)", "Number of Students Only"]:
            # Plot stacked/side-by-side bars for pure numbers instead of just percentage
            # Bar 1: Presents (Green-ish)
            rects_present = self.ax.bar(x - width/2, presents, width, color='#2ecc71', label='Presents')
            # Bar 2: Absents (Red-ish)
            rects_absent = self.ax.bar(x + width/2, absents, width, color='#e74c3c', label='Absents')
            
            self.ax.set_ylabel('Student Count', color='white')
            self.ax.yaxis.label.set_color('white')
            
            # Attach text labels to the bars
            self.ax.bar_label(rects_present, padding=3, color='white')
            self.ax.bar_label(rects_absent, padding=3, color='white')
            
            handles, labels = self.ax.get_legend_handles_labels()
            lines_handles.extend(handles)
            lines_labels.extend(labels)

        if view_type in ["Both (Numbers & Percentage)", "Percentage Only"]:
            if view_type == "Both (Numbers & Percentage)":
                target_ax = self.ax.twinx()
                target_color = '#f1c40f'
                target_ax.tick_params(axis='y', colors=target_color)
                target_ax.spines['right'].set_color('gray')
                target_ax.spines['top'].set_visible(False)
                target_ax.spines['left'].set_visible(False)
                target_ax.spines['bottom'].set_color('gray')
            else:
                target_ax = self.ax
                target_color = '#f1c40f'
                target_ax.tick_params(axis='y', colors='white')
                target_ax.yaxis.label.set_color('white')

            line = target_ax.plot(x, percentages, color=target_color, marker='o', linewidth=2, label='Attendance %')
            target_ax.set_ylabel('Percentage (%)', color=target_color if view_type == "Both (Numbers & Percentage)" else 'white')
            target_ax.set_ylim(0, 105)
            
            lines_handles.extend(line)
            lines_labels.append('Attendance %')

        self.ax.set_title(f'Attendance Overview', color='white')
        self.ax.set_xticks(x, dates)
        self.ax.tick_params(axis='x', rotation=45, colors='white')
        
        self.ax.legend(lines_handles, lines_labels, facecolor='#1e1e1e', labelcolor='white', edgecolor='gray', loc='upper left')
        
        # Base aesthetics
        self.figure.patch.set_facecolor('#1e1e1e')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_color('gray')
        self.ax.spines['left'].set_color('gray')

        self.figure.tight_layout()
        self.canvas.draw()

    def export_data(self):
        if self.current_df is None or self.current_df.empty:
            QMessageBox.warning(self, "Export Error", "No data to export. Generate a report first.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Export File", "Attendance_Export.csv", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                # Add human readable timestamp
                self.current_df.to_csv(file_path, index=False)
                QMessageBox.information(self, "Success", f"Data exported successfully to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to save file: {str(e)}")
