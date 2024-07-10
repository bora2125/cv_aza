import cv2
import numpy as np
import streamlit as st

class PolygonDrawer:
    def __init__(self):
        self.points = []
        self.drawing = False
        self.dragging = False
        self.drag_point = None

    def draw_polygon(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if not self.drawing:
                for i, point in enumerate(self.points):
                    if np.sqrt((x - point[0])**2 + (y - point[1])**2) < 10:
                        self.dragging = True
                        self.drag_point = i
                        return
            self.drawing = True
            self.points.append((x, y))
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.dragging and self.drag_point is not None:
                self.points[self.drag_point] = (x, y)
            if self.drawing or self.dragging:
                if self.drawing and not self.dragging:
                    cv2.line(param['img_copy'], self.points[-1], (x, y), (0, 255, 0), 2)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.dragging = False
            self.drag_point = None
        elif event == cv2.EVENT_RBUTTONDOWN:
            if self.points:
                closest_point = min(self.points, key=lambda p: (p[0]-x)**2 + (p[1]-y)**2)
                self.points.remove(closest_point)

    def update_image(self, img):
        img_copy = img.copy()
        if len(self.points) > 1:
            cv2.polylines(img_copy, [np.array(self.points)], False, (0, 255, 0), 2)
        for point in self.points:
            cv2.circle(img_copy, point, 3, (0, 0, 255), -1)
        return img_copy

    def draw_help_box(self, image):
        help_text = [
            "Commands:",
            "Left Click: Add/Drag point",
            "Right Click: Delete nearest point",
            "Close polygon: Button",
            "Undo last point: Button",
            "Reset all: Button",
            "Finish drawing: Button"
        ]
        
        box_margin = 10
        line_height = 20
        font_scale = 0.5
        font_thickness = 1
        box_width = 250
        box_height = len(help_text) * line_height + 2 * box_margin
        
        overlay = image.copy()
        cv2.rectangle(overlay, (image.shape[1] - box_width, 0), 
                      (image.shape[1], box_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)
        
        for i, line in enumerate(help_text):
            cv2.putText(image, line, 
                        (image.shape[1] - box_width + box_margin, (i + 1) * line_height), 
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)
        return image

def create_polygon_drawer(image):
    drawer = PolygonDrawer()
    img_copy = image.copy()
    img_with_help = drawer.draw_help_box(img_copy)
    
    st.image(img_with_help, channels="RGB", use_column_width=True)
    canvas_result = st.empty()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Cerrar polígono"):
            if len(drawer.points) > 2:
                cv2.line(img_copy, drawer.points[-1], drawer.points[0], (0, 255, 0), 2)
    with col2:
        if st.button("Deshacer último punto"):
            if drawer.points:
                drawer.points.pop()
    with col3:
        if st.button("Reiniciar"):
            drawer.points.clear()
    with col4:
        if st.button("Finalizar dibujo"):
            st.session_state.drawing_finished = True

    # Manejo de eventos del mouse
    canvas_result.on_click(lambda x, y: handle_mouse_event(drawer, img_copy, x, y, cv2.EVENT_LBUTTONDOWN))
    canvas_result.on_mouse_move(lambda x, y: handle_mouse_event(drawer, img_copy, x, y, cv2.EVENT_MOUSEMOVE))

    return drawer.points

def handle_mouse_event(drawer, img, x, y, event):
    drawer.draw_polygon(event, int(x), int(y), None, {'img_copy': img})
    updated_img = drawer.update_image(img)
    st.image(updated_img, channels="RGB", use_column_width=True)
