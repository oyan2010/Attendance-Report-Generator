import os
import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QDateEdit, QLineEdit, QPushButton, QFileDialog, QMessageBox, QGroupBox, QStackedWidget
)
from PyQt6.QtCore import QDate, Qt
import database

class DataEntryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- Top Section: Common Metadata ---
        meta_group = QGroupBox("Report Information")
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(15)

        # Date
        date_vbox = QVBoxLayout()
        date_label = QLabel("Date:")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        date_vbox.addWidget(date_label)
        date_vbox.addWidget(self.date_edit)

        # Day
        day_vbox = QVBoxLayout()
        day_label = QLabel("Day:")
        self.day_combo = QComboBox()
        self.day_combo.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        # Set to current day
        current_day_index = QDate.currentDate().dayOfWeek() - 1
        if 0 <= current_day_index <= 6:
            self.day_combo.setCurrentIndex(current_day_index)
        day_vbox.addWidget(day_label)
        day_vbox.addWidget(self.day_combo)

        # Class
        class_vbox = QVBoxLayout()
        class_label = QLabel("Class:")
        self.class_combo = QComboBox()
        self.class_combo.addItems([
            "11 Class (Boys)", "11 Class (Girls)",
            "12 Class (Boys)", "12 Class (Girls)"
        ])
        class_vbox.addWidget(class_label)
        class_vbox.addWidget(self.class_combo)

        meta_layout.addLayout(date_vbox)
        meta_layout.addLayout(day_vbox)
        meta_layout.addLayout(class_vbox)
        meta_group.setLayout(meta_layout)
        layout.addWidget(meta_group)

        # --- Entry Method Selector ---
        entry_method_layout = QHBoxLayout()
        self.btn_manual = QPushButton("Manual Entry")
        self.btn_manual.setCheckable(True)
        self.btn_manual.setChecked(True)
        self.btn_upload = QPushButton("File Upload (CSV/Excel)")
        self.btn_upload.setCheckable(True)

        self.btn_manual.clicked.connect(lambda: self.switch_entry_method(0))
        self.btn_upload.clicked.connect(lambda: self.switch_entry_method(1))

        entry_method_layout.addWidget(self.btn_manual)
        entry_method_layout.addWidget(self.btn_upload)
        layout.addLayout(entry_method_layout)

        # --- Dynamic Entry Section ---
        self.stacked_widget = QStackedWidget()

        # 1. Manual Entry Widget
        manual_widget = QWidget()
        manual_layout = QVBoxLayout(manual_widget)
        
        # Section selection for Manual
        section_hlayout = QHBoxLayout()
        section_label = QLabel("Section:")
        self.section_combo = QComboBox()
        self.section_combo.addItems(["PMB+PEB", "PCSB", "RMB+REB", "RCSB-1", "RCSB-2", "RICB"])
        section_hlayout.addWidget(section_label)
        section_hlayout.addWidget(self.section_combo)
        manual_layout.addLayout(section_hlayout)
        
        input_hlayout = QHBoxLayout()
        
        self.total_input = QLineEdit()
        self.total_input.setPlaceholderText("Total Students")
        
        self.present_input = QLineEdit()
        self.present_input.setPlaceholderText("Presents")
        
        self.absent_input = QLineEdit()
        self.absent_input.setPlaceholderText("Absents")
        
        input_hlayout.addWidget(QLabel("Total:"))
        input_hlayout.addWidget(self.total_input)
        input_hlayout.addWidget(QLabel("Presents:"))
        input_hlayout.addWidget(self.present_input)
        input_hlayout.addWidget(QLabel("Absents:"))
        input_hlayout.addWidget(self.absent_input)
        
        manual_layout.addLayout(input_hlayout)
        
        btn_save_manual = QPushButton("Save Manual Entry")
        btn_save_manual.clicked.connect(self.save_manual_entry)
        btn_save_manual.setObjectName("actionButton")
        manual_layout.addWidget(btn_save_manual)
        manual_layout.addStretch()

        # 2. Upload Entry Widget
        upload_widget = QWidget()
        upload_layout = QVBoxLayout(upload_widget)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setStyleSheet("color: #888; border: 1px dashed #555; padding: 20px; border-radius: 5px;")
        
        btn_browse = QPushButton("Browse CSV/Excel...")
        btn_browse.clicked.connect(self.browse_file)
        
        btn_process_upload = QPushButton("Process && Save Data")
        btn_process_upload.clicked.connect(self.process_upload)
        btn_process_upload.setObjectName("actionButton")

        upload_layout.addWidget(self.file_label)
        upload_layout.addWidget(btn_browse)
        upload_layout.addWidget(btn_process_upload)
        upload_layout.addStretch()

        self.stacked_widget.addWidget(manual_widget)
        self.stacked_widget.addWidget(upload_widget)

        layout.addWidget(self.stacked_widget)
        layout.addStretch()
        
        self.setLayout(layout)
        self.switch_entry_method(0)
        self.selected_file_path = None

    def switch_entry_method(self, index):
        self.stacked_widget.setCurrentIndex(index)
        if index == 0:
            self.btn_manual.setChecked(True)
            self.btn_upload.setChecked(False)
        else:
            self.btn_manual.setChecked(False)
            self.btn_upload.setChecked(True)

    def save_manual_entry(self):
        total_str = self.total_input.text()
        present_str = self.present_input.text()
        absent_str = self.absent_input.text()

        if not total_str or not present_str or not absent_str:
            QMessageBox.warning(self, "Input Error", "Please fill in all manual entry fields.")
            return

        try:
            total = int(total_str)
            present = int(present_str)
            absent = int(absent_str)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Values must be integers.")
            return

        self._save_to_db(total, present, absent)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Attendance Data File", "",
            "Data Files (*.csv *.xlsx *.xls);;All Files (*)"
        )
        if file_path:
            self.selected_file_path = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.file_label.setStyleSheet("color: #4CAF50; border: 1px solid #4CAF50; padding: 20px; border-radius: 5px;")

    def process_upload(self):
        if not getattr(self, 'selected_file_path', None):
            QMessageBox.warning(self, "Error", "Please browse and select a file first.")
            return

        # Read the file
        try:
            if self.selected_file_path.endswith('.csv'):
                df = pd.read_csv(self.selected_file_path)
            else:
                df = pd.read_excel(self.selected_file_path)
            
            # Detect columns
            section_col = total_col = present_col = absent_col = None
            for col in df.columns:
                col_lower = str(col).lower()
                if 'class' in col_lower or 'section' in col_lower:
                    if not section_col: section_col = col
                elif 'total' in col_lower and 'student' in col_lower:
                    total_col = col
                elif 'present' in col_lower:
                    present_col = col
                elif 'absent' in col_lower:
                    absent_col = col

            if not total_col and 'Total' in df.columns: total_col = 'Total'
            if not present_col and 'Presents' in df.columns: present_col = 'Presents'
            if not absent_col and 'Absents' in df.columns: absent_col = 'Absents'
            if not section_col and 'Classes' in df.columns: section_col = 'Classes'
            
            if not (section_col and total_col and present_col and absent_col):
                if 'Classes' in df.columns and 'Total Students' in df.columns and 'Presents' in df.columns and 'Absents' in df.columns:
                    section_col, total_col, present_col, absent_col = 'Classes', 'Total Students', 'Presents', 'Absents'
                else:
                    QMessageBox.warning(self, "Parsing Error", 
                        "Could not find required columns (Classes, Total Students, Presents, Absents) in the file.")
                    return

            records_added = 0
            date_str = self.date_edit.date().toString("yyyy-MM-dd")
            day_str = self.day_combo.currentText()
            class_name = self.class_combo.currentText()

            import re

            for _, row in df.iterrows():
                sec_raw = str(row[section_col]).strip()
                if sec_raw.lower() in ('nan', 'none', '') or 'total' in sec_raw.lower():
                    continue
                
                # Extract code only: take whatever is before first space or bracket
                sec_code = re.split(r'[\s\(]', sec_raw)[0].strip()
                
                if not sec_code:
                    continue
                
                try:
                    total_val = int(pd.to_numeric(row[total_col]))
                    present_val = int(pd.to_numeric(row[present_col]))
                    absent_val = int(pd.to_numeric(row[absent_col]))
                except (ValueError, TypeError):
                    continue

                percentage = round((present_val / total_val) * 100, 2) if total_val > 0 else 0.0

                database.save_attendance(
                    date_str, day_str, class_name, sec_code,
                    total_val, present_val, absent_val, percentage
                )
                records_added += 1

            QMessageBox.information(self, "Success", 
                f"Successfully extracted and saved {records_added} section records for Class {class_name} on {date_str}!")
            
        except Exception as e:
            QMessageBox.critical(self, "Processing Error", f"Failed to process file: {str(e)}")

    def _save_to_db(self, total, present, absent):
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        day_str = self.day_combo.currentText()
        class_name = self.class_combo.currentText()
        section = self.section_combo.currentText()
        
        # Calculate Percentage
        if total > 0:
            percentage = round((present / total) * 100, 2)
        else:
            percentage = 0.0

        database.save_attendance(
            date_str, day_str, class_name, section, 
            total, present, absent, percentage
        )

        QMessageBox.information(self, "Success", 
            f"Attendance saved successfully for {class_name} ({section}) on {date_str}!\n"
            f"Total: {total}, Present: {present}, Absent: {absent}, Percentage: {percentage}%")
        
        # Clear inputs
        self.total_input.clear()
        self.present_input.clear()
        self.absent_input.clear()
