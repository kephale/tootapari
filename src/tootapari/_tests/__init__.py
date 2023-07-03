from tootapari import TootapariWidget


def test_widget_creation(make_napari_viewer):
    viewer = make_napari_viewer()
    wdg = TootapariWidget(viewer)
    assert wdg is not None
