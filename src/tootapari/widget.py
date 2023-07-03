import os

from appdirs import user_config_dir, user_cache_dir
from dotenv import load_dotenv
from mastodon import Mastodon
from pathlib import Path

from qtpy.QtWidgets import (
    QPushButton,
    QWidget,
    QCheckBox,
    QVBoxLayout,
    QLabel,
    QPlainTextEdit,
)


load_dotenv(Path(user_config_dir("tootapari", "kephale")) / ".env")


class TootapariWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.mastodon = None

        # Textbox for entering prompt
        self.toot_textbox = QPlainTextEdit(self)
        self.toot_textbox.appendPlainText(
            "Tooted from #napari with #tootapari."
        )

        self.screenshot_checkbox = QCheckBox(self)

        btn = QPushButton("Toot!")
        btn.clicked.connect(self._on_click)

        # Layout and labels
        self.setLayout(QVBoxLayout())

        label = QLabel(self)
        label.setText("Message")
        self.layout().addWidget(label)
        self.layout().addWidget(self.toot_textbox)

        label = QLabel(self)
        label.setText("Screenshot with UI")
        self.layout().addWidget(label)
        self.layout().addWidget(self.screenshot_checkbox)

        self.layout().addWidget(btn)

    def login_mastodon(self):
        if self.mastodon:
            return
        self.mastodon = Mastodon(
            access_token=os.getenv("MASTODON_ACCESS_TOKEN"),
            api_base_url=os.getenv("MASTODON_INSTANCE_URL"),
        )
        return self.mastodon

    def _on_click(self):
        self.toot()

    def toot(self):
        if not self.login_mastodon():
            print("cannot login to mastodon")
            return
        screenshot_path = (
            Path(user_cache_dir("tootapari", "kephale"))
            / "tootapari_screenshot.png"
        )

        self.viewer.screenshot(
            screenshot_path, canvas_only=(not self.get_screenshot_with_ui())
        )

        text = self.toot_textbox.document().toPlainText()

        alt_text = f"A screenshot automatically generated with tootapari. The corresponding toot is: {text}."

        # Make a tempfile for the image
        media_metadata = self.mastodon.media_post(
            screenshot_path, mime_type="image/png", description=alt_text
        )

        self.mastodon.status_post(text, media_ids=media_metadata["id"])

    def get_screenshot_with_ui(self):
        return self.screenshot_checkbox.checkState()


if __name__ == "__main__":
    import napari

    viewer = napari.Viewer()
    viewer.window.resize(800, 600)

    widget = TootapariWidget(viewer)

    viewer.window.add_dock_widget(widget, name="tootapari")
