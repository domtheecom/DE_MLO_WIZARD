from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QDoubleSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QInputDialog,
)

from .builder import BuildError, build_resource
from .logging_utils import LogBus
from .shell_library import ShellLibrary


class MainWindow(QMainWindow):
    def __init__(self, base_dir: Path, log_bus: LogBus, logger) -> None:
        super().__init__()
        self.base_dir = base_dir
        self.log_bus = log_bus
        self.logger = logger
        self.library = ShellLibrary(base_dir)
        self.setWindowTitle("DE Scripts MLO Studio")
        self.setMinimumSize(980, 680)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.build_tab = QWidget()
        self.shell_tab = QWidget()
        self.export_tab = QWidget()
        self.logs_tab = QWidget()

        self.tabs.addTab(self.build_tab, "Build")
        self.tabs.addTab(self.shell_tab, "Shell Library")
        self.tabs.addTab(self.export_tab, "Export")
        self.tabs.addTab(self.logs_tab, "Logs")

        self._init_build_tab()
        self._init_shell_tab()
        self._init_export_tab()
        self._init_logs_tab()

        self._load_shells()
        self._load_branding()

        self.log_bus.subscribe(self._append_log)

    def _load_branding(self) -> None:
        branding_file = self.base_dir / "assets" / "branding.json"
        if not branding_file.exists():
            return
        branding = json.loads(branding_file.read_text(encoding="utf-8"))
        theme = branding.get("theme", {})
        accent = theme.get("accent", "#d62828")
        panel = theme.get("panel", "#1c1c1c")
        background = theme.get("background", "#121212")
        text = theme.get("text", "#f5f5f5")

        self.setStyleSheet(
            "QMainWindow { background-color: %s; color: %s; }"
            "QWidget { color: %s; }"
            "QTabWidget::pane { border: 1px solid %s; }"
            "QTabBar::tab { background: %s; padding: 10px; }"
            "QTabBar::tab:selected { background: %s; color: %s; }"
            "QPushButton { background-color: %s; color: white; padding: 8px 12px; border-radius: 4px; }"
            "QPushButton:hover { background-color: %s; }"
            "QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QListWidget { background-color: %s; border: 1px solid #333; padding: 6px; }"
            "QGroupBox { border: 1px solid #333; margin-top: 6px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }"
            % (
                background,
                text,
                text,
                accent,
                panel,
                accent,
                text,
                accent,
                theme.get("accent_secondary", accent),
                panel,
            )
        )

    def _init_build_tab(self) -> None:
        layout = QVBoxLayout()

        title = QLabel("DE Scripts MLO Studio")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignLeft)
        layout.addWidget(title)

        form_group = QGroupBox("Build Settings")
        form_layout = QFormLayout()

        self.prompt_input = QPlainTextEdit()
        self.prompt_input.setPlaceholderText("Describe the MLO build...")
        self.prompt_input.setPlainText(
            "Miami Dade Fire Rescue House 51 with 2 bays, dorms, kitchen, and a dispatch office."
        )

        self.resource_name_input = QLineEdit("de_mlo_build")

        output_layout = QHBoxLayout()
        self.output_path_input = QLineEdit(str(self.base_dir / "output"))
        output_button = QPushButton("Browse")
        output_button.clicked.connect(self._select_output_folder)
        output_layout.addWidget(self.output_path_input)
        output_layout.addWidget(output_button)

        coords_layout = QHBoxLayout()
        self.coord_x = QDoubleSpinBox()
        self.coord_y = QDoubleSpinBox()
        self.coord_z = QDoubleSpinBox()
        self.heading = QDoubleSpinBox()
        for widget in (self.coord_x, self.coord_y, self.coord_z, self.heading):
            widget.setRange(-999999.0, 999999.0)
            widget.setDecimals(3)
        self.heading.setRange(-360.0, 360.0)
        coords_layout.addWidget(QLabel("X"))
        coords_layout.addWidget(self.coord_x)
        coords_layout.addWidget(QLabel("Y"))
        coords_layout.addWidget(self.coord_y)
        coords_layout.addWidget(QLabel("Z"))
        coords_layout.addWidget(self.coord_z)
        coords_layout.addWidget(QLabel("Heading"))
        coords_layout.addWidget(self.heading)

        self.shell_dropdown = QComboBox()
        self.shell_dropdown.addItem("Auto")

        self.copy_shell_checkbox = QCheckBox("Copy Shell Files Into Resource")

        form_layout.addRow("Prompt", self.prompt_input)
        form_layout.addRow("Resource Name", self.resource_name_input)
        form_layout.addRow("Output Folder", output_layout)
        form_layout.addRow("Base Coords", coords_layout)
        form_layout.addRow("Shell Selector", self.shell_dropdown)
        form_layout.addRow("", self.copy_shell_checkbox)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self._generate)
        self.open_output_button = QPushButton("Open Output Folder")
        self.open_output_button.clicked.connect(self._open_output_folder)
        self.copy_steps_button = QPushButton("Copy CodeWalker Steps")
        self.copy_steps_button.clicked.connect(self._copy_steps)

        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.open_output_button)
        button_layout.addWidget(self.copy_steps_button)
        layout.addLayout(button_layout)

        self.build_tab.setLayout(layout)

    def _init_shell_tab(self) -> None:
        layout = QVBoxLayout()
        self.shell_list = QListWidget()
        import_button = QPushButton("Import Shell Folder")
        import_button.clicked.connect(self._import_shell)

        layout.addWidget(QLabel("Available Shells"))
        layout.addWidget(self.shell_list)
        layout.addWidget(import_button)
        self.shell_tab.setLayout(layout)

    def _init_export_tab(self) -> None:
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Export output is created when you click Generate."))
        layout.addWidget(QLabel("Use the Build tab to generate resources."))
        self.export_tab.setLayout(layout)

    def _init_logs_tab(self) -> None:
        layout = QVBoxLayout()
        self.logs_output = QTextEdit()
        self.logs_output.setReadOnly(True)
        layout.addWidget(self.logs_output)
        self.logs_tab.setLayout(layout)

    def _append_log(self, message: str) -> None:
        self.logs_output.append(message)

    def _select_output_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_path_input.setText(folder)

    def _open_output_folder(self) -> None:
        path = Path(self.output_path_input.text()).expanduser()
        if path.exists():
            QDesktopServices.openUrl(path.as_uri())
        else:
            QMessageBox.warning(self, "Output Folder", "Output folder does not exist yet.")

    def _copy_steps(self) -> None:
        instructions = (
            "1. Open CodeWalker.\n"
            "2. Load the generated PLACEME.ymap.\n"
            "3. Select the anchor prop at origin.\n"
            "4. Move/rotate as needed and export final YMAP."
        )
        QApplication.clipboard().setText(instructions)
        QMessageBox.information(self, "Copied", "CodeWalker steps copied to clipboard.")

    def _load_shells(self) -> None:
        self.shell_dropdown.clear()
        self.shell_dropdown.addItem("Auto")
        self.shell_list.clear()
        for shell in self.library.load_shells():
            self.shell_dropdown.addItem(shell["shell_name"])
            self.shell_list.addItem(shell["shell_name"])

    def _import_shell(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Shell Folder")
        if not folder:
            return
        shell_name, ok = QInputDialog.getText(self, "Shell Name", "Enter shell name:")
        if not ok or not shell_name:
            return
        try:
            metadata = self.library.import_shell_folder(Path(folder), shell_name)
            self.logger.info("Imported shell: %s", metadata.shell_name)
            self._load_shells()
        except Exception as exc:
            QMessageBox.critical(self, "Import Failed", str(exc))

    def _generate(self) -> None:
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Missing Prompt", "Please enter a prompt.")
            return

        resource_name = self.resource_name_input.text().strip()
        if not resource_name:
            QMessageBox.warning(self, "Missing Resource Name", "Please enter a resource name.")
            return

        output_dir = Path(self.output_path_input.text()).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)

        coords = (
            self.coord_x.value(),
            self.coord_y.value(),
            self.coord_z.value(),
            self.heading.value(),
        )

        try:
            resource_path = build_resource(
                base_dir=self.base_dir,
                prompt=prompt,
                resource_name=resource_name,
                output_dir=output_dir,
                base_coords=coords,
                shell_selection=self.shell_dropdown.currentText(),
                copy_shell_files=self.copy_shell_checkbox.isChecked(),
                logger=self.logger,
            )
        except BuildError as exc:
            QMessageBox.critical(self, "Build Failed", str(exc))
            return
        except Exception as exc:
            QMessageBox.critical(self, "Unexpected Error", f"{exc}")
            return

        QMessageBox.information(self, "Build Complete", f"Exported to {resource_path}")
        self.tabs.setCurrentWidget(self.logs_tab)
