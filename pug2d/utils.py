import sf
from .core import Camera

VERTICAL = 0
HORIZONTAL = 1

def split_view(camera, orientation, ratio=0.5):
    view = camera.object
    viewport = view.viewport
    if orientation == VERTICAL:
        w0 = w1 = view.width
        h0 = ratio*view.height
        h1 = view.height-h0
        wf0 = wf1 = viewport.width
        hf0 = ratio*viewport.height
        hf1 = viewport.height-hf0
        xf = viewport.left
        yf = viewport.top+ratio*viewport.height
    else:
        w0 = ratio*view.width
        w1 = view.width-w0
        h0 = h1 = view.height
        wf0 = ratio*viewport.width
        wf1 = viewport.width-wf0
        hf0 = hf1 = viewport.height
        xf = viewport.left+ratio*viewport.width
        yf = viewport.top
    
    x0 = w0//2
    y0 = h0//2
    x1 = w1//2
    y1 = h1//2
    view1 = sf.View.from_center_and_size((x0, y0), (w0, h0))
    view2 = sf.View.from_center_and_size((x1, y1), (w1, h1))
    view1.viewport = sf.FloatRect(viewport.left, viewport.top, wf0, hf0)
    view2.viewport = sf.FloatRect(xf, yf, wf1, hf1)
    return Camera(view1), Camera(view2)
