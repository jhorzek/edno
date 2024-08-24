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
            os.system("Xvfb :1 -screen 0 1600x1200x16  &")
            os.environ["DISPLAY"] = ":1.0"
        self.root = ctk.CTk()
        self.app = edno.EdnoCanvas(self.root)

    def test_nodes(self):
        class CM:
            def __init__(self, position):
                self.position = position

        self.app.context_menu = CM(position=[1, 3])
        self.app.canvas_context_menu.create_node(
            self.app.canvas_context_menu.node_classes["Ellipse"], "Ellipse"
        )
        self.app.context_menu = None

        self.app.context_menu = CM(position=[11, 2])
        self.app.canvas_context_menu.create_node(
            self.app.canvas_context_menu.node_classes["Rectangle"], "Rectangle"
        )
        self.app.context_menu = None
        # new_node = edno.Node(self.app.canvas, "first_node", 1, 10, "composite")
        # self.app.nodes.append
        self.assertEqual(len(self.app.nodes), 2)
        self.assertEqual(self.app.nodes[0].label, "node_1")
        self.assertEqual(self.app.coords(self.app.nodes[0].node_id), [1.0, 3.0])

        self.assertEqual(self.app.nodes[1].label, "node_2")
        self.assertEqual(self.app.coords(self.app.nodes[1].node_id), [11.0, 2.0])

        # check that we cannot create a node with the same name
        self.assertFalse(edno.check_label("node_1", self.app.nodes))

        # deleting nodes
        self.app.nodes[1].delete()
        self.assertEqual(len(self.app.nodes), 1)

        # move node
        self.app.nodes[0].move(delta_x=2.0, delta_y=-1.0)
        self.assertEqual(self.app.coords(self.app.nodes[0].node_id), [3.0, 2.0])
        self.assertRaises(ValueError, self.app.nodes[0].move_to, x=2.0, y=1.0)
        self.assertEqual(self.app.coords(self.app.nodes[0].node_id), [3.0, 2.0])

        # add arrow between nodes
        self.app.context_menu = CM(position=[1, 3])
        self.app.canvas_context_menu.create_node(
            self.app.canvas_context_menu.node_classes["Ellipse"], "Ellipse"
        )
        self.app.context_menu = None

        self.app.drawing_arrow = True
        self.app.arrow_start_node = self.app.nodes[1].node_id
        self.app.nodes[0].draw_arrow(event=None)
        self.app.drawing_arrow = False
        if self.app.temporary_arrow is not None:
            self.app.delete(self.app.temporary_arrow)

        # save node
        save_node = self.app.nodes[0].save()
        self.assertEqual(
            save_node,
            {
                "id": self.app.nodes[0].node_id,
                "type": "Ellipse",
                "label": "node_1",
                "position": [3.0, 2.0],
                "predictors": ["node_2"],
                "dependents": [],
            },
        )
        save_node = self.app.nodes[1].save()
        self.assertEqual(
            save_node,
            {
                "id": self.app.nodes[1].node_id,
                "type": "Ellipse",
                "label": "node_2",
                "position": [1.0, 3.0],
                "predictors": [],
                "dependents": ["node_1"],
            },
        )

        # delete connection
        self.app.arrows[0].delete()
        save_node = self.app.nodes[0].save()
        self.assertEqual(
            save_node,
            {
                "id": self.app.nodes[0].node_id,
                "type": "Ellipse",
                "label": "node_1",
                "position": [3.0, 2.0],
                "predictors": [],
                "dependents": [],
            },
        )
        save_node = self.app.nodes[1].save()
        self.assertEqual(
            save_node,
            {
                "id": self.app.nodes[1].node_id,
                "type": "Ellipse",
                "label": "node_2",
                "position": [1.0, 3.0],
                "predictors": [],
                "dependents": [],
            },
        )
        self.app.reset()

    def test_arrows(self):
        class CM:
            def __init__(self, position):
                self.position = position

        self.app.context_menu = CM(position=[1, 3])
        self.app.canvas_context_menu.create_node(
            self.app.canvas_context_menu.node_classes["Ellipse"], "Ellipse"
        )
        self.app.context_menu = None

        self.app.context_menu = CM(position=[11, 2])
        self.app.canvas_context_menu.create_node(
            self.app.canvas_context_menu.node_classes["Rectangle"], "Rectangle"
        )
        self.app.context_menu = None

        self.app.drawing_arrow = True
        self.app.arrow_start_node = self.app.nodes[1].node_id
        self.app.current_arrow_type = "directed"
        self.app.nodes[0].draw_arrow(event=None)
        self.app.drawing_arrow = False
        if self.app.temporary_arrow is not None:
            self.app.delete(self.app.temporary_arrow)

        self.assertEqual(len(self.app.arrows), 1)
        self.assertEqual(self.app.arrows[0].predictors_id, self.app.nodes[1].node_id)
        self.assertEqual(self.app.arrows[0].dependents_id, self.app.nodes[0].node_id)

        # move arrow
        start_coords = self.app.coords(self.app.arrows[0].id)
        self.app.nodes[1].move(delta_x=3.0, delta_y=1.0)
        # set estimate
        self.app.arrows[0].set_estimate(0.5, sig="**")

        # save arrow
        save_arrow = self.app.arrows[0].save()
        self.assertEqual(
            save_arrow,
            {
                "id": self.app.arrows[0].id,
                "arrow_type": "directed",
                "text": "0.50**",
                "parameter_label": "",
                "estimate": 0.5,
                "significance": "**",
                "position": self.app.coords(self.app.arrows[0].id),
                "predictors": self.app.nodes[1].get_label(),
                "predictors_type": self.app.nodes[1].type,
                "dependents": self.app.nodes[0].get_label(),
                "dependents_type": self.app.nodes[0].type,
            },
        )

        self.app.arrows[0].estimate.parameter_label = "param_1"
        self.app.arrows[0].estimate.update_text()

        save_arrow = self.app.arrows[0].save()
        self.assertEqual(
            save_arrow,
            {
                "id": self.app.arrows[0].id,
                "arrow_type": "directed",
                "text": "param_1=0.50**",
                "parameter_label": "param_1",
                "estimate": 0.5,
                "significance": "**",
                "position": self.app.coords(self.app.arrows[0].id),
                "predictors": self.app.nodes[1].get_label(),
                "predictors_type": self.app.nodes[1].type,
                "dependents": self.app.nodes[0].get_label(),
                "dependents_type": self.app.nodes[0].type,
            },
        )

        # delete arrow
        self.app.arrows[0].delete()
        self.assertEqual(len(self.app.arrows), 0)
        self.app.reset()


class TestTextBox(unittest.TestCase):
    def test_textbox(self):
        if os.name != "nt" and os.getenv("GITHUB_ACTIONS"):
            os.system("Xvfb :1 -screen 0 1600x1200x16  &")
            os.environ["DISPLAY"] = ":1.0"
        root = ctk.CTk()
        app = edno.EdnoCanvas(root)
        text_box = edno.TextBox(app, x=1, y=10, label="my_text")
        self.assertEqual(text_box.label, "my_text")
        self.assertEqual(text_box.node_id, 1)
        box_position = app.coords(text_box.shape_id)
        text_box.move(delta_x=5, delta_y=1)
        self.assertEqual(app.coords(text_box.node_id), [6.0, 11.0])
        self.assertTrue(text_box.get_location() == app.coords(text_box.node_id))
        text_box.set_label("new_text")
        self.assertEqual(text_box.label, "new_text")

        text_box_1 = edno.TextBox(app, x=1, y=10, label="my_text")
        text_box_2 = edno.TextBox(app, x=12, y=2, label="my_text")
        self.assertEqual(
            text_box_1.distance(text_box_2), {"x_dist": -11.0, "y_dist": 8.0}
        )


if __name__ == "__main__":
    unittest.main()
