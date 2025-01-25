from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QCheckBox, QPushButton, QScrollArea, QWidget
import sys


def show_checklist_popup(type_map, max_visible_items=10):
    """
    Create and display a checklist popup based on the provided type_map.

    Args:
        type_map (dict): A dictionary where keys are types and values are lists.
        max_visible_items (int): Maximum number of checkboxes visible before enabling scrolling.

    Returns:
        list: A list of selected types.
    """
    app = QApplication.instance() or QApplication(sys.argv)  # Ensure QApplication exists
    dialog = QDialog()
    dialog.setWindowTitle("Check List")

    layout = QVBoxLayout()
    checkboxes = []
    
    # Create a scrollable area for the checkboxes
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_widget = QWidget()
    scroll_layout = QVBoxLayout(scroll_widget)
    scroll_widget.setLayout(scroll_layout)
    
    # Create checkboxes for each key in the type_map
    for key, values in type_map.items():
        checkbox = QCheckBox(f"{key}: {len(values)}")
        scroll_layout.addWidget(checkbox)
        checkboxes.append((key, checkbox))
    
    # Add the scrollable area to the layout only if needed
    if len(checkboxes) > max_visible_items:
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
    else:
        layout.addWidget(scroll_widget)

    ok_button = QPushButton("확인")
    layout.addWidget(ok_button)

    def on_ok():
        # Store selected types in the dialog
        dialog.selected_types = [key for key, checkbox in checkboxes if checkbox.isChecked()]
        dialog.accept()

    ok_button.clicked.connect(on_ok)
    dialog.setLayout(layout)
    dialog.exec_()

    # Return the selected types
    return dialog.selected_types
