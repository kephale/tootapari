import os

from magicgui import magic_factory

from appdirs import user_config_dir, user_cache_dir
from dotenv import load_dotenv
from mastodon import Mastodon
from pathlib import Path


global mastodon
mastodon = None

load_dotenv(Path(user_config_dir("tootapari", "kephale")) / ".env")


def login_mastodon():
    global mastodon
    if mastodon:
        return
    mastodon = Mastodon(
        access_token=os.getenv("MASTODON_ACCESS_TOKEN"),
        api_base_url=os.getenv("MASTODON_INSTANCE_URL"),
    )
    return mastodon


@magic_factory(
    call_button="Toot!",
)
def toot_widget(
    viewer: "napari.viewer.Viewer",
    text: str = "Tooted from napari with tootapari.",
    screenshot_with_ui=True,
):
    global mastodon
    login_mastodon()
    screenshot_path = (
        Path(user_cache_dir("tootapari", "kephale"))
        / "tootapari_screenshot.png"
    )

    viewer.screenshot(screenshot_path, canvas_only=(not screenshot_with_ui))

    # Make a tempfile for the image
    media_metadata = mastodon.media_post(screenshot_path, "image/png")

    mastodon.status_post(text, media_ids=media_metadata["id"])


if __name__ == "__main__":
    import napari

    viewer = napari.Viewer()
    viewer.window.resize(800, 600)

    widget = toot_widget()

    viewer.window.add_dock_widget(widget, name="tootapari")
