from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class SettingsScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        categories = QListWidget()
        categories.addItems(
            ["Rede", "Seguranca", "Relatorios", "Armazenamento", "Notificacoes", "Sistema"]
        )
        categories.setCurrentRow(0)
        categories.setMaximumWidth(180)
        categories.setAlternatingRowColors(True)

        categories_panel = QWidget()
        categories_layout = QVBoxLayout(categories_panel)
        categories_layout.setContentsMargins(0, 0, 0, 0)
        categories_layout.setSpacing(10)
        categories_title = QLabel("Categorias")
        categories_title.setObjectName("SectionTitle")
        categories_layout.addWidget(categories_title)
        categories_layout.addWidget(categories, 1)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)

        title = QLabel("Configuracoes de rede")
        title.setObjectName("SectionTitle")
        content_layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.interface_combo = QComboBox()
        self.interface_combo.addItems(["eth0 (192.168.1.100)", "wlan0"])

        self.primary_dns = QLineEdit("8.8.8.8")
        self.secondary_dns = QLineEdit("8.8.4.4")
        self.gateway = QLineEdit("192.168.1.254")
        self.max_connections = QSpinBox()
        self.max_connections.setRange(1, 4096)
        self.max_connections.setValue(256)

        form.addRow("Interface de rede:", self.interface_combo)
        form.addRow("DNS primario:", self.primary_dns)
        form.addRow("DNS secundario:", self.secondary_dns)
        form.addRow("Gateway padrao:", self.gateway)
        form.addRow("Max. conexoes:", self.max_connections)

        self.ipv6_checkbox = QCheckBox("Habilitar IPv6")
        self.ipv6_checkbox.setChecked(True)
        self.proxy_checkbox = QCheckBox("Usar proxy")

        buttons = QHBoxLayout()
        buttons.addWidget(QPushButton("Aplicar"))
        buttons.addWidget(QPushButton("Cancelar"))
        buttons.addWidget(QPushButton("Restaurar padrao"))
        buttons.addStretch(1)

        content_layout.addLayout(form)
        content_layout.addWidget(self.ipv6_checkbox)
        content_layout.addWidget(self.proxy_checkbox)
        content_layout.addStretch(1)
        content_layout.addLayout(buttons)

        layout.addWidget(categories_panel)
        layout.addWidget(content, 1)
