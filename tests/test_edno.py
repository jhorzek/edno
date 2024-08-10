import unittest
import os
import customtkinter as ctk
import edno


# when running as a github action, we need to set up a 
# virtual display for the app to run.
# see https://stackoverflow.com/questions/67760308/test-tkinter-tcl-gui-using-github-actions

class TestGUI(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if os.name != "nt" and os.getenv("GITHUB_ACTIONS"):
            os.system('Xvfb :1 -screen 0 1600x1200x16  &')
            os.environ["DISPLAY"] = ":1.0"
        self.root = ctk.CTk()
        self.app = edno.EdnoCanvas(self.root)
        
    def test_nodes(self):
        class CM:
            def __init__(self, position):
                self.position = position
        self.app.context_menu = CM(position = [1, 3])
        self.app.canvas_context_menu.create_ellipse()
        self.app.context_menu = None

        self.app.context_menu = CM(position = [11, 2])
        self.app.canvas_context_menu.create_rectangle()
        self.app.context_menu = None
        # new_node = edno.Node(self.app.canvas, "first_node", 1, 10, "composite")
        # self.app.nodes.append
        self.assertEqual(len(self.app.nodes), 2)
        self.assertEqual(self.app.nodes[0].text, "var_1")
        self.assertEqual(self.app.coords(self.app.nodes[0].node_id), [1.0, 3.0])

        self.assertEqual(self.app.nodes[1].text, "var_2")
        self.assertEqual(self.app.coords(self.app.nodes[1].node_id), [11.0, 2.0])

        # check that we cannot create a node with the same name
        self.assertFalse(edno.check_label("var_2", self.app.nodes))

        # deleting nodes
        self.app.nodes[1].delete()
        self.assertEqual(len(self.app.nodes), 1)

        # move node
        self.app.nodes[0].move(delta_x = 2.0, delta_y = -1.0)
        self.assertEqual(self.app.coords(self.app.nodes[0].node_id), [3.0, 2.0])
        self.assertRaises(ValueError, self.app.nodes[0].move_to, x = 2.0, y = 1.0)
        self.assertEqual(self.app.coords(self.app.nodes[0].node_id), [3.0, 2.0])

        # add arrow between nodes
        self.app.context_menu = CM(position = [1, 3])
        self.app.canvas_context_menu.create_ellipse()
        self.app.context_menu = None

        self.app.drawing_arrow = True
        self.app.arrow_start_node = self.app.nodes[1].node_id
        self.app.nodes[0].draw_arrow(event=None)
        self.app.drawing_arrow = False

        # check arrow coordinates
        start_coords = self.app.coords(self.app.arrows[0].id)
        self.app.nodes[1].move(delta_x = 3.0, delta_y = 1.0)
        self.assertEqual(self.app.coords(self.app.arrows[0].id),
                        [start_coords[0] + 3.0, start_coords[1] + 1.0, start_coords[2], start_coords[3]])
        
        # save node
        save_node = self.app.nodes[0].save()
        self.assertEqual(save_node, {
            "id": self.app.nodes[0].node_id,
            "label": "var_1",
            "type": "ellipse",
            "position": [3.0, 2.0],
            "predictors": ["var_2"],
            "dependents": [],
            "r2": None
        })
        save_node = self.app.nodes[1].save()
        self.assertEqual(save_node, {
            "id": self.app.nodes[1].node_id,
            "label": "var_2",
            "type": "ellipse",
            "position": [4.0, 4.0],
            "predictors": [],
            "dependents": ["var_1"],
            "r2": None
        })

        # delete connection
        self.app.arrows[0].delete()
        save_node = self.app.nodes[0].save()
        self.assertEqual(save_node, {
            "id": self.app.nodes[0].node_id,
            "label": "var_1",
            "type": "ellipse",
            "position": [3.0, 2.0],
            "predictors": [],
            "dependents": [],
            "r2": None
        })
        save_node = self.app.nodes[1].save()
        self.assertEqual(save_node, {
            "id": self.app.nodes[1].node_id,
            "label": "var_2",
            "type": "ellipse",
            "position": [4.0, 4.0],
            "predictors": [],
            "dependents": [],
            "r2": None
        })
        self.app.reset()

    def test_arrows(self):
        class CM:
            def __init__(self, position):
                self.position = position
        self.app.context_menu = CM(position = [1, 3])
        self.app.canvas_context_menu.create_ellipse()
        self.app.context_menu = None

        self.app.context_menu = CM(position = [11, 2])
        self.app.canvas_context_menu.create_rectangle()
        self.app.context_menu = None

        self.app.drawing_arrow = True
        self.app.arrow_start_node = self.app.nodes[1].node_id
        self.app.nodes[0].draw_arrow(event=None)
        self.app.drawing_arrow = False

        self.assertEqual(len(self.app.arrows), 1)
        self.assertEqual(self.app.arrows[0].predictors_id, self.app.nodes[1].node_id)
        self.assertEqual(self.app.arrows[0].dependents_id, self.app.nodes[0].node_id)

        # move arrow
        start_coords = self.app.coords(self.app.arrows[0].id)
        self.app.nodes[1].move(delta_x = 3.0, delta_y = 1.0)
        self.assertEqual(self.app.coords(self.app.arrows[0].id),
                        [start_coords[0] + 3.0, start_coords[1] + 1.0, start_coords[2], start_coords[3]])

        # save arrow
        save_arrow = self.app.arrows[0].save()
        self.assertEqual(save_arrow, {
            "id": self.app.arrows[0].id,
            "estimate": None,
            "significance": None,
            "position": [start_coords[0] + 3.0, start_coords[1] + 1.0, start_coords[2], start_coords[3]],
            "predictors": self.app.nodes[1].get_label(),
            "dependents": self.app.nodes[0].get_label()
        })

        # delete arrow
        self.app.arrows[0].delete()
        self.assertEqual(len(self.app.arrows), 0)
        self.app.reset()


class TestTextBox(unittest.TestCase):
    def test_textbox(self):
        if os.name != "nt" and os.getenv("GITHUB_ACTIONS"):
            os.system('Xvfb :1 -screen 0 1600x1200x16  &')
            os.environ["DISPLAY"] = ":1.0"
        root = ctk.CTk()
        app = edno.EdnoCanvas(root)
        text_box = edno.TextBox(app, x=1, y=10, text="my_text")
        self.assertEqual(text_box.text, 'my_text')
        self.assertEqual(text_box.text_id, 1)
        self.assertEqual(text_box.shape, 'rectangle')
        box_position = app.coords(text_box.shape_id)
        text_box.move(delta_x = 5, delta_y = 1)
        self.assertEqual(app.coords(text_box.text_id), [6.0, 11.0])
        self.assertTrue(text_box.get_location() == app.coords(text_box.text_id))
        text_box.set_text("new_text")
        self.assertEqual(text_box.text, 'new_text')

        text_box_1 = edno.TextBox(app, x=1, y=10, text="my_text")
        text_box_2 = edno.TextBox(app, x=12, y=2, text="my_text")
        self.assertEqual(edno.distance(text_box_1, text_box_2),
                         {'x_dist': -11.0, 'y_dist': 8.0})

if __name__ == '__main__':
    unittest.main()
